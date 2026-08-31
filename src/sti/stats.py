"""Inference on prediction accuracy.

Task specificity
----------------
Within-task accuracy (the leading diagonal of the specificity matrix) is compared
with each off-diagonal cell. Both come from the *same* participants, so the
comparison is paired; the legacy implementation treated them as two independent
groups, and additionally read its data from module-level globals ``within`` /
``across`` rather than from its own arguments, so the arguments were partly
ignored. The manuscript main text describes a bootstrap while the SI describes a
t-test; the only bootstrap call in the legacy code is commented out. A paired
bootstrap is implemented here, with a paired t-test available for comparison.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import ttest_rel


def paired_bootstrap(
    a: np.ndarray, b: np.ndarray, *, n_boot: int = 10_000, seed: int = 0, ci: float = 95.0
) -> dict:
    """Bootstrap the paired difference ``a - b`` over participants.

    Returns the observed mean difference, its confidence interval, and a
    one-sided p-value for ``mean(a) > mean(b)`` obtained by recentring the
    bootstrap distribution on zero.
    """
    a, b = np.asarray(a, float), np.asarray(b, float)
    if a.shape != b.shape:
        raise ValueError(f"paired samples must match: {a.shape} vs {b.shape}")
    d = a - b
    n = d.size
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_boot, n))
    boot = d[idx].mean(axis=1)

    observed = float(d.mean())
    lo, hi = np.percentile(boot, [(100 - ci) / 2, 100 - (100 - ci) / 2])
    # p-value: how often does a null-centred bootstrap reach the observed effect?
    null = boot - boot.mean()
    p = (np.sum(null >= observed) + 1) / (n_boot + 1)
    return {
        "difference": observed,
        "ci_low": float(lo),
        "ci_high": float(hi),
        "p_bootstrap": float(p),
        "n": int(n),
    }


def stars(p: float) -> str:
    """Significance marker as used in the figure captions."""
    return "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""


def fdr_bh(pvals: np.ndarray) -> np.ndarray:
    """Benjamini-Hochberg adjusted p-values."""
    p = np.asarray(pvals, float)
    n = p.size
    order = np.argsort(p)
    adj = np.empty(n)
    adj[order] = np.minimum.accumulate((p[order] * n / np.arange(1, n + 1))[::-1])[::-1]
    return np.clip(adj, 0, 1)


def specificity_tests(
    results: pd.DataFrame, *, n_boot: int = 10_000, seed: int = 0, correct: bool = True,
    axis: str = "column",
) -> pd.DataFrame:
    """Test each off-diagonal cell against its diagonal, per task and hemisphere.

    Defaults to ``axis="column"``, the analysis that isolates specificity.

    ``axis="row"`` (the manuscript's original comparison) asks: does a model trained on
    task T predict T better than it predicts some other task's map? This is
    confounded by how predictable each target map is. A model whose own target is
    intrinsically hard -- as the motor contrast is here -- will predict easier
    maps better, and fail the row test even when it is perfectly specific.

    ``axis="column"`` asks the cleaner question: for a given target map, does the
    model trained on that task predict it better than models trained on other
    tasks? Target difficulty is held constant, so this isolates specificity.

    Report both: the row test answers "is this model selective for its own
    contrast", the column test answers "is this map best predicted by its own
    model".
    """
    if axis not in ("row", "column"):
        raise ValueError(f"axis must be 'row' or 'column', got {axis!r}")
    rows = []
    if axis == "row":
        groups = results.groupby(["hemi", "task"], sort=False)
        index_col, other_col = "task", "comparison_task"
    else:
        groups = results.groupby(["hemi", "comparison_task"], sort=False)
        index_col, other_col = "comparison_task", "task"

    for (hemi, task), block in groups:
        wide = block.pivot_table(index="subject", columns=other_col, values="pearson")
        if task not in wide.columns:
            continue
        within = wide[task].to_numpy()
        for other in wide.columns:
            if other == task:
                continue
            between = wide[other].to_numpy()
            ok = np.isfinite(within) & np.isfinite(between)
            res = paired_bootstrap(within[ok], between[ok], n_boot=n_boot, seed=seed)
            t, p_t = ttest_rel(within[ok], between[ok])
            rows.append({
                "hemi": hemi, "axis": axis,
                index_col: task, other_col: other,
                "mean_within": float(np.mean(within[ok])),
                "mean_between": float(np.mean(between[ok])),
                **res,
                "t": float(t), "p_ttest": float(p_t / 2 if t > 0 else 1 - p_t / 2),
            })
    df = pd.DataFrame(rows)
    if correct and not df.empty:
        df["p_fdr"] = fdr_bh(df["p_bootstrap"].to_numpy())
        df["stars"] = df["p_fdr"].map(stars)
    elif not df.empty:
        df["stars"] = df["p_bootstrap"].map(stars)
    return df


def compare_protocols(
    results_a: pd.DataFrame,
    results_b: pd.DataFrame,
    *,
    label_a: str = "neonatal",
    label_b: str = "adult_group_mean_loo",
    n_boot: int = 10_000,
    seed: int = 0,
) -> pd.DataFrame:
    """Compare within-task accuracy between two protocols (manuscript Fig. S7).

    The two protocols are evaluated on different individuals (neonates vs adults),
    so this is an unpaired comparison and uses a bootstrap of the difference in
    means rather than the paired test used for task specificity.
    """
    rng = np.random.default_rng(seed)
    rows = []
    for hemi in sorted(set(results_a.hemi) & set(results_b.hemi)):
        for task in sorted(set(results_a.task) & set(results_b.task)):
            pick = lambda d: d[(d.hemi == hemi) & (d.task == task) & (d.comparison_task == task)][
                "pearson"
            ].to_numpy()
            x, y = pick(results_a), pick(results_b)
            x, y = x[np.isfinite(x)], y[np.isfinite(y)]
            if x.size == 0 or y.size == 0:
                continue
            bx = x[rng.integers(0, x.size, size=(n_boot, x.size))].mean(axis=1)
            by = y[rng.integers(0, y.size, size=(n_boot, y.size))].mean(axis=1)
            diff = bx - by
            observed = float(x.mean() - y.mean())
            p = 2 * min(
                (np.sum(diff - diff.mean() >= observed) + 1) / (n_boot + 1),
                (np.sum(diff - diff.mean() <= observed) + 1) / (n_boot + 1),
            )
            # accuracy as a proportion of the comparison protocol's, with its own
            # interval: the ratio of two point estimates hides that they rest on
            # very different sample sizes
            ratio = bx / np.where(by == 0, np.nan, by)
            rows.append({
                "hemi": hemi, "task": task,
                f"mean_{label_a}": float(x.mean()), f"mean_{label_b}": float(y.mean()),
                "n_a": int(x.size), "n_b": int(y.size),
                "difference": observed,
                "ci_low": float(np.percentile(diff, 2.5)),
                "ci_high": float(np.percentile(diff, 97.5)),
                "p_bootstrap": float(min(p, 1.0)),
                "pct_of_b": float(100 * x.mean() / y.mean()) if y.mean() else np.nan,
                "pct_ci_low": float(np.nanpercentile(100 * ratio, 2.5)),
                "pct_ci_high": float(np.nanpercentile(100 * ratio, 97.5)),
            })
    df = pd.DataFrame(rows)
    if not df.empty:
        df["p_fdr"] = fdr_bh(df["p_bootstrap"].to_numpy())
        df["stars"] = df["p_fdr"].map(stars)
    return df
