import boto3
from matplotlib.widgets import SubplotTool
import nibabel as nib
import numpy as np 
import os
from os.path import exists as file_exists
import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm

### POOL SUBJECTS
subjlist = ['178950','189450','199453','209228','220721','298455','356948','419239','499566','561444','618952','680452','757764','841349','908860', '103818','113922','121618','130619','137229','151829','158035','171633','179346','190031','200008','210112','221319','299154','361234', '424939','500222','570243','622236','687163','769064','845458','911849','104416','114217','122317','130720','137532','151930','159744', '172029','180230','191235','200614','211316','228434','300618','361941','432332','513130','571144','623844','692964','773257','857263', '926862','122822','130821','137633','152427','160123','172938','180432','192035','200917','239944','303119', '365343','436239','513736','579665','638049','702133','774663','865363','930449','106521','114823','123521','130922','137936','152831', '160729','173334','180533','192136','201111','211619','249947','305830','366042','436845','516742','580650','645450','715041','782561', '871762','942658','106824','117021','123925','131823','138332','153025','162026','173536','180735','192439','201414','211821','251833', '310621','371843','445543','519950','580751','647858','720337','800941','871964','955465','107018','117122','125222','132017','138837', '153227','162329','173637','180937','193239','201818','211922','257542','314225','378857','454140', '523032', '585862','654350','725751', '803240','872562','959574','107422','117324','125424','133827','142828','153631','164030','173940','182739','194140','202719','212015', '257845','316633','381543','459453','525541','586460','654754','727553','812746','873968','966975']
#'105014', '114419', 
nsub=len(subjlist)
s3 = boto3.client('s3')
listcon = ['WORKING_MEM_2BK_BODY', 'WORKING_MEM_2BK_FACE', 'WORKING_MEM_2BK_PLACE', 'WORKING_MEM_2BK_TOOL', 'WORKING_MEM_0BK_BODY', 'WORKING_MEM_0BK_FACE', 'WORKING_MEM_0BK_PLACE', 'WORKING_MEM_0BK_TOOL', 'WORKING_MEM_2BK', 'WORKING_MEM_0BK', 'WORKING_MEM_BODY', 'WORKING_MEM_FACE', 'WORKING_MEM_PLACE', 'WORKING_MEM_TOOL', 'GAMBLING_PUNISH', 'GAMBLING_REWARD','MOTOR_CUE', 'MOTOR_LF', 'MOTOR_LH', 'MOTOR_RF', 'MOTOR_RH', 'MOTOR_T', 'MOTOR_AVG',  'LANGUAGE_MATH', 'LANGUAGE_STORY',  'SOCIAL_RANDOM', 'SOCIAL_TOM', 'RELATIONAL_MATCH', 'RELATIONAL_REL', 'EMOTION_FACES', 'EMOTION_SHAPES']  
ncon=len(listcon)
# Load results from previous analysis -  subjs are already pooled
# allresults is activation?
# topROI is the ranking of the most active ROIs
# DLPFtoproi is the ranking of the most active ROIs of the DLPFC
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

allresults = np.load('/home/chiaracaldinelli/smartonetheinside/allresults.npy', allow_pickle=True).ravel()[0]

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

DLPFroilistplot = ['26', '67', '68', '70', '71', '73', '83', '84', '85', '86', '87', '96', '98', '206', '247', '248', '250', '251', '253', '263', '264', '265', '266', '267', '276', '278']
mean_act_DLPF = np.load('/home/chiaracaldinelli/smartontheinside/DLPFCroi.npy')
mean_act_DLPF=np.mean(mean_act_DLPF,axis=0)

array_r = np.zeros([360, 13, nsub])
array_l = np.zeros([360, 13, nsub])
mean_conn_DLPF_r = np.zeros([360, 13])
mean_conn_DLPF_l = np.zeros([360, 13])

# For every sub, download the results and put all of them together
for sub in range(nsub):
    # Download files
    s3.download_file('smartontheinside', f'HCP_1200/{subjlist[sub]}/T1w/Diffusion.probtrackx2/{subjlist[sub]}_tractography_results_ROI.npy', f'/home/chiaracaldinelli/{subjlist[sub]}_tractography_results_ROI.npy')
    s3.download_file('smartontheinside', f'HCP_1200/{subjlist[sub]}/T1w/Diffusion.probtrackx2/{subjlist[sub]}_tractography_results_ROI.npy', f'/home/chiaracaldinelli/{subjlist[sub]}_tractography_results_VOXEL.npy')
    print(f'Downloading participant {subjlist[sub]}')
    # Load results
    x = np.load(f'/home/chiaracaldinelli/{subjlist[sub]}_tractography_results_ROI.npy',allow_pickle=True)
    x = np.ravel(x)[0]
    # Create an array to load the results for each hemisphere

    r = (x['R'])
    array_r[:,:,sub] = r
    l = (x['L'])
    array_l[:,:,sub] = l
mean_conn_DLPF_r = np.mean(array_r, axis=2)
mean_conn_DLPF_l = np.mean(array_l, axis=2)



