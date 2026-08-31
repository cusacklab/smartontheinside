"""DLPFC surface geometry.

The connectivity and activation vectors are length 2207 (L) / 2185 (R): one entry
per DLPFC seed vertex, in ascending fs_LR 32k vertex order. This module recovers
that vertex ordering from the parcellation label files so each entry can be given
a coordinate -- which is what the spatial-null analyses need.

Verified: the DLPFC mask derived here contains exactly 2207 (L) and 2185 (R)
vertices, matching ``config.N_SEED_VERTICES``.
"""

from __future__ import annotations

import functools
from pathlib import Path

import numpy as np

from sti.config import Config, DEFAULT_CONFIG, DLPFC_PARCELS, Hemisphere, N_SEED_VERTICES

LABEL_FILE = "ff.{hemi}.label.gii"
SURFACE_FILE = (
    "Q1-Q6_RelatedParcellation210.{hemi}."
    "midthickness_MSMAll_2_d41_WRN_DeDrift.32k_fs_LR.surf.gii"
)


def _parcellation_dir(config: Config) -> Path:
    return config.data_dir / "parcellations"


@functools.lru_cache(maxsize=4)
def dlpfc_vertex_indices(hemi: Hemisphere, parc_dir: str) -> np.ndarray:
    """fs_LR 32k vertex indices of the DLPFC mask, ascending.

    This is the ordering of the seed dimension in the connectivity and activation
    arrays.
    """
    import nibabel as nib

    labels = nib.load(str(Path(parc_dir) / LABEL_FILE.format(hemi=hemi)))
    data = labels.agg_data("NIFTI_INTENT_LABEL")
    mask = np.isin(data, DLPFC_PARCELS[hemi])
    idx = np.where(mask)[0]
    expected = N_SEED_VERTICES[hemi]
    if idx.size != expected:
        raise ValueError(
            f"DLPFC mask for hemisphere {hemi} has {idx.size} vertices, "
            f"expected {expected}. Check the parcellation files."
        )
    return idx


def dlpfc_coordinates(hemi: Hemisphere, config: Config = DEFAULT_CONFIG) -> np.ndarray:
    """``(n_vertices, 3)`` midthickness coordinates for the DLPFC seed vertices."""
    import nibabel as nib

    parc_dir = _parcellation_dir(config)
    idx = dlpfc_vertex_indices(hemi, str(parc_dir))
    surf = nib.load(str(parc_dir / SURFACE_FILE.format(hemi=hemi)))
    coords = surf.agg_data("NIFTI_INTENT_POINTSET")
    return np.asarray(coords)[idx]


def distance_matrix(hemi: Hemisphere, config: Config = DEFAULT_CONFIG) -> np.ndarray:
    """Pairwise Euclidean distance between DLPFC seed vertices, in mm.

    Euclidean distance on the midthickness surface is a close approximation to
    geodesic distance within a patch as compact and convex as the DLPFC, and it
    avoids requiring a mesh-traversal dependency. It is used to characterise the
    spatial autocorrelation of the observed maps in :mod:`sti.spatial_null`.
    """
    from scipy.spatial.distance import squareform, pdist

    return squareform(pdist(dlpfc_coordinates(hemi, config)))
