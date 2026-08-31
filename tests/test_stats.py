import numpy as np
import pandas as pd
import pytest

from sti.stats import compare_protocols, fdr_bh, paired_bootstrap, specificity_tests, stars


def _results(rng, within=0.45, between=0.12, n=40, sd=0.1):
    tasks = ["WM", "MOTOR", "SOCIAL"]
    return pd.DataFrame([
        dict(hemi=h, task=t, comparison_task=c, subject=f"s{s}",
             pearson=rng.normal(within if t == c else between, sd))
        for h in "LR" for t in tasks for c in tasks for s in range(n)
    ])


def test_paired_bootstrap_detects_and_rejects():
    rng = np.random.default_rng(0)
    hit = paired_bootstrap(rng.normal(0.5, 0.2, 60), rng.normal(0.2, 0.2, 60))
    assert hit["p_bootstrap"] < 0.01 and hit["ci_low"] > 0
    null = paired_bootstrap(rng.normal(0.3, 0.2, 60), rng.normal(0.3, 0.2, 60))
    assert null["p_bootstrap"] > 0.05


def test_paired_bootstrap_requires_matching_shapes():
    with pytest.raises(ValueError, match="paired"):
        paired_bootstrap(np.zeros(5), np.zeros(4))


def test_paired_bootstrap_uses_its_own_arguments():
    """Regression test: the legacy version read module-level globals, not its args."""
    rng = np.random.default_rng(0)
    a, b = rng.normal(1.0, 0.1, 50), rng.normal(0.0, 0.1, 50)
    assert paired_bootstrap(a, b)["difference"] == pytest.approx(np.mean(a - b))
    assert paired_bootstrap(b, a)["difference"] == pytest.approx(np.mean(b - a))


def test_specificity_tests_shape_and_direction():
    df = _results(np.random.default_rng(0))
    out = specificity_tests(df, n_boot=1000)
    assert len(out) == 2 * 3 * 2          # hemi x task x off-diagonal cells
    assert (out.mean_within > out.mean_between).all()
    assert (out.p_fdr < 0.05).all()
    assert set(out.stars) == {"***"}


def test_specificity_tests_null_case():
    rng = np.random.default_rng(1)
    out = specificity_tests(_results(rng, within=0.2, between=0.2), n_boot=1000)
    assert (out.p_fdr > 0.05).mean() > 0.5


def test_fdr_is_monotone_and_bounded():
    p = np.array([0.001, 0.01, 0.02, 0.2, 0.9])
    adj = fdr_bh(p)
    assert np.all(np.diff(adj[np.argsort(p)]) >= -1e-12)
    assert np.all((adj >= p - 1e-12) & (adj <= 1))


def test_stars_thresholds():
    assert (stars(0.0005), stars(0.005), stars(0.02), stars(0.2)) == ("***", "**", "*", "")


def test_compare_protocols_recovers_a_known_offset():
    df = _results(np.random.default_rng(0))
    shifted = df.copy()
    shifted["pearson"] -= 0.15
    out = compare_protocols(df, shifted, n_boot=1000)
    assert len(out) == 6
    assert out.difference.median() == pytest.approx(0.15, abs=0.03)
    assert (out.p_fdr < 0.05).all()
