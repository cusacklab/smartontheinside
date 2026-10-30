#!/bin/bash
# The real neonatal analysis on distance-regressed connectivity (reviewer 1's
# Donahue-style control), split across the cluster as a 10-task array: one
# (contrast, hemisphere) pair per shard. The cheap distance-ONLY model does not
# need the cluster: run `sti distance-control --results ...` anywhere.
#
#   sbatch pipelines/07_classification/slurm_distance_regressed.sh
#   sti merge --inputs 'data/results/shards/distance_regressed_*.csv' \
#             -o data/results/neonatal_N325_distance_regressed.csv
#
#SBATCH --job-name=sti_distreg
#SBATCH --partition=high-memory
#SBATCH --array=0-9
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=04:00:00
#SBATCH --output=slurm_logs/%x_%A_%a.out
#SBATCH --error=slurm_logs/%x_%A_%a.out

set -euo pipefail
REPO=/home/ubuntu/repos/smartontheinside
cd "$REPO"
mkdir -p data/results/shards slurm_logs

TASKS=(tfMRI_WM tfMRI_MOTOR tfMRI_LANGUAGE tfMRI_SOCIAL tfMRI_EMOTION)
HEMIS=(L R)
TASK=${TASKS[$(( SLURM_ARRAY_TASK_ID / 2 ))]}
HEMI=${HEMIS[$(( SLURM_ARRAY_TASK_ID % 2 ))]}

# BLAS threads must match the cpus we asked for, or every shard on a node will
# spawn 16 threads each and thrash
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-4}
export OPENBLAS_NUM_THREADS=$OMP_NUM_THREADS
export MKL_NUM_THREADS=$OMP_NUM_THREADS
export PYTHONPATH="$REPO/src"

echo "host=$(hostname) array_id=${SLURM_ARRAY_TASK_ID} task=${TASK} hemi=${HEMI} threads=$OMP_NUM_THREADS"
echo "started $(date -Is)"

# the term cohort file lists 326 subjects but the assembled array is N-325
# (one subject has no usable tractography), so the array + sidecar are the truth
/opt/fsl/bin/python3 -m sti.cli -v distance-control --regress \
    --cohort adults_analysis \
    --connectivity data/derivatives/conn_for_classifier_N-325_infants.npy \
    --tasks "$TASK" \
    --hemi "$HEMI" \
    -o "data/results/shards/distance_regressed_${TASK}_${HEMI}.csv"

echo "finished $(date -Is)"
