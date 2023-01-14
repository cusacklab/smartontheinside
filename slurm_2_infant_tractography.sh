#!/bin/bash
#SBATCH -J CC
#SBATCH --cpus-per-task=8
#SBATCH --output=/home/chiaracaldinelli/slurm-%j.out
#SBATCH --error=/home/chiaracaldinelli/slurm-%j.err


echo "Running tractography for SUBJ=$SUBJ"
source /home/chiaracaldinelli/smartontheinside/smartontheinside/infant_tractography.sh $SUBJ $SESS
