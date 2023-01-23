#!/bin/bash

DWIPTH=/dhcp/dhcp_dmri_pipeline

# DWIPTH=/home/chiaracaldinelli/probtrackx_try_slurm/

# for SUBJDIR in ${DWIPTH}/sub-CC*; do

for SUBJDIR in sub-CC00529AN18; do
    SUBJ=$(basename -- "$SUBJDIR")
    for SESSDIR in ${SUBJDIR}/ses-*/; do


        SUBJ=$(basename -- "$SUBJDIR")
        echo "Summarising tractography results for $SUBJ "
        export SUBJ=$SUBJ 
        sbatch --export=ALL, /home/chiaracaldinelli/smartontheinside/smartontheinside/slurm_res_2_summarise_res_infants.sh     


   done

done


    # for SUBJDIR in sub-CC00517XX14 sub-CC00152AN04 sub-CC00402XX06  sub-CC00518XX15  sub-CC00271XX08 sub-CC00525XX14 sub-CC00156XX08 sub-CC00406XX10 sub-CC00672BN13 sub-CC00275XX12 sub-CC00407AN11 sub-CC00284AN13 sub-CC00529AN18 ; do

