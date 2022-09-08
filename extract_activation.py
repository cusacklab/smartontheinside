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


# Upload the file
session = boto3.Session(profile_name='hcp')
s3 = session.client('s3')

# s3_client = boto3.client('s3', profile_name='hcp') # Don't use special profile
#response = s3_client.upload_file(file_name, neurana-imaging, object_name)


#hcp_keys = get_aws_hcp_keys()
#session = boto3.Session(aws_access_key_id=hcp_keys['AWS_ACCESS_KEY_ID'], aws_secret_access_key=hcp_keys['AWS_SECRET_ACCESS_KEY'])
#s3 = session.client('s3')


taskcondict = {
        'tfMRI_WM': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29], # 2BK_BODY, 2BK_FACE, 2BK_PLACE, 2BK_TOOL, 0BK_BODY, 0BK_FACE, 0BK_PLACE, 0BK_TOOL, 2BK, 0BK, 2BK-0BK, neg_2BK, neg_0BK, 0BK-2BK, BODY, FACE, PLACE, TOOL, BODY-AVG, FACE-AVG, PLACE-AVG, TOOL-AVG, neg_BODY, neg_FACE, neg_PLACE, neg_TOOL, AVG-BODY, AVG-FACE, AVG-PLACE, VG-TOOL
        'tfMRI_GAMBLING': [0, 1, 2, 3, 4, 5],     # PUNISH, REWARD, PUNISH-REWARD, neg_PUNISH, neg_REWARD, REWARD-PUNISH
        'tfMRI_MOTOR': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],  # CUE, LF, LH, RF, RH, T, AVG, CUE-AVG, LF-AVG, LH-AVG, RF-AVG, RH-AVG, T-AVG, neg_CUE, neg_LF, neg_LH, neg_RF, neg_RH, neg_T, neg_AVG, AVG-CUE, AVG-LF, AVG-LH, AVG-RF, AVG-RH, AVG-T
        'tfMRI_LANGUAGE': [0, 1, 2, 3, 4, 5],     # MATH, STORY, MATH-STORY, STORY-MATH, neg_MATH, neg_STORY
        'tfMRI_SOCIAL': [0, 1, 2, 3, 4, 5],     # RANDOM, TOM, RANDOM-TOM, neg_RANDOM, neg_TOM, TOM-RANDOM
        'tfMRI_RELATIONAL':[0, 1, 2, 3, 4, 5],   # MATCH, REL, MATCH-REL, REL-MATCH, neg_MATCH, neg_REL
        'tfMRI_EMOTION': [0, 1, 2, 3, 4, 5],     # FACES, SHAPES, FACES-SHAPES, neg_FACES, neg_SHAPES, SHAPES-FACES
        }
taskcondictnoneg = {
        'tfMRI_WM': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 14, 15, 16, 17], # 0 2BK_BODY, 1 2BK_FACE, 2 2BK_PLACE, 3 2BK_TOOL, 4 0BK_BODY, 5 0BK_FACE, 6 0BK_PLACE, 7 0BK_TOOL, 8 2BK, 9 0BK, 10 2BK-0BK, 11 neg_2BK, 12 neg_0BK, 13 0BK-2BK, 14 BODY, 15 FACE, 16 PLACE, 17 TOOL, 18 BODY-AVG, 19 FACE-AVG, 20 PLACE-AVG, 21 TOOL-AVG, 22 neg_BODY, 23 neg_FACE, 24 neg_PLACE, 25 neg_TOOL, 26 AVG-BODY, 27 AVG-FACE, 28 AVG-PLACE, 29 VG-TOOL
        'tfMRI_GAMBLING': [0, 1],     # PUNISH, REWARD, PUNISH-REWARD, neg_PUNISH, neg_REWARD, REWARD-PUNISH
        'tfMRI_MOTOR': [0, 1, 2, 3, 4, 5, 6],  # 0 CUE, 1 LF, 2 LH, 3 RF, 4 RH, 5 T, 6 AVG, 7 CUE-AVG, 8 LF-AVG, 9 LH-AVG, 10 RF-AVG, 11 RH-AVG, 12 T-AVG, 13 neg_CUE, 14 neg_LF, 15 neg_LH, 16 neg_RF, 17 neg_RH, 18 neg_T, 19 neg_AVG, 20 AVG-CUE, 21 AVG-LF, 22 AVG-LH, 23 AVG-RF, 24 AVG-RH, 25 AVG-T
        'tfMRI_LANGUAGE': [0, 1],     # MATH, STORY, MATH-STORY, STORY-MATH, neg_MATH, neg_STORY
        'tfMRI_SOCIAL': [0, 1],     # RANDOM, TOM, RANDOM-TOM, neg_RANDOM, neg_TOM, TOM-RANDOM
        'tfMRI_RELATIONAL':[0, 1],   # MATCH, REL, MATCH-REL, REL-MATCH, neg_MATCH, neg_REL
        'tfMRI_EMOTION': [0, 1],     # FACES, SHAPES, FACES-SHAPES, neg_FACES, neg_SHAPES, SHAPES-FACES
        }
