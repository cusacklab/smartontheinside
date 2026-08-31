"""Extract eddy motion metrics from the dHCP per-session QC reports.

The dHCP diffusion release does not publish eddy's ``.eddy_movement_rms`` files,
but it does ship a per-session ``_qc.pdf`` whose first page tabulates the summary
eddy produced. ``Average rel. motion`` is the volume-to-volume displacement --
the eddy analogue of framewise displacement, and the motion covariate the
manuscript specifies.

    python pipelines/00_cohorts/extract_motion.py \
        --release /dhcp/dhcp_dmri_pipeline -o config/neonatal_motion.tsv

Requires ``pdftotext`` (poppler-utils). Roughly 0.2 s per subject.
"""

from __future__ import annotations

import argparse
import csv
import re
import subprocess
from pathlib import Path

#: Output column -> the label as it appears in the QC report.
METRICS = {
    "abs_motion": r"Average abs\. motion \(mm\)",
    "rel_motion": r"Average rel\. motion \(mm\)",
    "outliers_pct": r"Total outliers \(%\)",
    "snr_b0": r"Average SNR \(b=0",
}


def parse_qc(pdf: Path) -> dict:
    """Pull the eddy summary metrics off the first page of a QC report."""
    # Page 1 is blank; the summary table is on page 2. -layout keeps each label on
    # the same line as its value -- without it labels and numbers arrive as two
    # separate blocks and cannot be paired
    out = subprocess.run(["pdftotext", "-layout", "-f", "1", "-l", "2", str(pdf), "-"],
                         capture_output=True, text=True, timeout=120)
    if out.returncode != 0:
        raise RuntimeError(f"pdftotext failed on {pdf.name}: {out.stderr.strip()[:120]}")
    text = out.stdout
    values = {}
    for key, label in METRICS.items():
        m = re.search(label + r"[^\n]*?(-?\d+\.\d+)", text)
        values[key] = float(m.group(1)) if m else ""
    return values


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--release", default="/dhcp/dhcp_dmri_pipeline", type=Path)
    ap.add_argument("--subjects", type=Path, default=None,
                    help="restrict to the subject IDs in this file, one per line")
    ap.add_argument("-o", "--output", default="config/neonatal_motion.tsv", type=Path)
    args = ap.parse_args()

    wanted = None
    if args.subjects:
        wanted = {l.strip().replace("sub-", "") for l in args.subjects.read_text().splitlines()
                  if l.strip() and not l.startswith("#")}

    rows, failed = [], []
    for pdf in sorted(args.release.glob("sub-*/ses-*/sub-*_qc.pdf")):
        subject = pdf.parent.parent.name.replace("sub-", "")
        if wanted is not None and subject not in wanted:
            continue
        session = pdf.parent.name.replace("ses-", "")
        try:
            rows.append({"participant_id": subject, "session_id": session, **parse_qc(pdf)})
        except Exception as exc:  # noqa: BLE001 - reported, not swallowed
            failed.append((subject, str(exc)[:80]))

    if not rows:
        raise SystemExit(f"no QC reports parsed under {args.release}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter="\t")
        w.writeheader()
        w.writerows(rows)

    have = sum(1 for r in rows if r["rel_motion"] != "")
    print(f"wrote {args.output}: {len(rows)} sessions, {have} with rel_motion")
    if failed:
        print(f"failed on {len(failed)}: {failed[:3]}")


if __name__ == "__main__":
    main()
