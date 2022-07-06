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

DLPFroilistplot = ['26', '67', '68', '70', '71', '73', '83', '84', '85', '86', '87', '96', '98', '206', '247', '248', '250', '251', '253', '263', '264', '265', '266', '267', '276', '278']
mean_act_DLPF = np.load('DLPFCroi.npy')
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
a = mean_act_DLPF[30,:]
ax = plt.scatter(mean_conn_DLPF_198, mean_act_DLPF[30,:])
plt.xlabel("Mean Connectivity DLPFC", fontsize=16)
plt.ylabel("Mean Activation DLPFC", fontsize=16)
plt.title('Emotion - Shape', fontsize=20)
outFileplotConAct = ("emotion.png")
plt.savefig(("plot_emotion.png"), dpi=200)
#print(("Figure saved as {0}".format(outFileplotConAct)))
print('Correlation for contrast Emotion')
print(np.corrcoef(mean_conn_DLPF_198, mean_act_DLPF[30,:]))


# 'LANGUAGE_STORY' (Language Con 1): [173 124 304]  
plt.figure()
mean_conn_DLPF_173 = np.zeros([26])
mean_conn_DLPF_173[0:13] = mean_conn_DLPF_r[172,:]
mean_conn_DLPF_173[13:] = mean_conn_DLPF_l[172,:]
a = mean_act_DLPF[30,:]
ax = plt.scatter(mean_conn_DLPF_173, mean_act_DLPF[30,:])
plt.xlabel("Mean Connectivity DLPFC", fontsize=16)
plt.ylabel("Mean Activation DLPFC", fontsize=16)
plt.title('Language - Story', fontsize=20)
outFileplotConAct = ("language-story.png")
plt.savefig(("plot_language.png"), dpi=200)
#print(("Figure saved as {0}".format(outFileplotConAct)))
print('Correlation for contrast Language - Story')
print(np.corrcoef(mean_conn_DLPF_198, mean_act_DLPF[24,:]))


# 'MOTOR_AVG' (Motor Con 6): [235  42  55] 
plt.figure()
mean_conn_DLPF_235 = np.zeros([26])
mean_conn_DLPF_235[0:13] = mean_conn_DLPF_r[234,:]
mean_conn_DLPF_235[13:] = mean_conn_DLPF_l[234,:]
a = mean_act_DLPF[30,:]
ax = plt.scatter(mean_conn_DLPF_235, mean_act_DLPF[22,:])
plt.xlabel("Mean Connectivity DLPFC", fontsize=16)
plt.ylabel("Mean Activation DLPFC", fontsize=16)
plt.title('Motor - Average', fontsize=20)
outFileplotConAct = ("motor-avg.png")
plt.savefig(("plot_motor.png"), dpi=200)
#print(("Figure saved as {0}".format(outFileplotConAct)))
print('Correlation for contrast Motor - Average')
print(np.corrcoef(mean_conn_DLPF_235, mean_act_DLPF[22,:]))


# 'SOCIAL_TOM' (Social Con 1): [335   1 181]
plt.figure()
mean_conn_DLPF_335 = np.zeros([26])
mean_conn_DLPF_335[0:13] = mean_conn_DLPF_r[334,:]
mean_conn_DLPF_335[13:] = mean_conn_DLPF_l[334,:]
a = mean_act_DLPF[30,:]
ax = plt.scatter(mean_conn_DLPF_335, mean_act_DLPF[26,:])
plt.xlabel("Mean Connectivity DLPFC", fontsize=16)
plt.ylabel("Mean Activation DLPFC", fontsize=16)
plt.title('Social - TOM', fontsize=20)
outFileplotConAct = ("social-tom.png")
plt.savefig(("plot_social.png"), dpi=200)
#print(("Figure saved as {0}".format(outFileplotConAct)))
print('Correlation for contrast Social - TOM')
print(np.corrcoef(mean_conn_DLPF_335, mean_act_DLPF[26,:]))


# 'WORKING_MEM_2BK' (WM Con 8): [201 186   6]
plt.figure()
mean_conn_DLPF_201 = np.zeros([26])
mean_conn_DLPF_201[0:13] = mean_conn_DLPF_r[200,:]
mean_conn_DLPF_201[13:] = mean_conn_DLPF_l[200,:]
a = mean_act_DLPF[30,:]
ax = plt.scatter(mean_conn_DLPF_201, mean_act_DLPF[26,:])
plt.xlabel("Mean Connectivity DLPFC", fontsize=16)
plt.ylabel("Mean Activation DLPFC", fontsize=16)
plt.title('Working memory - 2-back', fontsize=20)
outFileplotConAct = ("wm_2bk.png")
plt.savefig(("plot_wk.png"), dpi=200)
#print(("Figure saved as {0}".format(outFileplotConAct)))
print('Correlation for contrast Working Memory - 2-back')
print(np.corrcoef(mean_conn_DLPF_201, mean_act_DLPF[8,:]))

# 'LANGUAGE_STORY' (Language Con 1): [173 124 304]   'MOTOR_AVG' (Motor Con 6): [235  42  55] 'SOCIAL_TOM' (Social Con 1): [335   1 181]   'WORKING_MEM_2BK' (WM Con 8): [201 186   6]




    # Create regression model with 26 ROIs and 1 
    #result=sm.OLS(df.iloc[:,roi1][:np.size(matrix,0)],matrix).fit()
    #allresults[r][int(df.columns[roi1])-1][int(df.columns[roi2])-1]=np.array(result.params)