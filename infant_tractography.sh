#!/bin/bash
#SBATCH --gpus=1

# Chiara Caldinelli, caldinec@tcd.ie
# Cusack Lab, Trinity College Dublin

# This code will run tractography from the DLPF area to every single ROI outside it with data from the dHCP.
# This code will:
#   1- Create a tmp folder
#   2- Sync aws: retrieve native data used for step 3 from S3, in a temporary folder
#   3- ROI.gii → ROI.nii
#   4- Tractography


export PATH=/home/chiaracaldinelli/workbench/bin_linux64/:$PATH
export AWS_SHARED_CREDENTIALS_FILE=/home/chiaracaldinelli/.aws/credentials
export AWS_CONFIG_FILE=/home/chiaracalindelli/.aws/config
FSLDIR=/usr/local/fsl
. ${FSLDIR}/etc/fslconf/fsl.sh
PATH=${FSLDIR}/bin:${PATH}
export FSLDIR PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib:/usr/local/cuda/lib64:/usr/local/cuda/extras/CUPTI/lib64:/opt/amazon/efa/lib:/opt/amazon/openmpi/lib:/usr/local/lib:/usr/lib:


# 1- Create tmp folder
tmp_dir=$(mktemp -d -t chiara-$(date +%Y-%m-%d-%H-%M-%S)-XXXXXXXXXX)


# 2- Set dir
dir_bedpost=/dhcp/dhcp_dmri_pipeline/$SUBJ/*/dwi.bedpostX
dir_anat=/dhcp/dhcp_anat_pipeline/$SUBJ/*/anat/*_T1w_biasfield.nii.gz


# 3- ROI.gii → .nii
# DLPFC mask
for hem in L R ; do
    wb_command -label-to-volume-mapping /home/chiaracaldinelli/smartontheinside/ROIs/frontal.${hem}.label.gii /home/chiaracaldinelli/smartontheinside/Q1-Q6_RelatedParcellation210.${hem}.midthickness_MSMAll_2_d41_WRN_DeDrift.32k_fs_LR.surf.gii ${tmp_dir}/Diffusion.bedpostX/nodif_brain_mask.nii.gz ${tmp_dir}/frontal.${hem}.nii -nearest-vertex 1
    done
# ROIs
mkdir ${tmp_dir}/ROIs/
for roi in {1..180}; do
    wb_command -label-to-volume-mapping /home/chiaracaldinelli/smartontheinside/ROIs/ROI.${roi}.R.label.gii /home/chiaracaldinelli/smartontheinside/Q1-Q6_RelatedParcellation210.R.midthickness_MSMAll_2_d41_WRN_DeDrift.32k_fs_LR.surf.gii ${tmp_dir}/Diffusion.bedpostX/nodif_brain_mask.nii.gz ${tmp_dir}/ROIs/ROI.${roi}.nii -nearest-vertex 1
    done
for roi in {181..360}; do
    wb_command -label-to-volume-mapping /home/chiaracaldinelli/smartontheinside/ROIs/ROI.${roi}.L.label.gii /home/chiaracaldinelli/smartontheinside/Q1-Q6_RelatedParcellation210.L.midthickness_MSMAll_2_d41_WRN_DeDrift.32k_fs_LR.surf.gii ${tmp_dir}/Diffusion.bedpostX/nodif_brain_mask.nii.gz ${tmp_dir}/ROIs/ROI.${roi}.nii -nearest-vertex 1
    done

echo "Making list of ROIs"
find "${tmp_dir}/ROIs" -name "*.nii" > ${tmp_dir}/ROIs/allROIs.txt
more ${tmp_dir}/ROIs/allROIs.txt

# See what we've made
echo "Looking in temp directory"
echo ${tmp_dir}
ls ${tmp_dir}


# 4- Tractography
for hem in L R ; do
    mkdir -p ${tmp_dir}/probtrackx2_res/${hem}	
    cmd="probtrackx2_gpu --onewaycondition -P 5000 --forcedir --opd --os2t \
	    --rseed=1234 -s ${tmp_dir}/Diffusion.bedpostX/merged \
	    --dir=${tmp_dir}/probtrackx2/${hem} \
	    -m ${tmp_dir}/Diffusion.bedpostX/nodif_brain_mask.nii.gz  \
	    --targetmasks=${tmp_dir}/ROIs/allROIs.txt  \
	    -x ${tmp_dir}/frontal.${hem}.nii"
    echo $cmd
    eval $cmd
    ls ${tmp_dir}/probtrackx2/${hem}

done


# 5- Push results to S3
aws s3 sync ${tmp_dir}/probtrackx2/ s3://smartontheinside/HCP_1200/$SUBJ/T1w/Diffusion.probtrackx2/