#The most different contrasts from the previous analysis were: emotion-shape, language-story, motor-avg, social-tom, and working-mem-2bk. 
# Top ROIs for these contrasts: 
# 'EMOTION_SHAPES' (Emotion Con 1): [198 199 337]   'LANGUAGE_STORY' (Language Con 1): [173 124 304]   'MOTOR_AVG' (Motor Con 6): [235  42  55] 'SOCIAL_TOM' (Social Con 1): [335   1 181]   'WORKING_MEM_2BK' (WM Con 8): [201 186   6]


# 'EMOTION_SHAPES' (Emotion Con 1): [198 199 337]   
plt.figure()
mean_conn_DLPF_198 = np.zeros([26])
mean_conn_DLPF_198[0:13] = mean_conn_DLPF_r[197,:]
mean_conn_DLPF_198[13:] = mean_conn_DLPF_l[197,:]
mean_conn_DLPF_199 = np.zeros([26])
mean_conn_DLPF_199[0:13] = mean_conn_DLPF_r[198,:]
mean_conn_DLPF_199[13:] = mean_conn_DLPF_l[198,:]
mean_conn_DLPF_337 = np.zeros([26])
mean_conn_DLPF_337[0:13] = mean_conn_DLPF_r[336,:]
mean_conn_DLPF_337[13:] = mean_conn_DLPF_l[336,:]
ax = plt.scatter(mean_conn_DLPF_198, mean_act_DLPF[30,:])
plt.xlabel("Mean Connectivity DLPFC", fontsize=16)
plt.ylabel("Mean Activation DLPFC", fontsize=16)
plt.title('Emotion - Shape', fontsize=20)
outFileplotConAct = ("emotion.png")
plt.savefig(("plot_emotion.png"), dpi=200)
#print(("Figure saved as {0}".format(outFileplotConAct)))
print('Correlation for contrast Emotion ROI 198')
print(np.corrcoef(mean_conn_DLPF_198, mean_act_DLPF[30,:]))
print('Correlation for contrast Emotion ROI 199')
print(np.corrcoef(mean_conn_DLPF_199, mean_act_DLPF[30,:]))
print('Correlation for contrast Emotion ROI 337')
print(np.corrcoef(mean_conn_DLPF_337, mean_act_DLPF[30,:]))


# 'LANGUAGE_STORY' (Language Con 1): [173 124 304]  
plt.figure()
mean_conn_DLPF_173 = np.zeros([26])
mean_conn_DLPF_173[0:13] = mean_conn_DLPF_r[172,:]
mean_conn_DLPF_173[13:] = mean_conn_DLPF_l[172,:]
mean_conn_DLPF_124 = np.zeros([26])
mean_conn_DLPF_124[0:13] = mean_conn_DLPF_r[123,:]
mean_conn_DLPF_124[13:] = mean_conn_DLPF_l[123,:]
mean_conn_DLPF_304 = np.zeros([26])
mean_conn_DLPF_304[0:13] = mean_conn_DLPF_r[303,:]
mean_conn_DLPF_304[13:] = mean_conn_DLPF_l[303,:]
ax = plt.scatter(mean_conn_DLPF_173, mean_act_DLPF[24,:])
plt.xlabel("Mean Connectivity DLPFC", fontsize=16)
plt.ylabel("Mean Activation DLPFC", fontsize=16)
plt.title('Language - Story', fontsize=20)
outFileplotConAct = ("language-story.png")
plt.savefig(("plot_language.png"), dpi=200)
#print(("Figure saved as {0}".format(outFileplotConAct)))
print('Correlation for contrast Language - Story and ROI 173')
print(np.corrcoef(mean_conn_DLPF_173, mean_act_DLPF[24,:]))
print('Correlation for contrast Language - Story and ROI 124')
print(np.corrcoef(mean_conn_DLPF_124, mean_act_DLPF[24,:]))
print('Correlation for contrast Language - Story and ROI 304')
print(np.corrcoef(mean_conn_DLPF_304, mean_act_DLPF[24,:]))


# 'MOTOR_AVG' (Motor Con 6): [235  42  55] 
plt.figure()
mean_conn_DLPF_235 = np.zeros([26])
mean_conn_DLPF_235[0:13] = mean_conn_DLPF_r[234,:]
mean_conn_DLPF_235[13:] = mean_conn_DLPF_l[234,:]
mean_conn_DLPF_42 = np.zeros([26])
mean_conn_DLPF_42[0:13] = mean_conn_DLPF_r[41,:]
mean_conn_DLPF_42[13:] = mean_conn_DLPF_l[41,:]
mean_conn_DLPF_55 = np.zeros([26])
mean_conn_DLPF_55[0:13] = mean_conn_DLPF_r[54,:]
mean_conn_DLPF_55[13:] = mean_conn_DLPF_l[54,:]
a = mean_act_DLPF[30,:]
ax = plt.scatter(mean_conn_DLPF_235, mean_act_DLPF[22,:])
plt.xlabel("Mean Connectivity DLPFC", fontsize=16)
plt.ylabel("Mean Activation DLPFC", fontsize=16)
plt.title('Motor - Average', fontsize=20)
outFileplotConAct = ("motor-avg.png")
plt.savefig(("plot_motor.png"), dpi=200)
#print(("Figure saved as {0}".format(outFileplotConAct)))
print('Correlation for contrast Motor - Average and ROI 235')
print(np.corrcoef(mean_conn_DLPF_235, mean_act_DLPF[22,:]))
print('Correlation for contrast Motor - Average and ROI 42')
print(np.corrcoef(mean_conn_DLPF_42, mean_act_DLPF[22,:]))
print('Correlation for contrast Motor - Average and ROI 55')
print(np.corrcoef(mean_conn_DLPF_55, mean_act_DLPF[22,:]))


