"""Prediction accuracy as a function of age at scan (manuscript Fig. S9).

Regresses each neonate's prediction accuracy on postmenstrual age at scan,
covarying gestational age at birth and mean framewise displacement.

Data requirements
-----------------
``config/participants.tsv`` currently supplies only ``birth_age`` (gestational
age at birth). Two required covariates are **not** in this repository:

``scan_age``
    Postmenstrual age at scan, in weeks. Available per session in the dHCP
    release's ``sessions.tsv`` (one row per subject-session).
``mean_fd``
    Mean framewise displacement. Must be derived from the dHCP motion
    parameters or QC outputs for the diffusion acquisition.

Supply them as extra columns in the participants table, or as a separate TSV
passed to :func:`load_covariates`, keyed by subject ID.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from sti.cohorts import bare_id
from sti.config import Config, DEFAULT_CONFIG

#: Covariates the Fig. S9 model needs, beyond the accuracy itself.
REQUIRED_COVARIATES = ("scan_age", "birth_age", "mean_fd")

_ID_COLUMNS = ("participant_id", "pparticipant_id", "subject", "subject_id", "id")


class MissingCovariatesError(ValueError):
    """Raised when the covariates needed for the scan-age model are unavailable."""


def load_covariates(
    config: Config = DEFAULT_CONFIG,
    *,
    path: Path | None = None,
    extra: Path | None = None,
    require: bool = True,
) -> pd.DataFrame:
    """Load the neonatal covariate table, indexed by bare subject ID.

    ``extra`` is an optional second TSV/CSV merged on subject ID, for supplying
    ``scan_age`` and ``mean_fd`` without editing the participants file.
    """
    path = path or (config.config_dir / "participants.tsv")
    df = pd.read_csv(path, sep="\t")

    id_col = next((c for c in _ID_COLUMNS if c in df.columns), None)
    if id_col is None:
        raise MissingCovariatesError(
            f"{path} has no recognisable subject ID column (looked for {_ID_COLUMNS})"
        )
    df = df.rename(columns={id_col: "subject"})
    df["subject"] = df["subject"].astype(str).map(bare_id)

    if extra is not None:
        sep = "\t" if str(extra).endswith((".tsv", ".txt")) else ","
        ex = pd.read_csv(extra, sep=sep)
        ex_id = next((c for c in _ID_COLUMNS if c in ex.columns), None)
        if ex_id is None:
            raise MissingCovariatesError(f"{extra} has no recognisable subject ID column")
        ex = ex.rename(columns={ex_id: "subject"})
        ex["subject"] = ex["subject"].astype(str).map(bare_id)
        df = df.merge(ex, on="subject", how="left", suffixes=("", "_extra"))

    df = df.set_index("subject")
    if require:
        missing = [c for c in REQUIRED_COVARIATES if c not in df.columns]
        if missing:
            raise MissingCovariatesError(
                f"Missing covariate column(s) {missing} in {path}"
                + (f" (+ {extra})" if extra else "")
                + ".\n"
                "  scan_age : postmenstrual age at scan (weeks); dHCP sessions.tsv\n"
                "  mean_fd  : mean framewise displacement; derive from dHCP motion/QC outputs\n"
                "  birth_age: gestational age at birth (weeks); already in participants.tsv\n"
                "Pass require=False to inspect what is available."
            )
    return df


def subject_accuracy(results: pd.DataFrame, tasks: list[str] | None = None) -> pd.DataFrame:
    """Per-subject within-task accuracy, averaged over tasks, per hemisphere.

    Returns columns ``subject``, ``hemi``, ``accuracy``, ``n_tasks``.
    """
    within = results[results.task == results.comparison_task]
    if tasks is not None:
        within = within[within.task.isin(tasks)]
    out = (
        within.groupby(["subject", "hemi"])["pearson"]
        .agg(accuracy="mean", n_tasks="size")
        .reset_index()
    )
    out["subject"] = out["subject"].astype(str).map(bare_id)
    return out


def scan_age_regression(
    results: pd.DataFrame,
    covariates: pd.DataFrame,
    *,
    hemi: str | None = None,
    tasks: list[str] | None = None,
    predictors: tuple[str, ...] = REQUIRED_COVARIATES,
) -> tuple[pd.DataFrame, object]:
    """Regress prediction accuracy on scan age, controlling for the covariates.

    Returns ``(coefficient_table, fitted_model)``. The coefficient of interest is
    ``scan_age``: whether prediction from neonatal connectivity improves with age
    at scan across the neonatal period.
    """
    import statsmodels.api as sm

    acc = subject_accuracy(results, tasks=tasks)
    if hemi is not None:
        acc = acc[acc.hemi == hemi]
    acc = acc.groupby("subject", as_index=False)["accuracy"].mean()

    missing = [c for c in predictors if c not in covariates.columns]
    if missing:
        raise MissingCovariatesError(f"covariates lack {missing}")

    df = acc.merge(
        covariates[list(predictors)], left_on="subject", right_index=True, how="inner"
    ).dropna(subset=["accuracy", *predictors])
    if df.empty:
        raise MissingCovariatesError(
            "No subjects remain after merging accuracy with covariates -- check that "
            "subject IDs match (accuracy uses bare dHCP IDs, e.g. 'CC00060XX03')."
        )

    X = sm.add_constant(df[list(predictors)].astype(float))
    model = sm.OLS(df["accuracy"].astype(float), X).fit()

    table = pd.DataFrame({
        "term": model.params.index,
        "beta": model.params.to_numpy(),
        "se": model.bse.to_numpy(),
        "t": model.tvalues.to_numpy(),
        "p": model.pvalues.to_numpy(),
        "ci_low": model.conf_int()[0].to_numpy(),
        "ci_high": model.conf_int()[1].to_numpy(),
    })
    table.attrs["n"] = int(model.nobs)
    table.attrs["r_squared"] = float(model.rsquared)
    return table, model


def per_task_scan_age(
    results: pd.DataFrame, covariates: pd.DataFrame, **kwargs
) -> pd.DataFrame:
    """Per-task follow-up: the scan-age coefficient for each contrast separately."""
    rows = []
    for task in sorted(results.task.unique()):
        try:
            table, model = scan_age_regression(results, covariates, tasks=[task], **kwargs)
        except MissingCovariatesError:
            continue
        row = table[table.term == "scan_age"].iloc[0].to_dict()
        row["task"] = task
        row["n"] = table.attrs["n"]
        rows.append(row)
    df = pd.DataFrame(rows)
    if not df.empty:
        from sti.stats import fdr_bh, stars

        df["p_fdr"] = fdr_bh(df["p"].to_numpy())
        df["stars"] = df["p_fdr"].map(stars)
    return df
