import numpy as np
import pytest
from sklearn.linear_model import ElasticNet, LinearRegression

from sti.config import Config
from sti.model import build_estimator, fit, flatten, predict


def test_alpha_zero_is_ordinary_least_squares():
    assert isinstance(build_estimator(Config(alpha=0)), LinearRegression)
    assert isinstance(build_estimator(Config(alpha=0.4)), ElasticNet)


def test_flatten_collapses_subject_and_vertex():
    X = np.zeros((6, 40, 12))
    assert flatten(X).shape == (240, 12)
    assert flatten(X[0]).shape == (40, 12)   # single subject passes through


def test_fit_recovers_a_linear_mapping():
    rng = np.random.default_rng(0)
    X = rng.normal(size=(6, 40, 12))
    y = X @ rng.normal(size=12) + rng.normal(scale=0.05, size=(6, 40))
    model = fit(X, y, Config(alpha=0.01, l1_ratio=0.5))
    r = np.corrcoef(predict(model, X[[0]]), y[0])[0, 1]
    assert r > 0.95


def test_mismatched_shapes_raise():
    X = np.zeros((6, 40, 12))
    with pytest.raises(ValueError, match="rows"):
        fit(X, np.zeros((3, 40)), Config())


def test_config_validates_hyperparameters():
    with pytest.raises(ValueError):
        Config(l1_ratio=1.5)
    with pytest.raises(ValueError):
        Config(alpha=-1)
