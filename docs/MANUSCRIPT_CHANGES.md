# What needs to change in the manuscript

Generated 2026-08-31 from the restructured pipeline. Numbers below come from
`data/results/neonatal_N325*.csv`, reproducible with the commands in each section.

Status key: **[NUMBERS CHANGE]** existing claim needs new values · **[NEW]** fills
a `[TBD]` · **[DECISION]** needs an author call · **[PENDING]** analysis still to run.

## The seven decisions

Sections 1, 3, 4, 7 and 8 each need an author call; 7 and 8 carry two apiece.

| # | Decision | Section |
|---|---|---|
| 1 | State in Methods that 20 adults were held out for hyperparameter selection, which is what explains 175 → 155 | 1 |
| 2 | Make the column test the primary specificity analysis, and retire the matrix figure rather than relegating it | 3 |
| 3 | Reconcile the SI's contrast count (31 used, 22 stated) and document the rescaling the five-cluster result depends on | 4 |
| 4 | Promote the neonatal-vs-adult figure to the main text and move Fig. 4 to the SI | 7 |
| 5 | Qualify "most of the adult structure is present at birth" — it holds for emotion and working memory, less so for language and motor | 7 |
| 6 | Decide how to report the age effect, given age at scan and age at birth cannot be separated in a term-only cohort | 8 |
| 7 | Derive a motion summary from the raw data, or drop the covariate from the SI text | 8 |

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

| Test | Neonatal (n=325) | Adult group-average (n=155) |
|---|---|---|
| Row (as currently reported) | 26 / 40 | 33 / 40 |
| **Column** | **40 / 40** | **40 / 40** |

The same pattern appears in both analyses, so this is a property of the test, not
of the neonatal data.

