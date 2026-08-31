import numpy as np
import pandas as pd
import pytest

from sti.scan_age import (MissingCovariatesError, load_covariates, per_task_scan_age,
                          scan_age_regression, subject_accuracy)


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


def test_real_participants_file_reports_exactly_what_is_missing():
    with pytest.raises(MissingCovariatesError) as e:
        load_covariates()
    msg = str(e.value)
    assert "scan_age" in msg and "mean_fd" in msg
    assert "birth_age" not in msg.split("Missing covariate column(s)")[1].split(".")[0]


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
    table, model = scan_age_regression(res, cov)
    beta = dict(zip(table.term, table.beta))
    assert beta["scan_age"] == pytest.approx(0.02, abs=0.004)
    assert beta["mean_fd"] == pytest.approx(-0.30, abs=0.05)
    assert table.attrs["n"] == 100


def test_per_task_followup(data):
    res, cov = data
    out = per_task_scan_age(res, cov)
    assert set(out.task) == {"WM", "MOTOR"}
    assert (out.beta > 0).all() and (out.p_fdr < 0.05).all()


def test_missing_covariate_column_raises(data):
    res, cov = data
    with pytest.raises(MissingCovariatesError, match="mean_fd"):
        scan_age_regression(res, cov.drop(columns=["mean_fd"]))
