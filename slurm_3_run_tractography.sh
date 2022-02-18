
#!/bin/bash
#SBATCH --gpus=1

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
aws s3 sync s3://hcp-openaccess/HCP_1200/$SUBJ/T1w/Diffusion.bedpostX ${tmp_dir}/Diffusion.bedpostX/ --profile hcp
aws s3 cp s3://hcp-openaccess/HCP_1200/$SUBJ/T1w/T1w_acpc_dc.nii.gz ${tmp_dir}/ --profile hcp

# 3- ROI.gii → .nii
# DLPFC mask
for hem in 'L', 'R'; do
    wb_command -label-to-volume-mapping /dhcp/smartontheinside/smartontheinside/frontal.${hem}.label.gii /dhcp/smartontheinside/git/smartontheinside/smartontheinside/Q1-Q6_RelatedParcellation210.${hem}.midthickness_MSMAll_2_d41_WRN_DeDrift.32k_fs_LR.surf.gii ${tmp_dir}/T1w_acpc_dc.nii.gz ${dir}/frontal.${hem}.nii -nearest-vertex 1
    done
# ROIs
mkdir ${tmp_dir}/ROIs/
for roi in {1..15}; do
    wb_command -label-to-volume-mapping /dhcp/smartontheinside/git/smartontheinside/smartontheinside/ROIs/ROI.${roi}.R.label.gii /dhcp/smartontheinside/git/smartontheinside/smartontheinside/Q1-Q6_RelatedParcellation210.R.midthickness_MSMAll_2_d41_WRN_DeDrift.32k_fs_LR.surf.gii ${tmp_dir}/T1w_acpc_dc.nii.gz ${tmp_dir}/ROIs/ROI.${roi}.nii -nearest-vertex 1
    done
#for r in {181..360}; do
#    wb_command -label-to-volume-mapping /dhcp/smartontheinside/git/smartontheinside/smartontheinside/ROI.${roi}.L.label.gii /dhcp/smartontheinside/git/smartontheinside/smartontheinside/Q1-Q6_RelatedParcellation210.L.midthickness_MSMAll_2_d41_WRN_DeDrift.32k_fs_LR.surf.gii ${tmp_dir}/T1w_acpc_dc.nii.gz ${tmp_dir}/ROIs/ROI.${roi}.nii -nearest-vertex 1
#    done
cd ${tmp_dir}/ROIs/
ls > ${tmp_dir}/ROIs/allROIs.txt

# 4- Tractography
for hem in {'L', 'R'}; do
    probtrackx2 --onewaycondition -P 5000 --forcedir --opd --os2t \
	    --rseed=1234 -s ${tmp_dir}/Diffusion.bedpostX/merged \
	    --dir=${tmp_dir}/probtrackx2 \
	    -m ${tmp_dir}/Diffusion.bedpostX/merged/nodif_brain_mask.nii.gz  \
	    --targetmasks=${tmp_dir}/allROIs.txt  \
	    -x ${tmp_dir}/frontal.${hem}.nii \
        -o ${tmp_dir}/probtrackx2_res

# Push results to S3
aws s3 sync ${tmp_dir}/probtrackx2_res/ s3://smartontheinside/HCP_1200/$SUBJ/T1w/Diffusion.probtrackx2/
