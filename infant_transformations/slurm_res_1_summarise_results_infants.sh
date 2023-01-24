#!/bin/bash

# DWIPTH=/dhcp/dhcp_dmri_pipeline

DWIPTH=/home/chiaracaldinelli/test/


# preterm_babies = ( "sub-sub-CC00576XX16", "sub-sub-CC00492BN15", "sub-sub-CC00672BN13", "sub-sub-CC00407BN11", "sub-CC00465XX12", "sub-CC00723XX14", "sub-CC00161XX05", "sub-CC00907XX16", "sub-CC00136AN13", "sub-CC00063AN06", "sub-CC00703XX10", "sub-CC00087BN14", "sub-CC00712XX11", "sub-CC00135AN12", "sub-CC00248XX18", "sub-CC00350XX04", "sub-CC00754BN12", "sub-CC00563XX11", "sub-CC00754AN12", "sub-CC00422XX10", "sub-CC00293AN14", "sub-CC00121XX06", "sub-CC00804XX12", "sub-CC00845BN21", "sub-CC00244XX14", "sub-CC00237XX15", "sub-CC00695XX20", "sub-CC00218AN12", "sub-CC00621XX11", "sub-CC00154XX06", "sub-CC00629XX19", "sub-CC00186BN14", "sub-CC00571AN11", "sub-CC00572CN12", "sub-CC00192AN12", "sub-CC00889BN24", "sub-CC00518XX15", "sub-CC00686XX19", "sub-CC00305XX08", "sub-CC00670XX11", "sub-CC00525XX14", "sub-CC00284BN13", "sub-CC00290XX11", "sub-CC00301XX04", "sub-CC00326XX13", "sub-CC00529AN18", "sub-CC00764AN14", "sub-CC00135BN12", "sub-CC00829XX21", "sub-CC00764BN14", "sub-CC00129AN14", "sub-CC00227XX13", "sub-CC00833XX17", "sub-CC00788XX22", "sub-CC00406XX10", "sub-CC00129BN14", "sub-CC00186AN14", "sub-CC00489XX20", "sub-CC00124XX09", "sub-CC00657XX14", "sub-CC00526XX15", "sub-CC00530XX11", "sub-CC00632XX14", "sub-CC00245AN15", "sub-CC00231XX09", "sub-CC00845AN21", "sub-CC00760XX10", "sub-CC00177XX13", "sub-CC00281AN10", "sub-CC00238AN16", "sub-CC00648XX22", "sub-CC00517XX14", "sub-CC00351XX05", "sub-CC00216AN10", "sub-CC00702AN09", "sub-CC00838XX22", "sub-CC00805XX13", "sub-CC00407AN11", "sub-CC00245BN15", "sub-CC00284AN13", "sub-CC00768XX18", "sub-CC00823XX15", "sub-CC00147XX16", "sub-CC00389XX19", "sub-CC00569XX17", "sub-CC00735XX18", "sub-CC00293BN14", "sub-CC00570XX10", "sub-CC00152AN04", "sub-CC00672AN13", "sub-CC00797XX23", "sub-CC00855XX14", "sub-CC00792XX18", "sub-CC00309BN12", "sub-CC00087AN14", "sub-CC00418AN14", "sub-CC00600XX06", "sub-CC00771XX13", "sub-CC00423XX11", "sub-CC00418BN14", "sub-CC00661XX10", "sub-CC00627XX17", "sub-CC00830XX14", "sub-CC00492AN15", "sub-CC00132XX09", "sub-CC00218BN12", "sub-CC00271XX08", "sub-CC00628XX18", "sub-CC00689XX22", "sub-CC00385XX15", "sub-CC00785XX19", "sub-CC00747XX22", "sub-CC00238BN16", "sub-CC00361XX07", "sub-CC00529BN18", "sub-CC00770XX12", "sub-CC00395XX17", "sub-CC00617XX15", "sub-CC00191XX11" )
preterm_list=( sub-CC00576XX16 sub-CC00492BN15 sub-CC00672BN13 sub-CC00407BN11 sub-CC00465XX12 sub-CC00723XX14	sub-CC00161XX05	sub-CC00907XX16	sub-CC00136AN13	sub-CC00063AN06	sub-CC00703XX10	sub-CC00087BN14	sub-CC00712XX11	sub-CC00135AN12	sub-CC00248XX18	sub-CC00350XX04	sub-CC00754BN12	sub-CC00563XX11	sub-CC00754AN12	sub-CC00422XX10	sub-CC00293AN14	sub-CC00121XX06	sub-CC00804XX12	sub-CC00845BN21	sub-CC00244XX14	sub-CC00237XX15	sub-CC00695XX20	sub-CC00218AN12	sub-CC00621XX11	sub-CC00154XX06	sub-CC00629XX19	sub-CC00186BN14	sub-CC00571AN11	sub-CC00572CN12	sub-CC00192AN12	sub-CC00889BN24	sub-CC00518XX15	sub-CC00686XX19	sub-CC00305XX08	sub-CC00670XX11	sub-CC00525XX14	sub-CC00284BN13	sub-CC00290XX11	sub-CC00301XX04	sub-CC00326XX13	sub-CC00529AN18	sub-CC00764AN14	sub-CC00135BN12	sub-CC00829XX21	sub-CC00764BN14	sub-CC00129AN14	sub-CC00227XX13	sub-CC00833XX17	sub-CC00788XX22	sub-CC00406XX10	sub-CC00129BN14	sub-CC00186AN14	sub-CC00489XX20	sub-CC00124XX09	sub-CC00657XX14	sub-CC00526XX15	sub-CC00530XX11	sub-CC00632XX14	sub-CC00245AN15	sub-CC00231XX09	sub-CC00845AN21	sub-CC00760XX10	sub-CC00177XX13	sub-CC00281AN10	sub-CC00238AN16	sub-CC00648XX22	sub-CC00517XX14	sub-CC00351XX05	sub-CC00216AN10	sub-CC00702AN09	sub-CC00838XX22	sub-CC00805XX13	sub-CC00407AN11	sub-CC00245BN15	sub-CC00284AN13	sub-CC00768XX18	sub-CC00823XX15	sub-CC00147XX16	sub-CC00389XX19	sub-CC00569XX17	sub-CC00735XX18	sub-CC00293BN14	sub-CC00570XX10	sub-CC00152AN04	sub-CC00672AN13	sub-CC00797XX23	sub-CC00855XX14	sub-CC00792XX18	sub-CC00309BN12	sub-CC00087AN14	sub-CC00418AN14	sub-CC00600XX06	sub-CC00771XX13	sub-CC00423XX11	sub-CC00418BN14	sub-CC00661XX10	sub-CC00627XX17	sub-CC00830XX14	sub-CC00492AN15	sub-CC00132XX09	sub-CC00218BN12	sub-CC00271XX08	sub-CC00628XX18	sub-CC00689XX22	sub-CC00385XX15	sub-CC00785XX19	sub-CC00747XX22	sub-CC00238BN16	sub-CC00361XX07	sub-CC00529BN18	sub-CC00770XX12	sub-CC00395XX17	sub-CC00617XX15	sub-CC00191XX11 )


