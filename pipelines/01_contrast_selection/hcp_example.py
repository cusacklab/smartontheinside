from ecs_control import register_task, run_task, wait_for_completion
import boto3
import msgpack
import msgpack_numpy as m
from os import path
import numpy as np
import pandas as pd


def run_subjects(subjlist, do_wait_for_completion=True, output_bucket='neurana-imaging', output_prefix='hcp-test'):   
    response=[]
    for subj in subjlist:
        response.append(run_task(client, command = ['python3','/app/roi_extract_one_subject.py', "--subject", subj,  "--output_bucket",output_bucket, "--output_prefix",output_prefix ]))
        
    if do_wait_for_completion:
        wait_for_completion(client, response)
    
    return response
    
def get_results(subjlist, output_bucket=None, output_prefix=None):
    session = boto3.session.Session()
    client = session.client('s3')
    allresults={}
    for sub in subjlist:
        outfn=f'sub-{sub}_roi.msgpack-numpy'
        localfn=path.join('/tmp', outfn)
        client.download_file(output_bucket, path.join(output_prefix, outfn),localfn)
        with open(localfn, "rb") as data_file:
            byte_data = data_file.read()
        x_rec = msgpack.unpackb(byte_data, object_hook=m.decode)
        allresults[sub] = x_rec

    return allresults

