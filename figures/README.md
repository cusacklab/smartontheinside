# Figures

Every figure in the manuscript and SI, what produces it, and where it currently
stands. Regenerate everything in `manuscript/` with the commands listed; the
other two directories are reference material that this repository does not
produce.

## Main text

| Figure | Content | Produced by | Status |
|---|---|---|---|
| Fig. 1 | Overview schematic | Hand-drawn — no code | **Not in this repo** |
| Fig. 2 | Adult, own activation | `sti adult-loo` → `sti figures` | `manuscript/Fig2_adult_own_activation_*` |
| Fig. 3 | Neonatal prediction | `sti neonatal` → `sti figures` | `manuscript/Fig3_neonatal_*` |
| Fig. 4 | Neonatal vs adult accuracy, + % of adult | `sti compare --figures` | `manuscript/Fig4_neonate_vs_adult.png` |

## SI

| Figure | Content | Produced by | Status |
|---|---|---|---|
| Fig. S1 | Transformation schematic | Hand-drawn — no code | **Not in this repo** |
| Fig. S2 | Example adult→neonatal registration | `pipelines/05_neonatal_registration` output | Regenerate from pipeline |
| Fig. S3 | Representational similarity matrix | `sti contrasts --figures` | `manuscript/S3_similarity_matrix.png` |
| Fig. S4 | Hierarchical clustering | `sti contrasts --figures` | `manuscript/S4_dendrogram.png` |
| Fig. S5 | DLPFC parcel activation profiles | `sti contrasts --figures` | `manuscript/S5_parcel_profiles.png` |
| Fig. S6 | Hyperparameter grid | `sti hyperparams` → `plot_hyperparameter_grid` | `manuscript/S6_hyperparameter_grid.png` |
| Fig. S7 | Adult, group-average map | `sti adult-average` → `sti figures` | `manuscript/S7_adult_group_average_*` |
| Fig. S8 | Spatial null | `sti spatial-null --figures` | `manuscript/S8_spatial_null_*.png` (10) |
| Fig. S9 | Accuracy vs age at scan | `sti scan-age --figures` | `manuscript/S9_scan_age.png` |
| Table S1 | The 26 DLPFC parcels | `pipelines/02_rois/make_table_s1.py` | `data/results/table_S1_*.tsv` |

## Directories

**`manuscript/`** — current figures, regenerated from the analyses in
`data/results/`. Each is reproducible from the command in the tables above.

**`upstream_docker_hcp/`** — the *original* renderings of Figs. S3 and S4, from
the `docker-hcp` repository, kept only to compare against the current versions.
That stage is now integrated: see `pipelines/01_contrast_selection/` and run
`sti contrasts --figures`.

Two of these are worth knowing about. `rdmnoneg.png` is **blank** — axis labels
and no matrix, because `plt.imshow(rdm)` is commented out in the original script.
`rdm.png` shows all **86** contrasts including the negative ones, not the 31 the
analysis actually uses. So neither is the figure the SI describes.

**`superseded/`** — the figures that were in the repository root before the 2026
restructure (`matrix_*.png`). They were produced by `legacy/classifier_check_res.py`
from the 183-neonate analysis and are **superseded** by the `neonatal_N325_*`
figures. Kept for comparison with the current manuscript draft; do not reuse.

## Naming

Files are named for the figure they become: `Fig2_`, `Fig3_`, `Fig4_` for the
main text and `S3_`–`S9_` for the SI, so a filename maps to a manuscript slot
without cross-referencing this table.

The numbers live in one place, `sti.config.FIGURES`, rather than scattered
through the CLI — figure numbers move during review, and a renumber should be a
one-line edit per figure that cannot leave the filenames inconsistent with each
other.

Following the authors' decision, the neonatal-vs-adult comparison is Fig. 4 and
the adult group-average panel moved to S7 — a straight swap of those two slots,
leaving S3–S6 and S8–S9 untouched.

## The specificity heatmap is not part of the figure set

`sti figures` writes the line panel only. The heatmap is available behind
`--matrix`, but it is deliberately not produced by default: showing the same
data twice in two formats invites the reader to ask which is authoritative, and
the heatmap's orientation is the row-wise confound the line panel exists to
avoid.

The exact statistics that a heatmap could only approximate are written instead as
a supplementary table, `data/results/<prefix>_specificity_table.tsv`: one row per
(hemisphere, target map, competing model), giving the matched model's accuracy,
the rival's, their difference, a 95% interval and an FDR-corrected p. Across all
three analyses every one of the 120 comparisons favours the matched model
(largest p_FDR = 0.0002; smallest margin r = 0.018).

## Everything is now reproducible here

The only figures this repository does not produce are Fig. 1 and Fig. S1, which
are hand-drawn schematics, and Fig. S2, which is an example registration from
`pipelines/05_neonatal_registration`.

Regenerate the rest with:

```bash
sti contrasts --figures                                  # S3, S4, S5
sti hyperparams --grid data/cache/grid                   # S6
sti figures --results data/results/adult_loo_N155.csv     --prefix adult_loo_N155
sti figures --results data/results/neonatal_N325.csv      --prefix neonatal_N325
sti figures --results data/results/adult_average_N155.csv --prefix adult_average_N155
sti compare      --a ... --b ...                         # S7
sti spatial-null --figures ...                           # S8
sti scan-age     --figures ...                           # S9
python pipelines/02_rois/make_table_s1.py                # Table S1
```
