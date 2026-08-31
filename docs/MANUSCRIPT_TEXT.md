# Replacement text for decisions 1–5

Passages to paste into the manuscript, with track changes on. Each gives the
text to find and the text to replace it with. Nothing here has been applied —
the `.docx` files are edited by hand so that tracked changes, comments and
formatting survive.

Numbers are from `data/results/`; see [MANUSCRIPT_CHANGES.md](MANUSCRIPT_CHANGES.md)
for the reasoning behind each.

---

## Decision 1 — the held-out tuning participants

**Where:** *Materials and Methods*, "Participants", first sentence.

**Find:** "Adult data were 176 participants (99 female; 22–36 years) from the
Human Connectome Project 1200-subject release…"

**Replace with:**

> Adult data were 175 participants from the Human Connectome Project
> 1200-subject release, selected as the low-motion exploratory cohort of Ito et
> al. (2017). Twenty were held out to select the elastic-net hyperparameters and
> excluded from all reported analyses, leaving 155 participants; the reported
> accuracies are therefore independent of hyperparameter selection. Preprocessed
> task fMRI and diffusion data were obtained from the HCP via Amazon Web
> Services.

**And:** "…we included the 326 born at term (37–42 weeks gestation; 175 male)"

**Replace with:**

> …we included those born at term (37–42 weeks gestation). Usable tractography
> was obtained for 325 of the 326 term-born neonates; one was excluded for
> failed diffusion processing.

*(Check the female/male counts against the 155 and 325 actually analysed — the
current figures correspond to the full 176/326.)*

---

## Decision 2 — task specificity tested down columns

**Where:** *Materials and Methods*, "Predicting function from connectivity",
final sentence.

**Find:** "Task specificity was assessed by evaluating each task's model against
every task's activation and comparing within-task (diagonal) with between-task
(off-diagonal) accuracy by bootstrap across participants."

**Replace with:**

> Task specificity was assessed by evaluating every model against every
> contrast's activation map. For each target map we compared the accuracy of the
> model trained on that contrast with the accuracy of each model trained on a
> different contrast, using a paired bootstrap across participants (10,000
> resamples) with Benjamini–Hochberg correction. Comparing within a target map
> rather than within a model holds constant how predictable each map is: because
> the motor contrast is the least predictable target, a model trained on it
> predicts other contrasts' maps better than its own, and a within-model
> comparison would misreport that as a failure of specificity.

**Figure captions (Figs. 2 and 3), replace the specificity sentence with:**

> Prediction is task-specific. For each target contrast, the model trained on
> that contrast predicted it better than any model trained on another contrast
> (all 40 comparisons per analysis, p_FDR ≤ 0.0002). Upper panels show absolute
> accuracy; lower panels show the same values with each target's across-model
> mean subtracted, so that only specificity remains. Circled points mark each
> model's own target. Full pairwise statistics are in Table S2.

**Note:** the matrix figure is withdrawn; Table S2 is
`data/results/*_specificity_table.tsv`.

---

## Decision 3 — the contrast count and the clustering rescaling

**Where:** *SI Methods*, "Representational similarity analysis and hierarchical
clustering".

**Find:** "…we extracted the voxelwise beta values for each contrast across the
DLPFC of both hemispheres and then, for every possible pair of contrasts,
calculated the Pearson correlation…"

**Replace with:**

> …we extracted the mean beta value within each of the 26 DLPFC parcels for each
> of the 31 contrasts that were not simple task-versus-baseline comparisons,
> averaged across participants, and calculated the Pearson correlation between
> every pair of contrasts across parcels.

**And, after "displayed as a dendrogram using scipy.cluster.hierarchy package in
python 3.8", add:**

> Before clustering, correlations were rescaled from [−1, 1] to [0, 1]. This
> rescaling is not cosmetic: it halves the distances entering the linkage, and
> the threshold of 1.0 reported below yields five clusters with it and eight
> without.

**Also update in the main text** (*Materials and Methods*, "Functional profiles
of the adult DLPFC"): "we used 22 contrasts that were not simple
task-versus-baseline comparisons" → **31 contrasts**.

---

## Decision 5 — qualifying "present at birth"

**Where:** *Results*, heading and opening of the section currently titled "Most
of the adult, functionally relevant connectivity structure is present at birth".

**Suggested heading:**

> Most functionally relevant connectivity is present at birth, but not equally
> for every contrast

**Add to that section:**

> Prediction from neonatal connectivity reached a median of 90% of the accuracy
> obtained from adult connectivity (range 57–99%). For the emotion contrast in
> both hemispheres and working memory in the right hemisphere, the difference
> from adult prediction was not significant and the confidence interval on the
> ratio included 100%, so neonatal connectivity supported prediction
> indistinguishable from that of adults. The shortfall was largest for language
> (74% left, 84% right) and motor (71% left, 57% right).

**And in the Discussion:**

> The contrasts differ in how completely their functionally relevant
> connectivity is established at birth. Emotion and working memory were
> predicted from neonatal connectivity almost as well as from adult
> connectivity, whereas language showed the largest shortfall — consistent with
> a longer postnatal trajectory for the connectivity that distinguishes
> language-responsive prefrontal cortex, though the present design cannot test
> that directly.

**Caveat to add where the ratio is first reported:**

> This ratio compares two prediction accuracies rather than measuring
> connectivity maturity directly, and is bounded by the accuracy achievable in
> adults (r = 0.28–0.51 for the group-average map); measurement noise
> contributes to both terms.
