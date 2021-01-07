# To get ROI file wget https://www.dropbox.com/s/xppiw77mdtb5dls/ResultsRegions_ROI.dlabel.nii
import nibabel as nib
import numpy as np


# These should be DLPFC regions
roilist=[26,67,68,70,71,73,83,84,85,86,87,96,98]
# Also select task contrasts
taskcons=[1,3,77]

nroi=len(roilist)
ntaskcons=len(taskcons)

# Load fMRI task data
task_img=nib.load('Q1-Q6_RelatedParcellation210_tfMRI_ALLTASKS_level3_beta_hp200_s2_MSMAll_2_d41_WRN_DeDrift_norm.dscalar.nii')
task_dat=task_img.get_fdata()
# Find which vertices correspond to the cortex
task_surfmask=task_img.header.get_axis(1).surface_mask
task_dat_surf=task_dat[:,task_surfmask]

roi_img=nib.load('ResultsRegions_ROI.dlabel.nii')
roi_dat=roi_img.get_fdata().ravel()

meanact=np.zeros((ntaskcons,nroi))

for roiind, roi in enumerate(roilist):
    sel=task_dat_surf[:, roi_dat == roi]
    meanact[:, roiind] = np.mean(sel, 1)[taskcons]

print(meanact)

print(meanact.shape)