subjlist = ['178950','189450','199453','209228','220721','298455','356948','419239','499566','561444','618952','680452','757764','841349','908860', '103818','113922','121618','130619','137229','151829','158035','171633','179346','190031','200008','210112','221319','299154','361234', '424939','500222','570243','622236','687163','769064','845458','911849','104416','114217','122317','130720','137532','151930','159744', '172029','180230','191235','200614','211316','228434','300618','361941','432332','513130','571144','623844','692964','773257','857263', '926862','122822','130821','137633','152427','160123','172938','180432','192035','200917','239944','303119', '365343','436239','513736','579665','638049','702133','774663','865363','930449','106521','114823','123521','130922','137936','152831', '160729','173334','180533','192136','201111','211619','249947','305830','366042','436845','516742','580650','645450','715041','782561', '871762','942658','106824','117021','123925','131823','138332','153025','162026','173536', '180735','192439','201414','211821','251833', '310621','371843','445543','519950','580751','647858','720337','800941','871964','955465','107018','117122','125222','132017','138837', '153227','162329','173637','180937','193239','201818','211922','257542','314225','378857','454140', '523032', '585862','654350','725751', '803240','872562','959574','107422','117324','125424','133827','142828','153631','164030','173940','182739','194140','202719','212015', '257845','316633','381543','459453','525541','586460','654754','727553','812746','873968', '966975']
#'105014', '114419',

# All ROIS
roilist = range(1,361)
# Load up ROI files for L and R
roi_L_img=nib.load('Q1-Q6_RelatedParcellation210.L.CorticalAreas_dil_Colors.32k_fs_LR.dlabel.nii')
roi_R_img=nib.load('Q1-Q6_RelatedParcellation210.R.CorticalAreas_dil_Colors.32k_fs_LR.dlabel.nii')
roi_L_dat=roi_L_img.get_fdata().ravel().astype(int)
roi_R_dat=180 + roi_R_img.get_fdata().ravel().astype(int)
roi_dat=np.concatenate((roi_L_dat,roi_R_dat))


nvox = 59412
nsub=len(subjlist)
ntask = len(taskcondictnoneg)

# Initialise a space for the output summary values
act={}
for task, taskcon in taskcondictnoneg.items():
    act[task]=np.zeros((len(taskcon), nvox))
        
for sub in subjlist:
    print(f'Working on subject {sub}')
    # For each task, download file from HCP S3
    hcpbucket = 'hcp-openaccess'

    # Main loop over contrast files
    for task, taskcons in taskcondictnoneg.items():
        hcpkey = f'HCP_1200/{sub}/MNINonLinear/Results/{task}/{task}_hp200_s2_level2.feat/{sub}_{task}_level2_hp200_s2.dscalar.nii'
        #hcpkey = f'HCP_1200/199453/MNINonLinear/Results/tfMRI_WM/tfMRI_WM_hp200_s2_level2.feat/199453_tfMRI_WM_level2_hp200_s2.dscalar.nii'
        s3.download_file(hcpbucket, hcpkey, '/tmp/timeseries.nii')
        task_img = nib.load('/tmp/timeseries.nii')
        for conind, con in enumerate(taskcons):
            print(f'task {task} con {con}')
            # Pick out only voxels on the cortical surface
            task_dat=task_img.get_fdata()
            task_surfmask=task_img.header.get_axis(1).surface_mask
            task_dat_surf=task_dat[:,task_surfmask]
            act[task][conind] = task_dat_surf[conind]

    # Save dict
    np.save(f'/Users/chiara/{sub}_timeseries.npy', act) 

    # Upload to s3
    #s3.upload_file(f'/Users/chiara/{sub}_timeseries.npy', 'smartontheinside', f'Results/{sub}_timeseries.npy')


    # Load
#read_dictionary = np.load('my_file.npy',allow_pickle='TRUE').item()
#print(read_dictionary['hello']) # displays "world"