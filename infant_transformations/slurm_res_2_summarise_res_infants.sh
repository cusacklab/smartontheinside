#!/bin/bash
#SBATCH -J CC
#SBATCH --cpus-per-task=8
#SBATCH --output=/home/chiaracaldinelli/slurm-%j.out
#SBATCH --error=/home/chiaracaldinelli/slurm-%j.err


echo "Running transformations for SUBJ=${SUBJ} SESS=${SESS}"
source /home/chiaracaldinelli/smartontheinside/smartontheinside/infant_transformations/slurm_res_3_summarise_res_infants.sh $SUBJ $SESS
