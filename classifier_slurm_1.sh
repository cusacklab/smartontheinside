#!/bin/bash

# for alpha in 0.2 0.4 0.6 0.8; do
#     for l1_ratio in 0.2 0.4 0.6 0.8; do
for alpha in 0.6 0.8; do
    for l1_ratio in 0.8; do
        echo "Parameters: alpha = $alpha and l1_ratio = $l1_ratio"
        sbatch --export=ALL,alpha=$alpha,l1_ratio=$l1_ratio /home/chiaracaldinelli/smartontheinside/smartontheinside/classifier_slurm_2.sh  
    done
done