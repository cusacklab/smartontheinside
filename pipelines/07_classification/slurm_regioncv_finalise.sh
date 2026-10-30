#!/bin/bash
# Finalise the region-CV stack: merge every shard set, run the summaries and
# comparisons, render figures, and write a digest. Runs with
# --dependency=afterok on all the array jobs, so when it completes everything
# is on disk under data/results/regioncv/ regardless of who is watching.
#
#SBATCH --job-name=sti_rcv_final
#SBATCH --partition=high-memory
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=03:00:00
#SBATCH --output=slurm_logs/%x_%A.out
#SBATCH --error=slurm_logs/%x_%A.out

set -euo pipefail
REPO=/home/ubuntu/repos/smartontheinside
cd "$REPO"
OUT=data/results/regioncv
mkdir -p "$OUT"
export PYTHONPATH="$REPO/src"
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-4}
PY=/opt/fsl/bin/python3
DIGEST=$OUT/DIGEST.txt

{
echo "Region-CV stack finalised $(date -Is)"
echo

merge () { $PY -m sti.cli merge --inputs "data/results/shards/$1_*.csv" -o "$OUT/$2"; }

merge neonatal_regioncv            neonatal_regioncv_N325.csv
merge adult_loo_regioncv           adult_loo_regioncv_N155.csv
merge adult_average_regioncv       adult_average_regioncv_N155.csv
merge distreg_regioncv             neonatal_regioncv_distance_regressed.csv
merge pipenull_regioncv            pipeline_null_regioncv_N325.csv
merge pipenull_regressed_regioncv  pipeline_null_regressed_regioncv_N325.csv

echo; echo "=== within-task accuracy, all region-CV protocols ==="
$PY - <<'EOF'
import pandas as pd
base = "data/results/regioncv/"
for name in ["neonatal_regioncv_N325", "adult_loo_regioncv_N155",
             "adult_average_regioncv_N155", "neonatal_regioncv_distance_regressed"]:
    df = pd.read_csv(base + name + ".csv")
    w = df[df.task == df.comparison_task].groupby(["task", "hemi"])["pearson"].mean()
    print(f"\n--- {name} ---")
    print(w.round(3).to_string())
EOF

echo; echo "=== pipeline null (region-CV, raw features) vs observed ==="
$PY -m sti.cli pipeline-null --summarise "$OUT/pipeline_null_regioncv_N325.csv" \
    --results "$OUT/neonatal_regioncv_N325.csv" \
    -o "$OUT/pipeline_null_regioncv_summary.csv"

echo; echo "=== pipeline null (region-CV, distance-regressed) vs observed ==="
$PY -m sti.cli pipeline-null --summarise "$OUT/pipeline_null_regressed_regioncv_N325.csv" \
    --results "$OUT/neonatal_regioncv_distance_regressed.csv" \
    -o "$OUT/pipeline_null_regressed_regioncv_summary.csv"

echo; echo "=== neonatal vs adult ceiling (region-CV) ==="
$PY -m sti.cli compare --a "$OUT/neonatal_regioncv_N325.csv" \
    --b "$OUT/adult_average_regioncv_N155.csv" \
    -o "$OUT/compare_neonate_vs_adult_regioncv.csv"

echo; echo "=== figures and specificity tables ==="
$PY -m sti.cli figures --results "$OUT/neonatal_regioncv_N325.csv" \
    --prefix RegionCV_Fig3_neonatal --title "Neonatal (region-CV)"
$PY -m sti.cli figures --results "$OUT/adult_loo_regioncv_N155.csv" \
    --prefix RegionCV_Fig2_adult --title "Adult own map (region-CV)"
$PY -m sti.cli figures --results "$OUT/adult_average_regioncv_N155.csv" \
    --prefix RegionCV_S7_adult_average --title "Adult group average (region-CV)"

echo; echo "done $(date -Is)"
} 2>&1 | tee "$DIGEST"
