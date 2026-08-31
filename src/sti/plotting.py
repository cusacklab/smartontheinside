"""Figures for the classification analyses.

Colour choices here are computed, not eyeballed. The categorical palette is the
best-separating five-colour set found by ``tools/validate_palette.py`` over an
Okabe-Ito/Tol candidate pool: worst-case OKLab Delta-E is 23.3 for normal vision
and 22.2 under simulated protanopia, deuteranopia and tritanopia, so no two
contrasts rely on colour discrimination that a colour-blind reader lacks.

Correlations are signed, so the specificity matrices use a diverging map with a
neutral grey midpoint pinned at zero (never a rainbow). Magnitude-only surfaces
(the hyperparameter grid) use a single-hue sequential ramp.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

# Validated categorical palette; order is fixed and never cycled.
PALETTE: tuple[str, ...] = ("#E69F00", "#56B4E9", "#000000", "#332288", "#661100")

#: Markers give a second, non-colour channel for identity (print / CVD / forced colours).
MARKERS: tuple[str, ...] = ("o", "s", "^", "D", "v")

INK = "#1a1a1a"
MUTED = "#6b6b6b"
GRID = "#dcdcdc"


def _mpl():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def diverging_cmap():
    """Blue -> neutral grey -> orange, for signed correlations."""
    from matplotlib.colors import LinearSegmentedColormap

    return LinearSegmentedColormap.from_list(
        "sti_diverging", ["#0072B2", "#f2f2f2", "#D55E00"]
    )


def _style(ax):
    """Recessive axes: the data should be the darkest thing on the page."""
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(MUTED)
        ax.spines[side].set_linewidth(0.8)
    ax.tick_params(colors=MUTED, labelsize=8, width=0.8)
    for lbl in ax.get_xticklabels() + ax.get_yticklabels():
        lbl.set_color(INK)
    ax.set_axisbelow(True)


def save(fig, name: str, config=None, *, dpi: int = 300) -> Path:
    """Write a figure to the configured figure directory."""
    from sti.config import DEFAULT_CONFIG

    config = config or DEFAULT_CONFIG
    out = Path(config.figure_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / (name if name.endswith((".png", ".pdf", ".svg")) else f"{name}.png")
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor="white")
    return path


def plot_accuracy(results: pd.DataFrame, *, title: str = "", tasks=None):
    """Per-participant within-task accuracy, one panel per hemisphere.

    Figures 2A/B, 3A/B and 4A/B. Each point is one participant; the bar is the
    mean with a bootstrap 95% interval.
    """
    plt = _mpl()
    within = results[results.task == results.comparison_task]
    tasks = list(tasks or sorted(within.task.unique()))
    hemis = sorted(within.hemi.unique())

    fig, axes = plt.subplots(1, len(hemis), figsize=(3.2 * len(hemis), 3.4), sharey=True)
    axes = np.atleast_1d(axes)
    rng = np.random.default_rng(0)

    for ax, hemi in zip(axes, hemis):
        for i, task in enumerate(tasks):
            v = within[(within.hemi == hemi) & (within.task == task)]["pearson"].to_numpy()
            v = v[np.isfinite(v)]
            if v.size == 0:
                continue
            colour = PALETTE[i % len(PALETTE)]
            ax.scatter(
                i + rng.uniform(-0.16, 0.16, v.size), v,
                s=9, color=colour, alpha=0.45, linewidths=0, zorder=2,
                marker=MARKERS[i % len(MARKERS)],
            )
            boot = np.array([rng.choice(v, v.size).mean() for _ in range(2000)])
            ax.plot([i - 0.3, i + 0.3], [v.mean()] * 2, color=colour, lw=2, zorder=4)
            ax.plot([i, i], np.percentile(boot, [2.5, 97.5]), color=colour, lw=1.2, zorder=3)
        ax.axhline(0, color=MUTED, lw=0.8, ls=":", zorder=1)
        ax.set_xticks(range(len(tasks)))
        ax.set_xticklabels([t.replace("tfMRI_", "") for t in tasks], rotation=45, ha="right")
        ax.set_title(f"{hemi} hemisphere", fontsize=9, color=INK)
        ax.yaxis.grid(True, color=GRID, lw=0.6)
        _style(ax)
    axes[0].set_ylabel("prediction accuracy (r)", fontsize=9, color=INK)
    if title:
        fig.suptitle(title, fontsize=10, color=INK)
    fig.tight_layout()
    return fig


def plot_specificity_matrix(
    results: pd.DataFrame, *, tests: pd.DataFrame | None = None, title: str = ""
):
    """Model task (rows) against evaluated task (columns), one panel per hemisphere.

    Figures 2C/D and 3C/D. Asterisks mark off-diagonal cells significantly weaker
    than the diagonal of the same row.
    """
    plt = _mpl()
    hemis = sorted(results.hemi.unique())
    fig, axes = plt.subplots(1, len(hemis), figsize=(3.6 * len(hemis), 3.4))
    axes = np.atleast_1d(axes)
    vmax = float(np.nanmax(np.abs(results.pearson))) or 1.0

    for ax, hemi in zip(axes, hemis):
        m = results[results.hemi == hemi].pivot_table(
            index="task", columns="comparison_task", values="pearson", aggfunc="mean"
        )
        im = ax.imshow(m.values, cmap=diverging_cmap(), vmin=-vmax, vmax=vmax)
        labels = [t.replace("tfMRI_", "") for t in m.index]
        ax.set_xticks(range(len(m.columns)))
        ax.set_xticklabels([c.replace("tfMRI_", "") for c in m.columns], rotation=45, ha="right")
        ax.set_yticks(range(len(m.index)))
        # only the leftmost panel carries row labels; otherwise they collide with
        # the neighbouring panel's cells
        ax.set_yticklabels(labels if ax is axes[0] else [])
        for i, r in enumerate(m.index):
            for j, c in enumerate(m.columns):
                val = m.values[i, j]
                mark = ""
                if tests is not None and r != c:
                    # match on both orientations: the row test keys on (task=r),
                    # the column test on (comparison_task=c)
                    sel = tests[(tests.hemi == hemi) & (tests.task == r)
                                & (tests.comparison_task == c)]
                    if len(sel):
                        mark = sel.iloc[0].get("stars", "") or ""
                        if pd.isna(mark):
                            mark = ""
                ax.text(j, i, f"{val:.2f}\n{mark}".strip(), ha="center", va="center",
                        fontsize=7, color=INK)
        ax.set_title(f"{hemi} hemisphere", fontsize=9, color=INK)
        if ax is axes[len(axes) // 2]:
            ax.set_xlabel("evaluated against", fontsize=8, color=MUTED)
        ax.tick_params(labelsize=7, colors=MUTED, length=0)
        for s in ax.spines.values():
            s.set_visible(False)
    axes[0].set_ylabel("model trained on", fontsize=8, color=MUTED)
    fig.colorbar(im, ax=axes.tolist(), shrink=0.7, label="r")
    if title:
        fig.suptitle(title, fontsize=10, color=INK)
    return fig


def plot_hyperparameter_grid(grid: pd.DataFrame, *, metric: str = "mean_pearson",
                             highlight: tuple[float, float] | None = (0.4, 0.6)):
    """The hyperparameter surface (Fig. S6), with the selected cell marked.

    Magnitude only, so a single-hue sequential ramp -- unlike the legacy figure,
    which used a diverging map for a quantity with no meaningful midpoint.
    """
    plt = _mpl()
    piv = grid.pivot_table(index="alpha", columns="l1_ratio", values=metric)
    fig, ax = plt.subplots(figsize=(4.2, 4.4))
    im = ax.imshow(piv.values, cmap="Blues", aspect="auto")
    ax.set_xticks(range(len(piv.columns)))
    ax.set_xticklabels([f"{c:g}" for c in piv.columns])
    ax.set_yticks(range(len(piv.index)))
    ax.set_yticklabels([f"{i:g}" for i in piv.index])
    ax.set_xlabel("L1 ratio", fontsize=9, color=INK)
    ax.set_ylabel("alpha", fontsize=9, color=INK)
    if highlight is not None:
        a, l = highlight
        if a in list(piv.index) and l in list(piv.columns):
            ax.add_patch(plt.Rectangle(
                (list(piv.columns).index(l) - 0.5, list(piv.index).index(a) - 0.5),
                1, 1, fill=False, edgecolor="#D55E00", lw=2))
    ax.tick_params(labelsize=7, colors=MUTED, length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    fig.colorbar(im, ax=ax, shrink=0.8, label=metric.replace("_", " "))
    fig.tight_layout()
    return fig


def plot_spatial_null(observed: float, null: np.ndarray, *, p: float | None = None,
                      title: str = ""):
    """Observed accuracy against its spatial null distribution (Fig. S8)."""
    plt = _mpl()
    fig, ax = plt.subplots(figsize=(4.2, 3.0))
    ax.hist(null, bins=40, color="#c9d9e8", edgecolor="white", linewidth=0.4)
    ax.axvline(observed, color="#D55E00", lw=2,
               label=f"observed r = {observed:.3f}" + (f"  (p = {p:.3f})" if p is not None else ""))
    ax.set_xlabel("prediction accuracy (r) under spatial null", fontsize=9, color=INK)
    ax.set_ylabel("surrogates", fontsize=9, color=INK)
    ax.legend(fontsize=8, frameon=False)
    ax.yaxis.grid(True, color=GRID, lw=0.6)
    _style(ax)
    if title:
        ax.set_title(title, fontsize=9, color=INK)
    fig.tight_layout()
    return fig


def plot_scan_age(accuracy: pd.DataFrame, covariates: pd.DataFrame, *, title: str = ""):
    """Prediction accuracy against postmenstrual age at scan (Fig. S9)."""
    plt = _mpl()
    df = accuracy.merge(covariates[["scan_age"]], left_on="subject", right_index=True)
    fig, ax = plt.subplots(figsize=(4.2, 3.2))
    ax.scatter(df.scan_age, df.accuracy, s=14, color=PALETTE[1], alpha=0.6, linewidths=0)
    if len(df) > 2:
        b, a = np.polyfit(df.scan_age, df.accuracy, 1)
        xs = np.linspace(df.scan_age.min(), df.scan_age.max(), 50)
        ax.plot(xs, a + b * xs, color=PALETTE[4], lw=2)
    ax.set_xlabel("postmenstrual age at scan (weeks)", fontsize=9, color=INK)
    ax.set_ylabel("prediction accuracy (r)", fontsize=9, color=INK)
    ax.yaxis.grid(True, color=GRID, lw=0.6)
    _style(ax)
    if title:
        ax.set_title(title, fontsize=9, color=INK)
    fig.tight_layout()
    return fig


def plot_specificity_lines(
    results: pd.DataFrame,
    *,
    title: str = "",
    tasks=None,
    centre: bool = False,
    ci: bool = True,
    label_peaks: bool = False,
    axes=None,
    legend: bool = True,
    standalone: bool = True,
):
    """Task specificity read down columns: one line per model, x = target map.

    The comparison that matters is *within* each x position -- for this target
    map, does its own model predict it best? -- so it is drawn vertically, where
    the eye makes it naturally. The signature of specificity is that each line
    peaks at its own target; those points are ringed and labelled.

    A heatmap puts this comparison along the wrong axis: reading a row invites
    comparing a model across targets of differing difficulty, which is what made
    the motor contrast look like a failure of specificity when it is not.

    ``centre=True`` subtracts each target's across-model mean, removing the large
    differences in how predictable each map is so that only the specificity
    remains.
    """
    plt = _mpl()
    tasks = list(tasks or sorted(results.task.unique()))
    hemis = sorted(results.hemi.unique())
    short = [t.replace("tfMRI_", "") for t in tasks]

    if axes is None:
        fig, axes = plt.subplots(1, len(hemis), figsize=(4.1 * len(hemis), 3.8), sharey=True)
    else:
        fig = np.atleast_1d(axes)[0].figure
    axes = np.atleast_1d(axes)
    rng = np.random.default_rng(0)

    for ax, hemi in zip(axes, hemis):
        block = results[results.hemi == hemi]
        # mean and bootstrap CI of accuracy for every (model, target) cell
        cell = {}
        for m in tasks:
            for t in tasks:
                v = block[(block.task == m) & (block.comparison_task == t)]["pearson"].to_numpy()
                v = v[np.isfinite(v)]
                if v.size == 0:
                    continue
                boot = v[rng.integers(0, v.size, size=(1000, v.size))].mean(axis=1)
                cell[(m, t)] = (v.mean(), *np.percentile(boot, [2.5, 97.5]))

        offsets = {t: np.mean([cell[(m, t)][0] for m in tasks if (m, t) in cell])
                   for t in tasks} if centre else {t: 0.0 for t in tasks}

        for i, model in enumerate(tasks):
            xs, ys, los, his = [], [], [], []
            for j, target in enumerate(tasks):
                if (model, target) not in cell:
                    continue
                mean, lo, hi = cell[(model, target)]
                xs.append(j); ys.append(mean - offsets[target])
                los.append(lo - offsets[target]); his.append(hi - offsets[target])
            colour = PALETTE[i % len(PALETTE)]
            ax.plot(xs, ys, color=colour, lw=1.6, marker=MARKERS[i % len(MARKERS)],
                    markersize=5, label=short[i], zorder=2)
            if ci:
                ax.fill_between(xs, los, his, color=colour, alpha=0.15, lw=0, zorder=1)
            # ring and label the own-target point: the specificity signature
            if model in tasks:
                j = tasks.index(model)
                if (model, model) in cell:
                    y = cell[(model, model)][0] - offsets[model]
                    ax.plot([j], [y], marker="o", markersize=11, markerfacecolor="none",
                            markeredgecolor=colour, markeredgewidth=1.8, zorder=4)
                    if label_peaks:
                        ax.annotate(short[i], (j, y), textcoords="offset points",
                                    xytext=(0, 11), ha="center", fontsize=7,
                                    color=colour, fontweight="bold", zorder=5)

        ax.set_xticks(range(len(tasks)))
        ax.set_xticklabels(short, rotation=45, ha="right")
        ax.set_xlabel("target map (evaluated against)", fontsize=9, color=INK)
        ax.set_title(f"{hemi} hemisphere", fontsize=9, color=INK)
        ax.yaxis.grid(True, color=GRID, lw=0.6)
        ax.set_xlim(-0.4, len(tasks) - 0.6)
        if label_peaks:
            lo, hi = ax.get_ylim()
            ax.set_ylim(lo, hi + 0.16 * (hi - lo))   # room for the peak labels
        if centre:
            ax.axhline(0, color=MUTED, lw=0.8, ls=":", zorder=0)
        _style(ax)

    axes[0].set_ylabel("accuracy relative to\ntarget mean (r)" if centre
                       else "prediction accuracy (r)", fontsize=9, color=INK)
    if legend:
        axes[-1].legend(title="model trained on", fontsize=7, title_fontsize=7,
                        frameon=False, loc="center left", bbox_to_anchor=(1.02, 0.5))
    if title:
        fig.suptitle(title, fontsize=10, color=INK)
    if standalone:
        fig.tight_layout()
    return fig


def plot_specificity_panel(results: pd.DataFrame, *, title: str = "", tasks=None):
    """The full specificity story in one figure: absolute accuracy and specificity.

    Top row: raw accuracy, which shows how much the target maps differ in
    predictability -- the motor map is hard for every model.
    Bottom row: the same values with each target's across-model mean removed, so
    only specificity remains. Every line peaks at its own target.

    Splitting the two is the point. In a single heatmap they are superimposed,
    and target difficulty masquerades as a failure of specificity.
    """
    plt = _mpl()
    hemis = sorted(results.hemi.unique())
    fig, axs = plt.subplots(2, len(hemis), figsize=(4.1 * len(hemis), 6.6))
    axs = np.atleast_2d(axs)

    plot_specificity_lines(results, tasks=tasks, centre=False, axes=axs[0],
                           legend=False, standalone=False)
    plot_specificity_lines(results, tasks=tasks, centre=True, axes=axs[1],
                           label_peaks=True, legend=True, standalone=False)
    for ax in axs[0]:
        ax.set_xlabel("")
        ax.set_xticklabels([])
    for ax in axs[1]:
        ax.set_title("")
    # One y-range per row, taken from the union of both panels' data. Sharing to
    # the first panel instead would clip whichever hemisphere ranges wider.
    def _span(ax):
        vals = np.concatenate([
            np.asarray(l.get_ydata(), dtype=float).ravel()
            for l in ax.get_lines() if len(l.get_ydata())
        ]) if ax.get_lines() else np.array([0.0])
        vals = vals[np.isfinite(vals)]
        return vals.min(), vals.max()

    for row in axs:
        spans = [_span(ax) for ax in row]
        lo = min(s0 for s0, _ in spans)
        hi = max(s1 for _, s1 in spans)
        pad = 0.08 * (hi - lo)
        head = 0.20 * (hi - lo) if row is axs[-1] else pad   # room for peak labels
        for ax in row:
            ax.set_ylim(lo - pad, hi + head)
        for ax in row[1:]:
            ax.set_yticklabels([])

    axs[0][0].set_ylabel("prediction accuracy (r)", fontsize=9, color=INK)
    axs[1][0].set_ylabel("accuracy relative to\ntarget mean (r)", fontsize=9, color=INK)
    if title:
        fig.suptitle(title, fontsize=10, color=INK)
    fig.tight_layout()
    return fig
