# Resubmission plan

PNAS rejected MS# 2026-32616 on 2026-10-27 (editor + 2 reviewers; full text in
`pnas_reviews.txt`). This is the plan for addressing the reviews before
submitting elsewhere. Companion documents: [FINDINGS.md](FINDINGS.md) (code
audit), [MANUSCRIPT_CHANGES.md](MANUSCRIPT_CHANGES.md) (changes already
settled).

## Reading the rejection

The two reviews fail the paper for different reasons, and they need different
responses.

**Reviewer 1 is a methods review and a gift.** They accept the question,
praise the writing and documentation, and identify one real threat: because no
prediction is individually specific, the adult-to-neonate transfer could ride
on *positional* information (where a vertex sits in the DLPFC) rather than
function-specific connectivity — especially since tractography is biased
toward nearby targets and the group-average task maps are spatially coarse.
They then list exactly the controls that would settle it. If the results
survive those controls, R1 has handed us a substantially stronger paper.

**Reviewer 2 is a premise review.** Their core objection is the framing claim
that neonatal DLPFC "is a region in which the adult functions are known to be
absent": neonates demonstrably have motor function, language precursors in
inferior frontal cortex (Mahmoudzadeh 2013; Dehaene-Lambertz 2009), and early
frontal attention effects (Ellis). They also argue the data cannot test the
connectivity-scaffold hypothesis without longitudinal task fMRI. The first
point is correct and we should concede it fully — the absence claim is both
wrong and unnecessary for the paper. The second point defines what the paper
can and cannot claim, and the reframing must respect it rather than argue
with it.

**The editor's two reasons** — insufficient novelty for PNAS, and no
within-individual function+connectivity — map onto R2's two points. Neither
is fixable *for PNAS*; both are addressable for a strong field journal.

A useful fact for morale: of R2's eleven methods questions, six are already
answered by work sitting in this repo (motion, train/test leakage, elastic
net training, the neonate-vs-adult accuracy puzzle, betas-vs-contrasts, low
accuracies contextualised). The puzzle R2 flags — "why would neonatal accuracy
be higher than adult?" — was an artefact of the n=183 batch; at the corrected
n=325, neonatal accuracy is at or below adult everywhere (Fig. S7 analysis).

---

## Phase 0 — the go/no-go controls

Run these before any rewriting. They are R1's major issue, and if the result
does not survive them, the paper needs rethinking, not rewording.

### 0.1 Full-pipeline surrogate null (R1 suggestion 1) — the critical one

Our current spatial null (Fig. S8) holds the prediction fixed and resamples
the *target* map. R1 asks for the stronger version: generate
variogram-matched surrogate task maps, then run them through the **entire
two-step pipeline** — fit adult connectivity→surrogate-map models, transfer
the weights to neonates — and ask whether real task maps transfer better than
arbitrary smooth maps. If they don't, the transfer reflects shared positional
information.

- Cost control: use the group-average pipeline (one model per task ×
  hemisphere, as in Fig. 4), not per-subject LOO; 100–200 surrogates rather
  than 1,000 is defensible for a pipeline-level null. Shard on the cluster
  with the existing `sti merge` infrastructure.
- **Implemented** as `sti pipeline-null` (`sti.pipeline_null`,
  `slurm_pipeline_null.sh`, Fig. S10 slot). Because rank-resampled surrogates
  are vertex *permutations* of the group-mean map, each null draw applies one
  permutation to every adult's individual map — the whole training set is
  spatially rearranged coherently, preserving between-subject variability —
  and the pipeline reruns verbatim. Validated on synthetic cohorts
  (`tests/test_pipeline_null.py`): the null is beaten when adults and
  neonates share function-specific structure, and absorbs the transfer when
  connectivity encodes nothing but position. The summary's `excess_r`
  (observed minus null mean) is the share of transfer that position cannot
  explain — report it alongside p_spin. Awaiting the cluster run.

### 0.2 Distance controls (R1 suggestion 2)

Two analyses, same pipeline, different features:

