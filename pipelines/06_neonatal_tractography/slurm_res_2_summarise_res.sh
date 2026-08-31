#!/bin/bash
#SBATCH -J CC
#SBATCH --cpus-per-task=3
#SBATCH --output=/home/chiaracaldinelli/slurm-%j.out
#SBATCH --error=/home/chiaracaldinelli/slurm-%j.err



# import sys
# print ("Number of arguments:", len(sys.argv), "arguments")
# print ("Argument List:", str(sys.argv))
# $ python test.py arg1 arg2 arg3
# Number of arguments: 4 arguments.
# Argument List: ['test.py', 'arg1', 'arg2', 'arg3']


PYTHON="/foundcog/pyenv3.8/bin/python"
echo "Preparing results for classifier for SUBJ=${SUBJ}"
${PYTHON} /home/chiaracaldinelli/smartontheinside/smartontheinside/infant_classifier/slurm_res_3_summarise_res.py $SUBJ
