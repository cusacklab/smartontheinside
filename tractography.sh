#!/bin/bash

# This code will:
# 1- Create tmp folder
# 2- Sync aws
# 3- ROI.gii → .nii
# 4- Tractography

# 1- Create tmp folder
tmp_dir=$(mktemp -d -t chiara-$(date +%Y-%m-%d-%H-%M-%S)-XXXXXXXXXX)


# 2- Sync aws
aws s3 cp --profile hcp s3://hcp-openaccess/HCP_1200/996782/T1w/T1w_acpc_dc.nii.gz T1w_acpc_dc.nii.gz
aws s3 sync --profile hcp s3://hcp-openaccess/HCP_1200/996782/T1w/Native 996782/T1w/Native
aws s3 sync --profile hcp s3://hcp-openaccess/HCP_1200/996782/T1w/Diffusion.bedpostX 996782/T1w/Diffusion.bedpostX


# 3- ROI.gii → .nii
dir=/home/chiaracaldinelli/smartonetheinside/smartontheinside
for roi in {1..180}; do
    wb_command -label-to-volume-mapping ${dir}/ROIs/ROI.${roi}.L.label.gii ${dir}/Q1-Q6_RelatedParcellation210.L.midthickness_MSMAll_2_d41_WRN_DeDrift.32k_fs_LR.surf.gii ${dir}/mean_Rsamples.nii.gz /dhcp/smartontheinside/smartontheinside/ROIs/ROI.${roi}.L.nii -nearest-vertex 1
done


# 4- Tractography
/usr/local/fsl/bin/probtrackx2 -x /Users/chiara/smartontheinside/frontal.L.nii -l --onewaycondition -c 0.2 -S 2000 --steplength=0.5 -P 5000 --fibthresh=0.01 --distthresh=0.0 --sampvox=0.0 --forcedir --opd -s /Users/chiara/smartontheinside/./merged -m /Users/chiara/smartontheinside/./nodif_brain_mask --dir=/Users/chiara/smartontheinside/tractography-ouput
