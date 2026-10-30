#!/bin/bash
#SBATCH -J CC-extract_conn
#SBATCH --cpus-per-task=8
#SBATCH --output=/home/chiaracaldinelli/slurm-%j.out
#SBATCH --error=/home/chiaracaldinelli/slurm-%j.err


PYTHON="/home/chiaracaldinelli/chiara_env_3.6/bin/python"

echo "Running extract connectivity infants"
${PYTHON} /home/chiaracaldinelli/smartontheinside/smartontheinside/extract_conn_infants.py $sub
