"""Structural connectivity predicts functional selectivity in the DLPFC.

Analysis package for Caldinelli & Cusack: adult elastic-net models that predict
vertex-wise DLPFC task activation from tractography-derived connectivity, applied
unchanged to neonatal connectivity.

The pipeline stages that produce the inputs to this package (tractography,
registration, activation extraction) live in ``pipelines/``; this package covers
the classification stages only.
"""

__version__ = "0.2.0"

from sti.config import Config, Hemisphere, Task, TASKS, DEFAULT_CONFIG, DLPFC_PARCELS

__all__ = ["Config", "Hemisphere", "Task", "TASKS", "DEFAULT_CONFIG", "DLPFC_PARCELS", "__version__"]
