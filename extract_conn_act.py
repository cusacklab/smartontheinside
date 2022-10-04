import boto3
import nilearn
import nibabel as nib
import numpy as np
from matplotlib import pyplot as plt
import logging
from botocore.exceptions import ClientError
import argparse
import msgpack
import msgpack_numpy as m
from os import path
import boto3
import base64
from botocore.exceptions import ClientError
import json
import os
from numpy import absolute
import pandas as pd
from os.path import exists as file_exists

subjlist = [ '199453', '209228', '114419']
#subjlist = ['178950','189450','220721','298455','356948','419239','499566','561444','618952','680452','757764','841349','908860', '103818','113922','121618','130619','137229','151829','158035','171633','179346','190031','200008','210112','221319','299154','361234', '424939','500222','570243','622236','687163','769064','845458','911849','104416', '114217','122317','130720','137532','151930','159744', '172029','180230','191235','200614','211316','228434','300618','361941','432332','513130','571144','623844','692964','773257','857263', '926862','122822','130821','137633','152427','160123','172938','180432','192035','200917','239944','303119', '365343','436239','513736','579665','638049','702133','774663','865363','930449','106521','114823','123521','130922','137936','152831', '160729','173334','180533','192136','201111','211619','249947','305830','366042','436845','516742','580650','645450','715041','782561', '871762','942658','106824','117021','123925','131823','138332','153025','162026','173536', '180735','192439','201414','211821','251833', '310621','371843','445543','519950','580751','647858','720337','800941','871964','955465','107018','117122','125222','132017','138837', '153227','162329','173637','180937','193239','201818','211922','257542','314225','378857','454140', '523032', '585862','654350','725751', '803240','872562','959574','107422','117324','125424','133827','142828','153631','164030','173940','182739','194140','202719','212015', '257845','316633','381543','459453','525541','586460','654754','727553','812746','873968', '966975', '105014']
#subjlist = ['114419']
#['199453'] '209228',
nsub = len(subjlist)

# All ROIS
roilist = range(1,361)
# Load up ROI files for L and R
roi_L_img=nib.load('Q1-Q6_RelatedParcellation210.L.CorticalAreas_dil_Colors.32k_fs_LR.dlabel.nii')
roi_R_img=nib.load('Q1-Q6_RelatedParcellation210.R.CorticalAreas_dil_Colors.32k_fs_LR.dlabel.nii')
roi_L_dat=roi_L_img.get_fdata().ravel().astype(int)
roi_R_dat=180 + roi_R_img.get_fdata().ravel().astype(int)
roi_dat=np.concatenate((roi_L_dat,roi_R_dat))

# Selection of contrasts - based on previous analysis
taskcondict_selected = {
        'tfMRI_WM': [8], # 8 2BK
        'tfMRI_MOTOR': [6],  # 6 AVG
        'tfMRI_LANGUAGE': [1],     #  STORY
        'tfMRI_SOCIAL': [1],     # TOM
        'tfMRI_EMOTION': [1]     # SHAPES
        }

# Credentials for uploading data to the cusack lab s3
session = boto3.Session(profile_name='default')
s3 = session.client('s3')

# Name of ROIs in the DLPFC
frontalregs_right=[73,67,97,98,26,70,71,87,68,83,85,84,86] # All the ROIs in the right DLPFC regions
frontalregs_right.sort() #  1-180 is right, 181-360 is left
frontalregs_left=[x+180 for x in frontalregs_right]
frontalregs_left.sort()
DLPFroilist = frontalregs_right + frontalregs_left
nDLPFroi = len(frontalregs_right)
nvox = 177



# CONNECTIVITY # 
############################################################################################################
# Produce a file for each sub containing the number of streamlines originating from every ROI in the DLPFC #
############################################################################################################


