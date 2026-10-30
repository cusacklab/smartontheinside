#!/bin/bash
#SBATCH -J CC-tractography
#SBATCH --cpus-per-task=8
#SBATCH --output=/home/chiaracaldinelli/slurm-%j.out
#SBATCH --error=/home/chiaracaldinelli/slurm-%j.err


echo "Running tractography for SUBJ=${SUBJ} SESS=${SESS}"
source /home/chiaracaldinelli/smartontheinside/smartontheinside/infant_tractography_analysis/infant_tractography.sh $SUBJ $SESS
