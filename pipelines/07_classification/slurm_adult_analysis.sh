#!/bin/bash
# Adult leave-one-out analyses, split across the cluster.
#
# Which analysis runs is set by STI_ANALYSIS:
#   adult-loo      each model predicts the held-out adult's OWN map   (Fig. 2)
#   adult-average  each model predicts the group-average map          (Fig. 4)
#
# The work is 155 leave-one-out folds x 5 contrasts x 2 hemispheres = 1,550 model
# fits, about three hours in one process. Each (contrast, hemisphere) pair is
# independent, so this runs them as a 10-task array and merges the shards.
# Restricting a shard's model tasks does NOT restrict what it is compared
# against, so every shard still emits a complete row of the specificity matrix.
#
#   sbatch --export=ALL,STI_ANALYSIS=adult-loo pipelines/07_classification/slurm_adult_loo.sh
#   sti merge --inputs 'data/results/shards/adult_loo_*.csv' \
#             -o data/results/adult_loo_N155.csv
#
#SBATCH --job-name=sti_adult
#SBATCH --partition=high-memory
#SBATCH --array=0-9
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=03:00:00
#SBATCH --output=slurm_logs/%x_%A_%a.out
#SBATCH --error=slurm_logs/%x_%A_%a.out

set -euo pipefail
REPO=/home/ubuntu/repos/smartontheinside
cd "$REPO"
mkdir -p data/results/shards slurm_logs

ANALYSIS=${STI_ANALYSIS:-adult-average}
OUTNAME=${ANALYSIS//-/_}

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

echo "host=$(hostname) analysis=${ANALYSIS} array_id=${SLURM_ARRAY_TASK_ID} task=${TASK} hemi=${HEMI} threads=$OMP_NUM_THREADS"
echo "started $(date -Is)"

/opt/fsl/bin/python3 -m sti.cli -v "$ANALYSIS" \
    --cohort adults_analysis \
    --tasks "$TASK" \
    --hemi "$HEMI" \
    -o "data/results/shards/${OUTNAME}_${TASK}_${HEMI}.csv"

echo "finished $(date -Is)"
