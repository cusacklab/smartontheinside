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
prove connectivity carries no individual information.

**Protocol clarification (authors' intent, 2026-10-30).** Fig. 2 was never
meant as individual-differences prediction: it is the cross-subject
generalisation control — train without a subject, predict them from their own
connectivity — matching Fig. 3's training logic. Three distinct questions, one
figure each:

1. *Does the mapping generalise across subjects?* Fig. 2's job (shared-mapping
   claim; load-bearing, since neonatal transfer is only meaningful if the
   mapping is species-typical). The 0/10 benchmark does not damage it — it
   means Fig. 2's accuracy is carried by the shared component, which is all
   the argument needs.
2. *What is the adult ceiling for the neonatal transfer?* Fig. 4/S7's job —
   the only protocol matched to Fig. 3 target-for-target (group-average map).
   The target mismatch is also why R2 found neonatal accuracy "higher" than
   Fig. 2: a smooth group target is easier to hit than noisy individual maps.
3. *Does connectivity predict individual differences?* A different question
   (residual maps: corr(ŷᵢ − ȳ, yᵢ − ȳ)), not required by the paper, currently
   unsupported.

Manuscript consequence: keep Fig. 2, recaption as cross-subject
generalisation, draw the LOSO group-mean benchmark on the figure as a
reference line, and state in one sentence that individual-differences
prediction is a distinct question these data do not address (benchmark in SI).
Optional upgrade: the residual-map analysis answers R1's suggestion 6 with a
measurement either way (needs `--save-predictions` on `adult-loo`, one
cluster pass).

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
four fifths).

## 3b. The combined control — all ten cells pass

Surrogate null run on the distance-regressed features with the tuned penalty
(`sti pipeline-null --regress-distance`;
`data/results/pipeline_null_regressed_summary.csv`):

| | Observed r | Null mean | Excess | p_fdr |
|---|---|---|---|---|
| WM L / R | 0.45 / 0.45 | 0.17 / 0.16 | +0.28 / +0.29 | 0.006 / 0.006 |
| Social L / R | 0.38 / 0.37 | 0.16 / 0.14 | +0.21 / +0.24 | 0.006 / 0.006 |
| Language L / R | 0.39 / 0.36 | 0.16 / 0.16 | +0.23 / +0.20 | 0.006 / 0.006 |
| Emotion L / R | 0.34 / 0.37 | 0.15 / 0.14 | +0.19 / +0.22 | 0.006 / 0.006 |
| **Motor L / R** | 0.33 / 0.28 | 0.22 / 0.18 | **+0.11 / +0.11** | **0.040 / 0.028** |

**Motor rejoins the positive results.** Its raw transfer failed the null
because tractography's distance decay was actively corrupting the motor
prediction; with the decay removed, motor exceeds smooth-map transfer in both
hemispheres. Note the motor null is also the widest (null mean 0.18–0.22): the
motor map is the most geometry-predictable target, so the bar is highest
there, and the regressed transfer clears it anyway — at *, not **, which the
text should state plainly.

## 3c. The variance partition (Fig. 1b) — geometry interpolates, connectivity extrapolates

Commonality analysis under spatially blocked CV (`sti shares`;
`data/results/shares.csv`, panel `figures/manuscript/Fig1b_shares.png`).
Median across tasks and hemispheres:

| | Adult conn | Neonatal conn |
|---|---|---|
| Combined R² | 0.65 | 0.50 |
| Unique connectivity | **0.60** | **0.36** |
| Unique geometry | 0.03 | 0.05 |
| Shared | 0.04 | 0.05 |

This resolves the apparent tension with the distance-only model: geometry's
in-sample strength is *interpolation* (given most of a smooth map, position
fills in the rest), and under extrapolation to held-out patches it collapses
— while group-mean connectivity keeps predicting. Motor again carries the
largest geometric component in both cohorts (unique geometry up to 0.27 in
neonates). The neonatal unique connectional share (0.36) is 60% of the adult
one (0.60) in R² terms, consonant with the ~90% maturity figures in r terms.

## 4. The Phase 0 verdict

- **Go.** On the combined control — the full pipeline, distance-regressed
  features, variogram-matched surrogates — all five contrasts in both
  hemispheres carry function-specific connectivity information beyond
  geometry and smoothness, and that information transfers to all 325
  neonates (excess +0.11 to +0.29, all p_fdr < 0.05).
- **The honest headline numbers are increments, not absolute correlations**:
  smoothness alone transfers at r ≈ 0.15 through this pipeline; geometry
  in-sample reaches 0.23–0.64 depending on the map; connectivity adds
  +0.11–0.29 beyond both, already at birth.
- **Motor becomes the paper's internal demonstration**, not an embarrassment:
  the most geometry-predictable map, the one the raw pipeline failed on, and
  the one rescued by removing tractography's distance decay. It shows the
  controls have teeth and that the decay is a real artefact.
- **Fig. 2 cannot be framed as individual-level validation** (section 2:
  0/10 against the LOSO group-mean benchmark). It needs reframing as
  shared-across-individuals structure, with the benchmark reported.
- The paper this supports: which candidate organisers — smoothness, geometry,
  connectivity — specify adult DLPFC functional topography, in what shares,
  and which of those components is already present in neonatal connectivity.
  Framing discussion: see the resubmission plan, Phase 2 (now to be revised
  around the organisers framing).
