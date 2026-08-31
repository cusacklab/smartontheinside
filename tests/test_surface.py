"""The invariant tying surface geometry to the data arrays.

If these fail, the spatial-null analyses are attaching coordinates to the wrong
vertices.
"""
import numpy as np
import pytest

from sti.config import ALL_DLPFC_PARCELS, DEFAULT_CONFIG, DLPFC_PARCELS, N_SEED_VERTICES

nib = pytest.importorskip("nibabel")
PARC = DEFAULT_CONFIG.data_dir / "parcellations"
pytestmark = pytest.mark.skipif(not PARC.exists(), reason="parcellation files not present")


@pytest.mark.parametrize("hemi", ["L", "R"])
def test_dlpfc_mask_matches_the_data_dimensions(hemi):
    from sti.surface import dlpfc_vertex_indices

    idx = dlpfc_vertex_indices(hemi, str(PARC))
    assert idx.size == N_SEED_VERTICES[hemi]
    assert np.all(np.diff(idx) > 0), "vertex order must be ascending to match the arrays"


@pytest.mark.parametrize("hemi", ["L", "R"])
def test_coordinates_align_with_the_mask(hemi):
    from sti.surface import dlpfc_coordinates

    assert dlpfc_coordinates(hemi).shape == (N_SEED_VERTICES[hemi], 3)


def test_hemisphere_label_convention_is_as_documented():
    """1-180 are RIGHT and 181-360 LEFT in these files -- the opposite of the usual
    assumption, so it is asserted rather than trusted."""
    for hemi, sample in [("R", 26), ("L", 206)]:
        lt = nib.load(str(PARC / f"ff.{hemi}.label.gii")).labeltable.get_labels_as_dict()
        assert lt[sample].startswith(f"{hemi}_"), f"{sample} should be {hemi} hemisphere"
    assert len(ALL_DLPFC_PARCELS) == 26
    assert len(DLPFC_PARCELS["L"]) == len(DLPFC_PARCELS["R"]) == 13
    assert set(DLPFC_PARCELS["L"]) & set(DLPFC_PARCELS["R"]) == set()


@pytest.mark.parametrize("hemi", ["R"])
def test_distance_matrix_is_a_valid_metric(hemi):
    from sti.surface import distance_matrix

    D = distance_matrix(hemi)
    assert D.shape == (N_SEED_VERTICES[hemi],) * 2
    assert np.allclose(D, D.T) and np.allclose(np.diag(D), 0)
    assert D.max() < 200  # mm; a DLPFC patch, not a whole hemisphere
