#!/bin/bash
#SBATCH -J CC
#SBATCH --cpus-per-task=8
#SBATCH --output=/home/chiaracaldinelli/slurm-%j.out
#SBATCH --error=/home/chiaracaldinelli/slurm-%j.err


echo "Running tractography for SUBJ=${SUBJ}"
source /home/chiaracaldinelli/smartontheinside/smartontheinside/slurm_res_3_summarise_res_infants.sh $SUBJ
