#!/bin/bash
#SBATCH -J FH-CC
#SBATCH --cpus-per-task=8
#SBATCH --output=/home/chiaracaldinelli/smartonetheinside/smartontheinside/slurm-%j.out
#SBATCH --error=/home/chiaracaldinelli/smartonetheinside/smartontheinside/slurm-%j.err


echo "In fslurm_run_tractography.sh parameter SUBJ=$SUBJ"
/home/chiaracaldinelli/smartonetheinside/smartontheinside/slurm_run_tractography.sh $SUBJ
