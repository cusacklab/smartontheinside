#!/bin/bash

for subj in ; do
  echo "Running tractography for subjext chunklen $SUBJ"
  sbatch --export=SUBJ=$subj /home/chiaracaldinelli/smartonetheinside/smartontheinside/slurm_1job_tractography.sh  
done
