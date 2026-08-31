import numpy as np
import pytest
from scipy.stats import pearsonr

from sti.spatial_null import SurrogateMaps, null_correlations, p_spin


@pytest.fixture(scope="module")
def geometry():
    """A small 2-D lattice standing in for a cortical patch."""
    xs, ys = np.meshgrid(np.arange(22), np.arange(22))
    coords = np.column_stack([xs.ravel(), ys.ravel()]).astype(float)
    from scipy.spatial.distance import pdist, squareform
    return squareform(pdist(coords))


@pytest.fixture(scope="module")
def smooth_map(geometry):
    rng = np.random.default_rng(0)
    W = np.exp(-geometry / 3.0)
    W /= W.sum(1, keepdims=True)
    v = W @ rng.normal(size=geometry.shape[0])
    return (v - v.mean()) / v.std()


def test_surrogates_preserve_the_marginal_distribution(geometry, smooth_map):
    gen = SurrogateMaps(geometry, knn=200, n_pairs=20_000, seed=0)
    S = gen.generate(smooth_map, 5)
    assert S.shape == (5, smooth_map.size)
    for s in S:
        assert np.allclose(np.sort(s), np.sort(smooth_map))


def test_surrogates_match_the_variogram_better_than_permutation(geometry, smooth_map):
    gen = SurrogateMaps(geometry, knn=200, n_pairs=20_000, seed=0)
    rng = np.random.default_rng(1)
    target = gen.fast_variogram(smooth_map)
    err = lambda g: np.mean(np.abs(g - target)) / target.mean()
    surr = err(np.array([gen.fast_variogram(s) for s in gen.generate(smooth_map, 20)]).mean(0))
    perm = err(np.array([gen.fast_variogram(rng.permutation(smooth_map))
                         for _ in range(20)]).mean(0))
    assert surr < perm / 2, f"surrogate err {surr:.3f} not much better than permutation {perm:.3f}"


def test_null_is_wider_than_a_naive_permutation_null(geometry, smooth_map):
    """The whole point: ignoring autocorrelation makes everything look significant."""
    gen = SurrogateMaps(geometry, knn=200, n_pairs=20_000, seed=0)
    rng = np.random.default_rng(2)
    S = gen.generate(smooth_map, 100)
    other = gen.generate(smooth_map, 1)[0]
    spatial_sd = null_correlations(other, smooth_map, S).std()
    perm_sd = np.array([pearsonr(other, rng.permutation(smooth_map))[0]
                        for _ in range(200)]).std()
    assert spatial_sd > 3 * perm_sd


def test_detects_a_genuine_effect(geometry, smooth_map):
    gen = SurrogateMaps(geometry, knn=200, n_pairs=20_000, seed=0)
    rng = np.random.default_rng(3)
    S = gen.generate(smooth_map, 200)
    pred = smooth_map + rng.normal(scale=1.0, size=smooth_map.size)
    r = pearsonr(pred, smooth_map)[0]
    assert p_spin(r, null_correlations(pred, smooth_map, S)) < 0.05


def test_p_spin_never_returns_zero():
    null = np.zeros(100)
    assert p_spin(10.0, null) == pytest.approx(1 / 101)
    assert p_spin(-10.0, null, tail="less") == pytest.approx(1 / 101)
    assert 0 < p_spin(0.5, np.random.default_rng(0).normal(size=100), tail="two-sided") <= 1


def test_rejects_wrong_length_input(geometry, smooth_map):
    gen = SurrogateMaps(geometry, knn=200, n_pairs=20_000, seed=0)
    with pytest.raises(ValueError, match="vertices"):
        gen.generate(smooth_map[:-1], 1)
