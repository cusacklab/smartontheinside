import numpy as np
import pandas as pd
import pytest

from sti.hyperparams import load_grid, methods_sentence, rank_of, ridge_summary, select

GRID_DIR = "data/cache/grid"


@pytest.fixture(scope="module")
def grid():
    pytest.importorskip("pandas")
    try:
        return load_grid(GRID_DIR)
    except FileNotFoundError:
        pytest.skip(f"grid summaries not present at {GRID_DIR}")


def test_grid_loads_expected_shape(grid):
    assert len(grid) > 50
    assert {"alpha", "l1_ratio", "mean_pearson", "mean_score", "l1_penalty"} <= set(grid.columns)
    assert (grid.n_tasks == 5).all()


def test_published_choice_is_near_optimal(grid):
    """alpha=0.4 / l1=0.6 was chosen 'visually'; check it is defensible."""
    r = rank_of(grid, 0.4, 0.6)
    assert r["rank"] <= 5
    assert r["shortfall"] < 0.001


def test_selection_metric_matters(grid):
    """The legacy heatmap plotted R2 while the paper reports Pearson."""
    assert select(grid)["metric"] == "mean_pearson"
    assert select(grid, metric="mean_score")["metric"] == "mean_score"


def test_ridge_cells_share_similar_l1_penalty(grid):
    top = ridge_summary(grid, top=4)
    assert top.l1_penalty.max() / top.l1_penalty.min() < 2.0


def test_methods_sentence_is_specific(grid):
    s = methods_sentence(grid, 0.4, 0.6)
    assert "0.4" in s and "0.6" in s and "84" in s
    assert "visually" not in s.lower()


def test_unknown_cell_raises(grid):
    with pytest.raises(KeyError):
        rank_of(grid, 999.0, 0.5)
