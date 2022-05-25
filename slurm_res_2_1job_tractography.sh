#!/bin/bash
#SBATCH -J CC-SUMRES
#SBATCH --cpus-per-task=8
#SBATCH --output=/home/chiaracaldinelli/slurm-%j.out
#SBATCH --error=/home/chiaracaldinelli/slurm-%j.err


echo "In slurm_3_run_tractography.sh parameter SUBJ=$SUBJ"
bash /home/chiaracaldinelli/smartontheinside/slurm_res_3_summarize_res.py $SUBJ