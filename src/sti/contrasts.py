"""Contrast selection: which five task contrasts the study carries forward.

The 31 non-negative HCP contrasts are compared by the similarity of their spatial
activation patterns across the DLPFC, clustered, and one representative taken per
cluster. Produces manuscript Figs. S3 (similarity matrix), S4 (dendrogram) and
S5 (per-parcel profiles).

This reimplements ``pipelines/01_contrast_selection/MeanSTD.py`` from the
`docker-hcp` repository. The expensive half of that stage -- extracting each
subject's DLPFC betas from the HCP, one AWS container per subject -- has already
run, and its output is ``data/rois/DLPFCroi.npy`` (176 subjects x 31 contrasts x
26 parcels). Everything here is a correlation on a 31 x 26 matrix.

Three defects in the original are fixed; see that directory's README.

Note for the SI: this uses **31** contrasts, the number in the data array, not
the 22 the SI text states.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from sti.config import ALL_DLPFC_PARCELS, Config, DEFAULT_CONFIG

#: The 31 non-negative HCP contrasts, in the order of the data array's axis 1.
CONTRASTS: tuple[str, ...] = (
    "WORKING_MEM_2BK_BODY",
    "WORKING_MEM_2BK_FACE",
    "WORKING_MEM_2BK_PLACE",
    "WORKING_MEM_2BK_TOOL",
    "WORKING_MEM_0BK_BODY",
    "WORKING_MEM_0BK_FACE",
    "WORKING_MEM_0BK_PLACE",
    "WORKING_MEM_0BK_TOOL",
    "WORKING_MEM_2BK",
    "WORKING_MEM_0BK",
    "WORKING_MEM_BODY",
    "WORKING_MEM_FACE",
    "WORKING_MEM_PLACE",
    "WORKING_MEM_TOOL",
    "GAMBLING_PUNISH",
    "GAMBLING_REWARD",
    "MOTOR_CUE",
    "MOTOR_LF",
    "MOTOR_LH",
    "MOTOR_RF",
    "MOTOR_RH",
    "MOTOR_T",
    "MOTOR_AVG",
    "LANGUAGE_MATH",
    "LANGUAGE_STORY",
    "SOCIAL_RANDOM",
    "SOCIAL_TOM",
    "RELATIONAL_MATCH",
    "RELATIONAL_REL",
    "EMOTION_FACES",
    "EMOTION_SHAPES",
)

#: The five representatives carried into every later analysis, one per cluster.
REPRESENTATIVES: tuple[str, ...] = (
    "EMOTION_SHAPES", "SOCIAL_TOM", "WORKING_MEM_2BK", "MOTOR_AVG", "LANGUAGE_STORY",
)

#: Dendrogram height at which the SI cuts the tree.
CLUSTER_THRESHOLD: float = 1.0


def load_contrast_betas(config: Config = DEFAULT_CONFIG, path: Path | None = None) -> np.ndarray:
    """``(n_subjects, n_contrasts, n_parcels)`` mean beta per DLPFC parcel."""
    path = path or (config.data_dir / "rois" / "DLPFCroi.npy")
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. It is the output of the per-subject extraction "
            "in pipelines/01_contrast_selection."
        )
    data = np.load(path)
    if data.ndim != 3:
        raise ValueError(f"expected 3-D (subject, contrast, parcel), got {data.shape}")
    if data.shape[1] != len(CONTRASTS):
        raise ValueError(
            f"{path.name} has {data.shape[1]} contrasts but "
            f"{len(CONTRASTS)} names are defined"
        )
    if data.shape[2] != len(ALL_DLPFC_PARCELS):
        raise ValueError(
            f"{path.name} has {data.shape[2]} parcels, expected {len(ALL_DLPFC_PARCELS)}"
        )
    return data


def similarity_matrix(data: np.ndarray) -> np.ndarray:
    """Correlation between every pair of contrasts' spatial patterns (Fig. S3).

    Subjects are averaged first, then contrasts correlated across the 26 parcels.
    """
    return np.corrcoef(data.mean(axis=0))


def linkage(rsm: np.ndarray, method: str = "ward", *, rescale: bool = True):
    """Hierarchical clustering of the contrasts (Fig. S4).

    Each contrast's row of the similarity matrix is its feature vector, which is
    how the original analysis clustered and what scipy does with a square 2-D
    input. Ward linkage, as the SI states.

    ``rescale`` maps correlations from [-1, 1] onto [0, 1] before clustering.
    The original does this and the SI does not mention it, but it is load-bearing
    for the reported result: it halves every distance, so the SI's threshold of
    1.0 yields **five** clusters with it and **eight** without. With it, each of
    the five clusters contains exactly one of the five representative contrasts,
    reproducing the published selection exactly.
    """
    from scipy.cluster.hierarchy import linkage as _linkage

    return _linkage((rsm + 1) / 2 if rescale else rsm, method=method)


def clusters(rsm: np.ndarray, threshold: float = CLUSTER_THRESHOLD,
             method: str = "ward", *, rescale: bool = True):
    """Cluster assignment for each contrast at the SI's dendrogram cut."""
    from scipy.cluster.hierarchy import fcluster

    return fcluster(linkage(rsm, method, rescale=rescale), t=threshold,
                    criterion="distance")


def parcel_profiles(data: np.ndarray, contrasts=REPRESENTATIVES) -> dict:
    """Mean beta per DLPFC parcel for each representative contrast (Fig. S5)."""
    mean = data.mean(axis=0)
    return {c: mean[CONTRASTS.index(c)] for c in contrasts if c in CONTRASTS}
