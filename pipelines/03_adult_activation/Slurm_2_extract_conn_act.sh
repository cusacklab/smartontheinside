#!/bin/bash
#SBATCH -J CC
#SBATCH --cpus-per-task=8
#SBATCH --output=/home/chiaracaldinelli/slurm-%j.out
#SBATCH --error=/home/chiaracaldinelli/slurm-%j.err

PYTHON="/home/chiaracaldinelli/chiara_env_3.6/bin/python"

echo "Extracting connectivity and activation for SUBJ=$SUBJ"
${PYTHON} /home/chiaracaldinelli/smartontheinside/smartontheinside/extract_conn_act.py $SUBJ
#python /home/chiaracaldinelli/smartontheinside/smartontheinside/extract_conn_act.py $SUBJ