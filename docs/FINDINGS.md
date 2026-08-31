# Findings from the code audit

Recorded while restructuring the repository (2026-08). Ordered by how much they
affect the reported results. Items 1 and 2 need a decision before anything is
rerun or resubmitted.

---

## 1. The reported sample sizes do not match the code

The manuscript reports **176 adults** and **326 term neonates**. The committed
code ran **155 adults** and **183 neonates**.

**Neonates.** `legacy/classifier.py` assigns `subjlist_infants` twice: a
142-subject list, then a 183-subject list that silently overwrites it. The lists
are disjoint, and

```
142 (batch 1) + 183 (batch 2) + 1 excluded ('sub-CC00688XX21', "# non andato") = 326
```

which is exactly `config/subjects/neonates_term_all.txt`, verified
element-for-element. So 326 is the intended cohort, processed in two batches, and
only batch 2 was ever analysed. S3 holds no combined array — only
`conn_for_classifier_N-155_infants.npy` and `..._N-183_infants.npy`.

**Adults.** `sample_subjlist = 20` with `hyperparameter_subjects = False` performs
`subjlist = subjlist[20:]`, dropping the 20 hyperparameter-tuning subjects:
175 → 155. The full list is 175, not 176.

Excluding the tuning subjects is correct — it is what makes the reported accuracy
independent of hyperparameter selection — but the manuscript should say so, since
it explains 175 → 155.

The cohorts are now explicit files under `config/subjects/`, asserted in
`tests/test_cohorts.py`.

## 2. The per-task adult activation arrays were destroyed on S3

The extraction step saved activations locally per task but uploaded all five to
one key, so each overwrote the last. Only one unidentified task survives. These
are the models' response variable, so nothing can be rerun until they are
regenerated. Full detail in [DATA.md](DATA.md).

`sti.s3io.upload` now refuses to overwrite an existing key.

## 3. Predictions from all five tasks were written into one shared object

```python
pred = {'L': [], 'R': []}
all_pred = {x: pred for x in taskcondict_selected}
```

The comprehension binds the *same* dict to every key, so predictions from all
five tasks accumulated into one pair of lists. `all_pred` was pickled and
uploaded, so any downstream use of those files is affected. The reported
correlations are computed from `y_estimate` directly and are **not** affected.

Fixed in `sti.evaluate.Predictions`; regression test in
`tests/test_evaluate.py::test_predictions_are_not_aliased_across_tasks`.

## 4. The bootstrap in the results script reads globals, and is never called

`bootstrap_compare_two_groups(group1, group2)` shifts `within` and `across` —
module-level globals — rather than its own arguments. The only call site is
commented out. Meanwhile the main text describes "bootstrap across participants"
and the SI describes a t-test, so it is unclear what produced the reported
significance.

Note also that within- and between-task accuracies come from the *same*
participants, so the comparison is **paired**; treating them as independent groups
loses power. `sti.stats.paired_bootstrap` implements the paired version and
reports a t-test alongside for comparison.

## 5. "Visually chosen" hyperparameters — defensible, but restate it

The SI says alpha and the L1 ratio were "visually chosen" from a heatmap. Two
observations, both now reproducible via `sti hyperparams`:

- The legacy heatmap plotted **`score` (R²)** while the paper reports **Pearson
  r**. Selecting on one metric and reporting another is avoidable.
- Recovering all 84 stored grid cells and ranking them by mean within-task
  Pearson: **α = 0.4, L1 = 0.6 ranks 3rd of 84 and falls 0.0001 short of the
  maximum.** The choice is essentially optimal.

The surface is a flat ridge — accuracy tracks the L1 penalty strength
(α × L1 ratio) rather than either parameter alone — which is why a visual choice
landed in the right place. `sti.hyperparams.methods_sentence()` emits a
ready-to-use replacement for the "visually chosen" sentence.

**On nested cross-validation:** it is not needed. Tuning on 20 subjects and
reporting on the disjoint 155 is a held-out tuning split, which is stronger than
nested CV for this purpose — the reported accuracy comes from participants the
hyperparameters never saw. The weakness was never the absence of nested CV, only
the unstated selection criterion.

