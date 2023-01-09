#!/bin/bash

# From the adults mesh space to the infant


 

# for hemi in L R 
# do

#     # (1a) Map the Glasser surface parcellation into a volume, in adult MNI space using wb_command
#     wb_command -label-to-volume-mapping /home/chiaracaldinelli/smartontheinside/smartontheinside/ff.${hemi}.label.gii Q1-Q6_RelatedParcellation210.${hemi}.midthickness_MSMAll_2_d41_WRN_DeDrift.32k_fs_LR.surf.gii $FSLDIR/data/standard/MNI152_T1_1mm_brain.nii.gz /home/chiaracaldinelli/smartontheinside/smartontheinside/results/transformations/glasser_parcellation_surf2vol_${hemi}.nii -nearest-vertex 1


#     # (1b) Transform the resulting label volume into the infant space using ants
#     antsApplyTransforms -i /home/chiaracaldinelli/smartontheinside/smartontheinside/results/transformations/glasser_parcellation_surf2vol_${hemi}.nii -r /dhcp/rhodri_registration/atlases/dhcp_volume_40weeks/template_t1.nii.gz -t [/dhcp/rhodri_registration/analysis_2020-20-29/antsreg_t1_nodura_nocerebllum_in_template0GenericAffine.mat,1] -t /dhcp/rhodri_registration/analysis_2020-20-29/antsreg_t1_nodura_nocerebllum_in_template1Warp.nii.gz -o glasser_labels_dhcp_40weeks_${hemi}.nii.gz --interpolation NearestNeighbor

# done


# (2) dhcp template->dhcp individuals

# Applying the transforms using fsl's applywarp to/from the template volume space. So, for example, to transform from glasser_labels_dhcp_40weeks.nii.gz created in stage one to the individual baby. 
# Nearest neighbour interpolation as it is a label map. Registration between the individual space label map and the DTI data for that baby to be checked

for SUBJ in CC00907XX16; do
    for SES in 4230; do
        for hemi in L R ; do

            applywarp -i glasser_labels_dhcp_40weeks_${hemi}.nii.gz -o glasser_labels_dhcp_40weeks_sub${SUBJ}.nii.gz -r /dhcp/dhcp_dmri_pipeline/sub-CC00907XX16/ses-4230/dwi/nodif_brain_mask.nii.gz -w /dhcp/dhcp_dmri_pipeline/sub-${SUBJ}/ses-4230/xfm/sub-${SUBJ}_ses-4230_from-template40wk_to-dwi_mode-image.nii.gz --interp=nn -v
        done
    done
done
