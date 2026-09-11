# Connectivity before function

Analysis code for Caldinelli & Cusack, *"the structural connectivity that
distinguishes sub-regions of the adult dorsolateral prefrontal cortex is already
present in neonates"*.

Adult elastic-net models predict vertex-wise DLPFC task activation from
tractography-derived structural connectivity; those models are then applied,
unchanged, to neonatal connectivity from the dHCP.

## Layout

```
config/          subject cohorts and participant metadata (small, versioned)
pipelines/       the acquisition-to-matrix stages, in order (SLURM + shell + python)
src/sti/         the classification package -- the modelling and statistics
tests/           pytest suite (59 tests, no data required)
tools/           standalone utilities (palette validation)
data/            inputs and derivatives -- gitignored, S3-backed (see docs/DATA.md)
figures/         generated figures
legacy/          the original scripts, kept for provenance -- superseded by src/sti
docs/            data provenance, findings, original README
```

Data, figures and code are separate: `data/` and `logs/` are gitignored and
reproduced from S3, so the repository holds code and configuration only.

## Install

```bash
pip install -e ".[dev]"
pytest
```

## Pipeline stages

| Stage | Directory | What it does |
|-------|-----------|--------------|
| 00 | `pipelines/00_cohorts` | Derive term/preterm cohorts from participant metadata |
| 01 | `pipelines/01_rois` | Build DLPFC seed and target ROI masks from the Glasser parcellation |
| 02 | `pipelines/02_adult_activation` | Extract HCP task activation over DLPFC vertices |
| 03 | `pipelines/03_adult_tractography` | BEDPOSTX / PROBTRACKX2 seed-to-target in adults |
| 04 | `pipelines/04_neonatal_registration` | Carry the adult parcellation into neonatal space (ANTs) |
| 05 | `pipelines/05_neonatal_tractography` | Tractography in neonates; return maps to the adult surface |
| 06 | `pipelines/06_classification` | SLURM wrappers around the `sti` commands below |

## Running the analyses

Each analysis is a subcommand, so a run is a recorded command rather than a file
edited to flip `infants = 1`:

```bash
sti hyperparams   --grid data/cache/grid          # Fig. S6 + a Methods sentence
sti adult-loo     --cohort adults_analysis        # Fig. 2   each adult's own map
sti adult-average --cohort adults_analysis        # Fig. 4   the group-average map
sti neonatal      --neonates neonates_batch2      # Fig. 3   adult models on neonates
sti compare       --a data/results/neonatal.csv \
                  --b data/results/adult_average.csv   # Fig. S7
sti spatial-null  --results data/results/neonatal.csv  # Fig. S8
sti scan-age      --results data/results/neonatal.csv \
                  --extra config/sessions.tsv          # Fig. S9
```

All write tidy CSVs with one row per (task, comparison_task, hemisphere, subject).

## Before you rerun anything

Read **[docs/FINDINGS.md](docs/FINDINGS.md)**. Two issues affect what the numbers
mean:

- the manuscript reports 176 adults and 326 neonates; the code as committed ran
  **155 adults and 183 neonates**. Tractography is available for **325** of the
  326, so the full rerun is feasible — build the array with
  `sti build-connectivity --cohort neonates_term_all --allow-missing`;


## Credit

The original analysis was written by **Chiara Caldinelli**, who authored 236 of
the 248 commits in this repository's history. That history is preserved intact
through the 2026 restructure: `git log` and `git blame` still attribute her work
to her.

The repository as it stood at the end of her work — the state that produced the
results in the current manuscript — is archived at
[chiaracc/smartontheinside](https://github.com/chiaracc/smartontheinside) and is
the reference for anything in [docs/FINDINGS.md](docs/FINDINGS.md).

## Citation

See [CITATION.cff](CITATION.cff).

HCP data: WU-Minn Human Connectome Project, 1200-subject release.
dHCP data: Developing Human Connectome Project, second release.
