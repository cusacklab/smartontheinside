"""Smoke tests for the figures: they must render without error and be shaped right."""
import matplotlib
matplotlib.use("Agg")
import numpy as np
import pandas as pd
import pytest

from sti import plotting as P

TASKS = ["tfMRI_WM", "tfMRI_MOTOR", "tfMRI_SOCIAL"]


@pytest.fixture
def results():
    rng = np.random.default_rng(0)
    # each target differs in difficulty, and each is best predicted by its own model
    difficulty = {"tfMRI_WM": 0.45, "tfMRI_MOTOR": 0.15, "tfMRI_SOCIAL": 0.35}
    return pd.DataFrame([
        dict(hemi=h, task=m, comparison_task=t, subject=f"s{s}",
             pearson=rng.normal(difficulty[t] + (0.06 if m == t else 0), 0.04))
        for h in "LR" for m in TASKS for t in TASKS for s in range(30)
    ])


def test_specificity_lines_renders(results):
    fig = P.plot_specificity_lines(results, tasks=TASKS)
    assert len(fig.axes) == 2
    fig.clf()


def test_specificity_panel_has_four_axes(results):
    fig = P.plot_specificity_panel(results, tasks=TASKS)
    # 2 rows x 2 hemispheres
    assert len([a for a in fig.axes if a.get_lines()]) == 4
    fig.clf()


def test_centred_lines_peak_at_their_own_target(results):
    """The specificity signature the figure exists to show."""
    block = results[results.hemi == "L"]
    cell = block.pivot_table(index="task", columns="comparison_task", values="pearson")
    centred = cell - cell.mean(axis=0)          # subtract each target's across-model mean
    for model in TASKS:
        assert centred.loc[model].idxmax() == model, f"{model} should peak at its own target"


def test_panel_y_range_covers_both_hemispheres(results):
    """Sharing to the first panel would clip whichever hemisphere ranges wider."""
    skewed = results.copy()
    mask = skewed.hemi == "R"
    skewed.loc[mask, "pearson"] = skewed.loc[mask, "pearson"] - 0.5
    fig = P.plot_specificity_panel(skewed, tasks=TASKS)
    rows = [fig.axes[0:2], fig.axes[2:4]]
    for row in rows:
        for ax in row:
            lo, hi = ax.get_ylim()
            for line in ax.get_lines():
                y = np.asarray(line.get_ydata(), dtype=float)
                y = y[np.isfinite(y)]
                if y.size:
                    assert y.min() >= lo - 1e-9 and y.max() <= hi + 1e-9, "data clipped"
    fig.clf()


def test_palette_is_fixed_order_and_long_enough():
    assert len(P.PALETTE) >= 5 and len(P.MARKERS) >= 5
    assert len(set(P.PALETTE)) == len(P.PALETTE)
