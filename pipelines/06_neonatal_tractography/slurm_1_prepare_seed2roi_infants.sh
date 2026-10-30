#!/bin/bash

# DWIPTH=/dhcp/dhcp_dmri_pipeline

DWIPTH=/home/chiaracaldinelli/probtrackx_try_slurm/

# All subjects and sessions
for SUBJDIR in ${DWIPTH}/sub-CC*; do

    SUBJ=$(basename -- "$SUBJDIR")
    echo "summarising results for $SUBJ "
    export subj=$SUBJ
    sbatch --export=ALL, /home/chiaracaldinelli/smartontheinside/smartontheinside/slurm_res_2_summarise_res_infants.sh     

done