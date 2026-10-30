"""Full-pipeline spatial null: can the pipeline transfer *any* smooth map?

The Fig. S8 null (:mod:`sti.spatial_null`) holds the neonatal predictions fixed
and resamples the target map, which asks whether prediction and target align
beyond their shared smoothness. It cannot ask the stronger question a reviewer
will: whether the pipeline itself — fit adult connectivity→activation models,
transfer the weights to neonatal connectivity — carries real task maps better
than it carries arbitrary smooth maps. Connectivity profiles encode where a
vertex sits (tractography is biased toward nearby targets), and position may be
all that is needed to hit a spatially coarse target. If real task maps transfer
no better than matched surrogates, the adult-to-neonate transfer reflects
shared positional information, not function-specific structure.

Each null draw therefore reruns the entire two-step analysis on a spatially
rearranged training set:

1. A variogram-matched surrogate of the adult group-mean map is drawn as a
   vertex *permutation* (:meth:`~sti.spatial_null.SurrogateMaps.generate_permutations`),
   so it preserves the group map's values and spatial autocorrelation exactly.
2. The same permutation is applied to every adult's individual map. The
   training set keeps its between-subject variability at every vertex; only the
   topography moves, coherently across subjects.
3. The model is refitted on (adult connectivity, permuted maps), applied to
   every neonate, and each neonate's prediction is correlated with the permuted
   group-mean target. The across-neonate mean is one null value — the same
   statistic as the observed mean within-task accuracy.

The null's mean is itself a result: it estimates how much transfer accuracy
positional information alone buys, which belongs in the paper alongside the
p-value.

Surrogates are generated per task, so each null matches that map's own
smoothness. They do not preserve the between-task correlation structure; a
joint variant (one permutation shared across the five maps) would be the null
for the *specificity* result and can be added if needed.
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from sti import model as model_mod
from sti.config import Config, DEFAULT_CONFIG, Hemisphere
from sti.datasets import Activation, Connectivity
from sti.spatial_null import SurrogateMaps, correlation_matrix, p_spin

log = logging.getLogger(__name__)


def null_transfer(
    adult_connectivity: Connectivity,
    neonatal_connectivity: Connectivity,
    activation: Activation,
    *,
    hemi: Hemisphere,
    dist: np.ndarray,
    n_surrogates: int = 200,
    config: Config = DEFAULT_CONFIG,
    seed: int = 0,
    float32: bool = True,
    region_folds: np.ndarray | None = None,
) -> pd.DataFrame:
    """Null distribution of adult-to-neonate transfer accuracy for one task.

    Returns one row per surrogate with ``null_r``, the across-neonate mean
    correlation between the refitted model's predictions and the permuted
    target. Rows carry the seed, so shards that split one task's surrogates
    must use distinct seeds. With ``region_folds`` (vertex->region labels for
    this hemisphere), each refit is leave-one-region-out, matching the
    region-cross-validated observed statistic; the anatomical folds are not
    permuted, only the maps are.
    """
    task = activation.task
    y = activation.zscored()[hemi]  # (n_adults, n_vertices)
    group_mean = y.mean(axis=0)

    X_adult = adult_connectivity[hemi]
    X_inf = neonatal_connectivity[hemi]
    if float32:
        X_adult = model_mod.as_float32(X_adult)
        X_inf = model_mod.as_float32(X_inf)
    n_neo = X_inf.shape[0]
    Xf_inf = model_mod.flatten(X_inf)  # flattened once, reused per surrogate

    gen = SurrogateMaps(dist, seed=seed)
    perms = gen.generate_permutations(group_mean, n_surrogates)

    records: list[dict] = []
    for k, pi in enumerate(perms):
        if region_folds is not None:
            from sti.evaluate import stitched_predictions

            y_hat = stitched_predictions(X_adult, y[:, pi], X_inf, region_folds, config)
        else:
            fitted = model_mod.fit(X_adult, y[:, pi], config)
            y_hat = model_mod.predict(fitted, Xf_inf).reshape(n_neo, -1)
        r = correlation_matrix(y_hat, group_mean[pi][None, :])[:, 0]
        records.append({
            "protocol": "pipeline_null" + ("_regioncv" if region_folds is not None else ""),
            "algorithm": "LinearRegression" if config.alpha == 0 else "ElasticNet",
            "alpha": config.alpha,
            "l1_ratio": config.l1_ratio,
            "task": task,
            "hemi": hemi,
            "surrogate": k,
            "seed": seed,
            "n_neonates": n_neo,
            "null_r": float(r.mean()),
            "null_r_sd": float(r.std()),
        })
        log.info("pipeline null: task=%s hemi=%s surrogate %d/%d  null_r=%.3f",
                 task, hemi, k + 1, n_surrogates, records[-1]["null_r"])
    return pd.DataFrame.from_records(records)


def summarise(null: pd.DataFrame, observed: pd.DataFrame) -> pd.DataFrame:
    """Observed within-task transfer against the pipeline null, per task × hemisphere.

    ``null`` is the (merged) output of :func:`null_transfer`; ``observed`` is a
    neonatal results table (``sti neonatal``). ``excess_r`` — the observed
    accuracy minus the null mean — is the share of the transfer that positional
    information cannot explain.
    """
    from sti.stats import fdr_bh, stars

    rows = []
    for (task, hemi), grp in null.groupby(["task", "hemi"]):
        nr = grp["null_r"].to_numpy()
        obs_rows = observed[(observed.task == task) & (observed.hemi == hemi)
                            & (observed.comparison_task == task)]
        if obs_rows.empty:
            log.warning("no observed results for task=%s hemi=%s; skipping", task, hemi)
            continue
        obs = float(obs_rows["pearson"].mean())
        null_mean = float(nr.mean())
        rows.append({
            "hemi": hemi, "task": task,
            "observed_r": obs,
            "null_mean": null_mean,
            "null_sd": float(nr.std()),
            "null_p95": float(np.percentile(nr, 95)),
            "excess_r": obs - null_mean,
            "p_spin": p_spin(obs, nr),
            "n_surrogates": int(nr.size),
        })
    out = pd.DataFrame(rows)
    if not out.empty:
        out["p_fdr"] = fdr_bh(out["p_spin"].to_numpy())
        out["stars"] = out["p_fdr"].map(stars)
    return out
