# Stage 01 — contrast selection

Chooses the five representative task contrasts that every later stage uses, by
clustering the 31 non-negative HCP contrasts on the similarity of their DLPFC
activation patterns. Produces manuscript Figs. S3, S4 and S5.

These files came from the separate
[`rhodricusack/docker-hcp`](https://github.com/rhodricusack/docker-hcp)
repository and are vendored here for provenance. **Two very different costs live
in this stage:**

| | Cost | Status |
|---|---|---|
| Per-subject extraction of DLPFC contrast betas from the HCP | Heavy — ran on AWS ECS, one container per subject | Already run; output is `data/rois/DLPFCroi.npy` |
| The RSA, clustering and parcel profiles | Trivial — a `corrcoef` on a 31 × 26 matrix | Reimplemented in `sti.contrasts` |

So the analysis that produces the figures needs **no** cluster and **no** HCP
download: `DLPFCroi.npy` (176 subjects × 31 contrasts × 26 parcels) is the
extraction's output and is already in this repository.

## Files

`roi_extract_one_subject.py`, `Dockerfile`, `hcp_example.py`, `ecs_control.py`
— the containerised per-subject extraction and its ECS launcher. Kept for
provenance; re-running them means re-downloading the HCP task data.

`MeanSTD.py` — the original RSA/clustering script. **Superseded by
`sti contrasts`**, which fixes three defects in it:

- `plt.imshow(rdm)` is commented out (line 34), so the similarity matrix it
  saves as `rdmnoneg.png` is an empty set of axes with labels and no data;
- its DLPFC parcel list uses indices **96** and **276** where every other stage
  of the pipeline uses **97** and **277**, mislabelling two bars in Fig. S5;
- it renders a signed correlation matrix in `viridis`, a sequential map, so the
  sign of a correlation is not readable.

Run the current version with:

    sti contrasts --figures