'''''''''
for sub in range(nsub):
    print(f'Working on subject {subjlist[sub]} tractography data')

    for hemiind, hemi in enumerate(['R','L']):
        img=nib.load(f'ff.{hemi}.label.gii') # Load label file 
        labels=img.labeltable.get_labels_as_dict()
        dat = img.agg_data('NIFTI_INTENT_LABEL') # dat contains ROI and voxels' coordinates

        # Count number of voxels in all of the seeds in this hemi
        if hemiind ==0:
            nseedvox = np.sum([np.sum(dat==frontalregs_right[seed_roi]) for seed_roi in range(len(frontalregs_right))])
        else:
            nseedvox = np.sum([np.sum(dat==frontalregs_left[seed_roi]) for seed_roi in range(len(frontalregs_left))])

        vox_res = np.zeros((361, nseedvox))
        roi_res = np.zeros((nsub, 361, nDLPFroi))

        #all_seed_values = np.array(all_seed_values)
        for target_roi in range(1, 361): # For every target ROI (334 in total)
            if not target_roi in frontalregs_right:
                if not target_roi in frontalregs_left:
                    remotepath = f'HCP_1200/{subjlist[sub]}/T1w/Diffusion.probtrackx2/{hemi}/seeds_to_ROI.{target_roi}.shape.gii'
                    # Credentials for uploading data to the cusack lab s3
                    session = boto3.Session(profile_name='default')
                    s3 = session.client('s3')
                    bucket = 'smartontheinside'

                    #print(f'Downloading file {remotepath}')
                    s3.download_file(bucket, remotepath, f'/Users/chiara/{subjlist[sub]}_seeds_to_ROI.{target_roi}.shape.gii') 
                    img_s2t = nib.load(f'/Users/chiara/{subjlist[sub]}_seeds_to_ROI.{target_roi}.shape.gii')  
                    dat_s2t = img_s2t.agg_data() # dat_s2t has tractography results
                    all_seed_values=[]
                    
                    for seed_roi in range(len(frontalregs_right)): # for every ROI in the DLPFC    
                        if hemiind == 0:
                            seed_values=dat_s2t[dat==(frontalregs_right[seed_roi])]
                            coord = (dat==(frontalregs_right[seed_roi]))
                            true_count = sum(coord)
                            
                        else:
                            seed_values=dat_s2t[dat==(frontalregs_left[seed_roi])]
                        #print(len(seed_values))
                        all_seed_values.extend(seed_values)
                    

                        if file_exists(f'/home/chiaracaldinelli/{subjlist[sub]}_seeds_to_ROI.{target_roi}.shape.gii'):
                            os.remove(f'/home/chiaracaldinelli/{subjlist[sub]}_seeds_to_ROI.{target_roi}.shape.gii')
                        if hemiind == 0:
                            roi_res[sub, target_roi, seed_roi] = np.mean(seed_values)
                        else:
                            roi_res[sub, target_roi, seed_roi+13] = np.mean(seed_values)
                    #print(f'hemi is {hemi}')
                    vox_res[target_roi, :] = all_seed_values    

        np.save((f'/Users/chiara/{subjlist[sub]}_tractography_results_VOXEL_{hemi}.npy'), vox_res)
    np.save((f'/Users/chiara/{subjlist[sub]}_tractography_results_ROI.npy'), roi_res)

    s3.upload_file(f'/Users/chiara/{subjlist[sub]}_tractography_results_VOXEL_L.npy', 'smartontheinside', f'HCP_1200/{subjlist[sub]}/T1w/Diffusion.probtrackx2/{subjlist[sub]}_tractography_results_VOXEL_L.npy')
    s3.upload_file(f'/Users/chiara/{subjlist[sub]}_tractography_results_VOXEL_R.npy', 'smartontheinside', f'HCP_1200/{subjlist[sub]}/T1w/Diffusion.probtrackx2/{subjlist[sub]}_tractography_results_VOXEL_R.npy')
    s3.upload_file(f'/Users/chiara/{subjlist[sub]}_tractography_results_ROI.npy', 'smartontheinside', f'HCP_1200/{subjlist[sub]}/T1w/Diffusion.probtrackx2/{subjlist[sub]}ROI.npy')

    
    os.remove(f'/Users/chiara/{subjlist[sub]}_tractography_results_VOXEL_L.npy')
    os.remove(f'/Users/chiara/{subjlist[sub]}_tractography_results_VOXEL_R.npy')
    os.remove(f'/Users/chiara/{subjlist[sub]}_tractography_results_ROI.npy')

'''''''''

