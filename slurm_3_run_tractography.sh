#!/bin/bash

# Chiara Caldinelli, caldinec@tcd.ie
# Cusack Lab, Trinity College Dublin

# This code will run tractography from the DLPF area to every single ROI outside it. This will be run with a subgroup of the HCP 1200 subjects.
# This code will:
#   1- Create a tmp folder
#   2- Sync aws: retrieve native data used for step 3 from S3, in a temporary folder
#   3- ROI.gii → ROI.nii
#   4- Tractography


dir=/home/chiaracaldinelli/smartonetheinside/smartontheinside


# 1- Create tmp folder
tmp_dir=$(mktemp -d -t chiara-$(date +%Y-%m-%d-%H-%M-%S)-XXXXXXXXXX)


# 2- Sync aws
aws s3 sync s3://hcp-openaccess/HCP_1200/$SUBJ/T1w/T1w_acpc_dc.nii.gz ${tmp_dir}/ --profile hcp
aws s3 sync s3://hcp-openaccess/HCP_1200/$SUBJ/T1w/Diffusion.bedpostX ${tmp_dir}/ --profile hcp 


# 3- ROI.gii → .nii
# DLPFC mask
for hem in {'L', 'R'}; do
    wb_command -label-to-volume-mapping /dhcp/smartontheinside/smartontheinside/frontal.${hem}.label.gii /home/chiaracaldinelli/smartontheinside/smartontheinside/Q1-Q6_RelatedParcellation210.${hem}.midthickness_MSMAll_2_d41_WRN_DeDrift.32k_fs_LR.surf.gii ${dir}/T1w_acpc_dc.nii.gz ${dir}/frontal.${hem}.nii -nearest-vertex 1
# ROIs
for roi in {1..180}; do
    wb_command -label-to-volume-mapping ${tmp_dir}/ROIs/ROI.${roi}.R.label.gii /home/chiaracaldinelli/smartontheinside/smartontheinside/Q1-Q6_RelatedParcellation210.R.midthickness_MSMAll_2_d41_WRN_DeDrift.32k_fs_LR.surf.gii ${tmp_dir}/T1w_acpc_dc.nii.gz ${tmp_dir}ROI.${roi}.nii -nearest-vertex 1
    done
for r in {181..360}; do
    wb_command -label-to-volume-mapping ${tmp_dir}/ROIs/ROI.${roi}.L.label.gii /home/chiaracaldinelli/smartontheinside/smartontheinside/Q1-Q6_RelatedParcellation210.L.midthickness_MSMAll_2_d41_WRN_DeDrift.32k_fs_LR.surf.gii ${tmp_dir}/T1w_acpc_dc.nii.gz ${tmp_dir}/ROI.${roi}.nii -nearest-vertex 1
    done
ls >> ${tmp_dir}/allROIs.txt

# 4- Tractography
for hem in {'L', 'R'}; do
    /usr/local/fsl/bin/probtrackx2 -x /Users/chiara/smartontheinside/frontal.${hem}.nii -l --onewaycondition -c 0.2 -S 2000 --steplength=0.5 -P 5000 --fibthresh=0.01 --distthresh=0.0 --sampvox=0.0 --targetmasks /Users/chiara/smartontheinside/ROIs/allROIs.txt --forcedir --opd -s ${tmp_dir}/Diffusion.bedpostX/merged -m ${tmp_dir}/Diffusion.bedpostX/nodif_brain_mask --dir=/dhcp/smartontheiside/smartontheiside/output_tract_${q}
done
