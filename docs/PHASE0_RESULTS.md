# Phase 0 results — the distance controls

First results from the go/no-go controls in [REVISION_PLAN.md](REVISION_PLAN.md).
Distance-only model run 2026-10-30 (`sti distance-control`); the full-pipeline
surrogate null and the distance-regressed rerun are on the cluster (jobs
16514/16515) and will complete this picture.

**Summary so far: Reviewer 1's positional concern is substantively correct for
most contrasts.** Pure geometry — each DLPFC vertex's distance to every target
parcel, through the same elastic net — predicts the group-average maps as well
as or better than tractography does for motor, language, WM and (L) social, in
*both* cohorts. Emotion in both hemispheres, and right social, carry signal
beyond position. And at the individual level, connectivity predictions never
beat the leave-one-subject-out group-mean benchmark.

## 1. Group-average targets: neonatal (Fig. 3) and adult (Fig. 4) vs distance-only

Within-task r against the adult group-average map:

| | Neonatal conn | Adult conn (LOO) | Distance only |
|---|---|---|---|
| Emotion L / R | 0.40 / 0.46 | 0.42 / 0.47 | **0.24 / 0.23** |
| Social L / R | 0.33 / 0.43 | 0.36 / 0.46 | 0.40 / 0.30 |
| WM L / R | 0.43 / 0.43 | 0.47 / 0.43 | 0.48 / 0.48 |
| Language L / R | 0.38 / 0.36 | 0.51 / 0.42 | 0.49 / 0.45 |
| Motor L / R | 0.24 / 0.16 | 0.34 / 0.28 | **0.64 / 0.56** |

Median positional share: 118% of the neonatal accuracy, 104% of the adult.
Full tables: `data/results/distance_only.csv`, `positional_share.csv`.

Two readings, both important:

- **The confound is a property of the group-average analysis, not of the
  neonatal transfer.** Adults show the same pattern, so the neonatal result is
  no *worse* than the adult benchmark — but both are dominated by geometry for
  three to four of the five contrasts.
- **The comparison is tilted toward the distance model** (noiseless features,
  identical at train and test, no cross-cohort transfer). The two cluster
  controls are the fair versions: the pipeline null matches noise and
  transfer exactly, and the distance regression uses the real noisy features
  with only the decay removed. Judgement on motor/language/WM should wait for
  those; emotion's margin (+0.16 to +0.24) is unlikely to be overturned.

## 2. Individual-level benchmark (reviewer 1, suggestion 6) — failed

Fig. 2 protocol, every predictor scored against each adult's own map:

| | Own-connectivity (Fig. 2) | Distance only | LOSO group mean |
|---|---|---|---|
| Emotion L / R | 0.12 / 0.17 | 0.06 / 0.08 | **0.25 / 0.32** |
| Social L / R | 0.16 / 0.20 | 0.16 / 0.12 | **0.38 / 0.36** |
| WM L / R | 0.25 / 0.22 | 0.25 / 0.23 | **0.52 / 0.48** |
| Language L / R | 0.26 / 0.19 | 0.22 / 0.18 | **0.45 / 0.39** |
| Motor L / R | 0.22 / 0.16 | 0.39 / 0.29 | **0.61 / 0.50** |

Connectivity-based individual prediction beats the standard fingerprinting
benchmark in **0 / 10** cells — the LOSO group mean wins everywhere, by a
factor of about two. R1 stated the consequence in advance: the connectivity
profile "may carry little more than positional information, which would
constrain the interpretation of the adult-to-neonate generalization."

Nuance: individual activation maps are noisy, and test–retest reliability
bounds any individual-level prediction, so failing this benchmark does not
prove connectivity carries no individual information — but it does mean the
paper cannot claim individual-level validation, and Fig. 2's framing has to
change regardless of what the remaining controls show.

## 3. What this means for the checkpoint (preliminary)

- **Emotion (bilateral) and right social are the defensible core**: above
  geometry in both cohorts' group-average analyses.
- **Motor should probably become the paper's own negative control** rather
  than an embarrassment: geometry predicts it at 0.56–0.64 while connectivity
  manages 0.16–0.34, which is itself informative about what the method
  measures.
- If the pipeline null and distance regression confirm this split, the honest
  paper is substantially different from the submitted one: not "the
  connectivity that distinguishes adult subregions is present in neonates"
  across the board, but a task-resolved account of which functional
  distinctions are carried by connectivity beyond spatial layout — present in
  neonates for the contrasts where it exists in adults at all.
- Decision for the authors at the checkpoint, not before: whether that paper
  is the one to write, and where it goes.