# ACTIVATION # 
#################################################################################################
# Produce a file for each sub containing the activation for each vertex in each ROI of the DLPC #
#################################################################################################

#I found these files with the MSMall registered activations:
#s3://hcp-openaccess/HCP_1200/996782/MNINonLinear/Results/tfMRI_MOTOR/tfMRI_MOTOR_hp200_s2_level2_MSMAll.feat/996782_tfMRI_MOTOR_level2_hp200_s2_MSMAll.dscalar.nii

#These files can be split like this
#wb_command -cifti-separate 996782_tfMRI_MOTOR_level2_hp200_s2_MSMAll.dscalar.nii COLUMN  -metric CORTEX_LEFT m1_L.func.gii           
#wb_command -cifti-separate 996782_tfMRI_MOTOR_level2_hp200_s2_MSMAll.dscalar.nii COLUMN  -metric CORTEX_RIGHT  m1_R.func.gii   

# Credentials for uploading data to the cusack lab s3
session = boto3.Session(profile_name='default')
s3 = session.client('s3')
bucket = 'smartontheinside'

# Main loop over contrast files
for task, taskcons in taskcondict_selected.items():
    print(f'task {task}')
    for hemiind, hemi in enumerate(['R','L']):
        act = dict()
        act = np.zeros((nsub,nDLPFroi,nvox))
        act = dict.fromkeys(DLPFroilist)
        act_ROI = np.zeros((nsub,nDLPFroi))
        for subind, sub in enumerate(subjlist):
            # Credentials for HCP data
            #session = boto3.Session(profile_name='hcp')
            #s3 = session.client('s3')
            #hcpbucket = 'hcp-openaccess'
            #print(f'Working on subject {sub} fMRI data, task {task}')
            
            # For each task, download file from HCP S3
            hcpkey = f'/Results/{sub}_{task}_WM_m1_{hemi}.func.gii'
            print(hcpkey)
            s3.download_file(bucket, hcpkey, f'/Users/chiara/{sub}_{task}_WM_m1_{hemi}.func.gii')
            task_img = nib.load(f'{sub}_{task}_WM_m1_{hemi}.func.gii')

            for conind, con in enumerate(taskcons):
                # Pick out only voxels on the cortical surface
                task_dat=task_img.get_fdata()
                task_surfmask=task_img.header.get_axis(1).surface_mask
                task_dat_surf=task_dat[:,task_surfmask]
                all_seed_values=[]

                # NON HO CAPITO COSA FA QUESTO, COMINCIA DA QUI
                for seed_roi in range(len(frontalregs_right)): # for every ROI in the DLPFC    
                    if hemiind == 0:
                        sel = task_dat_surf[roi_dat == frontalregs_right[seed_roi]][con]

                        seed_values=dat_s2t[dat==(frontalregs_right[seed_roi])]
                        coord = (dat==(frontalregs_right[seed_roi]))
                        true_count = sum(coord)       
                    else:
                        sel = task_dat_surf[roi_dat == frontalregs_left[seed_roi]][con]
                    all_seed_values.extend(seed_values)

                # remove this!!!!
                #for roiind, roi in enumerate(DLPFroilist):
                #    sel = task_dat_surf[:, roi_dat == roi][con]
                #    act[roi] = sel


                    act_ROI[subind,seed_roi] = np.mean(sel)
                # Save dict
                np.save(f'/Users/chiara/{task}_{sub}_{hemi}_tfmri.npy', act) 
                np.save(f'/Users/chiara/{task}_{sub}_{hemi}_tfmri_ROI.npy', act_ROI) 



            # Upload to s3
            s3.upload_file(f'/Users/chiara/{task}_{sub}_{hemi}tfmri.npy', 'smartontheinside', f'Results/{task}_{sub}_{hemi}tfmri_ROI.npy')
            s3.upload_file(f'/Users/chiara/{task}_{sub}_{hemi}tfmri_ROI.npy', 'smartontheinside', f'Results/{task}_{sub}_{hemi}tfmri_ROI')
            os.remove(f'/Users/chiara/{task}_{sub}_{hemi}tfmri_ROI.npy')