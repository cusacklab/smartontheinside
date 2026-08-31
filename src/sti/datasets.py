"""Loading of the connectivity and activation matrices the models consume.

Two arrays drive every analysis:

``connectivity``
    ``(n_subjects, n_vertices, n_targets)`` -- for each DLPFC seed vertex, the
    number of streamlines reaching each of the 334 non-DLPFC target parcels.

``activation``
    ``(n_subjects, n_vertices)`` -- the GLM beta for one contrast at each DLPFC
    seed vertex.

Both are stored per hemisphere as a dict-of-arrays pickled inside a ``.npy``,
which is why loading goes through :func:`_load_hemi_dict` rather than ``np.load``.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from sti import s3io
from sti.config import Config, DEFAULT_CONFIG, HEMISPHERES, Hemisphere, N_SEED_VERTICES, Task

log = logging.getLogger(__name__)


class MissingDataError(FileNotFoundError):
    """Raised when a required input array cannot be found locally or on S3."""


def _load_hemi_dict(path: Path) -> dict[str, np.ndarray]:
    """Load a ``{'L': array, 'R': array}`` mapping saved with ``np.save``."""
    obj = np.load(path, allow_pickle=True)
    if obj.dtype == object and obj.shape == ():
        obj = obj.ravel()[0]
    elif obj.dtype == object:
        obj = obj.ravel()[0]
    if not isinstance(obj, dict):
        raise TypeError(f"{path} does not contain a hemisphere dict (got {type(obj)})")
    return obj


@dataclass(frozen=True)
class Connectivity:
    """Tractography connectivity for one cohort, per hemisphere."""

    data: dict[Hemisphere, np.ndarray]
    cohort: str

    def __getitem__(self, hemi: Hemisphere) -> np.ndarray:
        return self.data[hemi]

    @property
    def n_subjects(self) -> int:
        return next(iter(self.data.values())).shape[0]

    def validate(self) -> None:
        for hemi, arr in self.data.items():
            if arr.ndim != 3:
                raise ValueError(f"connectivity[{hemi}] must be 3D, got shape {arr.shape}")
            if arr.shape[1] != N_SEED_VERTICES[hemi]:
                raise ValueError(
                    f"connectivity[{hemi}] has {arr.shape[1]} seed vertices, "
                    f"expected {N_SEED_VERTICES[hemi]}"
                )
            if arr.shape[0] != self.n_subjects:
                raise ValueError("hemispheres disagree on subject count")


@dataclass(frozen=True)
class Activation:
    """Task activation for one cohort and contrast, per hemisphere."""

    data: dict[Hemisphere, np.ndarray]
    task: Task
    cohort: str

    def __getitem__(self, hemi: Hemisphere) -> np.ndarray:
        return self.data[hemi]

    @property
    def n_subjects(self) -> int:
        return next(iter(self.data.values())).shape[0]

    def validate(self) -> None:
        for hemi, arr in self.data.items():
            if arr.ndim != 2:
                raise ValueError(f"activation[{hemi}] must be 2D, got shape {arr.shape}")
            if arr.shape[1] != N_SEED_VERTICES[hemi]:
                raise ValueError(
                    f"activation[{hemi}] has {arr.shape[1]} vertices, "
                    f"expected {N_SEED_VERTICES[hemi]}"
                )

    def zscored(self) -> "Activation":
        """Z-score across vertices within each subject (as in the original analysis)."""
        from scipy.stats import zscore

        return Activation(
            data={h: zscore(a, axis=1) for h, a in self.data.items()},
            task=self.task,
            cohort=self.cohort,
        )


# --------------------------------------------------------------------------- #
# S3 key conventions
# --------------------------------------------------------------------------- #

def adult_connectivity_key(n: int) -> str:
    return f"Results/conn_for_classifier_N-{n}.npy"


def adult_activation_key(task: Task, n: int) -> str:
    """Per-task adult activation key.

    NOTE: these objects are absent from the bucket. ``legacy/classifier.py`` saved
    activations locally per task but uploaded all five to the single key
    ``Results/act_for_classifier_N-{n}.npy``, so each task overwrote the last and
    only one (unidentified) task survives there. Regenerate with
    ``pipelines/02_adult_activation``.
    """
    return f"Results/act_for_classifier_{task}_N-{n}.npy"


def neonatal_connectivity_key(n: int) -> str:
    return f"infant_classifier/conn_for_classifier_N-{n}_infants.npy"


# --------------------------------------------------------------------------- #
# Loaders
# --------------------------------------------------------------------------- #

def _resolve(key: str, local_name: str, config: Config, allow_download: bool) -> Path:
    local = config.derivatives_dir / local_name
    if local.exists():
        return local
    if not allow_download:
        raise MissingDataError(
            f"{local} not found and downloads are disabled "
            f"(would fetch s3://{config.s3_bucket}/{key})"
        )
    try:
        return s3io.fetch(key, config)
    except Exception as exc:  # noqa: BLE001 - surfaced with context below
        raise MissingDataError(
            f"Could not obtain {local_name}: not at {local}, and fetching "
            f"s3://{config.s3_bucket}/{key} failed ({exc})"
        ) from exc


def load_connectivity(
    n_subjects: int,
    *,
    neonatal: bool = False,
    config: Config = DEFAULT_CONFIG,
    allow_download: bool = True,
) -> Connectivity:
    """Load the connectivity array for a cohort of ``n_subjects``."""
    key = neonatal_connectivity_key(n_subjects) if neonatal else adult_connectivity_key(n_subjects)
    name = Path(key).name
    path = _resolve(key, name, config, allow_download)
    raw = _load_hemi_dict(path)
    conn = Connectivity(
        data={h: np.asarray(raw[h]) for h in HEMISPHERES if h in raw},
        cohort=("neonates" if neonatal else "adults") + f"_N-{n_subjects}",
    )
    conn.validate()
    return conn


def load_activation(
    task: Task,
    n_subjects: int,
    *,
    config: Config = DEFAULT_CONFIG,
    allow_download: bool = True,
) -> Activation:
    """Load adult activation for one contrast."""
    key = adult_activation_key(task, n_subjects)
    path = _resolve(key, Path(key).name, config, allow_download)
    raw = _load_hemi_dict(path)
    act = Activation(
        data={h: np.asarray(raw[h]) for h in HEMISPHERES if h in raw},
        task=task,
        cohort=f"adults_N-{n_subjects}",
    )
    act.validate()
    return act


def load_all_activations(
    tasks, n_subjects: int, *, config: Config = DEFAULT_CONFIG, allow_download: bool = True
) -> dict[Task, Activation]:
    """Load adult activation for every contrast, reporting all missing tasks at once."""
    out: dict[Task, Activation] = {}
    missing: list[str] = []
    for task in tasks:
        try:
            out[task] = load_activation(task, n_subjects, config=config, allow_download=allow_download)
        except MissingDataError as exc:
            missing.append(f"  {task}: {exc}")
    if missing:
        raise MissingDataError(
            "Adult activation data missing for "
            f"{len(missing)}/{len(list(tasks))} tasks:\n" + "\n".join(missing)
            + "\n\nThe per-task activation objects were overwritten on S3 (see "
            "sti.datasets.adult_activation_key). Regenerate them with "
            "pipelines/02_adult_activation/extract_conn_act.py."
        )
    return out
