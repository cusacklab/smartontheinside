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
) -> tuple[pd.DataFrame, Predictions]:
    """Leave-one-adult-out; each model predicts the held-out adult's own map (Fig. 2)."""
    records: list[dict] = []
    preds = Predictions.empty()

    for task, activation in activations.items():
        y_all = activation.zscored()
        for hemi in hemispheres:
            X = connectivity[hemi]
            if float32:
                X = model_mod.as_float32(X)
            y = y_all[hemi]

            for train_idx, test_idx in LeaveOneOut().split(X):
                i = int(test_idx[0])
                fitted = model_mod.fit(X[train_idx], y[train_idx], config)
                y_hat = model_mod.predict(fitted, X[test_idx])
                preds.add(task, hemi, y_hat)

                targets = {t: a[hemi][i] for t, a in activations.items()}
                records += _score_against_all(
                    y_hat, targets, task=task, hemi=hemi, subject=subjects[i],
                    config=config, protocol="adult_loo",
                )
            log.info("adult_loo done: task=%s hemi=%s", task, hemi)

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
) -> tuple[pd.DataFrame, Predictions]:
    """Leave-one-adult-out; each model predicts the group-average map (Fig. 4).

    The held-out adult is excluded from the group average as well as from
    training, so the target is independent of the test subject -- this is the
    like-for-like comparison with the neonatal protocol, where the neonate
    contributes nothing to the adult average.
    """
    records: list[dict] = []
    preds = Predictions.empty()

    for task, activation in activations.items():
        y_all = activation.zscored()
        for hemi in hemispheres:
            X = connectivity[hemi]
            if float32:
                X = model_mod.as_float32(X)
            y = y_all[hemi]

            for train_idx, test_idx in LeaveOneOut().split(X):
                i = int(test_idx[0])
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
                    config=config, protocol="adult_group_mean_loo",
                )
            log.info("adult_group_mean_loo done: task=%s hemi=%s", task, hemi)

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
) -> tuple[pd.DataFrame, Predictions]:
    """Train on all adults, apply unchanged to each neonate (Fig. 3).

    The adult models are fitted once per (task, hemisphere) and reused across
    neonates -- there is no leave-one-out here, because no neonate contributes to
    the training set.
    """
    records: list[dict] = []
    preds = Predictions.empty()

    for task, activation in activations.items():
        y_all = activation.zscored()
        for hemi in hemispheres:
            X_adult = adult_connectivity[hemi]
            X_inf = neonatal_connectivity[hemi]
            if float32:
                X_adult = model_mod.as_float32(X_adult)
                X_inf = model_mod.as_float32(X_inf)

            fitted = model_mod.fit(X_adult, y_all[hemi], config)
            targets = {t: a.zscored()[hemi].mean(axis=0) for t, a in activations.items()}

            for i in range(X_inf.shape[0]):
                y_hat = model_mod.predict(fitted, X_inf[i])
                preds.add(task, hemi, y_hat)
                records += _score_against_all(
                    y_hat, targets, task=task, hemi=hemi, subject=neonates[i],
                    config=config, protocol="neonatal",
                )
            log.info("neonatal done: task=%s hemi=%s (n=%d)", task, hemi, X_inf.shape[0])

    preds.finalise()
    return pd.DataFrame.from_records(records), preds


# --------------------------------------------------------------------------- #

def specificity_matrix(results: pd.DataFrame, hemi: Hemisphere | None = None) -> pd.DataFrame:
    """Mean prediction accuracy for every (model task, evaluated task) pair."""
    df = results if hemi is None else results[results.hemi == hemi]
    return df.pivot_table(
        index="task", columns="comparison_task", values="pearson", aggfunc="mean"
    )
