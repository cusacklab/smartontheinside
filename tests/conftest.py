import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sti.config import Config          # noqa: E402
from sti.datasets import Activation, Connectivity  # noqa: E402

TASKS = ["tfMRI_WM", "tfMRI_MOTOR"]


@pytest.fixture(scope="session")
def synthetic():
    """Small cohort with a shared connectivity backbone and task-specific weights.

    A shared backbone matters: without it there is no group-average spatial
    pattern for the group-mean protocols to predict.
    """
    rng = np.random.default_rng(1)
    nv, nt, n_adult, n_neo = {"L": 120, "R": 110}, 15, 8, 5
    weights = {t: rng.normal(size=nt) for t in TASKS}
    base = {h: rng.normal(size=(nv[h], nt)) for h in "LR"}

    def conn(n):
        return {h: base[h][None] + 0.3 * rng.normal(size=(n, nv[h], nt)) for h in "LR"}

    ca, ci = conn(n_adult), conn(n_neo)
    acts = {
        t: Activation(
            {h: ca[h] @ weights[t] + rng.normal(scale=0.3, size=(n_adult, nv[h])) for h in "LR"},
            t, "test",
        )
        for t in TASKS
    }
    return {
        "adult_conn": Connectivity(ca, "adults"),
        "neo_conn": Connectivity(ci, "neonates"),
        "acts": acts,
        "adults": [f"a{i}" for i in range(n_adult)],
        "neonates": [f"CC{i:08d}" for i in range(n_neo)],
        "config": Config(alpha=0.05, l1_ratio=0.5),
        "nv": nv,
    }
