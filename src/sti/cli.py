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
    res, _ = adult_loo(conn, acts, list(adults.subjects), config=cfg)
    res.to_csv(_out(args.output), index=False)
    print(f"wrote {args.output} ({len(res)} rows)")
    return 0


def cmd_adult_average(args) -> int:
    from sti.evaluate import adult_group_mean_loo

    cfg, adults, conn, acts, _ = _load_inputs(args)
    res, _ = adult_group_mean_loo(conn, acts, list(adults.subjects), config=cfg)
    res.to_csv(_out(args.output), index=False)
    print(f"wrote {args.output} ({len(res)} rows)")
    return 0


def cmd_neonatal(args) -> int:
    from sti.evaluate import neonatal

    cfg, adults, conn, acts, (neos, nconn) = _load_inputs(args, neonatal=True)
    res, _ = neonatal(conn, nconn, acts, list(neos.subjects), config=cfg)
    res.to_csv(_out(args.output), index=False)
    print(f"wrote {args.output} ({len(res)} rows, {neos.n} neonates)")
    return 0


def cmd_spatial_null(args) -> int:
    from sti.datasets import load_activation
    from sti.spatial_null import SurrogateMaps, null_correlations, p_spin
    from sti.surface import distance_matrix

    cfg = Config(alpha=args.alpha, l1_ratio=args.l1_ratio)
    res = pd.read_csv(args.results)
    rows = []
    for hemi in sorted(res.hemi.unique()):
        gen = SurrogateMaps(distance_matrix(hemi, cfg), seed=args.seed)
        for task in sorted(res.task.unique()):
            obs_r = res[(res.hemi == hemi) & (res.task == task) &
                        (res.comparison_task == task)]["pearson"].mean()
            act = load_activation(task, args.n_adults, config=cfg).zscored()[hemi].mean(axis=0)
            surr = gen.generate(act, args.n_surrogates)
            # correlate the group-average observed map against its own surrogates,
            # scaled to the observed accuracy: the null asks how large an r this
            # much spatial smoothness alone can produce
            null = null_correlations(act, act, surr)
            rows.append({"hemi": hemi, "task": task, "observed_r": obs_r,
                         "null_mean": float(null.mean()), "null_sd": float(null.std()),
                         "p_spin": p_spin(obs_r, null), "n_surrogates": args.n_surrogates})
            log.info("spatial null done: %s %s", hemi, task)
    out = pd.DataFrame(rows)
    out.to_csv(_out(args.output), index=False)
    print(out.round(4).to_string(index=False))
    print(f"\nwrote {args.output}")
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
        s.set_defaults(func=fn)

    s = sub.add_parser("neonatal", help="adult models applied to neonates (Fig. 3)")
    s.add_argument("--cohort", default="adults_analysis")
    s.add_argument("--neonates", default="neonates_batch2")
    s.add_argument("-o", "--output", default="data/results/neonatal.csv")
    s.set_defaults(func=cmd_neonatal)

    s = sub.add_parser("spatial-null", help="variogram-matched spatial null (Fig. S8)")
    s.add_argument("--results", required=True)
    s.add_argument("--n-surrogates", type=int, default=1000)
    s.add_argument("--n-adults", type=int, default=155)
    s.add_argument("--seed", type=int, default=0)
    s.add_argument("-o", "--output", default="data/results/spatial_null.csv")
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
