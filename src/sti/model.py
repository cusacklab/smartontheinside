"""The elastic-net model that predicts vertex activation from vertex connectivity.

One model is fitted per (contrast, hemisphere). Subjects and seed vertices are
collapsed into rows, so a fit sees ``(n_subjects * n_vertices, n_targets)``
predictors and one activation value per row.
"""

from __future__ import annotations

import logging

import numpy as np
from sklearn.base import BaseEstimator
from sklearn.linear_model import ElasticNet, LinearRegression

from sti.config import Config, DEFAULT_CONFIG

log = logging.getLogger(__name__)


def build_estimator(config: Config = DEFAULT_CONFIG) -> BaseEstimator:
    """Return the estimator for these hyperparameters.

    ``alpha == 0`` degenerates to ordinary least squares; scikit-learn warns and
    behaves poorly if ``ElasticNet`` is given alpha=0, so it is special-cased --
    matching the original analysis.
    """
    if config.alpha == 0:
        return LinearRegression()
    return ElasticNet(
        alpha=config.alpha,
        l1_ratio=config.l1_ratio,
        random_state=config.random_state,
    )


def flatten(X: np.ndarray) -> np.ndarray:
    """Collapse ``(n_subjects, n_vertices, n_targets)`` to rows of targets."""
    if X.ndim == 2:  # a single subject
        return X
    n_sub, n_vert, n_targ = X.shape
    return X.reshape(n_sub * n_vert, n_targ)


def flatten_y(y: np.ndarray) -> np.ndarray:
    """Collapse ``(n_subjects, n_vertices)`` to a 1-D response vector."""
    return np.asarray(y).reshape(-1)


def fit(X: np.ndarray, y: np.ndarray, config: Config = DEFAULT_CONFIG) -> BaseEstimator:
    """Fit one model. ``X`` may be 2-D or 3-D; ``y`` is flattened to match."""
    Xf, yf = flatten(X), flatten_y(y)
    if Xf.shape[0] != yf.shape[0]:
        raise ValueError(
            f"X has {Xf.shape[0]} rows but y has {yf.shape[0]}; "
            "subject/vertex dimensions disagree"
        )
    model = build_estimator(config)
    model.fit(Xf, yf)
    return model


def predict(model: BaseEstimator, X: np.ndarray) -> np.ndarray:
    """Predict activation, returning a flat vector of vertex predictions."""
    return np.asarray(model.predict(flatten(X))).reshape(-1)


def as_float32(X: np.ndarray) -> np.ndarray:
    """Downcast to float32.

    The adult connectivity array is ~0.9 GB in float64 per hemisphere and is
    re-materialised on every leave-one-out fold; float32 halves that at no
    meaningful cost to a regularised fit.
    """
    return np.asarray(X, dtype=np.float32)
