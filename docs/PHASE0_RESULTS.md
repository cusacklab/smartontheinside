# Phase 0 results — the go/no-go controls

Results from the controls in [REVISION_PLAN.md](REVISION_PLAN.md), run
2026-10-30. The distance-regressed rerun (tuned penalty, job 16534) is in
flight; everything else is final.

**Summary: the transfer result survives Reviewer 1's key test for four of the
five contrasts; motor does not survive it, and the individual-level
(fingerprinting) benchmark fails outright.** The full-pipeline surrogate null —
R1's suggestion 1, the destructive control with matched noise and matched
transfer — puts the positional share of the real pipeline's transfer at
r ≈ 0.13–0.20, and the observed accuracy exceeds it decisively everywhere
except motor. The constructive distance-only model (section 1) looks far more
damning, but it enjoys noiseless features and no cross-cohort transfer; the
pipeline null is the fair version of the same question. Motor fails both.

## 0. The full-pipeline surrogate null (Fig. S10) — passed, except motor

200 surrogates per cell: each draw spatially permutes every adult's map by one
variogram-matched permutation, refits the elastic net, transfers to all 325
neonates (`sti pipeline-null`; `data/results/pipeline_null_summary.csv`).

| | Observed r | Null mean | Excess | p_spin (FDR) |
|---|---|---|---|---|
| Emotion L / R | 0.40 / 0.46 | 0.15 / 0.14 | +0.25 / +0.32 | 0.006 / 0.006 |
| WM L / R | 0.43 / 0.43 | 0.17 / 0.15 | +0.26 / +0.28 | 0.006 / 0.006 |
| Social L / R | 0.33 / 0.43 | 0.16 / 0.13 | +0.17 / +0.29 | 0.006 / 0.006 |
| Language L / R | 0.38 / 0.36 | 0.16 / 0.15 | +0.22 / +0.20 | 0.006 / 0.006 |
| **Motor L / R** | 0.24 / 0.16 | 0.20 / 0.16 | **+0.04 / +0.00** | **0.20 / 0.47** |

p = 0.005 is the floor for 200 surrogates. Two numbers for the manuscript:
the pipeline transfers an arbitrary smooth map at r ≈ 0.15 (that is the
positional share under matched noise), and the real maps exceed it by
0.17–0.32 — except motor, whose transfer is fully accounted for by smoothness
plus position. Figures: `figures/manuscript/S10_pipeline_null_*.png`.

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

## 3. Distance-regressed connectivity — passed, and motor improves

Donahue-style control: each subject's exponential distance decay removed from
their profiles (log space, per-subject unit SD), penalty re-selected on the 20
held-out tuning adults only (`sti distance-control --tune`: alpha = 0.1,
l1 = 0.2, on a surface flat across three orders of magnitude — the first run
used the raw-count alpha, which zeroed every coefficient). Within-task
accuracy, n = 325 (`data/results/neonatal_N325_distance_regressed.csv`):

| | Raw | Distance-regressed | Retained |
|---|---|---|---|
| Emotion L / R | 0.40 / 0.46 | 0.34 / 0.37 | 85% / 79% |
| WM L / R | 0.43 / 0.43 | 0.45 / 0.45 | 107% / 106% |
| Social L / R | 0.33 / 0.43 | 0.38 / 0.37 | 115% / 88% |
| Language L / R | 0.38 / 0.36 | 0.40 / 0.36 | 104% / 101% |
| **Motor L / R** | 0.24 / 0.16 | **0.33 / 0.28** | **137% / 180%** |

Column specificity: 37/40 comparisons remain significant. The decay component
of the profiles is not what carries the transfer — removing it costs nothing
overall, and for motor it was actively *hurting* (accuracy rises by half to
four fifths). That leaves motor ambiguous: its raw transfer fails the pipeline
null, but its regressed transfer is substantially higher. The combined control
— the surrogate null run on the regressed features (job 16544,
`STI_REGRESS=1`) — settles whether regressed motor exceeds what position
carries through the same pipeline. Table to follow.

## 4. What this means for the checkpoint (preliminary)

- **The headline transfer claim survives the strongest control for emotion,
  WM, social and language** — observed accuracy exceeds what the real
  pipeline can carry positionally (r ≈ 0.15) by 0.17–0.32. This directly
  answers R1's major issue, with their own proposed analysis.
- **Motor fails both controls and should become the paper's explicit negative
  control**: geometry predicts the motor map at 0.56–0.64 in-sample, and the
  real pipeline's motor transfer is indistinguishable from smooth-map
  transfer. Naming this strengthens the paper; hiding it invites the review
  all over again.
- **The distance-only result (section 1) belongs in the paper as the
  constructive bound**: for language and WM, noiseless geometry alone can
  reconstruct the group-average map as well as tractography does — so the
  claim those contrasts support is "connectivity carries function-specific
  information beyond smoothness and position through a matched pipeline",
  not "connectivity outpredicts geometry in absolute terms".
- **Fig. 2 cannot be framed as individual-level validation** (section 2:
  0/10 against the LOSO group-mean benchmark). It needs reframing as
  shared-across-individuals structure, with the benchmark reported.
- Decision for the authors at the checkpoint: the paper this evidence
  supports is a task-resolved account — which adult functional distinctions
  are carried by connectivity beyond spatial layout, and the finding that
  those (and only those) are already present in neonatal connectivity.
  Whether that is the paper to write, and where it goes, is yours to call.
