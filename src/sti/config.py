"""Central configuration: paths, constants and model hyperparameters.

Everything the legacy scripts hard-coded at module scope (subject lists, the
analysis root baked to one person's home directory, alpha/l1_ratio, the
``infants = 1`` switch) is expressed here as data instead.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

Hemisphere = Literal["L", "R"]
HEMISPHERES: tuple[Hemisphere, ...] = ("L", "R")

Task = str

#: The five HCP contrasts carried forward from the RSA/clustering step, each the
#: representative of one cluster. Values are the contrast index within the task.
TASKS: dict[Task, int] = {
    "tfMRI_WM": 8,        # 2-back
    "tfMRI_MOTOR": 6,     # average
    "tfMRI_LANGUAGE": 1,  # story
    "tfMRI_SOCIAL": 1,    # theory of mind
    "tfMRI_EMOTION": 1,   # shapes
}

#: Number of DLPFC seed vertices per hemisphere.
N_SEED_VERTICES: dict[Hemisphere, int] = {"L": 2207, "R": 2185}

#: Number of non-DLPFC target parcels -- the number the manuscript reports.
N_TARGETS: int = 334

#: Target dimension of the stored connectivity arrays.
#:
#: The arrays carry all 360 parcels, not 334. The 26 DLPFC parcels were correctly
#: excluded from tractography (verified: those 26 columns are identically zero in
#: every array), so they are structural padding that the elastic net assigns zero
#: weight. The SI's claim that the DLPFC was excluded as a target is accurate --
#: do not "fix" the arrays down to 334, and do not read the extra columns as
#: DLPFC-to-DLPFC self-connectivity.
N_PARCELS: int = 360

#: The 26 DLPFC parcels (13 per hemisphere) of the Glasser parcellation:
#: SFL, 8Av, 8Ad, 8BL, 9p, 8C, p9-46v, 46, a9-46v, 9-46d, 9a, i6-8, s6-8.
#:
#: IMPORTANT: in the ``ff.{L,R}.label.gii`` files this project uses, label indices
#: 1-180 are the RIGHT hemisphere and 181-360 the LEFT (verified against the
#: embedded label names, e.g. 26 == "R_SFL_ROI", 206 == "L_SFL_ROI"). This is the
#: opposite of the more common assumption, so the mapping is spelled out here
#: rather than left implicit.
DLPFC_PARCELS_RH: tuple[int, ...] = (26, 67, 68, 70, 71, 73, 83, 84, 85, 86, 87, 97, 98)
DLPFC_PARCELS_LH: tuple[int, ...] = tuple(p + 180 for p in DLPFC_PARCELS_RH)
DLPFC_PARCELS: dict[Hemisphere, tuple[int, ...]] = {"L": DLPFC_PARCELS_LH, "R": DLPFC_PARCELS_RH}
ALL_DLPFC_PARCELS: tuple[int, ...] = tuple(sorted(DLPFC_PARCELS_LH + DLPFC_PARCELS_RH))

#: Hyperparameter grid searched on the held-out tuning subjects (SI, Fig. S6).
ALPHA_GRID: tuple[float, ...] = (0.1, 0.2, 0.4, 0.8, 1.6, 3.2, 6.4, 12.8, 25.6, 51.2)
L1_RATIO_GRID: tuple[float, ...] = (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)


#: Filename stem for each figure, keyed by the analysis that produces it.
#:
#: Figure numbers move during review, so they live here rather than scattered
#: through the CLI: renumbering is a one-line edit per figure, and the filenames
#: cannot drift out of step with each other.
#:
#: Current assignment follows the authors' decision to promote the
#: neonatal-vs-adult comparison to the main text and move the adult
#: group-average panel to the SI, which is a straight swap of those two slots.
FIGURES: dict[str, str] = {
    "adult_loo": "Fig2_adult_own_activation",
    "neonatal": "Fig3_neonatal",
    "neonate_vs_adult": "Fig4_neonate_vs_adult",   # promoted from S7
    "similarity_matrix": "S3_similarity_matrix",
    "dendrogram": "S4_dendrogram",
    "parcel_profiles": "S5_parcel_profiles",
    "hyperparameter_grid": "S6_hyperparameter_grid",
    "adult_average": "S7_adult_group_average",     # demoted from Fig. 4
    "spatial_null": "S8_spatial_null",
    "scan_age": "S9_scan_age",
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Config:
    """Paths and model settings for one analysis run.

    Paths default to the repository layout and can be overridden by the
    ``STI_DATA_DIR`` / ``STI_FIGURE_DIR`` environment variables, so the same code
    runs on a laptop, an AWS node or a SLURM worker without edits.
    """

    # --- model ---
    alpha: float = 0.4
    l1_ratio: float = 0.6
    random_state: int = 42

    # --- data location ---
    repo_root: Path = field(default_factory=_repo_root)
    s3_bucket: str = "smartontheinside"

    def __post_init__(self) -> None:
        if not 0.0 <= self.l1_ratio <= 1.0:
            raise ValueError(f"l1_ratio must be in [0, 1], got {self.l1_ratio}")
        if self.alpha < 0.0:
            raise ValueError(f"alpha must be non-negative, got {self.alpha}")

    # --- derived paths ---
    @property
    def data_dir(self) -> Path:
        return Path(os.environ.get("STI_DATA_DIR", self.repo_root / "data"))

    @property
    def figure_dir(self) -> Path:
        """Where generated figures are written.

        Defaults to ``figures/manuscript`` rather than ``figures`` so generated
        output never mixes with ``figures/superseded`` (the pre-2026 figures) or
        ``figures/upstream_docker_hcp`` (figures this repository does not
        produce). See figures/README.md.
        """
        return Path(os.environ.get("STI_FIGURE_DIR", self.repo_root / "figures" / "manuscript"))

    @property
    def config_dir(self) -> Path:
        return self.repo_root / "config"

    @property
    def cache_dir(self) -> Path:
        """Local cache for objects pulled from S3."""
        return self.data_dir / "cache"

    @property
    def derivatives_dir(self) -> Path:
        return self.data_dir / "derivatives"

    @property
    def results_dir(self) -> Path:
        return self.data_dir / "results"

    @property
    def slug(self) -> str:
        """Short identifier for this hyperparameter setting, used in filenames."""
        return f"alpha-{self.alpha:g}_l1ratio-{self.l1_ratio:g}"


DEFAULT_CONFIG = Config()
