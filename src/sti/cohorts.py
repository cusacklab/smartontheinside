"""Subject cohorts, read from ``config/subjects/*.txt``.

The legacy scripts pasted subject ID lists into six different files, which is how
they drifted apart. ``legacy/classifier.py`` additionally assigned
``subjlist_infants`` twice, so the 142-subject batch 1 was silently overwritten by
the 183-subject batch 2 and never analysed -- which is why the code ran 183
neonates while the manuscript reports 326. Here each cohort is named, versioned
and loaded from one file.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sti.config import Config, DEFAULT_CONFIG

#: Cohort name -> (filename, description).
COHORTS: dict[str, tuple[str, str]] = {
    "adults_all": ("adults_all.txt", "All HCP adults available to the study (n=175)."),
    "adults_hyperparam": ("adults_hyperparam.txt", "Adults held out for hyperparameter selection (n=20)."),
    "adults_analysis": ("adults_analysis.txt", "Adults in the reported analysis (n=155)."),
    "neonates_batch1": ("neonates_batch1.txt", "dHCP term neonates, batch 1 (n=142); never analysed by the legacy code."),
    "neonates_batch2": ("neonates_batch2.txt", "dHCP term neonates, batch 2 (n=183); the legacy analysed sample."),
    "neonates_term_all": ("neonates_term_all.txt", "All dHCP term neonates (n=326); the manuscript cohort."),
}


@dataclass(frozen=True)
class Cohort:
    """A named list of subject IDs."""

    name: str
    subjects: tuple[str, ...]
    description: str = ""

    def __len__(self) -> int:
        return len(self.subjects)

    def __iter__(self):
        return iter(self.subjects)

    def __repr__(self) -> str:
        return f"Cohort({self.name!r}, n={len(self)})"

    @property
    def n(self) -> int:
        return len(self.subjects)


def _read_ids(path: Path) -> tuple[str, ...]:
    if not path.exists():
        raise FileNotFoundError(f"Subject list not found: {path}")
    ids = [
        line.strip()
        for line in path.read_text().splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        raise ValueError(f"Duplicate subject IDs in {path.name}: {sorted(dupes)}")
    return tuple(ids)


def load_cohort(name: str, config: Config = DEFAULT_CONFIG) -> Cohort:
    """Load a named cohort from ``config/subjects/``."""
    if name not in COHORTS:
        raise KeyError(f"Unknown cohort {name!r}. Available: {sorted(COHORTS)}")
    filename, description = COHORTS[name]
    ids = _read_ids(config.config_dir / "subjects" / filename)
    return Cohort(name=name, subjects=ids, description=description)


def dhcp_id(subject: str) -> str:
    """Return the BIDS-style ``sub-CCXXXXXXXX`` form of a dHCP subject ID."""
    return subject if subject.startswith("sub-") else f"sub-{subject}"


def bare_id(subject: str) -> str:
    """Return the dHCP subject ID without the ``sub-`` prefix."""
    return subject[4:] if subject.startswith("sub-") else subject
