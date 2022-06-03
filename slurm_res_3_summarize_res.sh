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


# 1- Create tmp folder
tmp_dir=$(mktemp -d -t chiara-$(date +%Y-%m-%d-%H-%M-%S)-XXXXXXXXXX)
# 2- Sync aws
for subj in 178950 189450 199453 209228 220721 298455 356948 419239 499566 561444 618952 680452 757764 841349 908860 103818 113922 121618 130619 137229 151829 158035 171633 179346 190031 200008 210112 221319 299154 361234 424939 500222 570243 622236 687163 769064 845458 911849 104416 114217 122317 130720 137532 151930 159744 172029 180230 191235 200614 211316 228434 300618 361941 432332 513130 571144 623844 692964 773257 857263 926862 105014 114419 122822 130821 137633 152427 160123 172938 180432 192035 200917 211417 239944 303119 365343 436239 513736 579665 638049 702133 774663 865363 930449 106521 114823 123521 130922 137936 152831 160729 173334 180533 192136 201111 211619 249947 305830 366042 436845 516742 580650 645450 715041 782561 871762 942658 106824 117021 123925 131823 138332 153025 162026 173536 180735 192439 201414 211821 251833 310621 371843 445543 519950 580751 647858 720337 800941 871964 955465 107018 117122 125222 132017 138837 153227 162329 173637 180937 193239 201818 211922 257542 314225 378857 454140 523032 585862 654350 725751 803240 872562 959574 107422 117324 125424 133827 142828 153631 164030 173940 182739 194140 202719 212015 257845 316633 381543 459453 525541 586460 654754 727553 812746 873968 966975; do
    echo "Converting volume to surface for subject $subj"
    aws s3 sync s3://smartontheinside/HCP_1200/$subj/T1w/ROIs/ ${tmp_dir}/ROIs/
    aws s3 cp s3://smartontheinside/HCP_1200/$subj/T1w/frontal.L.nii ${tmp_dir}
    aws s3 cp s3://smartontheinside/HCP_1200/$subj/T1w/frontal.R.nii ${tmp_dir}
    aws s3 cp s3://hcp-openaccess/HCP_1200/$subj/T1w/fsaverage_LR32k/${subj}.L.midthickness_MSMAll.32k_fs_LR.surf.gii ${tmp_dir} --profile hcp
    aws s3 cp s3://hcp-openaccess/HCP_1200/$subj/T1w/fsaverage_LR32k/${subj}.R.midthickness_MSMAll.32k_fs_LR.surf.gii ${tmp_dir} --profile hcp
# 3- volume to surface
    for hem in L R ; do
        wb_command -volume-to-surface-mapping ${tmp_dir}/frontal.${hem}.nii ${tmp_dir}/${subj}.${hem}.midthickness_MSMAll.32k_fs_LR.surf.gii -enclosing ${tmp_dir}/frontal.${hem}.shape.gii
        for roi in {1..360}; do
            wb_command -volume-to-surface-mapping ${tmp_dir}/ROIs/ROI.${roi}.nii ${tmp_dir}/${subj}.${hem}.midthickness_MSMAll.32k_fs_LR.surf.gii -enclosing ${tmp_dir}/ROIs/ROI.${roi}.shape.gii
        done
    done
# 4- Push results to S3
#aws s3 sync ${tmp_dir}/Diffusion.probtrackx2/ s3://smartontheinside/HCP_1200/$SUBJ/T1w/Diffusion.probtrackx2/
    aws s3 cp ${tmp_dir}/frontal.L.shape.gii s3://smartontheinside/HCP_1200/$subj/T1w/frontal.L.shape.gii
    aws s3 cp ${tmp_dir}/frontal.R.shape.gii s3://smartontheinside/HCP_1200/$subj/T1w/frontal.R.shape.gii
    aws s3 sync ${tmp_dir}/ROIs/ s3://smartontheinside/HCP_1200/$subj/T1w/ROIs/
done