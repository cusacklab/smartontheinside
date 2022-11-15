#!/bin/bash
#SBATCH -J CC
#SBATCH --cpus-per-task=8
#SBATCH --output=/home/chiaracaldinelli/slurm-%j.out
#SBATCH --error=/home/chiaracaldinelli/slurm-%j.err

PYTHON="/home/chiaracaldinelli/chiara_env_3.6/bin/python"

echo "Running elastic net model"
${PYTHON} /home/chiaracaldinelli/smartontheinside/smartontheinside/classifier.py $alpha $l1_ratio