# Data provenance

Nothing in `data/` is version-controlled. This file records where each input came
from so the directory can be rebuilt.

Bucket: `s3://smartontheinside/`

## Model inputs

| What | Key | Size | Notes |
|------|-----|------|-------|
| Adult connectivity, analysed cohort | `Results/conn_for_classifier_N-155.npy` | 1.8 GB | `{'L','R'}` dict, `(155, n_vertices, 334)` |
| Adult connectivity, full cohort | `Results/conn_for_classifier_N-175.npy` | 2.1 GB | before the 20 tuning subjects are removed |
| Neonatal connectivity, batch 2 | `infant_classifier/conn_for_classifier_N-183_infants.npy` | 2.2 GB | the cohort the legacy code analysed |
| Neonatal connectivity, earlier | `infant_classifier/conn_for_classifier_N-155_infants.npy` | 2.2 GB | an earlier cohort revision |
| Adult activation, per task | `Results/act_for_classifier_{task}_N-155.npy` | — | **MISSING — see below** |
| Hyperparameter grid | `Results/classifier_results_alpha-*_l1ratio-*/summary_N-20.csv` | small | 84 cells recovered |

## The missing activation arrays

`legacy/classifier.py` saved activations locally per task:

    act_for_classifier_{task}_N-{nsub}.npy

but uploaded all five tasks to a single key:

    Results/act_for_classifier_N-{nsub}.npy

so each task overwrote the previous one. What survives on S3 is one unidentified
task, shape `(155, n_vertices)` per hemisphere — no task dimension. The per-task
keys the code reads do not exist.

These arrays are the models' response variable, so **no classification analysis
can be rerun until they are regenerated** with
`pipelines/02_adult_activation/extract_conn_act.py`.

`sti.s3io.upload` now refuses to overwrite an existing key, so this cannot recur.

## Local reference files (small, versioned)

| File | Purpose |
|------|---------|
| `config/participants.tsv` | dHCP participants: gender, birth age, birth weight, singleton |
| `config/subjects/*.txt` | the cohorts, one ID per line |
| `data/parcellations/ff.{L,R}.label.gii` | Glasser parcellation per hemisphere |
| `data/parcellations/*.midthickness*.surf.gii` | surface geometry for the spatial null |

## Covariates still required

`config/participants.tsv` has `birth_age` only. The scan-age analysis (Fig. S9)
additionally needs, from the dHCP release:

- `scan_age` — postmenstrual age at scan, from the release's `sessions.tsv`;
- `mean_fd` — mean framewise displacement, derived from the motion/QC outputs.

Supply either as extra columns or via `sti scan-age --extra <file.tsv>`.
