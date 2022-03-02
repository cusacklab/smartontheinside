#!/bin/bash
#SBATCH -J SOTI-CC
#SBATCH --cpus-per-task=8
#SBATCH --output=/home/chiaracaldinelli/slurm-%j.out
#SBATCH --error=/home/chiaracaldinelli/smartontheinside/slurm-%j.err


echo "In slurm_3_run_tractography.sh parameter SUBJ=$SUBJ"
/home/chiaracaldinelli/smartontheinside/slurm_run_tractography.sh $SUBJ
