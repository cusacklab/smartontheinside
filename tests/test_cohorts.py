"""The subject-count arithmetic that the manuscript and the legacy code disagree on."""
import pytest

from sti.cohorts import COHORTS, bare_id, dhcp_id, load_cohort


@pytest.mark.parametrize("name,n", [
    ("adults_all", 175), ("adults_hyperparam", 20), ("adults_analysis", 155),
    ("neonates_batch1", 142), ("neonates_batch2", 183), ("neonates_term_all", 326),
])
def test_cohort_sizes(name, n):
    assert load_cohort(name).n == n


def test_adult_split_is_disjoint_and_exhaustive():
    all_, tune, analysis = (load_cohort(f"adults_{x}") for x in ("all", "hyperparam", "analysis"))
    assert set(tune.subjects) & set(analysis.subjects) == set()
    assert set(tune.subjects) | set(analysis.subjects) == set(all_.subjects)


def test_neonatal_batches_are_disjoint_and_sum_to_the_manuscript_cohort():
    b1, b2, term = (load_cohort(f"neonates_{x}") for x in ("batch1", "batch2", "term_all"))
    assert set(b1.subjects) & set(b2.subjects) == set()
    assert set(b1.subjects) | set(b2.subjects) <= set(term.subjects)
    # batch1 + batch2 + the single excluded subject == the 326 the manuscript reports
    missing = set(term.subjects) - set(b1.subjects) - set(b2.subjects)
    assert missing == {"CC00688XX21"}
    assert b1.n + b2.n + 1 == term.n == 326


def test_no_duplicate_ids():
    for name in COHORTS:
        subs = load_cohort(name).subjects
        assert len(set(subs)) == len(subs), name


def test_id_helpers_roundtrip():
    assert dhcp_id("CC00060XX03") == "sub-CC00060XX03"
    assert bare_id("sub-CC00060XX03") == "CC00060XX03"
    assert dhcp_id(dhcp_id("CC1")) == "sub-CC1"
