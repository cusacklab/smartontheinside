"""Distance controls: how much of the prediction does position alone buy?

Reviewer 1's second control (Donahue et al., 2016, J Neurosci). Tractography is
biased toward nearby targets, so a vertex's connectivity profile partly encodes
*where the vertex sits*, and position may suffice to predict a spatially coarse
activation map. Two complementary analyses bound that confound:

1. **Distance-only model** (:func:`distance_only_results`): replace each DLPFC
   vertex's connectivity profile with its distance to every target parcel and
   run the same model against the same targets. Its accuracy is the positional
   baseline — what the pipeline achieves with geometry and nothing else.
2. **Distance-regressed connectivity** (:func:`regress_distance`): remove the
   exponential distance decay from every connectivity profile and rerun the
   real analysis. What survives is the part of the result that proximity
   cannot carry.

Together with the full-pipeline surrogate null (:mod:`sti.pipeline_null`) these
triangulate the same question — the distance-only model estimates the
positional share *constructively*, the surrogate null *destructively*.

Distance features mirror the connectivity layout exactly: column ``t - 1`` is
Glasser parcel ``t``, geodesic along the ipsilateral midthickness mesh
(multi-source Dijkstra from all of the parcel's vertices), Euclidean to the
nearest vertex of contralateral parcels (no mesh spans the hemispheres), and
identically zero for the 26 DLPFC parcels, as in the tractography arrays.

A note on the neonatal side: both cohorts' arrays are indexed in adult fs_LR
32k space, so one set of distance features serves both. For the regression
control the decay is fitted per subject, so the global scale difference
between neonatal and adult anatomy is absorbed by each subject's own fitted
decay constant.
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from scipy import sparse
from scipy.spatial import cKDTree

from sti import model as model_mod
from sti.config import (ALL_DLPFC_PARCELS, Config, DEFAULT_CONFIG, HEMISPHERES,
                        Hemisphere, N_PARCELS, Task)
from sti.datasets import Activation, Connectivity

log = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# geometry (plain arrays, so it is testable on synthetic meshes)
# --------------------------------------------------------------------------- #

def mesh_graph(coords: np.ndarray, triangles: np.ndarray) -> sparse.csr_matrix:
    """Sparse edge-length graph of a triangulated surface.

    Edges shared by two triangles must appear once, not summed, so the edge
    list is deduplicated before the matrix is built.
    """
    i = np.concatenate([triangles[:, 0], triangles[:, 1], triangles[:, 2]])
    j = np.concatenate([triangles[:, 1], triangles[:, 2], triangles[:, 0]])
    pairs = np.unique(np.sort(np.column_stack([i, j]), axis=1), axis=0)
    w = np.linalg.norm(coords[pairs[:, 0]] - coords[pairs[:, 1]], axis=1)
    n = coords.shape[0]
    g = sparse.coo_matrix((w, (pairs[:, 0], pairs[:, 1])), shape=(n, n))
    return (g + g.T).tocsr()


def geodesic_to_sources(graph: sparse.csr_matrix, sources: np.ndarray) -> np.ndarray:
    """Geodesic distance from every vertex to the nearest of ``sources``."""
    from scipy.sparse.csgraph import dijkstra

    return dijkstra(graph, directed=False, indices=np.asarray(sources), min_only=True)


def distance_features_from_geometry(
    seed_vertices: np.ndarray,
    ipsi_coords: np.ndarray,
    ipsi_triangles: np.ndarray,
    ipsi_parcels: dict[int, np.ndarray],
    contra_coords: np.ndarray,
    contra_parcels: dict[int, np.ndarray],
    *,
    n_parcels: int = N_PARCELS,
    exclude: tuple[int, ...] = ALL_DLPFC_PARCELS,
) -> np.ndarray:
    """``(n_seeds, n_parcels)`` distances, column ``t - 1`` = parcel label ``t``.

    ``ipsi_parcels`` / ``contra_parcels`` map parcel label -> vertex indices on
    that hemisphere's surface. Excluded (DLPFC) columns are left at zero to
    mirror the connectivity arrays.
    """
    out = np.zeros((seed_vertices.size, n_parcels), dtype=np.float32)
    graph = mesh_graph(ipsi_coords, ipsi_triangles)
    seed_coords = ipsi_coords[seed_vertices]

    for label, verts in ipsi_parcels.items():
        if label in exclude:
            continue
        out[:, label - 1] = geodesic_to_sources(graph, verts)[seed_vertices]
    for label, verts in contra_parcels.items():
        if label in exclude:
            continue
        d, _ = cKDTree(contra_coords[verts]).query(seed_coords)
        out[:, label - 1] = d

    if not np.isfinite(out).all():
        raise ValueError("non-finite geodesic distances: the mesh is disconnected")
    return out


# --------------------------------------------------------------------------- #
# loader for the real surfaces
# --------------------------------------------------------------------------- #

def _surface(hemi: Hemisphere, config: Config) -> tuple[np.ndarray, np.ndarray]:
    import nibabel as nib
    from sti.surface import SURFACE_FILE

    surf = nib.load(str(config.data_dir / "parcellations" / SURFACE_FILE.format(hemi=hemi)))
    return (np.asarray(surf.agg_data("NIFTI_INTENT_POINTSET"), dtype=float),
            np.asarray(surf.agg_data("NIFTI_INTENT_TRIANGLE")))


def _parcels(hemi: Hemisphere, config: Config) -> dict[int, np.ndarray]:
    """Parcel label -> vertex indices on this hemisphere's surface."""
    import nibabel as nib
    from sti.surface import LABEL_FILE

    img = nib.load(str(config.data_dir / "parcellations" / LABEL_FILE.format(hemi=hemi)))
    data = np.asarray(img.agg_data("NIFTI_INTENT_LABEL"))
    return {int(label): np.where(data == label)[0]
            for label in np.unique(data) if label != 0}


