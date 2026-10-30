#!/bin/bash
# Submit the whole region-CV stack with dependencies. Safe to walk away from:
# the finalise job runs only after every array job succeeds and leaves all
# merged tables, summaries, figures and a DIGEST under data/results/regioncv/.
set -euo pipefail
REPO=/home/ubuntu/repos/smartontheinside
cd "$REPO"
S=pipelines/07_classification

A=$(sbatch --parsable --export=ALL,STI_ANALYSIS=neonatal          --job-name=sti_rcv_neo   $S/slurm_regioncv.sh)
B=$(sbatch --parsable --export=ALL,STI_ANALYSIS=adult-loo         --job-name=sti_rcv_aloo  $S/slurm_regioncv.sh)
C=$(sbatch --parsable --export=ALL,STI_ANALYSIS=adult-average     --job-name=sti_rcv_aavg  $S/slurm_regioncv.sh)
D=$(sbatch --parsable --export=ALL,STI_ANALYSIS=distance-regressed --job-name=sti_rcv_dreg $S/slurm_regioncv.sh)
E=$(sbatch --parsable --export=ALL,STI_ANALYSIS=pipeline-null     --job-name=sti_rcv_null  $S/slurm_regioncv.sh)
F=$(sbatch --parsable --export=ALL,STI_ANALYSIS=pipeline-null-regressed --job-name=sti_rcv_nullr $S/slurm_regioncv.sh)

# the shares partition with leave-one-region-out folds (independent of the rest)
G=$(sbatch --parsable --job-name=sti_rcv_shares --partition=high-memory \
    --cpus-per-task=4 --mem=32G --time=08:00:00 \
    --output=slurm_logs/%x_%A.out --error=slurm_logs/%x_%A.out \
    --wrap "cd $REPO && export PYTHONPATH=$REPO/src OMP_NUM_THREADS=4 && \
            /opt/fsl/bin/python3 -m sti.cli -v shares --folds regions \
            --connectivity data/derivatives/conn_for_classifier_N-325_infants.npy \
            --figures -o data/results/regioncv/shares_regions.csv")

H=$(sbatch --parsable --dependency=afterok:$A:$B:$C:$D:$E:$F $S/slurm_regioncv_finalise.sh)

echo "submitted: neonatal=$A adult-loo=$B adult-average=$C distance-regressed=$D"
echo "           pipeline-null=$E pipeline-null-regressed=$F shares=$G finalise=$H"
echo "finalise job $H writes data/results/regioncv/DIGEST.txt when everything is done"