# All subjects and sessions
for SUBJDIR in ${DWIPTH}/sub-CC*; do
    SUBJ=$(basename -- "$SUBJDIR")

    for preterm in $preterm_list ; do
        if [ "$SUBJ" == "$preterm" ]; then
            echo "$SUBJ is preterm"
        else
            for SESSDIR in ${SUBJDIR}/ses-*/; do
                if [[ -d "$SESSDIR" ]]; then
                    SESS=$(basename -- "$SESSDIR")
                    
                    # Check if transformation was already computed
                    aws s3 ls s3://smartontheinside/infant_tractography/${SUBJ}/T1w/Diffusion.probtrackx2/L/seeds_to_ROI.360.shape.gii
                    if [[ $? -ne 0 ]]; then

                        # Check for bedpostX outputs
                        if [[ -f "${DWIPTH}/${SUBJ}/${SESS}/dwi.bedpostX/merged_f1samples.nii.gz" ]]; then
                            echo "running infant transformations for $SUBJ $SESS "
                            export SUBJ=$SUBJ 
                            export SESS=$SESS 
                            sbatch --export=ALL, /home/chiaracaldinelli/smartontheinside/smartontheinside/infant_transformations/slurm_res_2_summarise_res_infants.sh	
                        fi
                    else
                        echo "subject $SUBJ transformations were already computed"
                    fi
		        fi 	  
            done
        fi
    done
done