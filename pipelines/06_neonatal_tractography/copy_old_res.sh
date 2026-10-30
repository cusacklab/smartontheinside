#!/bin/bash

DWIPTH=/dhcp/dhcp_dmri_pipeline
# DWIPTH=/home/chiaracaldinelli/rerun_roi97

# All subjects and sessions
for SUBJDIR in ${DWIPTH}/sub-CC*; do
    SUBJ=$(basename -- "$SUBJDIR")
    for SESSDIR in ${SUBJDIR}/ses-*/; do
		if [[ -d "$SESSDIR" ]];then
			SESS=$(basename -- "$SESSDIR")
			# Check for bedpostX outputs
			if [[ -f "${DWIPTH}/${SUBJ}/${SESS}/dwi.bedpostX/merged_f1samples.nii.gz" ]]; then
				echo "With bedpostX output ${SUBJ}_${SESS}"
				aws s3 mv s3://smartontheinside/infant_tractography/${SUBJ}/T1w/Diffusion.probtrackx2/R/ s3://smartontheinside/infant_tractography/old_results_roi96/${SUBJ}/T1w/Diffusion.probtrackx2/ --recursive

			fi	
		fi 	    
   done

done