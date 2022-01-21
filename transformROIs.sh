#!/bin/bash

dir=/home/chiaracaldinelli/smartonetheinside/smartontheinside


for roi in {1..180}; do
    wb_command -label-to-volume-mapping ${dir}/ROIs/ROI.${roi}.R.label.gii ${dir}/Q1-Q6_RelatedParcellation210.R.midthickness_MSMAll_2_d41_WRN_DeDrift.32k_fs_LR.surf.gii ${dir}/mean_Rsamples.nii.gz /dhcp/smartontheinside/smartontheinside/ROIs/ROI.${roi}.nii -nearest-vertex 1
done

for roi in {181..360}; do
    wb_command -label-to-volume-mapping ${dir}/ROIs/ROI.${roi}.L.label.gii ${dir}/Q1-Q6_RelatedParcellation210.L.midthickness_MSMAll_2_d41_WRN_DeDrift.32k_fs_LR.surf.gii ${dir}/mean_Rsamples.nii.gz /dhcp/smartontheinside/smartontheinside/ROIs/ROI.${roi}.nii -nearest-vertex 1
done