def distance_features(
    hemi: Hemisphere, *, config: Config = DEFAULT_CONFIG, cache: bool = True
) -> np.ndarray:
    """``(n_seed_vertices, 360)`` distances for one hemisphere's DLPFC seeds.

    Cached under ``data/cache`` because the 360 Dijkstra/KD-tree passes take
    about a minute per hemisphere.
    """
    from sti.surface import dlpfc_vertex_indices

    cache_path = config.cache_dir / f"distance_features_{hemi}.npy"
    if cache and cache_path.exists():
        return np.load(cache_path)

    other: Hemisphere = "R" if hemi == "L" else "L"
    seeds = dlpfc_vertex_indices(hemi, str(config.data_dir / "parcellations"))
    ipsi_coords, ipsi_tri = _surface(hemi, config)
    contra_coords, _ = _surface(other, config)
    out = distance_features_from_geometry(
        seeds, ipsi_coords, ipsi_tri, _parcels(hemi, config),
        contra_coords, _parcels(other, config),
    )
    if cache:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        np.save(cache_path, out)
        log.info("cached %s", cache_path)
    return out


# --------------------------------------------------------------------------- #
# control 1: the distance-only model
# --------------------------------------------------------------------------- #

def distance_only_results(
    distances: dict[Hemisphere, np.ndarray],
    activations: dict[Task, Activation],
    *,
    config: Config = DEFAULT_CONFIG,
    hemispheres=HEMISPHERES,
) -> pd.DataFrame:
    """The neonatal protocol with distance features in place of connectivity.

    Geometry is identical for every subject, so fitting the pipeline's stacked
    per-subject targets against repeated features has exactly the same argmin
    as fitting the group-mean map once (the between-subject variance term does
    not depend on the coefficients) — the fit here uses the group mean, and is
    therefore one model per (task, hemisphere) with a single deterministic
    prediction: the accuracy position alone buys.
    """
    records = []
    for task, activation in activations.items():
        for hemi in hemispheres:
            X = model_mod.as_float32(distances[hemi])
            y_mean = activation.zscored()[hemi].mean(axis=0)
            fitted = model_mod.fit(X, y_mean, config)
            y_hat = model_mod.predict(fitted, X)
            for comparison_task, a in activations.items():
                target = a.zscored()[hemi].mean(axis=0)
                r = float(np.corrcoef(y_hat, target)[0, 1])
                records.append({
                    "protocol": "distance_only",
                    "algorithm": "LinearRegression" if config.alpha == 0 else "ElasticNet",
                    "alpha": config.alpha, "l1_ratio": config.l1_ratio,
                    "task": task, "comparison_task": comparison_task,
                    "hemi": hemi, "subject": "geometry", "pearson": r,
                })
            log.info("distance-only done: task=%s hemi=%s", task, hemi)
    return pd.DataFrame.from_records(records)


def positional_share(distance_results: pd.DataFrame, observed: pd.DataFrame) -> pd.DataFrame:
    """Distance-only accuracy against the observed within-task accuracy."""
    rows = []
    for (task, hemi), grp in distance_results.groupby(["task", "hemi"]):
        d = float(grp[grp.comparison_task == task]["pearson"].mean())
        obs_rows = observed[(observed.task == task) & (observed.hemi == hemi)
                            & (observed.comparison_task == task)]
        if obs_rows.empty:
            continue
        obs = float(obs_rows["pearson"].mean())
        rows.append({
            "hemi": hemi, "task": task,
            "observed_r": obs, "distance_only_r": d,
            "excess_r": obs - d,
            "pct_positional": 100.0 * d / obs if obs else np.nan,
        })
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# control 2: distance-regressed connectivity
# --------------------------------------------------------------------------- #

def regress_distance(
    connectivity: Connectivity, distances: dict[Hemisphere, np.ndarray]
) -> Connectivity:
    """Remove each subject's exponential distance decay from their profiles.

    Tractography counts fall off roughly as ``c ~ A * exp(-d / lambda)``
    (Donahue et al., 2016), which is linear in ``d`` after a log transform. Per
    subject and hemisphere, ``log1p(c)`` is regressed on ``d`` across every
    (seed vertex, target) pair and the residuals become the features. The fit
    is per subject, so differences in head size (neonates vs adults) land in
    each subject's own decay constant rather than in the residuals. Excluded
    (DLPFC) columns have ``d == 0`` and stay identically zero.
    """
    out: dict[Hemisphere, np.ndarray] = {}
    for hemi, X in connectivity.data.items():
        d = np.asarray(distances[hemi], dtype=np.float32)
        keep = d.reshape(-1) > 0  # the zero-padded DLPFC columns
        dk = d.reshape(-1)[keep]
        A = np.column_stack([dk, np.ones_like(dk)])
        res = np.zeros_like(X, dtype=np.float32)
        for s in range(X.shape[0]):
            c = np.log1p(np.asarray(X[s], dtype=np.float32).reshape(-1)[keep])
            coef, *_ = np.linalg.lstsq(A, c, rcond=None)
            flat = np.zeros(d.size, dtype=np.float32)
            flat[keep] = c - A @ coef
            res[s] = flat.reshape(d.shape)
        out[hemi] = res
        log.info("distance regressed out: hemi=%s (%d subjects)", hemi, X.shape[0])
    return Connectivity(data=out, cohort=f"{connectivity.cohort}_distance_regressed")
