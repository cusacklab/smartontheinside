#!/bin/bash

DWIPTH=/dhcp/dhcp_dmri_pipeline

# DWIPTH=/home/chiaracaldinelli/probtrackx_try_slurm/

# All subjects and sessions
for SUBJDIR in ${DWIPTH}/sub-CC*; do
    SUBJ=$(basename -- "$SUBJDIR")
	echo 
    for SESSDIR in ${SUBJDIR}/ses-*/; do
		if [[ -d "$SESSDIR" ]];then
			SESS=$(basename -- "$SESSDIR")
			# Check for bedpostX outputs
			if [[ -f "${DWIPTH}/${SUBJ}/${SESS}/dwi.bedpostX/merged_f1samples.nii.gz" ]]; then

				echo "$SUBJ" >> subject_list_infants.csv

			fi
				
		fi 	    
   done

done