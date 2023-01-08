#!/bin/bash

# From the adults mesh space to the infant


# 3- .gii → .nii
# (1a) Map the Glasser surface parcellation into a volume, in adult MNI space. You can use wb_command --label-to-volume. 
# As the surface, use the MNI template surface space not individual data, and as a destination volume space, use $FSLDIR/data/standard/MNI152_T1_1mm_brain.nii.gz


for hemi in L R 
do
    wb_command -label-to-volume-mapping /home/chiaracaldinelli/smartontheinside/ROIs/ff.${hemi}.label.gii Q1-Q6_RelatedParcellation210.L.midthickness_MSMAll_2_d41_WRN_DeDrift.32k_fs_LR.surf.gii $FSLDIR/data/standard/MNI152_T1_1mm_brain.nii.gz /home/chiaracaldinelli/transformations/glasser_parcellation_surf2vol_${hemi}.nii -nearest-vertex 1
done
