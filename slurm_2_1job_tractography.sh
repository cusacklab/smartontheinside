#!/bin/bash
#SBATCH -J SOTI-CC
#SBATCH --cpus-per-task=8
#SBATCH --output=/dhcp/smartonetheinside/smartontheinside/slurm/slurm-%j.out
#SBATCH --error=/dhcp/chiaracaldinelli/smartonetheinside/smartontheinside/slurm/slurm-%j.err


echo "In slurm_3_run_tractography.sh parameter SUBJ=$SUBJ"
/home/chiaracaldinelli/smartonetheinside/smartontheinside/slurm_run_tractography.sh $SUBJ
