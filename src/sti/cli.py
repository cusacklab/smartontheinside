"""Command-line entry points.

Each analysis in the paper is one subcommand, so a run is a recorded command
rather than a file edited to flip ``infants = 1``. Results are written as tidy
CSVs that the figure commands consume.

    sti hyperparams   --grid data/cache/grid
    sti adult-loo     --cohort adults_analysis
    sti adult-average --cohort adults_analysis
    sti neonatal      --neonates neonates_batch2
    sti spatial-null  --results results/neonatal.csv
    sti scan-age      --results results/neonatal.csv --extra config/sessions.tsv
    sti compare       --a results/neonatal.csv --b results/adult_average.csv
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from sti.config import Config, TASKS

log = logging.getLogger("sti")


def _shard(args):
    """Which models to train and which hemispheres, for one cluster shard."""
    tasks = [t.strip() for t in args.tasks.split(",")] if args.tasks else None
    if tasks:
        unknown = [t for t in tasks if t not in TASKS]
        if unknown:
            raise SystemExit(f"unknown task(s) {unknown}; choose from {sorted(TASKS)}")
    hemis = tuple(args.hemi.split(",")) if args.hemi else ("L", "R")
    return tasks, hemis


def _out(path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def _load_inputs(args, *, neonatal: bool = False):
    from sti.cohorts import load_cohort
    from sti.datasets import load_all_activations, load_connectivity

    cfg = Config(alpha=args.alpha, l1_ratio=args.l1_ratio)
    adults = load_cohort(args.cohort, cfg)
    acts = load_all_activations(TASKS, adults.n, config=cfg)
    conn = load_connectivity(adults.n, config=cfg)
    if not neonatal:
        return cfg, adults, conn, acts, None
    neos = load_cohort(args.neonates, cfg)
    nconn = load_connectivity(neos.n, neonatal=True, config=cfg)
    return cfg, adults, conn, acts, (neos, nconn)


def cmd_hyperparams(args) -> int:
    from sti.hyperparams import load_grid, methods_sentence, rank_of, ridge_summary, select

    grid = load_grid(args.grid)
    print(f"grid cells: {len(grid)}")
    print("\nbest by mean within-task Pearson:", select(grid))
    print("best by mean R2:                 ", select(grid, metric="mean_score"))
    print(f"\ntop cells (note the near-constant l1_penalty = alpha x l1_ratio):")
    print(ridge_summary(grid).round(4).to_string(index=False))
    r = rank_of(grid, args.alpha, args.l1_ratio)
    print(f"\npublished choice alpha={args.alpha:g}, l1_ratio={args.l1_ratio:g}: "
          f"rank {r['rank']}/{r['n_cells']}, {r['shortfall']:+.5f} from optimum")
    print("\n--- Methods sentence ---\n" + methods_sentence(grid, args.alpha, args.l1_ratio))
    if args.output:
        grid.to_csv(_out(args.output), index=False)
        print(f"\nwrote {args.output}")
    return 0


def cmd_adult_loo(args) -> int:
    from sti.evaluate import adult_loo

    cfg, adults, conn, acts, _ = _load_inputs(args)
    tasks, hemis = _shard(args)
    res, _ = adult_loo(conn, acts, list(adults.subjects), config=cfg,
                       hemispheres=hemis, model_tasks=tasks)
    res.to_csv(_out(args.output), index=False)
    print(f"wrote {args.output} ({len(res)} rows)")
    return 0


def cmd_adult_average(args) -> int:
    from sti.evaluate import adult_group_mean_loo

    cfg, adults, conn, acts, _ = _load_inputs(args)
    tasks, hemis = _shard(args)
    res, _ = adult_group_mean_loo(conn, acts, list(adults.subjects), config=cfg,
                                  hemispheres=hemis, model_tasks=tasks)
    res.to_csv(_out(args.output), index=False)
    print(f"wrote {args.output} ({len(res)} rows)")
    return 0


def cmd_neonatal(args) -> int:
    from sti.cohorts import load_cohort
    from sti.datasets import load_all_activations, load_connectivity, load_connectivity_file
    from sti.evaluate import neonatal

    cfg = Config(alpha=args.alpha, l1_ratio=args.l1_ratio)
    adults = load_cohort(args.cohort, cfg)
    acts = load_all_activations(TASKS, adults.n, config=cfg)
    conn = load_connectivity(adults.n, config=cfg)

    if args.connectivity:
        # explicit array + its subject sidecar: the array's subjects are the
        # truth, not the cohort file, because they can legitimately differ
        nconn, subjects = load_connectivity_file(args.connectivity)
        if subjects is None:
            cohort = load_cohort(args.neonates, cfg)
            if cohort.n != nconn.n_subjects:
                log.error(
                    "%s has %d subjects but cohort %s has %d, and no .subjects.txt "
                    "sidecar is present to resolve which rows are which.",
                    args.connectivity, nconn.n_subjects, args.neonates, cohort.n)
                return 1
            subjects = list(cohort.subjects)
    else:
        cohort = load_cohort(args.neonates, cfg)
        nconn = load_connectivity(cohort.n, neonatal=True, config=cfg)
        subjects = list(cohort.subjects)

    tasks, hemis = _shard(args)
    res, preds = neonatal(conn, nconn, acts, subjects, config=cfg,
                          hemispheres=hemis, model_tasks=tasks)
    res.to_csv(_out(args.output), index=False)
    print(f"wrote {args.output} ({len(res)} rows, {nconn.n_subjects} neonates)")
    if args.save_predictions:
        import numpy as np
        out = _out(args.save_predictions)
        np.savez_compressed(
            out, **{f"{t}__{h}": v for (t, h), v in preds.values.items()},
            subjects=np.array(subjects))
        print(f"wrote {out} (predicted maps, needed by `sti spatial-null`)")
    return 0


def cmd_spatial_null(args) -> int:
    """Is the observed accuracy larger than spatial autocorrelation alone allows?"""
    import numpy as np

    from sti.datasets import load_activation
    from sti.spatial_null import SurrogateMaps, group_null_distribution, p_spin
    from sti.surface import distance_matrix

    cfg = Config(alpha=args.alpha, l1_ratio=args.l1_ratio)
    res = pd.read_csv(args.results)
    preds = np.load(args.predictions, allow_pickle=True)

    rows, null_dists = [], {}
    for hemi in sorted(res.hemi.unique()):
        gen = SurrogateMaps(distance_matrix(hemi, cfg), seed=args.seed)
        for task in sorted(res.task.unique()):
            key = f"{task}__{hemi}"
            if key not in preds:
                log.warning("no predictions for %s; skipping", key)
                continue
            observed = float(res[(res.hemi == hemi) & (res.task == task) &
                                 (res.comparison_task == task)]["pearson"].mean())
            target = load_activation(task, args.n_adults, config=cfg).zscored()[hemi].mean(axis=0)
            surr = gen.generate(target, args.n_surrogates)
            null = group_null_distribution(preds[key], surr)
            null_dists[key] = null
            rows.append({
                "hemi": hemi, "task": task, "observed_r": observed,
                "null_mean": float(null.mean()), "null_sd": float(null.std()),
                "null_p95": float(np.percentile(null, 95)),
                "p_spin": p_spin(observed, null),
                "n_surrogates": args.n_surrogates, "n_subjects": preds[key].shape[0],
            })
            log.info("spatial null done: %s %s  observed=%.3f p=%.4f",
                     hemi, task, observed, rows[-1]["p_spin"])

    out = pd.DataFrame(rows)
    if not out.empty:
        from sti.stats import fdr_bh, stars
        out["p_fdr"] = fdr_bh(out["p_spin"].to_numpy())
        out["stars"] = out["p_fdr"].map(stars)
    out.to_csv(_out(args.output), index=False)
    print(out.round(4).to_string(index=False))
    print(f"\nwrote {args.output}")

    if args.save_null and null_dists:
        # the full distributions, so Fig. S8 can be redrawn without recomputing
        np.savez_compressed(_out(args.save_null), **null_dists)
        print(f"wrote {args.save_null} (null distributions)")
    if args.figures and null_dists:
        from sti import plotting as P
        for key, null in null_dists.items():
            task, hemi = key.split("__")
            r = out[(out.hemi == hemi) & (out.task == task)].iloc[0]
            fig = P.plot_spatial_null(
                r.observed_r, null, p=r.p_spin,
                title=f"{task.replace('tfMRI_', '')} {hemi}")
            print(f"wrote {P.save(fig, f'spatial_null_{task}_{hemi}', cfg)}")
    return 0


def cmd_scan_age(args) -> int:
    from sti.scan_age import load_covariates, per_task_scan_age, scan_age_regression

    cfg = Config()
    res = pd.read_csv(args.results)
    cov = load_covariates(cfg, extra=Path(args.extra) if args.extra else None)
    table, model = scan_age_regression(res, cov)
    print(f"n = {table.attrs['n']}, R2 = {table.attrs['r_squared']:.3f}\n")
    print(table.round(4).to_string(index=False))
    print("\nper task:")
    print(per_task_scan_age(res, cov).round(4).to_string(index=False))
    if args.output:
        table.to_csv(_out(args.output), index=False)
        print(f"\nwrote {args.output}")
    return 0


def cmd_compare(args) -> int:
    from sti.stats import compare_protocols

    a, b = pd.read_csv(args.a), pd.read_csv(args.b)
    out = compare_protocols(a, b)
    print(out.round(4).to_string(index=False))
    if args.output:
        out.to_csv(_out(args.output), index=False)
        print(f"\nwrote {args.output}")
    return 0


def cmd_build_connectivity(args) -> int:
    """Aggregate per-subject tractography into a cohort connectivity array."""
    import numpy as np

    from sti.cohorts import load_cohort
    from sti.datasets import build_connectivity, neonatal_tractography_key, adult_tractography_key
    from sti import s3io

    cfg = Config()
    cohort = load_cohort(args.cohort, cfg)
    key_fn = neonatal_tractography_key if args.neonatal else adult_tractography_key

    subjects, missing = [], []
    for sub in cohort.subjects:
        if all(s3io.exists(key_fn(sub, h), cfg) for h in ("L", "R")):
            subjects.append(sub)
        else:
            missing.append(sub)
    if missing:
        msg = f"{len(missing)} of {cohort.n} subjects lack tractography: {missing[:10]}"
        if not args.allow_missing:
            log.error("%s. Pass --allow-missing to build from the rest.", msg)
            return 1
        log.warning("%s -- excluded", msg)

    data = {h: build_connectivity(subjects, h, neonatal=args.neonatal, config=cfg)
            for h in ("L", "R")}
    out = _out(args.output)
    np.save(out, data, allow_pickle=True)
    # record which subjects are in the array, in order -- the arrays carry no IDs
    sidecar = out.with_suffix(".subjects.txt")
    sidecar.write_text("\n".join(subjects) + "\n")
    print(f"wrote {out} ({len(subjects)} subjects; "
          f"L{data['L'].shape} R{data['R'].shape})")
    print(f"wrote {sidecar}")
    if missing:
        print(f"excluded {len(missing)}: {', '.join(missing)}")
    return 0


def cmd_figures(args) -> int:
    """Render the accuracy and task-specificity figures for a results CSV."""
    from sti import plotting as P
    from sti.stats import specificity_tests

    cfg = Config()
    res = pd.read_csv(args.results)
    prefix = args.prefix or Path(args.results).stem

    # Both orientations. The row test is the manuscript's comparison; the column
    # test holds the target map fixed and so is not confounded by how predictable
    # each map is. Stars on the figure come from the column test.
    tests = {
        axis: specificity_tests(res, n_boot=args.n_boot, seed=args.seed, axis=axis)
        for axis in ("row", "column")
    }
    outs = [
        P.save(P.plot_accuracy(res, title=args.title), f"{prefix}_accuracy", cfg),
        P.save(P.plot_specificity_matrix(res, tests=tests["column"], title=args.title),
               f"{prefix}_specificity", cfg),
    ]
    for o in outs:
        print(f"wrote {o}")
    for axis, t in tests.items():
        csv = _out(Path(args.results).with_name(f"{prefix}_specificity_{axis}.csv"))
        t.to_csv(csv, index=False)
        ok = int(((t.difference > 0) & (t.p_fdr < 0.05)).sum())
        print(f"wrote {csv}  ({ok}/{len(t)} with the diagonal significantly higher)")

    within = res[res.task == res.comparison_task]
    print("\nmean within-task accuracy (r):")
    print(within.groupby(["hemi", "task"])["pearson"].agg(["mean", "std", "count"])
          .round(4).to_string())
    return 0


def cmd_merge(args) -> int:
    """Concatenate result shards from a cluster run into one table."""
    import glob

    paths = sorted(p for pat in args.inputs for p in glob.glob(pat))
    if not paths:
        raise SystemExit(f"no files matched {args.inputs}")
    frames = [pd.read_csv(p) for p in paths]
    out = pd.concat(frames, ignore_index=True)

    key = ["protocol", "task", "comparison_task", "hemi", "subject"]
    key = [c for c in key if c in out.columns]
    dupes = int(out.duplicated(subset=key).sum())
    if dupes:
        log.warning("%d duplicate rows across shards; keeping the first of each", dupes)
        out = out.drop_duplicates(subset=key, keep="first")

    out.to_csv(_out(args.output), index=False)
    print(f"merged {len(paths)} shards -> {args.output} ({len(out)} rows)")
    if {"task", "hemi"} <= set(out.columns):
        got = out.groupby(["hemi", "task"]).size()
        print(f"  {out.hemi.nunique()} hemispheres x {out.task.nunique()} model tasks, "
              f"{out.subject.nunique()} subjects")
        missing = [f"{h}/{t}" for h in sorted(out.hemi.unique()) for t in sorted(TASKS)
                   if (h, t) not in got.index]
        if missing:
            log.warning("no rows for: %s -- a shard may have failed", ", ".join(missing))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="sti", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("-v", "--verbose", action="store_true")
    p.add_argument("--alpha", type=float, default=0.4)
    p.add_argument("--l1-ratio", dest="l1_ratio", type=float, default=0.6)
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("hyperparams", help="select hyperparameters from the stored grid")
    s.add_argument("--grid", default="data/cache/grid")
    s.add_argument("-o", "--output", default=None)
    s.set_defaults(func=cmd_hyperparams)

    for name, fn, helptext in [
        ("adult-loo", cmd_adult_loo, "leave-one-adult-out, own activation (Fig. 2)"),
        ("adult-average", cmd_adult_average, "leave-one-adult-out, group average (Fig. 4)"),
    ]:
        s = sub.add_parser(name, help=helptext)
        s.add_argument("--cohort", default="adults_analysis")
        s.add_argument("-o", "--output", default=f"data/results/{name.replace('-', '_')}.csv")
        s.add_argument("--tasks", default=None,
                       help="comma-separated model tasks for this shard (default: all)")
        s.add_argument("--hemi", default=None, help="L, R, or L,R (default: both)")
        s.set_defaults(func=fn)

    s = sub.add_parser("neonatal", help="adult models applied to neonates (Fig. 3)")
    s.add_argument("--cohort", default="adults_analysis")
    s.add_argument("--neonates", default="neonates_batch2")
    s.add_argument("--connectivity", default=None,
                   help="explicit connectivity array; its .subjects.txt sidecar "
                        "names the rows, overriding --neonates")
    s.add_argument("-o", "--output", default="data/results/neonatal.csv")
    s.add_argument("--save-predictions", default=None,
                   help="npz of predicted maps; required for `sti spatial-null`")
    s.add_argument("--tasks", default=None,
                   help="comma-separated model tasks for this shard (default: all)")
    s.add_argument("--hemi", default=None, help="L, R, or L,R (default: both)")
    s.set_defaults(func=cmd_neonatal)

    s = sub.add_parser("spatial-null", help="variogram-matched spatial null (Fig. S8)")
    s.add_argument("--results", required=True)
    s.add_argument("--predictions", required=True,
                   help="npz from `sti neonatal --save-predictions`")
    s.add_argument("--n-surrogates", type=int, default=1000)
    s.add_argument("--n-adults", type=int, default=155)
    s.add_argument("--seed", type=int, default=0)
    s.add_argument("-o", "--output", default="data/results/spatial_null.csv")
    s.add_argument("--save-null", default=None,
                   help="npz of the full null distributions, for redrawing Fig. S8")
    s.add_argument("--figures", action="store_true",
                   help="also render one null histogram per task and hemisphere")
    s.set_defaults(func=cmd_spatial_null)

    s = sub.add_parser("scan-age", help="accuracy vs postmenstrual age at scan (Fig. S9)")
    s.add_argument("--results", required=True)
    s.add_argument("--extra", default=None, help="TSV supplying scan_age and mean_fd")
    s.add_argument("-o", "--output", default=None)
    s.set_defaults(func=cmd_scan_age)

    s = sub.add_parser("compare", help="neonatal vs adult accuracy (Fig. S7)")
    s.add_argument("--a", required=True)
    s.add_argument("--b", required=True)
    s.add_argument("-o", "--output", default=None)
    s.set_defaults(func=cmd_compare)

    s = sub.add_parser("build-connectivity",
                       help="aggregate per-subject tractography into a cohort array")
    s.add_argument("--cohort", required=True)
    s.add_argument("--neonatal", action="store_true", default=True)
    s.add_argument("--adult", dest="neonatal", action="store_false")
    s.add_argument("--allow-missing", action="store_true",
                   help="build from the available subjects instead of failing")
    s.add_argument("-o", "--output", required=True)
    s.set_defaults(func=cmd_build_connectivity)

    s = sub.add_parser("figures", help="render accuracy and specificity figures")
    s.add_argument("--results", required=True)
    s.add_argument("--prefix", default=None)
    s.add_argument("--title", default="")
    s.add_argument("--n-boot", type=int, default=10000)
    s.add_argument("--seed", type=int, default=0)
    s.set_defaults(func=cmd_figures)

    s = sub.add_parser("merge", help="concatenate result shards from a cluster run")
    s.add_argument("--inputs", nargs="+", required=True, help="paths or globs")
    s.add_argument("-o", "--output", required=True)
    s.set_defaults(func=cmd_merge)

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S",
    )
    try:
        return args.func(args)
    except Exception as exc:  # noqa: BLE001 - CLI boundary
        log.error("%s: %s", type(exc).__name__, exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
