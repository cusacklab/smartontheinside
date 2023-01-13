#!/bin/bash
#SBATCH --gpus=1

# Chiara Caldinelli, caldinec@tcd.ie
# Cusack Lab, Trinity College Dublin

# This code will run tractography from the DLPF area to every single ROI outside it with data from the dHCP.
# This code will:
#   1- Create a tmp folder

#   4- Tractography


export PATH=/home/chiaracaldinelli/workbench/bin_linux64/:$PATH
export AWS_SHARED_CREDENTIALS_FILE=/home/chiaracaldinelli/.aws/credentials
export AWS_CONFIG_FILE=/home/chiaracaldinelli/.aws/config
FSLDIR=/usr/local/fsl
. ${FSLDIR}/etc/fslconf/fsl.sh
PATH=${FSLDIR}/bin:${PATH}
export FSLDIR PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib:/usr/local/cuda/lib64:/usr/local/cuda/extras/CUPTI/lib64:/opt/amazon/efa/lib:/opt/amazon/openmpi/lib:/usr/local/lib:/usr/lib:



################## 1- Create tmp folder ##################
tmp_dir=$(mktemp -d -t chiara-$(date +%Y-%m-%d-%H-%M-%S)-XXXXXXXXXX)
# See what we've made
echo "Looking in temp directory"
echo ${tmp_dir}
ls ${tmp_dir}


#################################################
################### 2- Set dir ##################
#################################################
echo $SESS
bedpostX_dir=/dhcp/dhcp_dmri_pipeline/sub-$SUBJ/$SESS/dwi.bedpostX
dir_anat=/dhcp/dhcp_anat_pipeline/$SUBJ/*/anat/*_T1w_biasfield.nii.gz
# /dhcp/dhcp_dmri_pipeline/sub-${SUBJ}/ses-*/xfm/sub-${SUBJ}_ses-*_from-template40wk_to-dwi_mode-image.nii.gz
# /dhcp/dhcp_dmri_pipeline/sub-CC00907XX16/ses-*/dwi/nodif_brain_mask.nii.gz

# Create a list for DLPFC regions and one for all the other regions
roilist=( $(seq 1 360 ) )
DLPFroilist=(26 67 68 70 71 73 83 84 85 86 87 96 98 206 247 248 250 251 253 263 264 265 266 267 276 278)

for DLPFCroi in DLPFroilist; do 
    unset roilist[DLPFCroi]
done
echo ${roilist[@]}



for hemi in L R ; do

    if [ -f /home/chiaracaldinelli/transformations/frontal_labels_dhcp_40weeks_${hemi}_sub-${SUBJ}.nii.gz ]; then
        echo "glasser_labels_dhcp_40weeks_${hemi}_sub-${SUBJ} already created"

    fi
        echo "running sub-${SUBJ}"
        applywarp -i /home/chiaracaldinelli/smartontheinside/smartontheinside/results/transformations/frontal_labels_dhcp_40weeks_${hemi}.nii.gz -o /home/chiaracaldinelli/transformations/frontal_labels_dhcp_40weeks_${hemi}_sub-${SUBJ} -w /dhcp/dhcp_dmri_pipeline/sub-${SUBJ}/${SESS}/xfm/sub-${SUBJ}_${SESS}_from-template40wk_to-dwi_mode-image.nii.gz -r /dhcp/dhcp_dmri_pipeline/sub-CC00907XX16/ses-*/dwi/nodif_brain_mask.nii.gz --interp=nn

    if [ -f /home/chiaracaldinelli/transformations/glasser_labels_dhcp_40weeks_${hemi}_sub-${SUBJ}.nii.gz ]; then
        echo "frontal_labels_dhcp_40weeks_${hemi}_sub-${SUBJ} already created"

    fi
        echo "running sub-${SUBJ}"
        applywarp -i /home/chiaracaldinelli/smartontheinside/smartontheinside/results/transformations/glasser_labels_dhcp_40weeks_${hemi}.nii.gz -o /home/chiaracaldinelli/transformations/frontal_glasser_labels_dhcp_40weeks_${hemi}_sub-${SUBJ} -w /dhcp/dhcp_dmri_pipeline/sub-${SUBJ}/${SESS}/xfm/sub-${SUBJ}_ses-*_from-template40wk_to-dwi_mode-image.nii.gz -r /dhcp/dhcp_dmri_pipeline/sub-CC00907XX16/${SESS}/dwi/nodif_brain_mask.nii.gz --interp=nn
done

# Add the 2 hemispheres together
fslmaths /home/chiaracaldinelli/transformations/glasser_labels_dhcp_40weeks_L_sub-${SUBJ} -add /home/chiaracaldinelli/transformations/glasser_labels_dhcp_40weeks_R_sub-${SUBJ} /home/chiaracaldinelli/transformations/glasser_labels_dhcp_40weeks_LR_sub-${SUBJ}




#############################################################################
################### 3- Split parcellation into single ROIs ##################
#############################################################################

TOSPLIT=/home/chiaracaldinelli/smartontheinside/smartontheinside/results/transformations/glasser_labels_dhcp_40weeks # change it to a mask with all the targets
TEXTOUT=${TOSPLIT}_list.txt
rm $TEXTOUT
CWD=`pwd`
COUNTS=`fslstats $TOSPLIT -H 370 0 370` # COUNT VOXELS IN EACH REGION
IND=0

for X in $COUNTS
do
    if [ $X != "0.000000" ]; then    # ONLY INCLUDE REGIONS WITH VOXELS
        echo "Found ROI $IND with $X voxels"

    if [[ " $IND " =~ " 0 " ]]; then
        echo "Exclude background"
    fi

    if [[ " ${DLPFroilist[*]} " =~ " ${IND} " ]]; then
        echo "${IND} part of DLPFC"
        fslmaths $TOSPLIT -thr $IND -uthr $IND ${TOSPLIT}_${IND}
        echo ${TOSPLIT}_${IND} >> ${TEXTOUT}
    fi

    if [[ ! " ${DLPFroilist[*]} " =~ " ${IND} " ]]; then
        fslmaths $TOSPLIT -thr $IND -uthr $IND ${TOSPLIT}_${IND}
        echo ${TOSPLIT}_${IND} >> ${TEXTOUT}
    fi
    fi

IND=$(($IND+1))
done



#######################################################
################### 4- Tractography ###################
#######################################################

for HEMI in L R ; do
    # mkdir -p ${tmp_dir}/probtrackx2_res/${HEMI}
    mkdir -p /home/chiaracaldinelli/probtrackx2_res_${SUBJ}/${HEMI}
    # cmd="probtrackx2_gpu --onewaycondition -P 5000 --forcedir --opd --os2t \


    probtrackx2 \
    --samples=${bedpostX_dir}/merged \
    --seed=/home/chiaracaldinelli/transformations/frontal_labels_dhcp_40weeks_${HEMI}_sub-${SUBJ} \
    --mask=${bedpostX_dir}/nodif_brain_mask.nii.gz  \
    --loopcheck --simple --forcedir \
    --dir=/home/chiaracaldinelli/probtrackx2_res_${SUBJ}/${HEMI} \
    --opd -V 1

done


################### 5- Push results to S3
# aws s3 sync ${tmp_dir}/probtrackx2/ s3://smartontheinside/HCP_1200/$SUBJ/T1w/Diffusion.probtrackx2/


# --dir=${tmp_dir}/probtrackx2/${HEMI} \