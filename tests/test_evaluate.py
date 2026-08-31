import numpy as np
import pandas as pd
import pytest

from sti.evaluate import Predictions, adult_group_mean_loo, adult_loo, neonatal, specificity_matrix

TASKS = ["tfMRI_WM", "tfMRI_MOTOR"]


def _within_beats_between(results):
    m = specificity_matrix(results, "L")
    diag = np.mean([m.loc[t, t] for t in TASKS])
    off = np.mean([m.loc[a, b] for a in TASKS for b in TASKS if a != b])
    return diag, off


@pytest.mark.parametrize("protocol", ["adult_loo", "adult_group_mean_loo", "neonatal"])
def test_protocols_recover_task_specificity(synthetic, protocol):
    s = synthetic
    if protocol == "adult_loo":
        res, _ = adult_loo(s["adult_conn"], s["acts"], s["adults"], config=s["config"])
    elif protocol == "adult_group_mean_loo":
        res, _ = adult_group_mean_loo(s["adult_conn"], s["acts"], s["adults"], config=s["config"])
    else:
        res, _ = neonatal(s["adult_conn"], s["neo_conn"], s["acts"], s["neonates"],
                          config=s["config"])
    diag, off = _within_beats_between(res)
    assert diag > off, f"{protocol}: within={diag:.3f} not > between={off:.3f}"


def test_result_frame_shape_and_columns(synthetic):
    s = synthetic
    res, _ = neonatal(s["adult_conn"], s["neo_conn"], s["acts"], s["neonates"], config=s["config"])
    expected = len(TASKS) * 2 * len(s["neonates"]) * len(TASKS)
    assert len(res) == expected
    assert {"protocol", "task", "comparison_task", "hemi", "subject", "pearson"} <= set(res.columns)
    assert set(res.subject) == set(s["neonates"])
    assert res.protocol.unique().tolist() == ["neonatal"]


def test_predictions_are_not_aliased_across_tasks(synthetic):
    """Regression test for the legacy bug ``all_pred = {t: pred for t in tasks}``.

    That comprehension gave every task a reference to one shared dict, so all five
    tasks appended into the same pair of lists.
    """
    s = synthetic
    _, preds = adult_loo(s["adult_conn"], s["acts"], s["adults"],
                         config=s["config"], hemispheres=("L",))
    assert set(preds.values) == {(t, "L") for t in TASKS}
    a, b = preds.values[(TASKS[0], "L")], preds.values[(TASKS[1], "L")]
    assert not np.allclose(a, b)
    assert a.shape == (len(s["adults"]), s["nv"]["L"])


def test_predictions_container_starts_empty_per_key():
    p = Predictions.empty()
    p.add("t1", "L", np.zeros(3))
    p.add("t2", "L", np.ones(3))
    p.finalise()
    assert not np.allclose(p.values[("t1", "L")], p.values[("t2", "L")])


def test_group_mean_target_excludes_the_test_subject(synthetic):
    """The held-out adult must not contribute to the group average it is scored against."""
    s = synthetic
    res, _ = adult_group_mean_loo(s["adult_conn"], s["acts"], s["adults"],
                                  config=s["config"], hemispheres=("L",))
    assert len(res) == len(TASKS) * len(s["adults"]) * len(TASKS)
    assert res.pearson.notna().all()


def test_model_tasks_shards_training_but_not_comparison(synthetic):
    """A shard must still emit a complete row of the specificity matrix.

    If restricting the models also restricted the comparison targets, each
    cluster shard would return a 1x1 matrix and the merged result would have no
    off-diagonal cells.
    """
    s = synthetic
    shard, _ = neonatal(s["adult_conn"], s["neo_conn"], s["acts"], s["neonates"],
                        config=s["config"], hemispheres=("L",), model_tasks=[TASKS[0]])
    assert set(shard.task) == {TASKS[0]}                 # one model trained
    assert set(shard.comparison_task) == set(TASKS)      # all targets compared
    assert len(shard) == len(s["neonates"]) * len(TASKS)


def test_shards_reproduce_the_unsharded_run(synthetic):
    s = synthetic
    full, _ = neonatal(s["adult_conn"], s["neo_conn"], s["acts"], s["neonates"],
                       config=s["config"], hemispheres=("L",))
    shards = [
        neonatal(s["adult_conn"], s["neo_conn"], s["acts"], s["neonates"],
                 config=s["config"], hemispheres=("L",), model_tasks=[t])[0]
        for t in TASKS
    ]
    merged = pd.concat(shards, ignore_index=True)
    key = ["task", "comparison_task", "hemi", "subject"]
    j = full.merge(merged, on=key, suffixes=("_full", "_shard"))
    assert len(j) == len(full)
    assert np.allclose(j.pearson_full, j.pearson_shard)
