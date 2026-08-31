"""Contrast selection must reproduce the five published representatives."""
import numpy as np
import pytest

from sti.config import ALL_DLPFC_PARCELS
from sti.contrasts import (CONTRASTS, CLUSTER_THRESHOLD, REPRESENTATIVES, clusters,
                           linkage, load_contrast_betas, parcel_profiles,
                           similarity_matrix)

pytestmark = pytest.mark.skipif(
    not (__import__("pathlib").Path("data/rois/DLPFCroi.npy").exists()),
    reason="DLPFCroi.npy not present",
)


@pytest.fixture(scope="module")
def data():
    return load_contrast_betas()


def test_data_shape_matches_the_declared_names(data):
    assert data.shape[1] == len(CONTRASTS) == 31
    assert data.shape[2] == len(ALL_DLPFC_PARCELS) == 26


def test_similarity_matrix_is_a_valid_correlation_matrix(data):
    rsm = similarity_matrix(data)
    assert rsm.shape == (len(CONTRASTS),) * 2
    assert np.allclose(rsm, rsm.T)
    assert np.allclose(np.diag(rsm), 1.0)
    assert rsm.min() >= -1.0 and rsm.max() <= 1.0


def test_clustering_reproduces_the_five_published_representatives(data):
    """Each cluster should contain exactly one contrast the paper carried forward."""
    assign = clusters(similarity_matrix(data), threshold=CLUSTER_THRESHOLD)
    assert len(set(assign)) == 5, "the SI reports five clusters"
    for c in set(assign):
        members = {CONTRASTS[i] for i in range(len(assign)) if assign[i] == c}
        assert len(members & set(REPRESENTATIVES)) == 1, (
            f"cluster {c} should contain exactly one representative"
        )


def test_the_rescaling_is_load_bearing(data):
    """MeanSTD.py rescales r to [0,1] before clustering; the SI does not say so.

    Without it the SI's threshold of 1.0 does not give five clusters, so the
    step cannot be dropped as cosmetic.
    """
    rsm = similarity_matrix(data)
    from scipy.cluster.hierarchy import fcluster

    with_rescale = fcluster(linkage(rsm, rescale=True), t=1.0, criterion="distance")
    without = fcluster(linkage(rsm, rescale=False), t=1.0, criterion="distance")
    assert len(set(with_rescale)) == 5
    assert len(set(without)) != 5


def test_parcel_profiles_shape(data):
    prof = parcel_profiles(data)
    assert set(prof) == set(REPRESENTATIVES)
    for v in prof.values():
        assert v.shape == (len(ALL_DLPFC_PARCELS),)