Every target map is best predicted by its own model, in both hemispheres, margins
0.019–0.145 (median 0.067). This **strengthens** the specificity claim and
removes the need for the hedge now in the Fig. 2 and 3 captions ("within-task
prediction *generally* exceeded between-task prediction").

**Recommendation.** Report the column test as the primary specificity analysis,
keep the row test as secondary, and state plainly that the motor contrast is
poorly predicted by every model.

**The matrix figure should be replaced.** A heatmap forces the reader to compare
along rows, which is the confounded direction. `sti figures` now produces a line
panel as the primary specificity figure (`*_specificity.png`): x is the target
map, one line per model, so the comparison that matters is vertical. The top row
shows raw accuracy (making the motor map's difficulty obvious); the bottom row
subtracts each target's across-model mean, leaving only specificity — and every
line then peaks at its own target, in both hemispheres, with the own-model point
ringed and labelled. The heatmap is still written as
`*_specificity_matrix.png` for reference.

Both test tables are written too (`*_specificity_column.csv`, `*_specificity_row.csv`).

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

## 6. Figure 4 — adult prediction of the group-average map **[NUMBERS CHANGE]**

Run on the cluster as a 10-task array (`slurm_adult_average.sh`); 51 minutes of
compute, 5.7 minutes wall clock. Mean within-task accuracy, n=155:

| Contrast | Left | Right |
|---|---|---|
| Language (story) | 0.514 | 0.421 |
| Working memory | 0.469 | 0.432 |
| Emotion | 0.419 | 0.469 |
| Social | 0.363 | 0.460 |
| Motor | 0.335 | 0.275 |

Motor is the least predictable map here too, so its low neonatal accuracy is a
property of the contrast rather than of neonatal data.

## 7. Figure S7 — neonatal vs adult accuracy **[NEW]** **[DECISION]**

**Recommendation: promote this to the main text, and move Fig. 4 to the SI.**

Fig. 4's own caption states its purpose — "for comparison with the neonatal
predictions in Fig. 3". This figure *is* that comparison, made explicitly and
with statistics, and it shows both sets of means, so nothing Fig. 4 conveys is
lost. A standalone panel that asks the reader to hold Fig. 3 in mind and
subtract is strictly weaker than the subtraction drawn for them.

**Fig. 2 should stay.** It is the only analysis that predicts each adult's *own*
map rather than a group average, which is the more stringent claim and the one a
reviewer will look for: without it the paper only ever predicts a smooth
group-average target. It also supports its own Results section, which would
otherwise be left without a figure. Fig. 2 and Fig. 4 are not redundant with each
other -- Fig. 2 is individual-level validation, Fig. 4 is a baseline that exists
only for the neonatal comparison. It is Fig. 4 that this figure replaces.

That keeps four main-text figures with a cleaner arc: the method works in adults
(2), it works from neonatal connectivity (3), and it works nearly as well as in
adults (this one).

### The maturity framing

The figure now has a second panel giving neonatal accuracy as a percentage of
adult, with a bootstrapped interval:

| | Left | Right |
|---|---|---|
| Emotion | 95% | **99%** |
| Working memory | 91% | **98%** |
| Social | 90% | 92% |
| Language | 74% | 84% |
| Motor | 71% | **57%** |

Median 90%. For right emotion and right working memory the interval spans 100%,
so neonatal prediction is statistically indistinguishable from adult.

**Caveat to state.** This is a ratio of two prediction accuracies, not a direct
measure of connectivity maturity, and it is bounded by the adult ceiling: adult
group-average prediction is itself only r ~ 0.28-0.51, so "90% of adult" is 90%
of a modest ceiling, and both numerator and denominator carry measurement noise.
The claim it supports is that neonatal connectivity carries most of the
*functionally relevant, measurable* structure -- not that it is 90% mature.



Fills a `[TBD]`. Unpaired bootstrap of the difference in means, FDR-corrected.

| | Left | Right |
|---|---|---|
| Emotion | −0.022 (n.s.) | −0.006 (n.s.) |
| Working memory | −0.044 ** | −0.007 (n.s.) |
| Social | −0.037 *** | −0.035 * |
| Language | −0.136 *** | −0.066 *** |
| Motor | −0.096 *** | −0.117 *** |

Prediction from neonatal connectivity is **statistically indistinguishable from
prediction from adult connectivity** for emotion in both hemispheres and for
right working memory. It is significantly lower for language and motor, where the
shortfall is largest.

**Decision needed.** The Results heading "Most of the adult, functionally
relevant connectivity structure is present at birth" is supportable but should be
qualified: the claim holds most strongly for emotion and working memory, and less
so for language and motor. That language shows the largest neonatal shortfall is
interesting in its own right and worth a sentence in the Discussion rather than
being left implicit.

## 8. Figure S9 — accuracy and age at scan **[NEW]** **[DECISION]**

Fills a `[TBD]`. `scan_age` was recovered from the per-subject `sessions.tsv`
files in `/dhcp/dhcp_dmri_pipeline` and joined to the release `participants.tsv`
(`pipelines/00_cohorts/build_covariates.py`). All 325 analysed neonates have
complete data, and none has more than one session.

**Considered separately**, both ages relate to prediction accuracy:

| Predictor | Simple correlation with accuracy |
|---|---|
| Postmenstrual age at scan | r = +0.292, p < 0.0001 |
| Gestational age at birth | r = +0.311, p < 0.0001 |

**Considered jointly**, they cannot be separated. The two correlate at r = 0.71
in a term-only cohort, and in the joint model gestational age at birth absorbs
most of the shared variance:

| Term | β (per week) | p |
|---|---|---|
| Age at scan | 0.0022 | 0.056 |
| Gestational age at birth | 0.0045 | **0.006** |

Model R² = 0.107, n = 325, variance inflation 2.02 for both terms. Per contrast,
only language shows an independent effect of age at scan
(β = 0.0044, p_FDR = 0.0095).

**Decision needed.** The SI plans to regress accuracy on age at scan *controlling
for* gestational age at birth. That control absorbs most of the effect, so the
honest statement is that accuracy increases with age across the neonatal period
but that a term-only cohort cannot attribute it specifically to age at scan
rather than to age at birth. The effect is also small: 0.016 r across the whole
7-week scan-age range, against a cohort accuracy range of 0.28–0.42.

**Motion could not be included.** The manuscript specifies mean framewise
displacement as a covariate. The dHCP diffusion release does not publish one:
the pipeline JSON records `MotionCompensation: 1`, a flag that correction was
applied rather than a metric, and eddy's movement-RMS outputs are not
distributed. Of the session-level nuisance variables that *are* released,
sedation has almost no variance here (5 of 325 infants). Either derive a motion
summary from the raw data or drop the covariate from the SI text.

## 9. Also worth a line in the Methods

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
