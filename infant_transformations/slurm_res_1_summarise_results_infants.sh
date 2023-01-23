#!/bin/bash

# DWIPTH=/dhcp/dhcp_dmri_pipeline

DWIPTH=/home/chiaracaldinelli/probtrackx_try_slurm/

# All subjects and sessions
for SUBJDIR in ${DWIPTH}/sub-CC*; do
    SUBJ=$(basename -- "$SUBJDIR")
    for SESSDIR in ${SUBJDIR}/ses-*/; do
		if [[ -d "$SESSDIR" ]];then
			SESS=$(basename -- "$SESSDIR")
			# Check for bedpostX outputs
			if [[ -f "${DWIPTH}/${SUBJ}/${SESS}/dwi.bedpostX/merged_f1samples.nii.gz" ]]; then
                echo "running infant transformations for $SUBJ $SESS "
                export SUBJ=$SUBJ 
                export SESS=$SESS 
                sbatch --export=ALL, /home/chiaracaldinelli/smartontheinside/smartontheinside/infant_transformations/slurm_res_2_summarise_res_infants.sh	
			fi
		fi 	    
   done
done