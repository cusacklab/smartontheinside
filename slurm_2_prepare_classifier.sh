#!/bin/bash
#SBATCH -J CC
#SBATCH --cpus-per-task=8
#SBATCH --mem=4G
#SBATCH --output=/home/chiaracaldinelli/slurm-%j.out
#SBATCH --error=/home/chiaracaldinelli/slurm-%j.err


echo "Extracting connectivity and activation for SUBJ=$sub"
python /home/chiaracaldinelli/smartontheinside/slurm_res_summarise_res_PANDAS.py.py $sub