## 6. Hemisphere label convention is the reverse of the usual one

In `ff.{L,R}.label.gii`, label indices **1–180 are RIGHT** and **181–360 are
LEFT** — confirmed from the embedded label names (`26 = R_SFL_ROI`,
`206 = L_SFL_ROI`). The files are correctly named and the code is self-consistent,
but the convention is easy to invert. Asserted in
`tests/test_surface.py::test_hemisphere_label_convention_is_as_documented`.

The DLPFC mask derived from these files contains exactly 2207 (L) and 2185 (R)
vertices, matching the data arrays — so vertex ordering is recoverable, which is
what makes the spatial null possible.

## 7. Result pickles are 21.6 GB each

`res` is a cumulative DataFrame re-pickled inside the innermost loop, so each
write contains every previous result. `Results/final_parameters_.../
tfMRI_MOTOR_subject_N-183.pickle` is 21.6 GB. Results are now collected as
records and framed once.

## 8. `makerois.py` builds the non-DLPFC mask with the wrong loop variable

```python
for r in regs:
    maskNOT_DLPFC[datNOT_DLPFC == reg] = 1   # 'reg', not 'r'
```

`reg` leaks from the preceding loop, so the mask marks only region 278 rather
than all 334 non-DLPFC regions. The tractography targets were built from
individual `ROI.N` masks, and a search of the repository confirms
`NOT_frontal.{L,R}.label.gii` is **written but never read**, so no result depends
on it. The files in `data/rois/` should nonetheless not be trusted.

## 9. Smaller items

- Paths were hard-coded to `/home/chiaracaldinelli` and `os.getlogin()`, which
  fails under SLURM (no controlling terminal). Now `sti.config` with
  `STI_DATA_DIR` / `STI_FIGURE_DIR`.
- Subject lists were pasted into six files and had drifted: `RankROIs.py` and
  `chiara_hcp_roi.py` include subject `114419`, which the classifier's list omits.
  Cohorts now live in `config/subjects/` and are loaded, not pasted.
- `conn_for_classifierL.npy` and `conn_for_classifierR.npy` in the old repo root
  are **both** `(361, 2185)` — the R-hemisphere vertex count. The "L" file does
  not hold left-hemisphere data. They look like single-subject debug artefacts;
  they are not read by any analysis.
- The activation z-scoring is per subject across vertices. Pearson correlation is
  invariant to that, so mixing z-scored and raw maps in the adult comparison is
  harmless — noted so nobody "fixes" it into a real change.

---

## What the extensions add

| Manuscript | Was | Now |
|---|---|---|
| Fig. S6 hyperparameters | "visually chosen" | `sti hyperparams` — explicit criterion, rank 3/84 |
| Fig. S7 neonate vs adult | `[TBD]` | `sti compare` — unpaired bootstrap, FDR |
| Fig. S8 spatial null | `[TBD]` | `sti spatial-null` — variogram-matched surrogates |
| Fig. S9 scan age | `[TBD]` | `sti scan-age` — OLS, needs two dHCP covariates |

**On the spatial null.** The manuscript flags an unresolved problem: rotating a
map defined only on the DLPFC sends most vertices outside the mask, with nothing
to put in their place. This is avoided by generating variogram-matched surrogates
(Burt et al. 2020) *within* the mask, which the manuscript itself names as the
alternative. No rotation is needed and no model is refitted — the prediction is
held fixed and only the target map is resampled.

Validated in `tests/test_spatial_null.py`: surrogates reproduce the observed
variogram, preserve the marginal distribution exactly, detect a genuine effect,
and give a null **> 10× wider** than a naive permutation null. That last point is
the reason the analysis matters — a permutation null would make almost anything
look significant.

A caution worth carrying into the manuscript: on a patch this compact, two
*independently generated* smooth maps can correlate at |r| ≈ 0.7 purely from
shared spatial structure. Raw correlations between DLPFC maps should not be read
without a spatial null.
