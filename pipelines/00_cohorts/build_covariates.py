"""Assemble the neonatal covariate table from the dHCP release.

The dHCP splits its metadata: `participants.tsv` at the release root holds
birth variables, and age at scan lives in a per-subject `sessions.tsv`. This
script joins them into one table keyed by subject, for `sti scan-age`.

    python pipelines/00_cohorts/build_covariates.py \
        --release /dhcp/dhcp_dmri_pipeline -o config/neonatal_covariates.tsv

Motion is not in the release as a data file, but it is recoverable: each
session's `_qc.pdf` is generated from eddy and its page 2 carries the motion
summary. Extract it first with `extract_motion.py`, then pass the result to
`--motion` here.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def _read_motion(path: Path) -> dict:
    """Motion metrics keyed by subject, from extract_motion.py."""
    out = {}
    with open(path) as f:
        for row in csv.DictReader(f, delimiter="\t"):
            sub = row["participant_id"].replace("sub-", "")
            out.setdefault(sub, row)   # first session, matching the choice below
    return out


def build(release: Path, motion: Path | None = None) -> list[dict]:
    participants = {}
    with open(release / "participants.tsv") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            pid = (row.get("participant_id") or row.get("pparticipant_id") or "").strip()
            if pid:
                participants[pid.replace("sub-", "")] = row

    motion_by_subject = _read_motion(motion) if motion else {}
    rows, multi = [], []
    for sess_file in sorted(release.glob("sub-*/sub-*_sessions.tsv")):
        subject = sess_file.parent.name.replace("sub-", "")
        with open(sess_file) as f:
            sessions = list(csv.DictReader(f, delimiter="\t"))
        if not sessions:
            continue
        if len(sessions) > 1:
            multi.append((subject, len(sessions)))
            # one session per infant: take the earliest scan, deterministically
            sessions.sort(key=lambda s: float(s.get("scan_age") or "inf"))
        s = sessions[0]
        p = participants.get(subject, {})
        rows.append({
            "participant_id": subject,
            "session_id": s.get("session_id", ""),
            "scan_age": s.get("scan_age", ""),
            "birth_age": p.get("birth_age", ""),
            "birth_weight": p.get("birth_weight", ""),
            "gender": p.get("gender", ""),
            "singleton": p.get("singleton", ""),
            "scan_head_circumference": s.get("scan_head_circumference", ""),
            "radiology_score": s.get("radiology_score", ""),
            "sedation": s.get("sedation", ""),
            "n_sessions": len(sessions),
        })
        mot = motion_by_subject.get(subject, {})
        rows[-1].update({
            # eddy's average relative motion is the volume-to-volume
            # displacement -- the diffusion analogue of framewise displacement
            "mean_fd": mot.get("rel_motion", ""),
            "abs_motion": mot.get("abs_motion", ""),
            "outliers_pct": mot.get("outliers_pct", ""),
            "snr_b0": mot.get("snr_b0", ""),
        })
    if multi:
        print(f"note: {len(multi)} subjects have >1 session; used the earliest scan")
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--release", default="/dhcp/dhcp_dmri_pipeline", type=Path)
    ap.add_argument("-o", "--output", default="config/neonatal_covariates.tsv", type=Path)
    ap.add_argument("--motion", type=Path, default=None,
                    help="TSV from extract_motion.py, merged on subject ID")
    args = ap.parse_args()

    rows = build(args.release, args.motion)
    if not rows:
        raise SystemExit(f"no sessions.tsv found under {args.release}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter="\t")
        w.writeheader()
        w.writerows(rows)
    have_age = sum(1 for r in rows if r["scan_age"])
    have_fd = sum(1 for r in rows if r.get("mean_fd"))
    print(f"wrote {args.output}: {len(rows)} subjects, {have_age} with scan_age, "
          f"{have_fd} with mean_fd")


if __name__ == "__main__":
    main()
