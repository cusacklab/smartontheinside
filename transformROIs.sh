#!/bin/bash

dir=/home/chiaracaldinelli/smartontheinside/
dir_roi=/home/chiaracaldinelli/smartontheinside/ROIs/
regs=(seq 1 360)
frontal_regs=( 26 67 68 70 71 73 83 84 85 86 87 97 98 206 247 248 250 251 253 263 264 265 266 267 276 278 )


for roi in ${regs[@]}; do
    if regs>180
    then
        hem=R
    fi
        hem=L
    if [[ -f ${hem}ROI.${roi}.R.nii ]]
        wb_command -label-to-volume-mapping ROI.${roi}.${hem}.label.gii ${hem}Q1-Q6_RelatedParcellation210.${hem}.midthickness_MSMAll_2_d41_WRN_DeDrift.32k_fs_LR.surf.gii ${hem}mean_Rsamples.nii.gz ${hem}ROI.${roi}.R.nii -nearest-vertex 1

done
