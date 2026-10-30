# Introduction — resubmission draft

Draft prose for the rewritten Introduction, structured around the organisers
framing agreed 2026-10-30: development leads; geometry as implemented
(distance features; the surrogate null covers smooth-map content generally);
the variance-partition ("shares") analysis is promised for Fig. 1b. Citations
are bracketed slots for checking. This is a draft to react to, not final text.

Writing constraints in force: this is a fresh submission, not a response to
the PNAS reviews — controls are presented as the paper's own inferential
standard. The fixed phrase for the claim level is **"the adult task
repertoire"**; no sentence should be readable as a claim that neonatal DLPFC
is inactive. Do not use the late emergence of visual categorisation as a
contrast [infants show visual categories in neural activity: O'Doherty …
Cusack, 2026, Nat Neurosci].

---

## ¶1 — The phenomenon, opened from development

> At term birth, a human is still years away from comprehending a story,
> months from reaching for an object, and more than a decade from the mature
> working memory of an adult. Yet in every neurotypical adult, these functions
> occupy a consistent arrangement of subregions within dorsolateral prefrontal
> cortex (DLPFC): topographies of task preference that recur, individual after
> individual, across working memory, language, social cognition, emotion and
> action [refs: HCP task battery; DLPFC parcellation/function]. Consistency on
> this scale demands a specifying mechanism. Something constrains which patch
> of prefrontal cortex comes to serve which function — and whatever it is must
> exist before the functions do. What is it, and how early is it in place?

## ¶2 — The candidate specifiers

> Three broad classes of answer are on offer. The first is *geometry*: a
> patch's fate follows from its position in the cortical sheet. Positional
> identity is established early by morphogen gradients [Rakic protomap;
> O'Leary], macroscale function is organised along smooth spatial gradients
> [Margulies 2016], and much of adult functional organisation is predictable
> from the geometry of the cortex alone [Pang et al. 2023; subsequent debate].
> The second is *extrinsic connectivity*: a patch computes what its
> connections allow, so function follows the connectional fingerprint
> [Passingham et al. 2002] — an account with causal support from rewiring
> experiments [Sur] and correlational support from studies predicting adult
> functional selectivity from connectivity [Saygin et al. 2011; Osher et al.
> 2016]. The third is *local microstructure*: cytoarchitectonic identity could
> determine both a region's connections and its eventual function, making
> connectivity a marker rather than a mechanism [Kubota et al. 2025]. These
> accounts are not exclusive, and in any adult dataset their signatures are
> correlated: connectivity is itself spatially organised, and microstructure
> varies smoothly with position. Demonstrating that any one of them predicts
> function is therefore, by itself, uninformative.

## ¶3 — The inferential standard

> The entanglement is not hypothetical. Diffusion tractography is biased
> toward nearby targets, so a vertex's tractography profile partly encodes
> its position; and group-average activation maps are spatially smooth, so a
> model needs little more than position to approximate them. A
> connectivity-based prediction of function can therefore succeed as a
> re-description of geometry [cf. Donahue et al. 2016; Pang et al. 2023].
> Every claim in this paper accordingly takes the form of an *increment over
> a geometry-matched baseline*. We quantify what spatial smoothness alone
> achieves, by passing surrogate maps with matched spatial autocorrelation
> through our entire analysis pipeline; what explicit geometry achieves, with
> a model given only each vertex's distances to the rest of the brain; and
> what connectivity adds beyond both, including after the distance dependence
> of tractography is removed from its profiles. We further partition the
> adult functional map into geometric, connectional and shared components
> (Fig. 1b).

## ¶4 — Development as the lever

> These specifiers differ most sharply in *when* their information becomes
> available relative to experience. We make no claim that neonatal DLPFC is
> inactive or uncommitted: it shows organised spontaneous activity, responses
> to speech are detectable in frontal cortex even in premature neonates
> [Mahmoudzadeh 2013; Dehaene-Lambertz], attentional signals appear within
> months [Ellis], and neural activity can reveal function well before
> behaviour does — infants hold visual category information that overt
> behaviour alone would not show [O'Doherty … Cusack 2026]. Our premise is
> narrower and behavioural: the functions indexed by our five contrasts —
> instructed working memory, narrative comprehension, explicit mentalising,
> cued action selection, emotion recognition — constitute an *adult task
> repertoire* that emerges over years and matures into the second decade
> [Wellman ToM meta; Luna WM development; Gogtay 2004], and DLPFC is among
> the last cortical territories to mature by every anatomical index [Chugani
> & Phelps 1986; Huttenlocher & Dabholkar 1997; Gogtay 2004]. At term,
> essentially all of the experience of performing this repertoire lies in the
> future. Whatever precursor computations neonatal DLPFC performs, a
> specification of the repertoire's adult topography that is measurable at
> birth cannot have been installed by performing it. Connectivity-based
> proto-organisation of this kind has been demonstrated in ventral temporal
> cortex, where connectivity at age five predicts where the visual word form
> area will emerge by age eight [Saygin et al. 2016]. Here we ask the
> corresponding question at the beginning of postnatal life, for five domains
> at once, and under explicit geometric controls: is the *connectional*
> component of adult DLPFC topography — the part geometry cannot carry —
> already present in the neonatal connectome?

## ¶5 — This study and its predictions

> We studied the topography of five task activations within DLPFC in 155
> adults (Human Connectome Project) and structural connectivity in the same
> adults and in 325 term neonates (Developing Human Connectome Project),
> within a single predictive framework: identical models, targets and metrics
> throughout, so that competing accounts differ only in the information they
> are allowed. Four predictions follow from the accounts above. (P1) If
> functional topography is unconstrained smooth variation, real task maps
> should transfer from adults to neonates no better than surrogate maps of
> matched smoothness. (P2) If geometry suffices, distances alone should
> predict the maps as well as tractography does, and removing distance
> information from tractography should abolish its predictive power. (P3) If
> extrinsic connectivity contributes, it should predict adult topography
> beyond these geometric baselines, with task specificity. (P4) If that
> connectional contribution requires postnatal experience of the repertoire,
> it should be absent at birth; if it is part of the scaffold, it should be
> present. We find that geometry is a genuinely strong predictor — for the
> motor contrast, the strongest available, a result that reclassifies one of
> our own five contrasts and demonstrates that the controls discriminate —
> but that connectivity carries a function-specific increment beyond geometry
> for all five domains, and that this increment is already present, at 79 to
> 115 percent of its adult strength, in the first weeks of life.

---

## Notes for the co-author pass

- ¶1 "the functions occupy a consistent arrangement": supported by Fig. 2 as
  recaptioned (cross-subject generalisation), plus the parcel-profile ANOVA.
- ¶2 deliberately gives microstructure equal billing as a *candidate* and
  ¶3/¶5 do not promise to test it — Discussion handles it (Kubota point).
  This keeps the design's scope honest.
- ¶3 promises the shares partition (Fig. 1b): `sti shares`, in progress.
- ¶4 carries the temporal-asymmetry argument; the Saygin VWFA citation sits
  here as the nearest prior art, with the extension stated as: measurement at
  birth, five domains, geometric controls.
- ¶5's "79 to 115 percent" is the distance-regressed retention range
  (PHASE0_RESULTS §3); swap for the maturity-panel percentages if the final
  figure set leads with those instead.
- Title candidates under this framing: "Geometry and connectivity in the
  neonatal specification of prefrontal functional topography"; "The
  connectional component of adult prefrontal organisation is present at
  birth"; or keep the subtitle form: "The structural connectivity that
  distinguishes adult prefrontal subregions is present in neonates" with the
  geometry work carried by the abstract.
