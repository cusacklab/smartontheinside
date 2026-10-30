#!/bin/bash
# Region-cross-validated reruns of every protocol: leave-one-DLPFC-region-out
# stacked on top of the existing subject-level cross-validation, so no
# prediction ever comes from a model that saw its own territory.
#
# One (contrast, hemisphere) pair per array task; STI_ANALYSIS picks the
# protocol. Submitted as a dependency stack by submit_regioncv_stack.sh.
#
#SBATCH --job-name=sti_regioncv
#SBATCH --partition=high-memory
#SBATCH --array=0-9
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=14:00:00
#SBATCH --output=slurm_logs/%x_%A_%a.out
#SBATCH --error=slurm_logs/%x_%A_%a.out

set -euo pipefail
REPO=/home/ubuntu/repos/smartontheinside
cd "$REPO"
mkdir -p data/results/shards slurm_logs

ANALYSIS=${STI_ANALYSIS:?set STI_ANALYSIS}
CONN=data/derivatives/conn_for_classifier_N-325_infants.npy

TASKS=(tfMRI_WM tfMRI_MOTOR tfMRI_LANGUAGE tfMRI_SOCIAL tfMRI_EMOTION)
HEMIS=(L R)
TASK=${TASKS[$(( SLURM_ARRAY_TASK_ID / 2 ))]}
HEMI=${HEMIS[$(( SLURM_ARRAY_TASK_ID % 2 ))]}

export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-4}
export OPENBLAS_NUM_THREADS=$OMP_NUM_THREADS
export MKL_NUM_THREADS=$OMP_NUM_THREADS
export PYTHONPATH="$REPO/src"
PY=/opt/fsl/bin/python3

echo "host=$(hostname) analysis=${ANALYSIS} task=${TASK} hemi=${HEMI}"
echo "started $(date -Is)"

case "$ANALYSIS" in
  neonatal)
    $PY -m sti.cli -v neonatal --region-cv --cohort adults_analysis \
        --connectivity "$CONN" --tasks "$TASK" --hemi "$HEMI" \
        -o "data/results/shards/neonatal_regioncv_${TASK}_${HEMI}.csv" ;;
  adult-loo|adult-average)
    OUT=${ANALYSIS//-/_}
    $PY -m sti.cli -v "$ANALYSIS" --region-cv --cohort adults_analysis \
        --tasks "$TASK" --hemi "$HEMI" \
        -o "data/results/shards/${OUT}_regioncv_${TASK}_${HEMI}.csv" ;;
  pipeline-null)
    $PY -m sti.cli -v pipeline-null --region-cv --cohort adults_analysis \
        --connectivity "$CONN" --tasks "$TASK" --hemi "$HEMI" \
        --n-surrogates "${STI_N_SURROGATES:-100}" \
        -o "data/results/shards/pipenull_regioncv_${TASK}_${HEMI}.csv" ;;
  pipeline-null-regressed)
    $PY -m sti.cli --alpha 0.1 --l1-ratio 0.2 -v pipeline-null --region-cv \
        --regress-distance --cohort adults_analysis \
        --connectivity "$CONN" --tasks "$TASK" --hemi "$HEMI" \
        --n-surrogates "${STI_N_SURROGATES:-100}" \
        -o "data/results/shards/pipenull_regressed_regioncv_${TASK}_${HEMI}.csv" ;;
  distance-regressed)
    $PY -m sti.cli --alpha 0.1 --l1-ratio 0.2 -v distance-control --regress \
        --region-cv --cohort adults_analysis \
        --connectivity "$CONN" --tasks "$TASK" --hemi "$HEMI" \
        -o "data/results/shards/distreg_regioncv_${TASK}_${HEMI}.csv" ;;
  *) echo "unknown STI_ANALYSIS=$ANALYSIS" >&2; exit 1 ;;
esac

echo "finished $(date -Is)"
