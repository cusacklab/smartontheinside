"""Leave-one-region-out cross-validation of the evaluation protocols."""

import numpy as np
import pytest

from sti.config import Config
from sti.datasets import Activation, Connectivity
from sti.evaluate import neonatal, stitched_predictions

CONFIG = Config(alpha=0.0)


def _data(seed=0, n_adult=6, n_neo=4, n_vert=120, n_feat=15, n_regions=6):
    rng = np.random.default_rng(seed)
    folds = np.repeat(np.arange(n_regions), n_vert // n_regions)
    base = rng.normal(size=(n_vert, n_feat))
    w = rng.normal(size=n_feat)
    target = base @ w
    conn = lambda n: Connectivity(
        data={"L": base[None] + 0.05 * rng.normal(size=(n, n_vert, n_feat))},
        cohort="synthetic")
    acts = {"tfMRI_SYNTH": Activation(
        data={"L": target[None] + 0.3 * target.std() * rng.normal(size=(n_adult, n_vert))},
        task="tfMRI_SYNTH", cohort="synthetic")}
    return conn(n_adult), conn(n_neo), acts, folds, target


def test_stitched_predictions_cover_every_vertex_without_leakage():
    adult, neo, acts, folds, _ = _data()
    y = acts["tfMRI_SYNTH"].zscored()["L"]
    out = stitched_predictions(adult["L"], y, neo["L"], folds, CONFIG)
    assert out.shape == (4, 120)
    assert np.isfinite(out).all()


def test_feature_signal_survives_region_cv():
    """A connectivity-driven map should still be predicted in unseen regions."""
    adult, neo, acts, folds, target = _data()
    res, _ = neonatal(adult, neo, acts, [f"n{i}" for i in range(4)],
                      config=CONFIG, hemispheres=("L",),
                      region_folds={"L": folds})
    within = res[res.task == res.comparison_task]
    assert (res.protocol == "neonatal_regioncv").all()
    assert within.pearson.mean() > 0.7


def test_region_mean_signal_cannot_score_positively_under_region_cv():
    """A map that is ONLY region means must not yield positive accuracy when
    the features carry no region information. (It scores at or BELOW zero:
    each fold's intercept is the mean of the other regions, which
    anti-correlates with the held-out region's mean -- the bias from stitched
    intercepts is conservative, never flattering.)"""
    rng = np.random.default_rng(3)
    n_vert, n_regions = 120, 6
    folds = np.repeat(np.arange(n_regions), n_vert // n_regions)
    region_means = rng.normal(size=n_regions)[folds]
    X = rng.normal(size=(6, n_vert, 15))  # pure noise features
    adult = Connectivity(data={"L": X}, cohort="s")
    neo = Connectivity(data={"L": rng.normal(size=(4, n_vert, 15))}, cohort="s")
    acts = {"tfMRI_SYNTH": Activation(
        data={"L": region_means[None] + 0.1 * rng.normal(size=(6, n_vert))},
        task="tfMRI_SYNTH", cohort="s")}
    res, _ = neonatal(adult, neo, acts, [f"n{i}" for i in range(4)],
                      config=CONFIG, hemispheres=("L",),
                      region_folds={"L": folds})
    within = res[res.task == res.comparison_task]
    assert within.pearson.mean() < 0.05


def test_region_cv_changes_the_prediction():
    adult, neo, acts, folds, _ = _data()
    plain, _ = neonatal(adult, neo, acts, list("abcd"), config=CONFIG,
                        hemispheres=("L",))
    cv, _ = neonatal(adult, neo, acts, list("abcd"), config=CONFIG,
                     hemispheres=("L",), region_folds={"L": folds})
    assert (plain.protocol == "neonatal").all()
    a = plain[plain.task == plain.comparison_task].pearson.to_numpy()
    b = cv[cv.task == cv.comparison_task].pearson.to_numpy()
    assert not np.allclose(a, b)