if __name__=='__main__':
    output_bucket='neurana-imaging'
    output_prefix='hcp_test'
    session = boto3.session.Session()
    client = session.client('ecs', region_name='eu-west-1')
    response = register_task(client)
    subjlist = ['178950','189450','199453','209228','220721','298455','356948','419239','499566','561444','618952','680452','757764','841349','908860', '103818','113922','121618','130619','137229','151829','158035','171633','179346','190031','200008','210112','221319','299154','361234', '424939','500222','570243','622236','687163','769064','845458','911849','104416','114217','122317','130720','137532','151930','159744', '172029','180230','191235','200614','211316','228434','300618','361941','432332','513130','571144','623844','692964','773257','857263', '926862','105014','114419','122822','130821','137633','152427','160123','172938','180432','192035','200917','211417','239944','303119', '365343','436239','513736','579665','638049','702133','774663','865363','930449','106521','114823','123521','130922','137936','152831', '160729','173334','180533','192136','201111','211619','249947','305830','366042','436845','516742','580650','645450','715041','782561', '871762','942658','106824','117021','123925','131823','138332','153025','162026','173536','180735','192439','201414','211821','251833', '310621','371843','445543','519950','580751','647858','720337','800941','871964','955465','107018','117122','125222','132017','138837', '153227','162329','173637','180937','193239','201818','211922','257542','314225','378857','454140','523032','585862','654350','725751', '803240','872562','959574','107422','117324','125424','133827','142828','153631','164030','173940','182739','194140','202719','212015', '257845','316633','381543','459453','525541','586460','654754','727553','812746','873968','966975']
    nsub=len(subjlist)
    response = run_subjects(subjlist, output_bucket=output_bucket, output_prefix=output_prefix)
    allresults=get_results(subjlist, output_bucket=output_bucket, output_prefix=output_prefix )


    taskcondictnoneg = {
        'tfMRI_WM': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 14, 15, 16, 17], # 0 2BK_BODY, 1 2BK_FACE, 2 2BK_PLACE, 3 2BK_TOOL, 4 0BK_BODY, 5 0BK_FACE, 6 0BK_PLACE, 7 0BK_TOOL, 8 2BK, 9 0BK, 10 2BK-0BK, 11 neg_2BK, 12 neg_0BK, 13 0BK-2BK, 14 BODY, 15 FACE, 16 PLACE, 17 TOOL, 18 BODY-AVG, 19 FACE-AVG, 20 PLACE-AVG, 21 TOOL-AVG, 22 neg_BODY, 23 neg_FACE, 24 neg_PLACE, 25 neg_TOOL, 26 AVG-BODY, 27 AVG-FACE, 28 AVG-PLACE, 29 VG-TOOL
        'tfMRI_GAMBLING': [0, 1],     # PUNISH, REWARD, PUNISH-REWARD, neg_PUNISH, neg_REWARD, REWARD-PUNISH
        'tfMRI_MOTOR': [0, 1, 2, 3, 4, 5, 6],  # 0 CUE, 1 LF, 2 LH, 3 RF, 4 RH, 5 T, 6 AVG, 7 CUE-AVG, 8 LF-AVG, 9 LH-AVG, 10 RF-AVG, 11 RH-AVG, 12 T-AVG, 13 neg_CUE, 14 neg_LF, 15 neg_LH, 16 neg_RF, 17 neg_RH, 18 neg_T, 19 neg_AVG, 20 AVG-CUE, 21 AVG-LF, 22 AVG-LH, 23 AVG-RF, 24 AVG-RH, 25 AVG-T
        'tfMRI_LANGUAGE': [0, 1],     # MATH, STORY, MATH-STORY, STORY-MATH, neg_MATH, neg_STORY
        'tfMRI_SOCIAL': [0, 1],     # RANDOM, TOM, RANDOM-TOM, neg_RANDOM, neg_TOM, TOM-RANDOM
        'tfMRI_RELATIONAL':[0, 1],   # MATCH, REL, MATCH-REL, REL-MATCH, neg_MATCH, neg_REL
        'tfMRI_EMOTION': [0, 1],     # FACES, SHAPES, FACES-SHAPES, neg_FACES, neg_SHAPES, SHAPES-FACES
        }
    taskcondict = {
        'tfMRI_WM': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29], # 2BK_BODY, 2BK_FACE, 2BK_PLACE, 2BK_TOOL, 0BK_BODY, 0BK_FACE, 0BK_PLACE, 0BK_TOOL, 2BK, 0BK, 2BK-0BK, neg_2BK, neg_0BK, 0BK-2BK, BODY, FACE, PLACE, TOOL, BODY-AVG, FACE-AVG, PLACE-AVG, TOOL-AVG, neg_BODY, neg_FACE, neg_PLACE, neg_TOOL, AVG-BODY, AVG-FACE, AVG-PLACE, VG-TOOL
        'tfMRI_GAMBLING': [0, 1, 2, 3, 4, 5],     # PUNISH, REWARD, PUNISH-REWARD, neg_PUNISH, neg_REWARD, REWARD-PUNISH
        'tfMRI_MOTOR': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],  # CUE, LF, LH, RF, RH, T, AVG, CUE-AVG, LF-AVG, LH-AVG, RF-AVG, RH-AVG, T-AVG, neg_CUE, neg_LF, neg_LH, neg_RF, neg_RH, neg_T, neg_AVG, AVG-CUE, AVG-LF, AVG-LH, AVG-RF, AVG-RH, AVG-T
        'tfMRI_LANGUAGE': [0, 1, 2, 3, 4, 5],     # MATH, STORY, MATH-STORY, STORY-MATH, neg_MATH, neg_STORY
        'tfMRI_SOCIAL': [0, 1, 2, 3, 4, 5],     # RANDOM, TOM, RANDOM-TOM, neg_RANDOM, neg_TOM, TOM-RANDOM
        'tfMRI_RELATIONAL':[0, 1, 2, 3, 4, 5],   # MATCH, REL, MATCH-REL, REL-MATCH, neg_MATCH, neg_REL
        'tfMRI_EMOTION': [0, 1, 2, 3, 4, 5],     # FACES, SHAPES, FACES-SHAPES, neg_FACES, neg_SHAPES, SHAPES-FACES
        }


    DLPFroilist = [26, 67, 68, 70, 71, 73, 83, 84, 85, 86, 87, 96, 98, 206, 247, 248, 250, 251, 253, 263, 264, 265, 266, 267, 276, 278]
    nDLPFroi = len(DLPFroilist)
    topROI = {}
    
    indexDF = ['WORKING_MEM_2BK_BODY', 'WORKING_MEM_2BK_FACE', 'WORKING_MEM_2BK_PLACE', 'WORKING_MEM_2BK_TOOL', 'WORKING_MEM_0BK_BODY', 'WORKING_MEM_0BK_FACE', 'WORKING_MEM_0BK_PLACE', 'WORKING_MEM_0BK_TOOL', 'WORKING_MEM_2BK', 'WORKING_MEM_0BK', 'WORKING_MEM_2BK-0BK', 'WORKING_MEM_neg_2BK', 'WORKING_MEM_neg_0BK', 'WORKING_MEM_0BK-2BK', 'WORKING_MEM_BODY', 'WORKING_MEM_FACE', 'WORKING_MEM_PLACE', 'WORKING_MEM_TOOL', 'WORKING_MEM_BODY-AVG', 'WORKING_MEM_FACE-AVG', 'WORKING_MEM_PLACE-AVG', 'WORKING_MEM_TOOL-AVG', 'WORKING_MEM_neg_BODY', 'WORKING_MEM_neg_FACE', 'neg_PLACE', 'WORKING_MEM_neg_TOOL', 'WORKING_MEM_AVG-BODY', 'WORKING_MEM_AVG-FACE', 'WORKING_MEM_AVG-PLACE', 'WORKING_MEM_VG-TOOL', 'GAMBLING_PUNISH', 'GAMBLING_REWARD', 'GAMBLING_PUNISH-REWARD', 'GAMBLING_neg_PUNISH', 'GAMBLING_neg_REWARD', 'GAMBLING_REWARD-PUNISH', 'MOTOR_CUE', 'MOTOR_LF', 'MOTOR_LH', 'MOTOR_RF', 'MOTOR_RH', 'MOTOR_T', 'MOTOR_AVG', 'MOTOR_CUE-AVG', 'MOTOR_LF-AVG', 'MOTOR_LH-AVG', 'MOTOR_RF-AVG', 'MOTOR_RH-AVG', 'MOTOR_T-AVG', 'MOTOR_neg_CUE', 'MOTOR_neg_LF', 'MOTOR_neg_LH', 'MOTOR_neg_RF', 'MOTOR_neg_RH', 'MOTOR_neg_T', 'MOTOR_neg_AVG', 'MOTOR_AVG-CUE', 'MOTOR_AVG-LF', 'MOTOR_AVG-LH', 'MOTOR_AVG-RF', 'MOTOR_AVG-RH', 'MOTOR_AVG-T', 'LANGUAGE_MATH', 'LANGUAGE_STORY', 'LANGUAGE_MATH-STORY', 'LANGUAGE_STORY-MATH', 'LANGUAGE_neg_MATH', 'LANGUAGE_neg_STORY', 'SOCIAL_RANDOM', 'SOCIAL_TOM', 'SOCIAL_RANDOM-TOM', 'SOCIAL_neg_RANDOM', 'SOCIAL_neg_TOM', 'SOCIAL_TOM-RANDOM', 'RELATIONAL_MATCH', 'RELATIONAL_REL', 'RELATIONAL_MATCH-REL', 'RELATIONAL_REL-MATCH', 'RELATIONAL_neg_MATCH', 'RELATIONAL_neg_REL', 'EMOTION_FACES', 'EMOTION_SHAPES', 'EMOTION_FACES-SHAPES', 'EMOTION_neg_FACES', 'EMOTION_neg_SHAPES', 'EMOTION_SHAPES-FACES']
    indexDFnoneg = ['WORKING_MEM_2BK_BODY', 'WORKING_MEM_2BK_FACE', 'WORKING_MEM_2BK_PLACE', 'WORKING_MEM_2BK_TOOL', 'WORKING_MEM_0BK_BODY', 'WORKING_MEM_0BK_FACE', 'WORKING_MEM_0BK_PLACE', 'WORKING_MEM_0BK_TOOL', 'WORKING_MEM_2BK', 'WORKING_MEM_0BK', 'WORKING_MEM_BODY', 'WORKING_MEM_FACE', 'WORKING_MEM_PLACE', 'WORKING_MEM_TOOL', 'GAMBLING_PUNISH', 'GAMBLING_REWARD','MOTOR_CUE', 'MOTOR_LF', 'MOTOR_LH', 'MOTOR_RF', 'MOTOR_RH', 'MOTOR_T', 'MOTOR_AVG',  'LANGUAGE_MATH', 'LANGUAGE_STORY',  'SOCIAL_RANDOM', 'SOCIAL_TOM', 'RELATIONAL_MATCH', 'RELATIONAL_REL', 'EMOTION_FACES', 'EMOTION_SHAPES']   

    ncon = len(indexDFnoneg)
    DLPFtoproi = np.zeros((len(subjlist),ncon,nDLPFroi)) # Create a matrix for storing DLPFC ROIs' values
    
    newlist = []
    for task, taskcons in taskcondictnoneg.items():
        for conind, con in enumerate(taskcons):
            print(f'task {task} con {con}')
            dat = np.vstack([allresults[subj][task][conind,:] for subj in allresults])
            # take mean across subjects
            mnact = np.mean(dat, axis=0)
            newlist.append(mnact)
            # use argsort along roi axis to find top rois         
            sortedregions = np.argsort(mnact)
            topROI = sortedregions[-3:]
            file = open(('TopROI.txt'),'a') 
            file.write("\n The 3 most active ROIs for task %s, contrast %s are %s"%(task,con,topROI))
            file.close()

    for sub in range(nsub):
        for roi in range(nDLPFroi):
            listcon = []
            for task, taskcons in taskcondictnoneg.items():
                for conind, con in enumerate(taskcons):
                    print(f'task {task} con {con}')
                    dat = np.vstack([allresults[subj][task][conind,:] for subj in allresults])
                    data = dat[sub]
                    listcon.append(data[(DLPFroilist[roi])])
            DLPFtoproi[sub,:,roi] = listcon 


    file = open(('TopROI.txt'),'a') 
    file.write("\n ************************")
    file.close()

    np.save(("allresults.npy"), allresults)
    np.save(("topROI.npy"), topROI)  
    np.save(("DLPFCroi.npy"), DLPFtoproi)