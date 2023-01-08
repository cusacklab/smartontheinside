#!/bin/bash

# From the adults mesh space to the infant


# inmesh=/dhcp/dhcp_anat_pipeline/sub-${subjid}/ses-$session/anat/Native/sub-${subjid}_ses-${session}_left_sphere.rot.surf.gii #needs to be a sphere
inmesh=/dhcp/dhcp_anat_pipeline/sub-CC00221XX07/ses-75000/anat/sub-CC00221XX07_ses-75000_hemi-L_space-T2w_sphere.surf.gii #needs to be a sphere

refmesh=/dhcp/rhodri_registration/atlases/dhcp_surface/dHCP.week40.L.sphere.surf.gii
refdata=/dhcp/rhodri_registration/atlases/dhcp_surface/dHCP.week40.L.sulc.shape.gii
indata=/dhcp/dhcp_anat_pipeline/sub-CC00221XX07/ses-75000/anat/sub-CC00221XX07_ses-75000_hemi-L_space-T2w_sulc.shape.gii
outname=/home/chiaracaldinelli/sub-${subjid}_ses-${session}_left_


for subjind in CC00221XX07 ; do
msm --inmesh=${inmesh} --refmesh=${refmesh} --indata=${indata} --refdata=${refdata} --out=${outname} --verbose
done