# 'SOCIAL_TOM' (Social Con 1): [335   1 181]
plt.figure()
mean_conn_DLPF_335 = np.zeros([26])
mean_conn_DLPF_335[0:13] = mean_conn_DLPF_r[334,:]
mean_conn_DLPF_335[13:] = mean_conn_DLPF_l[334,:]
mean_conn_DLPF_1 = np.zeros([26])
mean_conn_DLPF_1[0:13] = mean_conn_DLPF_r[0,:]
mean_conn_DLPF_1[13:] = mean_conn_DLPF_l[0,:]
mean_conn_DLPF_55 = np.zeros([26])
mean_conn_DLPF_55[0:13] = mean_conn_DLPF_r[4,:]
mean_conn_DLPF_55[13:] = mean_conn_DLPF_l[4,:]
a = mean_act_DLPF[30,:]
ax = plt.scatter(mean_conn_DLPF_335, mean_act_DLPF[26,:])
plt.xlabel("Mean Connectivity DLPFC", fontsize=16)
plt.ylabel("Mean Activation DLPFC", fontsize=16)
plt.title('Social - TOM', fontsize=20)
outFileplotConAct = ("social-tom.png")
plt.savefig(("plot_social.png"), dpi=200)
#print(("Figure saved as {0}".format(outFileplotConAct)))
print('Correlation for contrast Social - TOM and ROI 335')
print(np.corrcoef(mean_conn_DLPF_335, mean_act_DLPF[26,:]))
print('Correlation for contrast Social - TOM and ROI 1')
print(np.corrcoef(mean_conn_DLPF_1, mean_act_DLPF[26,:]))
print('Correlation for contrast Social - TOM and ROI 55')
print(np.corrcoef(mean_conn_DLPF_55, mean_act_DLPF[26,:]))


# 'WORKING_MEM_2BK' (WM Con 8): [201 186   6]
plt.figure()
mean_conn_DLPF_201 = np.zeros([26])
mean_conn_DLPF_201[0:13] = mean_conn_DLPF_r[200,:]
mean_conn_DLPF_201[13:] = mean_conn_DLPF_l[200,:]
mean_conn_DLPF_186 = np.zeros([26])
mean_conn_DLPF_186[0:13] = mean_conn_DLPF_r[185,:]
mean_conn_DLPF_186[13:] = mean_conn_DLPF_l[185,:]
mean_conn_DLPF_6 = np.zeros([26])
mean_conn_DLPF_6[0:13] = mean_conn_DLPF_r[5,:]
mean_conn_DLPF_6[13:] = mean_conn_DLPF_l[5,:]
a = mean_act_DLPF[30,:]
ax = plt.scatter(mean_conn_DLPF_201, mean_act_DLPF[8,:])
plt.xlabel("Mean Connectivity DLPFC", fontsize=16)
plt.ylabel("Mean Activation DLPFC", fontsize=16)
plt.title('Working memory - 2-back', fontsize=20)
outFileplotConAct = ("wm_2bk.png")
plt.savefig(("plot_wk.png"), dpi=200)
#print(("Figure saved as {0}".format(outFileplotConAct)))
print('Correlation for contrast Working Memory - 2-back and ROI 201')
print(np.corrcoef(mean_conn_DLPF_201, mean_act_DLPF[8,:]))
print('Correlation for contrast Working Memory - 2-back and ROI 186')
print(np.corrcoef(mean_conn_DLPF_186, mean_act_DLPF[8,:]))
print('Correlation for contrast Working Memory - 2-back and ROI 6')
print(np.corrcoef(mean_conn_DLPF_6, mean_act_DLPF[8,:]))

# 'LANGUAGE_STORY' (Language Con 1): [173 124 304]   'MOTOR_AVG' (Motor Con 6): [235  42  55] 'SOCIAL_TOM' (Social Con 1): [335   1 181]   'WORKING_MEM_2BK' (WM Con 8): [201 186   6]




    # Create regression model with 26 ROIs and 1 
    #result=sm.OLS(df.iloc[:,roi1][:np.size(matrix,0)],matrix).fit()
    #allresults[r][int(df.columns[roi1])-1][int(df.columns[roi2])-1]=np.array(result.params)