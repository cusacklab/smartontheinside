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

def parse_args():
    parser = argparse.ArgumentParser(description='ROI Extraction from HCP Data')

    parser.add_argument('--subject', type=str, default=None, help='HCP subject number')
    parser.add_argument('--profile_name', type=str, default=None, help='Profile in aws credentials')
    parser.add_argument('--output_bucket', type=str, default='neurana-imaging', help='Bucket')
    parser.add_argument('--output_prefix', type=str, default='roi_extract', help='Output prefix')
  
    return parser.parse_args()

import boto3
import base64
from botocore.exceptions import ClientError
import json
import os

def get_aws_hcp_keys():
    # First try environment variables
    print(os.getenv('HCP_KEYS'))
        
    secret_name = "aws/hcp"
    region_name = "eu-west-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        print(e.response['Error']['Code'])
        
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        
        secret = json.loads(get_secret_value_response['SecretString'])
        
    return secret


def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3') # Don't use special profile
    response = s3_client.upload_file(file_name, bucket, object_name)
    print(f'Uploading to bucket {bucket} object_name {object_name}')
    return response

def main(args):
    sub=args.subject
    print(f'Working on subject {sub}')

    hcp_keys = get_aws_hcp_keys()
    session = boto3.Session(aws_access_key_id=hcp_keys['AWS_ACCESS_KEY_ID'], aws_secret_access_key=hcp_keys['AWS_SECRET_ACCESS_KEY'])

    s3 = session.client('s3')

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

    # All ROIS
    roilist = range(1,361)
    # Load up ROI files for L and R
    roi_L_img=nib.load('rois/Q1-Q6_RelatedParcellation210.L.CorticalAreas_dil_Colors.32k_fs_LR.dlabel.nii')
    roi_R_img=nib.load('rois/Q1-Q6_RelatedParcellation210.R.CorticalAreas_dil_Colors.32k_fs_LR.dlabel.nii')
    roi_L_dat=roi_L_img.get_fdata().ravel().astype(int)
    roi_R_dat=180 + roi_R_img.get_fdata().ravel().astype(int)
    roi_dat=np.concatenate((roi_L_dat,roi_R_dat))

    # Handy later 
    nroi = len(roilist)
    ntask = len(taskcondictnoneg)

    # Initialise a space for the output summary values
    meanact={}
    for task, taskcon in taskcondictnoneg.items():
        meanact[task]=np.zeros((len(taskcon), nroi))
        

    # Main loop over contrast files
    for task, taskcon in taskcondictnoneg.items():
        # For each task
        # Download file from HCP S3. 
        hcpbucket = 'hcp-openaccess'
        hcpkey = f'HCP_1200/{sub}/MNINonLinear/Results/{task}/{task}_hp200_s2_level2.feat/{sub}_{task}_level2_hp200_s2.dscalar.nii'
        try:
            s3.download_file(hcpbucket, hcpkey, '/tmp/timeseries.nii')     
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                print(f'Not found on s3 bucket:{hcpbucket} key:{hcpkey}')
                raise
            else:
                print("Unexpected error: %s" % e)
                raise
        except:
            print("Unexpected error: %s" % e)
            raise

        task_img = nib.load('/tmp/timeseries.nii')

        # Pick out only voxels on the cortical surface
        task_dat=task_img.get_fdata()
        task_surfmask=task_img.header.get_axis(1).surface_mask
        task_dat_surf=task_dat[:,task_surfmask]

        # For each ROI, summarise activity in the selected regions and contrasts for this task
        for roiind, roi in enumerate(roilist):
            sel=task_dat_surf[:, roi_dat == roi]
            meanact[task][:, roiind] = np.mean(sel, 1)[taskcon]

    # Write output file
    outfn=f'sub-{sub}_roi.msgpack-numpy'
    outpth='/tmp'
    x_enc = msgpack.packb(meanact, default=m.encode)
    with open(path.join(outpth,outfn),'wb') as f:
        msgpack.dump(meanact, f, default=m.encode)

    # Upload to s3
    print(upload_file(path.join(outpth,outfn), args.output_bucket, path.join(args.output_prefix, outfn)))
        
if __name__=='__main__':
    args = parse_args()
    main(args)