1. **Geodesic-distance-only model**: replace each vertex's connectivity
   profile with its geodesic distances to the non-DLPFC targets
   (`wb_command -surface-geodesic-distance` on the midthickness surfaces) and
   rerun everything. This quantifies how much of the reported accuracy pure
   position buys.
2. **Distance-regressed connectivity** (Donahue et al., 2016): regress
   log-distance out of the connectivity profiles, rerun. This shows what
   survives once the proximity bias of tractography is removed.

**Checkpoint.** The paper's claim becomes: real connectivity beats the
distance-only model, and the task maps beat pipeline-level surrogates. If
both hold, everything downstream is writing. If distance alone reproduces
most of the accuracy, the honest paper is about positional scaffolding, and
the framing changes fundamentally — decide then, together.

## Phase 1 — supporting analyses

Ordered by evidential value; all are feasible with data already in the repo
or on S3.

1. **LOSO group-average benchmark in adults** (R1 suggestion 6). Test whether
   individual-level adult predictions beat the leave-one-subject-out
   population-average task map — the standard fingerprinting benchmark. This
   determines which claim the paper can make about individual specificity,
   and R1 explicitly ties the interpretation of the transfer result to it.
   Data: the recovered per-task adult activation arrays (FINDINGS §2).
2. **Actual-vs-predicted map figure** (R1 suggestion 3; R2 asks the same —
   "what do these predictions look like in the brain?"). Surface plots of
   observed and predicted maps per task: group-average prediction plus two or
   three individual examples, adult and neonate. Extend `sti figures`.
   Nothing communicates "the accuracy is real but modest" more honestly, and
   both reviewers asked for it.
3. **Model weight maps with the Haufe (2014) transform** (R1 suggestion 4).
   Plot activation patterns A = cov(X)·W rather than raw elastic-net weights;
   show which connectivity targets drive each task's prediction. Feeds
   directly into the tract-anatomy story R2 asks about ("what are the actual
   tracts?").
4. **Direct adult-vs-neonate connectivity profile comparison** (R1
   suggestion 5). Correlate the group-mean profiles and test whether the
   high-weight features from (3) are the preserved ones. This is the analysis
   that would let the paper say *which* connections are adult-like at birth,
   not just that the predictions transfer.
5. **Registration QC audit** (R2). Document the dHCP→adult registration
   checks: what was run, how many subjects passed, what was done with
   failures. If no systematic check exists, run one (e.g., post-registration
   surface-overlap or label-agreement metric per subject) and report the
   distribution.
6. **Out-of-sample R²/NMSE alongside Pearson r** for the within-adult models
   (R1 minor 2), with the stated rationale for using correlation in the
   cross-group transfer. Plus the full predicted×actual correlation matrix
   across tasks and predictors — this single table serves R1 minors 2 and
   several of R2's "what does it look like" questions.

## Phase 2 — reframing (R2 + editor)

No new data can fix these; writing can.

- **Retract the absence claim.** Remove "a region in which the adult
  functions are known to be absent" and the "connectivity before function"
  framing wherever it implies functional silence. Cite the neonatal frontal
  literature R2 lists (Mahmoudzadeh 2013; Dehaene-Lambertz 2009; Ellis et
  al.) *in the Introduction*, not as a Discussion concession. The defensible
  claim: the adult-like division of labour among DLPFC subregions — the
  mapping from connectivity to five distinct task preferences — is present at
  birth, long before adult-level performance of those functions.
- **Retitle.** "Connectivity before function" cannot survive the concession.
  Candidate direction: "The structural connectivity that distinguishes adult
  prefrontal subregions is present in neonates" (the subtitle already carries
  the result; drop the contested half).
- **Reposition novelty honestly.** Prior longitudinal work (VWFA: connectivity
  at 5 predicts function at 8) tested the scaffold hypothesis *directly*; we
  do not. Our contribution: association cortex at birth, five task domains
  simultaneously, and a quantitative within-cohort adult benchmark. State the
  design's limit plainly — without neonatal task fMRI we test whether
  functionally relevant connectivity is present, not whether it causally
  scaffolds — and claim exactly that.
- **Rewrite the Significance statement** from scratch under the new framing
  (R2 called it out specifically).
