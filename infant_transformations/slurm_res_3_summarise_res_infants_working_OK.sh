#!/bin/bash

# Chiara Caldinelli, caldinec@tcd.ie
# Cusack Lab, Trinity College Dublin

# This code will summarise results from tractography

export PATH=/home/chiaracaldinelli/workbench/bin_linux64/:$PATH
export AWS_SHARED_CREDENTIALS_FILE=/home/chiaracaldinelli/.aws/credentials
export AWS_CONFIG_FILE=/home/chiaracalindelli/.aws/config
FSLDIR=/usr/local/fsl
. ${FSLDIR}/etc/fslconf/fsl.sh
PATH=${FSLDIR}/bin:${PATH}
export FSLDIR PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib:/usr/local/cuda/lib64:/usr/local/cuda/extras/CUPTI/lib64:/opt/amazon/efa/lib:/opt/amazon/openmpi/lib:/usr/local/lib:/usr/lib:


roilist=($(seq 1 360 ))
DLPFroilist=(26 67 68 70 71 73 83 84 85 86 87 96 98 206 247 248 250 251 253 263 264 265 266 267 276 278)



# 1- Create tmp folder
# tmp_dir=$(mktemp -d -t chiara-$(date +%Y-%m-%d-%H-%M-%S)-XXXXXXXXXX)
# tmp_dir=/home/chiaracaldinelli/test/$SUBJ
tmp_dir=/home/chiaracaldinelli/test_25_jan/$SUBJ


# 2- Do transformations
    
for hem in L R ; do

    aws s3 sync s3://smartontheinside/infant_tractography/${SUBJ}/Diffusion.probtrackx2/${hem}/ ${tmp_dir}/T1w/Diffusion.probtrackx2/${hem}/
    rm ${tmp_dir}/T1w/Diffusion.probtrackx2/${hem}/seed2target_40weeks_*
    rm ${tmp_dir}/T1w/Diffusion.probtrackx2/${hem}/seed2target_to_MNI_template_*
    rm ${tmp_dir}/T1w/Diffusion.probtrackx2/${hem}/*shape.gii
    

    for roi in "${roilist[@]}"; do

        if [[  " ${DLPFroilist[*]} " =~ " ${roi} " ]]; then
            echo "${roi} part of DLPFC"
        
        else

                
            # apply warp: seed2target.nii --> label40weeks.nii 
            now=$(date +"%T")
            echo "*************** Current time : $now ***************"
            if [ -f ${tmp_dir}/T1w/Diffusion.probtrackx2/${hem}/unexisting_${SUBJ}_${roi}.nii.gz ]; then

                echo "applywarp run already"
            else

                echo "Running applywarp for ROI ${roi} for SUBJect ${SUBJ}"

                applywarp -i ${tmp_dir}/T1w/Diffusion.probtrackx2/${hem}/seeds_to_glasser_labels_dhcp_40weeks_LR_${SUBJ}_${roi}.nii.gz \
                            -o ${tmp_dir}/T1w/Diffusion.probtrackx2/${hem}/seed2target_40weeks_${SUBJ}_${roi}.nii.gz \
                            -w /dhcp/dhcp_dmri_pipeline/${SUBJ}/${SESS}/xfm/${SUBJ}_${SESS}_from-dwi_to-template40wk_mode-image.nii.gz \
                            -r /dhcp/rhodri_registration/atlases/dhcp_volume_40weeks/template_t1.nii.gz     
                # change to 1mm infant template 
                # change output name
                # OLD FILE -r /dhcp/rhodri_registration/atlases/dhcp_volume_40weeks/template_t1.nii.gz 
            fi

            now=$(date +"%T")
            echo "*************** Current time : $now ***************"
            # ants: label 40 weeks .nii --> dhcp template40weeks
            echo "Running antsApplyTransforms for ROI ${roi} for SUBJect ${SUBJ}"
            antsApplyTransforms -i ${tmp_dir}/T1w/Diffusion.probtrackx2/${hem}/seed2target_40weeks_${SUBJ}_${roi}.nii.gz \
                -r /dhcp/rhodri_registration/atlases/fsl/MNI152_T1_1mm_brain.nii.gz \
                -t /dhcp/rhodri_registration/analysis_2020-20-29/antsreg_t1_nodura_nocerebllum_in_template1Warp.nii.gz \
                -t /dhcp/rhodri_registration/analysis_2020-20-29/antsreg_t1_nodura_nocerebllum_in_template0GenericAffine.mat \
                -o ${tmp_dir}/T1w/Diffusion.probtrackx2/${hem}/seed2target_to_MNI_template_${SUBJ}_${roi}.nii.gz
            # change -r to MNI 1mm template 
            # -r /dhcp/rhodri_registration/atlases/fsl/MNI152_T1_1mm_brain.nii.gz \ high res
            # -r /dhcp/rhodri_registration/atlases/dhcp_volume_40weeks/template_t1.nii.gz \ low res
            # change output name

            now=$(date +"%T")
            echo "*************** Current time : $now ***************"
            # wb_command: volume to surface
            echo "Running wb_command volume2surface for ROI ${roi} for SUBJect ${SUBJ}"
            wb_command -volume-to-surface-mapping ${tmp_dir}/T1w/Diffusion.probtrackx2/${hem}/seed2target_to_MNI_template_${SUBJ}_${roi}.nii.gz \
                /home/chiaracaldinelli/smartontheinside/smartontheinside/parcellations_and_masks/Q1-Q6_RelatedParcellation210.${hem}.midthickness_MSMAll_2_d41_WRN_DeDrift.32k_fs_LR.surf.gii \
                -enclosing \
                ${tmp_dir}//T1w/Diffusion.probtrackx2/${hem}/seeds_to_ROI_MNI_template.${roi}.shape.gii
        
        fi
    done
    
done

# 4- Push results to S3
# aws s3 sync ${tmp_dir}/T1w/Diffusion.probtrackx2/L/ s3://smartontheinside/infant_tractography/${SUBJ}/T1w/Diffusion.probtrackx2/L/
# aws s3 sync ${tmp_dir}/T1w/Diffusion.probtrackx2/R/ s3://smartontheinside/infant_tractography/${SUBJ}/T1w/Diffusion.probtrackx2/R/

aws s3 sync ${tmp_dir}/$SUBJ/Diffusion.probtrackx2/L/ s3://smartontheinside/infant_tractography/${SUBJ}/Diffusion.probtrackx2/L/
aws s3 sync ${tmp_dir}/$SUBJ/Diffusion.probtrackx2/R/ s3://smartontheinside/infant_tractography/${SUBJ}/Diffusion.probtrackx2/R/