#!/bin/bash

DWIPTH=/dhcp/dhcp_dmri_pipeline

# DWIPTH=/home/chiaracaldinelli/probtrackx_try_slurm/

# All subjects and sessions
for SUBJDIR in ${DWIPTH}/sub-CC*; do
    SUBJ=$(basename -- "$SUBJDIR")
    for SESSDIR in ${SUBJDIR}/ses-*/; do
		if [[ -d "$SESSDIR" ]];then
			SESS=$(basename -- "$SESSDIR")
			# Check for bedpostX outputs
			if [[ -f "${DWIPTH}/${SUBJ}/${SESS}/dwi.bedpostX/merged_f1samples.nii.gz" ]]; then
				echo "With bedpostX output ${SUBJ}_${SESS}"
				if [[ -f "${DWIPTH}/${SUBJ}/${SESS}/probtrackx2/done_run_probtrackx2" ]]; then
					echo "Already ran probtrackx2"
				else
					echo "running first code for $SUBJ $SESS "
					export SUBJ=$SUBJ 
					export SESS=$SESS 
					sbatch --export=ALL, /home/chiaracaldinelli/smartontheinside/smartontheinside/slurm_2_infant_tractography.sh 
				fi		
			fi
				
		fi 	    
   done

done