- **Discussion additions**: (a) third-variable interpretations — areal
  identity/cytoarchitecture rather than connectivity per se (Kubota et al.
  2025), which R1 asks for by name; (b) tractography's documented
  limitations, including the distance bias, now quantified by Phase 0.2
  rather than hand-waved; (c) rework the "three possibilities" passage —
  R2 dismantled possibility 3 ("not functional at all"), so cut it and let
  possibilities 1–2 carry the section, consistent with the new framing.

## Phase 3 — methods and SI fixes

Small, definite items. Several are already done (left column of the ledger
below); the rest are documentation.

| Reviewer point | Action | Status |
|---|---|---|
| Motion comparability (R2) | Eddy-derived motion covariate, all 325 neonates; report adult motion alongside | **Done** (FINDINGS §8; needs adult side) |
| Elastic-net training / LOO details (R2) | Held-out 20-subject tuning split, explicit grid criterion | **Done** (`sti hyperparams`) |
| Leakage concern (R2) | Tuning subjects disjoint from reported sample; say so in Methods | **Done**, needs the Methods sentence (decision 1) |
| Neonatal > adult accuracy puzzle (R2) | Resolved by corrected n=325 cohort; neonatal ≤ adult throughout | **Done** (Fig. S7 analysis) |
| Betas vs contrast estimates (R1 minor 1, R2) | Verify from `extract_conn_act.py` which feature was used; state precisely, incl. any thresholding and per-task normalisation | To check |
| Name the 13 DLPFC parcels (R1 minor 3) | Spell out HCP-MMP names in Methods and Fig. S5 | Quick |
| Circularity of parcel ANOVA in main text (R1 minor 4) | Add the sentence; already flagged in SI | Quick |
| Fig. S3 without motor + adjusted colormap (R1 minor 5) | One `sti figures` variant | Quick |
| Ward linkage metric (R1 minor 6) | Use √(2(1−r)) or switch linkage; rerun dendrogram (Fig. S4) | Quick |
| Tractography parameters, masks, streamline normalisation (R2) | Document from the pipeline scripts (`pipelines/04–06`); state normalisation scheme and reference group | Documentation |
| Why per-infant rather than average infant connectivity (R2) | One Methods sentence: per-infant gives a distribution and subject-level covariates (age, motion analyses depend on it) | Quick |
| LANG_MATH / contrast selection rationale (R2) | Tie to the contrast-selection pipeline (`pipelines/01_contrast_selection`), state the reliability criterion; connects to decision 3 | Writing |
| "Sub-regions" terminology (R2) | Audit usage; reserve for the parcel analyses, use "vertex-wise organisation" for the main models | Writing |

Everything in MANUSCRIPT_CHANGES.md (sample sizes, column-test specificity,
corrected ANOVA, spatial null, scan age) goes in regardless — those were
needed before the reviews existed.

## Phase 4 — venue

Decide after Phase 0 results are in, since the strength of the controls
shapes the pitch. Realistic targets, given two-reviewer depth of methods and
a developmental-cognitive-neuroscience audience:

- **Nature Communications** — if Phase 0/1 produce a clearly stronger paper.
- **eLife** — review model suits a paper with this much methodological
  transparency; the public repo is an asset there.
- **Imaging Neuroscience** or **Cerebral Cortex** — strong, sympathetic
  methodological audience; likely smoothest path.
- **Developmental Cognitive Neuroscience** — safest fit if we want speed.

PNAS reviews are not transferred, so all reviewer-facing material goes into
the manuscript itself, not a response letter.

## Suggested order of work

1. Phase 0.2 distance controls first — cheapest, and most informative about
   whether there is a problem (days, mostly compute).
2. Phase 0.1 pipeline null (cluster job; build while 0.2 runs).
3. **Checkpoint — review Phase 0 together before writing.**
4. Phase 1 items 1–4 in parallel with Phase 2 drafting.
5. Phase 3 sweep, then full-manuscript consistency pass against
   MANUSCRIPT_CHANGES.md.
6. Venue call, reformat, submit.
