# To get ROI file wget https://www.dropbox.com/s/xppiw77mdtb5dls/ResultsRegions_ROI.dlabel.nii
import nibabel as nib
import numpy as np


# These should be DLPFC regions
roilist=[26, 67, 68, 70, 71, 73, 83, 84, 85, 86, 87, 96, 98]
# Selecting these task contrasts: 'tfMRI_WM_2BK','tfMRI_WM_0BK', 'tfMRI_WM_BODY', 'tfMRI_WM_FACE', 'tfMRI_WM_PLACE', 'tfMRI_WM_TOOL', 'tfMRI_GAMBLING_PUNISH',
#'tfMRI_GAMBLING_REWARD', 'tfMRI_MOTOR_CUE', 'tfMRI_MOTOR_LF', 'tfMRI_MOTOR_LH', 'tfMRI_MOTOR_RF', 'tfMRI_MOTOR_RH', 'tfMRI_MOTOR_T', 'tfMRI_LANGUAGE_MATH', 
#'tfMRI_LANGUAGE_STORY', 'tfMRI_SOCIAL_RANDOM', 'tfMRI_SOCIAL_TOM', 'tfMRI_RELATIONAL_MATCH', 'tfMRI_RELATIONAL_REL', 'tfMRI_EMOTION_FACES', 'tfMRI_EMOTION_SHAPES'
taskcons=[8, 9, 14, 15, 16, 17, 30, 31, 36, 37, 38, 39, 40, 41, 62, 63, 68, 69, 80, 81] 


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
