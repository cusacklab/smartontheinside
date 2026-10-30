"""Generate Table S1: the DLPFC parcels, with their Glasser labels.

The SI lists this as `[TBD: list labels]`. The labels are in the parcellation
files, so the table is generated rather than transcribed.

    python pipelines/02_rois/make_table_s1.py -o data/results/table_S1_dlpfc_parcels.tsv
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from sti.config import DLPFC_PARCELS, DEFAULT_CONFIG, N_SEED_VERTICES  # noqa: E402


def main() -> None:
    import nibabel as nib
    import numpy as np

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-o", "--output", default="data/results/table_S1_dlpfc_parcels.tsv")
    args = ap.parse_args()

    parc = DEFAULT_CONFIG.data_dir / "parcellations"
    rows = []
    for hemi in ("L", "R"):
        img = nib.load(str(parc / f"ff.{hemi}.label.gii"))
        names = img.labeltable.get_labels_as_dict()
        data = img.agg_data("NIFTI_INTENT_LABEL")
        for index in DLPFC_PARCELS[hemi]:
            label = names.get(index, "")
            rows.append({
                "hemisphere": hemi,
                "label_index": index,
                "label_name": label,
                # strip the prefix/suffix, not every occurrence: a plain replace
                # turns "L_SFL_ROI" into "SFROI"
                "area": label.removeprefix(f"{hemi}_").removesuffix("_ROI"),
                "n_vertices": int(np.sum(data == index)),
            })

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter="\t")
        w.writeheader()
        w.writerows(rows)

    for hemi in ("L", "R"):
        total = sum(r["n_vertices"] for r in rows if r["hemisphere"] == hemi)
        assert total == N_SEED_VERTICES[hemi], (
            f"{hemi}: parcel vertices sum to {total}, expected {N_SEED_VERTICES[hemi]}"
        )
    print(f"wrote {out}: {len(rows)} parcels "
          f"({len(rows)//2} per hemisphere), vertex counts match the data arrays")


if __name__ == "__main__":
    main()
