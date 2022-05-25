#!/bin/bash
#SBATCH --gpus=1

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


# 1- Create tmp folder
tmp_dir=$(mktemp -d -t chiara-$(date +%Y-%m-%d-%H-%M-%S)-XXXXXXXXXX)



# 2- Sync aws
#aws s3 sync s3://smartontheinside/HCP_1200/$SUBJ/T1w/Diffusion.probtrackx2/ ${tmp_dir}/Diffusion.probtrackx2/

aws s3 sync s3://smartontheinside/HCP_1200/$SUBJ/T1w/ROIs/ ${tmp_dir}/ROIs/
aws s3 cp s3://smartontheinside/HCP_1200/$SUBJ/T1w/frontal.L.nii ${tmp_dir}
aws s3 cp s3://smartontheinside/HCP_1200/$SUBJ/T1w/frontal.R.nii ${tmp_dir}
aws s3 cp s3://hcp-openaccess/HCP_1200/$SUBJ/T1w/fsaverage_LR32k/${SUBJ}.L.midthickness_MSMAll.32k_fs_LR.surf.gii ${tmp_dir} --profile hcp
aws s3 cp s3://hcp-openaccess/HCP_1200/$SUBJ/T1w/fsaverage_LR32k/${SUBJ}.R.midthickness_MSMAll.32k_fs_LR.surf.gii ${tmp_dir} --profile hcp


# 3- volume to surface
for hem in L R ; do
    wb_command -volume-to-surface-mapping ${tmp_dir}/frontal.${hem}.nii ${tmp_dir}/${SUBJ}.${hem}.midthickness_MSMAll.32k_fs_LR.surf.gii -enclosing ${tmp_dir}/frontal.${hem}.shape.gii
    
for roi in {1..360}; do
    wb_command -volume-to-surface-mapping ${tmp_dir}/ROIs/ROI.${roi}.nii ${tmp_dir}/${SUBJ}.${hem}.midthickness_MSMAll.32k_fs_LR.surf.gii -enclosing ${tmp_dir}/ROIs/ROI.${roi}.shape.gii
    done

    #for roi in {1..360}; do
        #wb_command -volume-to-surface-mapping ${tmp_dir}/Diffusion.probtrackx2/${hem}/seeds_to_ROI.${roi}.nii.gz ${tmp_dir}/${SUBJ}.${hem}.midthickness_MSMAll.32k_fs_LR.surf.gii -enclosing ${tmp_dir}/Diffusion.probtrackx2/${hem}/seeds_to_ROI.${roi}.shape.gii
        #done
    done




# 4- Push results to S3
#aws s3 sync ${tmp_dir}/Diffusion.probtrackx2/ s3://smartontheinside/HCP_1200/$SUBJ/T1w/Diffusion.probtrackx2/
aws s3 cp ${tmp_dir}/frontal.L.shape.gii s3://smartontheinside/HCP_1200/$SUBJ/T1w/frontal.L.shape.gii
aws s3 cp ${tmp_dir}/frontal.R.shape.gii s3://smartontheinside/HCP_1200/$SUBJ/T1w/frontal.R.shape.gii
aws s3 sync ${tmp_dir}/ROIs/ s3://smartontheinside/HCP_1200/$SUBJ/T1w/ROIs/

