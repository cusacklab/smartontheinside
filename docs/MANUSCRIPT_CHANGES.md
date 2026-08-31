# What needs to change in the manuscript

Generated 2026-08-31 from the restructured pipeline. Numbers below come from
`data/results/neonatal_N325*.csv`, reproducible with the commands in each section.

Status key: **[NUMBERS CHANGE]** existing claim needs new values · **[NEW]** fills
a `[TBD]` · **[DECISION]** needs an author call · **[PENDING]** analysis still to run.

---

## 1. Sample sizes **[NUMBERS CHANGE]** **[DECISION]**

| Reported | Actual |
|---|---|
| 176 adults | **155** analysed (175 available, minus 20 held out for hyperparameters) |
| 326 term neonates | **325** analysed (326 in the cohort; `CC00688XX21` has no usable tractography) |

The neonatal analysis has now been **rerun at n=325**, so the manuscript's cohort
is matched for the first time. The previously reported results came from 183
neonates — batch 2 only — because `subjlist_infants` was assigned twice in the
legacy script and the 142-subject batch 1 was silently overwritten.

**Decision needed.** The Methods should state that 20 adults were held out for
hyperparameter selection and excluded from the reported sample; that is what
makes the reported accuracy independent of the tuning, and it explains 175 → 155.
It is currently unexplained.

## 2. Figure 3 — neonatal prediction **[NUMBERS CHANGE]**

`sti neonatal --neonates neonates_term_all` (n=325). Mean within-task accuracy:

| Contrast | Left | Right |
|---|---|---|
| Working memory (2-back) | 0.425 | 0.425 |
| Emotion (shapes) | 0.397 | 0.463 |
| Language (story) | 0.378 | 0.355 |
| Social (ToM) | 0.326 | 0.425 |
| Motor (average) | **0.239** | **0.158** |

Every contrast is well clear of zero in all 325 neonates. The headline claim
holds at the full cohort.

**The motor contrast is a genuine outlier** and should be named as such in the
text rather than left for a reader to notice: it is the least predictable map in
both hemispheres, by a wide margin.

## 3. Task specificity — test down columns, not along rows **[NUMBERS CHANGE]** **[DECISION]**

This is the most substantive change.

The current analysis compares along **rows**: does a model predict its own task
better than it predicts other tasks? That conflates model specificity with how
predictable each target map is. Because the motor map is intrinsically hard, the
motor model predicts every other map better than its own, and fails the row test
despite being the best available predictor of motor.

Comparing down **columns** — for a given target map, does its own model beat
models trained on other tasks — holds target difficulty constant:

| Test | Comparisons with the diagonal significantly higher |
|---|---|
| Row (as currently reported) | 26 / 40 |
| **Column** | **40 / 40** |

Every target map is best predicted by its own model, in both hemispheres, margins
0.019–0.145 (median 0.067). This **strengthens** the specificity claim and
removes the need for the hedge now in the Fig. 2 and 3 captions ("within-task
prediction *generally* exceeded between-task prediction").

**Recommendation.** Report the column test as the primary specificity analysis,
keep the row test as secondary, and state plainly that the motor contrast is
poorly predicted by every model. Figure captions need rewording: asterisks now
mark cells where the diagonal model beats that column's model on the *same*
target map.

Both tables are written by `sti figures`
(`*_specificity_column.csv`, `*_specificity_row.csv`).

## 4. Spatial null — Fig. S8 **[NEW]**

Replaces `[TBD]` in *SI Methods, Spatial null* and the Fig. S8 caption.

**Method text.** Rotating a map defined only on the DLPFC sends most vertices
outside the mask with nothing to put in their place — the boundary problem the
current draft flags as unresolved. Instead, 1,000 variogram-matched surrogate
maps (Burt et al., 2020) were generated *within* the DLPFC mask for each adult
group-average activation map. Surrogates preserve the spatial autocorrelation and
the exact value distribution of the observed map while destroying its
correspondence with the prediction. Each neonate's predicted map was held fixed
and correlated against every surrogate; the null is the distribution of the
across-neonate mean. No model is refitted, so the null costs seconds rather than
1,000 refits.

**Result.** All ten task × hemisphere combinations exceed the null
(p_spin ≤ 0.002, FDR-corrected p ≤ 0.002; the floor for 1,000 surrogates is
0.001). Null means were ≈ 0 (−0.005 to +0.001) with SD ≈ 0.055. Every observed
value exceeded the null 95th percentile; the smallest margin over the null mean
was 0.160 (right motor, 3.4 null SDs).

**Worth stating.** The spatial null is about three times wider than a naive
permutation null (SD 0.055 vs ≈ 0.02). On a patch as compact as the DLPFC, two
independently generated smooth maps can correlate at |r| ≈ 0.7 from shared
spatial structure alone, so raw correlations between DLPFC maps should not be
interpreted without a spatial null.

## 5. Hyperparameters — Fig. S6 **[NUMBERS CHANGE]**

Replaces "The best parameters were visually chosen".

All 84 stored grid cells were recovered and ranked. **α = 0.4, L1 ratio = 0.6
ranks 3rd of 84 by mean within-task Pearson correlation and falls 0.0001 short of
the grid maximum** — the choice is essentially optimal and needs no defending,
only restating with a criterion.

Two points for the SI: the original heatmap plotted `score` (R²) while the paper
reports Pearson r; and the surface is a flat ridge in which accuracy tracks the
L1 penalty strength (α × L1 ratio) rather than either parameter alone, which is
why a visual choice landed correctly.

`sti hyperparams` prints a ready-to-use replacement sentence.

**Nested cross-validation is not needed.** Tuning on 20 held-out subjects and
reporting on the disjoint 155 is a held-out tuning split, which is stronger than
nested CV here: the reported accuracy comes from participants the hyperparameters
never saw. The weakness was never the absence of nested CV, only the unstated
criterion. The `[TBD: describe the folds and grid]` in Materials and Methods
should be replaced with a description of this design.

## 6. Still to run **[PENDING]**

| Item | Status |
|---|---|
| Fig. 4, adult group-average prediction | Cluster array job ready (`slurm_adult_average.sh`, ~20 min) |
| Fig. S7, neonate vs adult comparison | Needs Fig. 4 first, then `sti compare` |
| Fig. S9, scan-age analysis | **Blocked on data** — see below |

**Fig. S9 is blocked.** `config/participants.tsv` supplies `birth_age` only. The
model needs `scan_age` (postmenstrual age at scan, in the dHCP `sessions.tsv`)
and `mean_fd` (derived from the dHCP motion/QC outputs). Neither is in this
repository or either S3 bucket. The analysis runs as soon as they are supplied
(`sti scan-age --extra <file.tsv>`).

## 7. Also worth a line in the Methods

- **Targets.** The connectivity arrays carry 360 columns, not 334. The 26 DLPFC
  columns are identically zero, confirming the DLPFC was excluded from
  tractography as the SI states. Harmless, but worth knowing if anyone inspects
  the deposited arrays.
- **Data and code availability.** `[TBD: repository/DOI]` can now become
  `github.com/cusacklab/smartontheinside` plus a Zenodo DOI at acceptance.
- **Statistics.** The main text says specificity was tested by bootstrap, the SI
  says a t-test, and the only bootstrap in the legacy code was never called.
  These now agree: a paired bootstrap across participants, FDR-corrected, with a
  paired t-test reported alongside. The comparison is paired because within- and
  between-task accuracies come from the same participants.
