# Legacy scripts

The original analysis scripts, kept for provenance. **Do not run these** — they
are superseded by `src/sti` and the `sti` command.

| File | Superseded by |
|------|---------------|
| `classifier.py` | `sti.evaluate.adult_loo`, `sti.evaluate.neonatal` |
| `clclassifier_for_revisions.py` | `sti.evaluate.adult_group_mean_loo` |
| `classifier_check_res.py` | `sti.stats`, `sti.plotting` |
| `classifier_check_res_for_revisions.py` | `sti.stats`, `sti.plotting` |
| `classifier_check_res_hyperparameters.py` | `sti.hyperparams` |
| `plots.py` | `sti.plotting` |

They hard-code paths to `/home/chiaracaldinelli`, select the analysis by editing
`infants = 1`, and contain the defects documented in
[../docs/FINDINGS.md](../docs/FINDINGS.md) — most consequentially the duplicate
`subjlist_infants` assignment that reduced the neonatal sample from 326 to 183,
and the S3 upload that destroyed the per-task adult activation arrays.

Retained because they are what produced the results currently in the manuscript.
