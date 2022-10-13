#!/bin/bash
#SBATCH -J CC
#SBATCH --cpus-per-task=8
#SBATCH --output=/home/chiaracaldinelli/slurm-%j.out
#SBATCH --error=/home/chiaracaldinelli/slurm-%j.err


echo "Extracting connectivity and activation for SUBJ=$SUBJ"
python /home/chiaracaldinelli/smartontheinside/extract_conn_act.py $SUBJ