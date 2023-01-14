#!/bin/bash

DWIPTH=/dhcp/dhcp_dmri_pipeline

# All subjects and sessions
for SUBJDIR in ${DWIPTH}/sub-CC*; do
    SUBJ=$(basename -- "$SUBJDIR")
    for SESSDIR in ${SUBJDIR}/ses-*/; do
	if [[ -d "$SESSDIR" ]]
	then
		SESS=$(basename -- "$SESSDIR")
		# Check for bedpostX outputs
		if [[ -f "${DWIPTH}/${SUBJ}/${SESS}/dwi.bedpostX/merged_f1samples.nii.gz" ]]; then
  			echo "With bedpostX output ${SUBJ}_${SESS}"
			if [[ -f "${DWIPTH}/${SUBJ}/${SESS}/probtrackx2/done_run_probtrackx2" ]]; then
				echo "Already ran probtrackx2"
			else
				sbatch /home/chiaracaldinelli/smartontheinside/smartontheinside/slurm_2_infant_tractography.sh $SUBJ $SESS
			fi		
		fi
			
	fi 	    
   done

done









# All subjects and sessions
for SUBJDIR in ${DWIPTH}/sub-CC*; do
    SUBJ=$(basename -- "$SUBJDIR")
    for SESSDIR in ${SUBJDIR}/ses-*/; do
        if [[ -d "$SESSDIR" ]]; then
            SESS=$(basename -- "$SESSDIR")
            echo "Working on subject $SUBJ"
            sbatch --export=ALL,SUBJ=$SUBJ,SESS=$SESS /home/chiaracaldinelli/smartontheinside/smartontheinside/slurm_2_infant_tractography.sh  
        fi
    done
done