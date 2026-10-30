"""The geometry/connectivity variance partition (Fig. 1b)."""

import numpy as np
import pytest

from sti.shares import partition, spatial_folds


@pytest.fixture(scope="module")
def geometry():
    rng = np.random.default_rng(0)
    coords = rng.uniform(0, 40, size=(400, 3))
    return coords, rng


def _features(coords, rng, n_feat=15, smooth_scale=8.0):
    """Smooth spatial features (geometry-like) on the point cloud."""
    from scipy.spatial.distance import cdist
    anchors = rng.uniform(0, 40, size=(n_feat, 3))
    return np.exp(-cdist(coords, anchors) / smooth_scale)


def test_spatial_folds_are_contiguous(geometry):
    coords, _ = geometry
    labels = spatial_folds(coords, k=5)
    assert set(labels) == set(range(5))
    # a block's spread must be clearly smaller than the cloud's: blocks are local
    spread = np.mean([coords[labels == b].std(axis=0).mean() for b in range(5)])
    assert spread < 0.75 * coords.std(axis=0).mean()


def test_partition_attributes_geometry_to_geometry(geometry):
    """y built from G alone: unique_C must be ~0 even though C correlates with G."""
    coords, rng = geometry
    G = _features(coords, rng)
    C = 0.7 * G @ rng.normal(size=(G.shape[1], 20)) + 0.3 * rng.normal(size=(400, 20))
    y = G @ rng.normal(size=G.shape[1])
    res = partition(G, C, y, coords, k=5)
    assert res["r2_geometry"] > 0.6
    assert res["unique_connectivity"] < 0.1
    assert res["unique_geometry"] > 0.15


def test_partition_finds_a_unique_connectivity_component(geometry):
    """y depends on a C component independent of G: unique_C must be large."""
    coords, rng = geometry
    G = _features(coords, rng)
    C_indep = rng.normal(size=(400, 20))  # not a function of position
    C = np.hstack([0.5 * G[:, :5], C_indep])
    y = C_indep @ rng.normal(size=20) + 0.5 * (G @ rng.normal(size=G.shape[1]))
    res = partition(G, C, y, coords, k=5)
    assert res["unique_connectivity"] > 0.3
    assert res["r2_combined"] > res["r2_geometry"] + 0.2
    # the commonality identities hold by construction
    assert res["unique_geometry"] + res["unique_connectivity"] + res["shared"] == \
        pytest.approx(res["r2_combined"], abs=1e-9)


def test_partition_handles_constant_columns(geometry):
    coords, rng = geometry
    G = _features(coords, rng)
    G[:, 0] = 0.0  # a zero-padded column must not produce NaNs
    C = rng.normal(size=(400, 10))
    y = G @ rng.normal(size=G.shape[1])
    res = partition(G, C, y, coords, k=4)
    assert all(np.isfinite(v) for v in res.values() if isinstance(v, float))
