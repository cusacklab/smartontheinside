#!/bin/bash
# Full-pipeline surrogate null (reviewer 1's key control), split across the
# cluster as a 10-task array: one (contrast, hemisphere) pair per shard, each
# refitting the model on N_SURROGATES spatially permuted training sets and
# transferring to all neonates.
#
# Each shard draws its own surrogates for its own map, so a shared seed is
# fine ACROSS shards; only splitting one task's surrogates over several shards
# would need distinct --seed values.
#
#   sbatch pipelines/07_classification/slurm_pipeline_null.sh
#   sti merge --inputs 'data/results/shards/pipeline_null_*.csv' \
#             -o data/results/pipeline_null_N325.csv
#   sti pipeline-null --summarise data/results/pipeline_null_N325.csv \
#             --results data/results/neonatal_N325.csv \
#             -o data/results/pipeline_null_summary.csv --figures
#
#SBATCH --job-name=sti_pipenull
#SBATCH --partition=high-memory
#SBATCH --array=0-9
#SBATCH --cpus-per-task=4
#SBATCH --mem=24G
#SBATCH --time=08:00:00
#SBATCH --output=slurm_logs/%x_%A_%a.out
#SBATCH --error=slurm_logs/%x_%A_%a.out

set -euo pipefail
REPO=/home/ubuntu/repos/smartontheinside
cd "$REPO"
mkdir -p data/results/shards slurm_logs

N_SURROGATES=${STI_N_SURROGATES:-200}

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

echo "host=$(hostname) array_id=${SLURM_ARRAY_TASK_ID} task=${TASK} hemi=${HEMI} n_surrogates=${N_SURROGATES} threads=$OMP_NUM_THREADS"
echo "started $(date -Is)"

/opt/fsl/bin/python3 -m sti.cli -v pipeline-null \
    --cohort adults_analysis \
    --neonates neonates_term_all \
    --tasks "$TASK" \
    --hemi "$HEMI" \
    --n-surrogates "$N_SURROGATES" \
    -o "data/results/shards/pipeline_null_${TASK}_${HEMI}.csv"

echo "finished $(date -Is)"
