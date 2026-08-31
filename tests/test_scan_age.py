import numpy as np
import pandas as pd
import pytest

from sti.scan_age import (CORE_COVARIATES, MOTION_COVARIATE, MissingCovariatesError,
                          load_covariates, per_task_scan_age, scan_age_regression,
                          subject_accuracy)


@pytest.fixture
def data():
    rng = np.random.default_rng(0)
    subs = [f"CC{i:08d}" for i in range(100)]
    scan_age = rng.uniform(37, 45, 100)
    fd = rng.uniform(0, 0.5, 100)
    cov = pd.DataFrame(
        dict(scan_age=scan_age, birth_age=rng.uniform(37, 42, 100), mean_fd=fd), index=subs
    )
    cov.index.name = "subject"
    recs = []
    for i, s in enumerate(subs):
        base = 0.1 + 0.02 * (scan_age[i] - 37) - 0.3 * fd[i]
        for h in "LR":
            for t in ["WM", "MOTOR"]:
                for c in ["WM", "MOTOR"]:
                    recs.append(dict(subject=s, hemi=h, task=t, comparison_task=c,
                                     pearson=(base if t == c else 0.05) + rng.normal(0, 0.03)))
    return pd.DataFrame(recs), cov


def test_release_participants_file_lacks_scan_age():
    """participants.tsv alone is not enough: scan_age lives in the sessions files."""
    with pytest.raises(MissingCovariatesError) as e:
        load_covariates()
    assert "scan_age" in str(e.value)


def test_motion_is_not_a_required_covariate():
    """The dHCP diffusion release publishes no motion summary, so the model must
    run without one rather than refusing."""
    assert MOTION_COVARIATE not in CORE_COVARIATES
    assert CORE_COVARIATES == ("scan_age", "birth_age")


def test_available_columns_load_without_require():
    cov = load_covariates(require=False)
    assert "birth_age" in cov.columns and len(cov) == 445


def test_subject_accuracy_uses_only_the_diagonal(data):
    res, _ = data
    acc = subject_accuracy(res)
    assert set(acc.columns) == {"subject", "hemi", "accuracy", "n_tasks"}
    assert (acc.n_tasks == 2).all()          # two within-task cells per subject/hemi


def test_regression_recovers_known_coefficients(data):
    res, cov = data
    table, model = scan_age_regression(res, cov, predictors=("scan_age", "birth_age", "mean_fd"))
    beta = dict(zip(table.term, table.beta))
    assert beta["scan_age"] == pytest.approx(0.02, abs=0.004)
    assert beta["mean_fd"] == pytest.approx(-0.30, abs=0.05)
    assert table.attrs["n"] == 100


def test_regression_runs_without_motion(data):
    res, cov = data
    table, _ = scan_age_regression(res, cov.drop(columns=["mean_fd"]))
    assert "mean_fd" not in set(table.term)
    assert dict(zip(table.term, table.beta))["scan_age"] > 0


def test_collinearity_is_reported(data):
    res, cov = data
    table, _ = scan_age_regression(res, cov)
    assert set(table.attrs["vif"]) == set(CORE_COVARIATES)
    assert all(v >= 1.0 for v in table.attrs["vif"].values())


def test_per_task_followup(data):
    res, cov = data
    out = per_task_scan_age(res, cov)
    assert set(out.task) == {"WM", "MOTOR"}
    assert (out.beta > 0).all() and (out.p_fdr < 0.05).all()


def test_missing_requested_predictor_raises(data):
    res, cov = data
    with pytest.raises(MissingCovariatesError, match="mean_fd"):
        scan_age_regression(res, cov.drop(columns=["mean_fd"]),
                            predictors=("scan_age", "mean_fd"))


def test_built_covariate_table_covers_the_analysed_cohort():
    """The table built from the dHCP release must cover every analysed neonate."""
    from pathlib import Path

    cov_path = Path("config/neonatal_covariates.tsv")
    subs_path = Path("data/derivatives/conn_for_classifier_N-325_infants.subjects.txt")
    if not (cov_path.exists() and subs_path.exists()):
        pytest.skip("built covariates or cohort sidecar not present")

    cov = pd.read_csv(cov_path, sep="\t").set_index("participant_id")
    subs = [l.strip() for l in subs_path.read_text().splitlines() if l.strip()]
    missing = [s for s in subs if s not in cov.index]
    assert not missing, f"no covariates for {len(missing)} subjects: {missing[:5]}"
    assert cov.loc[subs, "scan_age"].notna().all()
    assert cov.loc[subs, "birth_age"].notna().all()
    # one session per infant, as the manuscript states
    assert (cov.loc[subs, "n_sessions"] == 1).all()
