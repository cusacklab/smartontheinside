#!/bin/bash

for alpha in 0.1, 0.2, 0.4, 0.8 1.6 3.2 6.4 12.8 25.6 51.2; do
    for l1_ratio in 0 0.2 0.4 0.6 0.8 1.0; do

        echo "Parameters: alpha = $alpha and l1_ratio = $l1_ratio"
        sbatch --export=ALL,alpha=$alpha,l1_ratio=$l1_ratio /home/chiaracaldinelli/smartontheinside/smartontheinside/classifier_slurm_2.sh  
    done
done