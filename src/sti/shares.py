"""Variance partition of the adult functional map: geometry vs connectivity.

The Introduction (Fig. 1b) promises the shares: how much of each group-average
activation map is explained by geometry alone, by connectivity alone, by
either (shared), and by neither. Commonality analysis over three models given
identical treatment —

    G   distance features (``sti.distance_control.distance_features``)
    C   the cohort's group-mean connectivity profile per vertex
    GC  both, concatenated

with ``unique_G = R2_GC − R2_C``, ``unique_C = R2_GC − R2_G`` and
``shared = R2_G + R2_C − R2_GC``.

Smoothness would inflate an ordinary cross-validation (neighbouring vertices
land in train and test), so R² is computed out-of-sample over *spatially
blocked* folds: vertices are clustered into contiguous blocks by k-means on
their coordinates and each block is held out in turn. Features are
standardised per fold (geometry is in mm, connectivity in streamline counts),
and one penalty is chosen per fold by inner blocked CV on the combined model,
then applied to all three models, so the models differ only in the
information they are allowed.
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from sti.config import Config

log = logging.getLogger(__name__)

ALPHA_GRID: tuple[float, ...] = (0.003, 0.01, 0.03, 0.1, 0.3)


def spatial_folds(coords: np.ndarray, k: int = 10, seed: int = 0) -> np.ndarray:
    """Contiguous vertex blocks by k-means on surface coordinates."""
    from sklearn.cluster import KMeans

    return KMeans(n_clusters=k, n_init=4, random_state=seed).fit_predict(coords)


def _standardise(train: np.ndarray, test: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mu = train.mean(axis=0)
    sd = train.std(axis=0)
    sd[sd == 0] = 1.0  # the zero-padded DLPFC columns
    return (train - mu) / sd, (test - mu) / sd


def _fit_predict(Xtr, ytr, Xte, alpha: float, l1_ratio: float) -> np.ndarray:
    from sklearn.linear_model import ElasticNet

    m = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, random_state=0, max_iter=5000)
    m.fit(Xtr, ytr)
    return m.predict(Xte)


def _select_alpha(X, y, labels, blocks, l1_ratio: float) -> float:
    """Inner blocked CV on the combined model: one penalty per outer fold."""
    best, best_mse = ALPHA_GRID[0], np.inf
    for alpha in ALPHA_GRID:
        se = 0.0
        for b in blocks:
            tr, te = labels != b, labels == b
            Xtr, Xte = _standardise(X[tr], X[te])
            pred = _fit_predict(Xtr, y[tr] - y[tr].mean(), Xte, alpha, l1_ratio)
            se += float(np.sum((y[te] - y[tr].mean() - pred) ** 2))
        if se < best_mse:
            best, best_mse = alpha, se
    return best


def partition(
    G: np.ndarray,
    C: np.ndarray,
    y: np.ndarray,
    coords: np.ndarray,
    *,
    k: int = 10,
    l1_ratio: float = 0.5,
    seed: int = 0,
    fold_labels: np.ndarray | None = None,
) -> dict:
    """Spatially blocked commonality analysis of one map.

    Folds are ``fold_labels`` when given — one fold per label, e.g. the 13
    DLPFC regions of the hemisphere for leave-one-region-out — and otherwise
    ``k`` contiguous k-means blocks of the coordinates. Returns out-of-sample
    R² for G, C and G+C, the commonality partition, and the out-of-sample
    Pearson correlations.
    """
    y = np.asarray(y, dtype=float).reshape(-1)
    G = np.asarray(G, dtype=np.float32)
    C = np.asarray(C, dtype=np.float32)
    if fold_labels is None:
        labels = spatial_folds(coords, k=k, seed=seed)
    else:
        labels = np.asarray(fold_labels).reshape(-1)
        if labels.size != y.size:
            raise ValueError(f"{labels.size} fold labels for {y.size} vertices")
    fold_ids = np.unique(labels)
    k = fold_ids.size
    models = {"G": G, "C": C, "GC": np.hstack([G, C])}

    oof = {m: np.full(y.size, np.nan) for m in models}
    for n_done, b in enumerate(fold_ids):
        tr, te = labels != b, labels == b
        inner_blocks = [i for i in fold_ids if i != b]
        inner_labels = labels[tr]
        alpha = _select_alpha(models["GC"][tr], y[tr], inner_labels, inner_blocks, l1_ratio)
        for name, X in models.items():
            Xtr, Xte = _standardise(X[tr], X[te])
            oof[name][te] = y[tr].mean() + _fit_predict(
                Xtr, y[tr] - y[tr].mean(), Xte, alpha, l1_ratio)
        log.info("shares: fold %d/%d alpha=%g", n_done + 1, k, alpha)

    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = {m: 1.0 - float(np.sum((y - p) ** 2)) / ss_tot for m, p in oof.items()}
    pearson = {m: float(np.corrcoef(y, p)[0, 1]) for m, p in oof.items()}
    return {
        "r2_geometry": r2["G"], "r2_connectivity": r2["C"], "r2_combined": r2["GC"],
        "unique_geometry": r2["GC"] - r2["C"],
        "unique_connectivity": r2["GC"] - r2["G"],
        "shared": r2["G"] + r2["C"] - r2["GC"],
        "unexplained": 1.0 - r2["GC"],
        "pearson_geometry": pearson["G"], "pearson_connectivity": pearson["C"],
        "pearson_combined": pearson["GC"],
        "k_folds": k, "l1_ratio": l1_ratio,
    }


def shares_table(
    distances: dict,
    connectivity_by_cohort: dict[str, "object"],
    activations: dict,
    coords_fn,
    *,
    k: int = 10,
    l1_ratio: float = 0.5,
    config: Config | None = None,
    fold_labels_fn=None,
) -> pd.DataFrame:
    """The full partition: every task × hemisphere × cohort.

    ``connectivity_by_cohort`` maps a cohort name to a ``Connectivity``;
    ``coords_fn(hemi)`` returns the seed-vertex coordinates. When
    ``fold_labels_fn(hemi)`` is given, its labels define the folds
    (leave-one-region-out); otherwise k-means blocks are used.
    """
    rows = []
    for cohort, conn in connectivity_by_cohort.items():
        for hemi in ("L", "R"):
            C = np.asarray(conn[hemi], dtype=np.float32).mean(axis=0)
            coords = coords_fn(hemi)
            folds = fold_labels_fn(hemi) if fold_labels_fn is not None else None
            for task, activation in activations.items():
                y = activation.zscored()[hemi].mean(axis=0)
                res = partition(distances[hemi], C, y, coords, k=k,
                                l1_ratio=l1_ratio, fold_labels=folds)
                rows.append({"cohort": cohort, "task": task, "hemi": hemi, **res})
                log.info("shares done: %s %s %s  uG=%.3f uC=%.3f shared=%.3f",
                         cohort, task, hemi, res["unique_geometry"],
                         res["unique_connectivity"], res["shared"])
    return pd.DataFrame(rows)
