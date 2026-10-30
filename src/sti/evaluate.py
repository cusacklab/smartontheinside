"""The three evaluation protocols reported in the paper.

============================  ====================================  =========
Protocol                      Trained on / evaluated against        Figure
============================  ====================================  =========
:func:`adult_loo`             adults, leave-one-out; own activation  Fig. 2
:func:`adult_group_mean_loo`  adults, leave-one-out; group-average   Fig. 4
:func:`neonatal`              all adults; adult group-average        Fig. 3
============================  ====================================  =========

Each returns a tidy :class:`pandas.DataFrame` with one row per
(task, comparison_task, hemisphere, subject), so the leading diagonal
(``task == comparison_task``) is within-task accuracy and the off-diagonal cells
give the task-specificity matrix.

The legacy scripts accumulated results into one growing DataFrame and re-pickled
it inside the innermost loop, which is why the stored infant pickles are 21.6 GB
each. Here results are collected as records and framed once at the end.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.stats import pearsonr
from sklearn.model_selection import LeaveOneOut

from sti import model as model_mod
from sti.config import Config, DEFAULT_CONFIG, HEMISPHERES, Hemisphere, Task
from sti.datasets import Activation, Connectivity

log = logging.getLogger(__name__)


@dataclass
class Predictions:
    """Per-(task, hemisphere) predicted activation, one row per subject."""

    values: dict[tuple[Task, Hemisphere], np.ndarray]

    @classmethod
    def empty(cls) -> "Predictions":
        # NOTE: built per key. The legacy code wrote
        #   pred = {'L': [], 'R': []}; all_pred = {t: pred for t in tasks}
        # which gives every task a reference to the SAME dict, so all five tasks
        # appended into one pair of lists.
        return cls(values={})

    def add(self, task: Task, hemi: Hemisphere, vector: np.ndarray) -> None:
        self.values.setdefault((task, hemi), []).append(np.asarray(vector))

    def finalise(self) -> None:
        self.values = {k: np.vstack(v) for k, v in self.values.items()}


def _record(*, task, comparison_task, hemi, subject, r, p, config, protocol) -> dict:
    return {
        "protocol": protocol,
        "algorithm": "LinearRegression" if config.alpha == 0 else "ElasticNet",
        "alpha": config.alpha,
        "l1_ratio": config.l1_ratio,
        "task": task,
        "comparison_task": comparison_task,
        "hemi": hemi,
        "subject": subject,
        "pearson": r,
        "p_value": p,
    }


def stitched_predictions(X_tr, y_tr, X_te, folds, config) -> np.ndarray:
    """Leave-one-region-out predictions, stitched into full maps.

    For each region fold, the model is fitted on the training subjects'
    vertices OUTSIDE the region and predicts the test subjects' vertices
    INSIDE it, so no prediction ever comes from a model that saw its own
    territory -- interpolation across vertices is excluded by construction.

    Note on stitched intercepts: each fold's intercept is estimated from the
    other regions, so structure carried purely by region means scores at or
    below zero (the leave-one-out means anti-correlate with the held-out
    mean). The bias is conservative -- region means cannot masquerade as
    positive transfer; only feature-driven structure can score.

    ``X_tr``: (n_train_subjects, n_vertices, n_targets); ``y_tr``:
    (n_train_subjects, n_vertices); ``X_te``: (n_test_subjects, n_vertices,
    n_targets); ``folds``: (n_vertices,) region label per vertex. Returns
    (n_test_subjects, n_vertices).
    """
    folds = np.asarray(folds).reshape(-1)
    if folds.size != X_tr.shape[1]:
        raise ValueError(f"{folds.size} fold labels for {X_tr.shape[1]} vertices")
    out = np.empty((X_te.shape[0], X_te.shape[1]), dtype=np.float64)
    for b in np.unique(folds):
        tr_v, te_v = folds != b, folds == b
        fitted = model_mod.fit(X_tr[:, tr_v, :], y_tr[:, tr_v], config)
        out[:, te_v] = model_mod.predict(
            fitted, model_mod.flatten(X_te[:, te_v, :])
        ).reshape(X_te.shape[0], -1)
    return out


def _score_against_all(
    y_hat: np.ndarray,
    targets: dict[Task, np.ndarray],
    *,
    task: Task,
    hemi: Hemisphere,
    subject: str,
    config: Config,
    protocol: str,
) -> list[dict]:
    """Correlate one prediction against the observed map for every contrast."""
    out = []
    for comparison_task, y_obs in targets.items():
        r, p = pearsonr(np.asarray(y_obs).reshape(-1), y_hat)
        out.append(
            _record(
                task=task, comparison_task=comparison_task, hemi=hemi,
                subject=subject, r=r, p=p, config=config, protocol=protocol,
            )
        )
    return out


# --------------------------------------------------------------------------- #

def adult_loo(
    connectivity: Connectivity,
    activations: dict[Task, Activation],
    subjects: list[str],
    *,
    config: Config = DEFAULT_CONFIG,
    hemispheres=HEMISPHERES,
    float32: bool = True,
    model_tasks=None,
    region_folds=None,
) -> tuple[pd.DataFrame, Predictions]:
    """Leave-one-adult-out; each model predicts the held-out adult's own map (Fig. 2).

    With ``region_folds`` (a dict of per-hemisphere vertex->region labels),
    predictions are additionally leave-one-region-out via
    :func:`stitched_predictions`.
    """
    records: list[dict] = []
    preds = Predictions.empty()
    protocol = "adult_loo" + ("_regioncv" if region_folds is not None else "")

    # model_tasks restricts which models are TRAINED, so the work can be split
    # across cluster jobs. Every model is still evaluated against every task's
    # map, so each shard yields a complete row of the specificity matrix.
    for task in (model_tasks if model_tasks is not None else list(activations)):
        activation = activations[task]
        y_all = activation.zscored()
        for hemi in hemispheres:
            X = connectivity[hemi]
            if float32:
                X = model_mod.as_float32(X)
            y = y_all[hemi]

            for train_idx, test_idx in LeaveOneOut().split(X):
                i = int(test_idx[0])
                if region_folds is not None:
                    y_hat = stitched_predictions(
                        X[train_idx], y[train_idx], X[test_idx],
                        region_folds[hemi], config)[0]
                else:
                    fitted = model_mod.fit(X[train_idx], y[train_idx], config)
                    y_hat = model_mod.predict(fitted, X[test_idx])
                preds.add(task, hemi, y_hat)

                targets = {t: a[hemi][i] for t, a in activations.items()}
                records += _score_against_all(
                    y_hat, targets, task=task, hemi=hemi, subject=subjects[i],
                    config=config, protocol=protocol,
                )
            log.info("%s done: task=%s hemi=%s", protocol, task, hemi)

    preds.finalise()
    return pd.DataFrame.from_records(records), preds


def adult_group_mean_loo(
    connectivity: Connectivity,
    activations: dict[Task, Activation],
    subjects: list[str],
    *,
    config: Config = DEFAULT_CONFIG,
    hemispheres=HEMISPHERES,
    float32: bool = True,
    model_tasks=None,
    region_folds=None,
) -> tuple[pd.DataFrame, Predictions]:
    """Leave-one-adult-out; each model predicts the group-average map (Fig. 4).

    The held-out adult is excluded from the group average as well as from
    training, so the target is independent of the test subject -- this is the
    like-for-like comparison with the neonatal protocol, where the neonate
    contributes nothing to the adult average. With ``region_folds``,
    predictions are additionally leave-one-region-out.
    """
    records: list[dict] = []
    preds = Predictions.empty()
    protocol = "adult_group_mean_loo" + ("_regioncv" if region_folds is not None else "")

    # model_tasks restricts which models are TRAINED, so the work can be split
    # across cluster jobs. Every model is still evaluated against every task's
    # map, so each shard yields a complete row of the specificity matrix.
    for task in (model_tasks if model_tasks is not None else list(activations)):
        activation = activations[task]
        y_all = activation.zscored()
        for hemi in hemispheres:
            X = connectivity[hemi]
            if float32:
                X = model_mod.as_float32(X)
            y = y_all[hemi]

            for train_idx, test_idx in LeaveOneOut().split(X):
                i = int(test_idx[0])
                if region_folds is not None:
                    y_hat = stitched_predictions(
                        X[train_idx], y[train_idx], X[test_idx],
                        region_folds[hemi], config)[0]
                else:
                    fitted = model_mod.fit(X[train_idx], y[train_idx], config)
                    y_hat = model_mod.predict(fitted, X[test_idx])
                preds.add(task, hemi, y_hat)

                # group average over training subjects only
                targets = {
                    t: a.zscored()[hemi][train_idx].mean(axis=0)
                    for t, a in activations.items()
                }
                records += _score_against_all(
                    y_hat, targets, task=task, hemi=hemi, subject=subjects[i],
                    config=config, protocol=protocol,
                )
            log.info("%s done: task=%s hemi=%s", protocol, task, hemi)

    preds.finalise()
    return pd.DataFrame.from_records(records), preds


def neonatal(
    adult_connectivity: Connectivity,
    neonatal_connectivity: Connectivity,
    activations: dict[Task, Activation],
    neonates: list[str],
    *,
    config: Config = DEFAULT_CONFIG,
    hemispheres=HEMISPHERES,
    float32: bool = True,
    model_tasks=None,
    region_folds=None,
) -> tuple[pd.DataFrame, Predictions]:
    """Train on all adults, apply unchanged to each neonate (Fig. 3).

    The adult models are fitted once per (task, hemisphere) and reused across
    neonates -- there is no leave-one-out here, because no neonate contributes to
    the training set. With ``region_folds``, predictions are additionally
    leave-one-region-out.
    """
    records: list[dict] = []
    preds = Predictions.empty()
    protocol = "neonatal" + ("_regioncv" if region_folds is not None else "")

    # model_tasks restricts which models are TRAINED, so the work can be split
    # across cluster jobs. Every model is still evaluated against every task's
    # map, so each shard yields a complete row of the specificity matrix.
    for task in (model_tasks if model_tasks is not None else list(activations)):
        activation = activations[task]
        y_all = activation.zscored()
        for hemi in hemispheres:
            X_adult = adult_connectivity[hemi]
            X_inf = neonatal_connectivity[hemi]
            if float32:
                X_adult = model_mod.as_float32(X_adult)
                X_inf = model_mod.as_float32(X_inf)

            if region_folds is not None:
                all_hat = stitched_predictions(
                    X_adult, y_all[hemi], X_inf, region_folds[hemi], config)
            else:
                fitted = model_mod.fit(X_adult, y_all[hemi], config)
                all_hat = None
            targets = {t: a.zscored()[hemi].mean(axis=0) for t, a in activations.items()}

            for i in range(X_inf.shape[0]):
                y_hat = all_hat[i] if all_hat is not None else model_mod.predict(fitted, X_inf[i])
                preds.add(task, hemi, y_hat)
                records += _score_against_all(
                    y_hat, targets, task=task, hemi=hemi, subject=neonates[i],
                    config=config, protocol=protocol,
                )
            log.info("%s done: task=%s hemi=%s (n=%d)", protocol, task, hemi, X_inf.shape[0])

    preds.finalise()
    return pd.DataFrame.from_records(records), preds


# --------------------------------------------------------------------------- #

def specificity_matrix(results: pd.DataFrame, hemi: Hemisphere | None = None) -> pd.DataFrame:
    """Mean prediction accuracy for every (model task, evaluated task) pair."""
    df = results if hemi is None else results[results.hemi == hemi]
    return df.pivot_table(
        index="task", columns="comparison_task", values="pearson", aggfunc="mean"
    )
