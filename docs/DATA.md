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
| Adult activation, per task | `backups-2026-01-27/.../act_for_classifier_{task}_N-{155,175,20}.npy` | 5-6 MB | **recovered from backup — see below** |
| Per-subject neonatal tractography | `Results/sub-{id}_infants_tractography_results_VOXEL_{L,R}.npy` | 6 MB each | 325 subjects, both hemispheres |
| Hyperparameter grid | `Results/classifier_results_alpha-*_l1ratio-*/summary_N-20.csv` | small | 84 cells recovered |

## The per-task activation arrays (recovered)

`s3://foundcog/backups-2026-01-27/home/chiaracaldinelli/` is a backup of the
original analysis home directory, and it contains all fifteen per-task activation
files — five contrasts x three cohort sizes (N-20, N-155, N-175). They are
verified genuine: correct shapes, and pairwise correlations between the
group-mean maps of 0.23-0.84, so they are five distinct contrasts rather than
copies. Fetch with:

```bash
aws s3 cp s3://foundcog/backups-2026-01-27/home/chiaracaldinelli/ data/derivatives/ \
  --recursive --exclude '*' --include 'act_for_classifier_*'
```

### How they were lost from the working bucket

`legacy/classifier.py` saved activations locally per task:

    act_for_classifier_{task}_N-{nsub}.npy

but uploaded all five tasks to a single key:

    Results/act_for_classifier_N-{nsub}.npy

so each task overwrote the previous one. What survives on S3 is one unidentified
task, shape `(155, n_vertices)` per hemisphere — no task dimension. The per-task
keys the code reads do not exist.

These arrays are the models' response variable. They no longer need
regenerating — the backup above supersedes that — but the working bucket's copy
should not be trusted.

`sti.s3io.upload` now refuses to overwrite an existing key, so this cannot recur.

## Local reference files (small, versioned)

| File | Purpose |
|------|---------|
| `config/participants.tsv` | dHCP participants: gender, birth age, birth weight, singleton |
| `config/subjects/*.txt` | the cohorts, one ID per line |
| `data/parcellations/ff.{L,R}.label.gii` | Glasser parcellation per hemisphere |
| `data/parcellations/*.midthickness*.surf.gii` | surface geometry for the spatial null |

## Target dimension: 360, not 334

The stored connectivity arrays carry **360** target columns, not the 334 the
manuscript reports. The 26 DLPFC columns are identically zero in every array, so
the DLPFC really was excluded from tractography exactly as the SI states; the
extra columns are structural padding that the elastic net gives zero weight. Do
not trim the arrays to 334, and do not read those columns as DLPFC self-connectivity.

## Rebuilding a cohort array

Per-subject tractography exists for **325 of the 326** term neonates — all of
batch 1 and all of batch 2. The one exception is `CC00688XX21`, the subject the
legacy code commented out as "non andato". To build the full-cohort array:

```bash
sti build-connectivity --cohort neonates_term_all --allow-missing \
    -o data/derivatives/conn_for_classifier_N-325_infants.npy
```

Per-subject files are streamed and deleted as they are read, so peak disk use is
one file rather than ~4 GB. A `.subjects.txt` sidecar records the subject order,
since the arrays themselves carry no IDs.

## Neonatal covariates

Built from the dHCP diffusion release mounted at `/dhcp/dhcp_dmri_pipeline`:

```bash
python pipelines/00_cohorts/build_covariates.py \
    --release /dhcp/dhcp_dmri_pipeline -o config/neonatal_covariates.tsv
```

The release splits its metadata: `participants.tsv` at the root holds birth
variables, while age at scan lives in a per-subject `sessions.tsv`. The script
joins them. All 325 analysed neonates have complete `scan_age` and `birth_age`,
and none has more than one session.

**Motion is not available.** The release publishes no per-subject motion
summary: the diffusion JSON records `MotionCompensation: 1`, a flag rather than a
metric, and eddy's movement-RMS outputs are not distributed. `sti scan-age`
therefore defaults to `scan_age, birth_age`; pass `--predictors` to add a motion
column if you derive one.
