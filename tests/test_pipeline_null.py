"""The full-pipeline surrogate null (reviewer 1's key control).

The two synthetic-cohort tests are the scientific validation: the null must be
beatable when adults and neonates share function-specific structure, and must
NOT be beatable when their connectivity encodes nothing but spatial position —
which is exactly the confound the control exists to expose.
"""

import numpy as np
import pandas as pd
import pytest

from sti.config import Config
from sti.datasets import Activation, Connectivity
from sti.pipeline_null import null_transfer, summarise
from sti.spatial_null import SurrogateMaps


@pytest.fixture(scope="module")
def geometry():
    """A small 2-D lattice standing in for a cortical patch."""
    xs, ys = np.meshgrid(np.arange(22), np.arange(22))
    coords = np.column_stack([xs.ravel(), ys.ravel()]).astype(float)
    from scipy.spatial.distance import pdist, squareform
    return coords, squareform(pdist(coords))


def _smooth(dist, v, scale=3.0):
    W = np.exp(-dist / scale)
    return (W / W.sum(1, keepdims=True)) @ v


# --------------------------------------------------------------------------- #
# generate_permutations


def test_permutations_reproduce_resampled_surrogates(geometry):
    _, dist = geometry
    rng = np.random.default_rng(0)
    x = _smooth(dist, rng.normal(size=dist.shape[0]))
    a = SurrogateMaps(dist, knn=200, n_pairs=20_000, seed=7)
    b = SurrogateMaps(dist, knn=200, n_pairs=20_000, seed=7)
    assert np.allclose(a.generate(x, 3), x[b.generate_permutations(x, 3)])


def test_permutations_are_permutations(geometry):
    _, dist = geometry
    rng = np.random.default_rng(1)
    x = _smooth(dist, rng.normal(size=dist.shape[0]))
    perms = SurrogateMaps(dist, knn=200, n_pairs=20_000, seed=0).generate_permutations(x, 4)
    identity = np.arange(dist.shape[0])
    for pi in perms:
        assert np.array_equal(np.sort(pi), identity)
        assert not np.array_equal(pi, identity)


# --------------------------------------------------------------------------- #
# the two validation cohorts


def _cohorts(geometry, *, positional_only: bool, seed=0):
    """Synthetic adult + neonate data on the lattice.

    ``positional_only=False``: activation is a weighted sum of connectivity
    features that both cohorts share — function-specific structure the pipeline
    should transfer better than any surrogate.

    ``positional_only=True``: connectivity features are distances to anchor
    vertices (pure position) and the activation map is an independent smooth
    map. Whatever transfers is positional, and the null should absorb it.
    """
    coords, dist = geometry
    rng = np.random.default_rng(seed)
    n_vert, n_feat, n_adult, n_neo = dist.shape[0], 20, 8, 6

    if positional_only:
        anchors = rng.choice(n_vert, size=n_feat, replace=False)
        base = dist[:, anchors]  # (n_vert, n_feat): position and nothing else
        target = _smooth(dist, rng.normal(size=n_vert))  # unrelated smooth map
    else:
        base = rng.normal(size=(n_vert, n_feat))
        w = rng.normal(size=n_feat)
        target = base @ w

    def conn(n_sub, noise):
        X = base[None] + noise * rng.normal(size=(n_sub, n_vert, n_feat))
        return Connectivity(data={"L": X}, cohort="synthetic")

    acts = target[None] + 0.5 * target.std() * rng.normal(size=(n_adult, n_vert))
    activation = Activation(data={"L": acts}, task="tfMRI_SYNTH", cohort="synthetic")
    return conn(n_adult, 0.1 * base.std()), conn(n_neo, 0.1 * base.std()), activation, dist


CONFIG = Config(alpha=0.0)  # OLS: fast, and regularisation is irrelevant here


def _run(geometry, *, positional_only, n_surrogates=40):
    adult, neo, act, dist = _cohorts(geometry, positional_only=positional_only)
    null = null_transfer(adult, neo, act, hemi="L", dist=dist,
                         n_surrogates=n_surrogates, config=CONFIG, seed=0)
    # the observed statistic, computed the same way the real pipeline does
    from sti import model as model_mod
    from sti.spatial_null import correlation_matrix
    y = act.zscored()["L"]
    fitted = model_mod.fit(adult["L"], y, CONFIG)
    preds = model_mod.predict(fitted, model_mod.flatten(neo["L"])).reshape(len(neo["L"]), -1)
    observed = float(correlation_matrix(preds, y.mean(0)[None]).mean())
    obs_df = pd.DataFrame([{"task": "tfMRI_SYNTH", "hemi": "L",
                            "comparison_task": "tfMRI_SYNTH", "pearson": observed}])
    return summarise(null, obs_df).iloc[0]


def test_function_specific_structure_beats_the_null(geometry):
    row = _run(geometry, positional_only=False)
    assert row.observed_r > 0.5, "synthetic transfer should be easy"
    assert row.p_spin < 0.05
    assert row.excess_r > 0.2


def test_positional_structure_is_absorbed_by_the_null(geometry):
    """The point of the control: position-only transfer must NOT look significant."""
    row = _run(geometry, positional_only=True)
    assert row.observed_r > 0.2, \
        "positional features should transfer *something* — that is the confound"
    assert row.p_spin > 0.05
    assert row.observed_r < row.null_p95


# --------------------------------------------------------------------------- #
# bookkeeping


def test_output_shape_and_summary_columns(geometry):
    adult, neo, act, dist = _cohorts(geometry, positional_only=False)
    null = null_transfer(adult, neo, act, hemi="L", dist=dist,
                         n_surrogates=5, config=CONFIG, seed=3)
    assert len(null) == 5
    assert set(null.surrogate) == set(range(5))
    assert (null.seed == 3).all()
    assert (null.n_neonates == 6).all()

    obs = pd.DataFrame([{"task": "tfMRI_SYNTH", "hemi": "L",
                         "comparison_task": "tfMRI_SYNTH", "pearson": 0.9}])
    out = summarise(null, obs)
    for col in ("observed_r", "null_mean", "null_sd", "null_p95",
                "excess_r", "p_spin", "p_fdr", "stars"):
        assert col in out.columns
    assert out.p_spin.iloc[0] == pytest.approx(1 / 6)  # (0 + 1) / (5 + 1)
