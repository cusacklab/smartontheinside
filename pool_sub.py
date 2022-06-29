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
subjlist = ['178950','189450','199453','209228','220721','298455','356948','419239','499566','561444','618952','680452','757764','841349','908860', '103818','113922','121618','130619','137229','151829','158035','171633','179346','190031','200008','210112','221319','299154','361234', '424939','500222','570243','622236','687163','769064','845458','911849','104416','114217','122317','130720','137532','151930','159744', '172029','180230','191235','200614','211316','228434','300618','361941','432332','513130','571144','623844','692964','773257','857263', '926862','105014', '114419', '122822','130821','137633','152427','160123','172938','180432','192035','200917','239944','303119', '365343','436239','513736','579665','638049','702133','774663','865363','930449','106521','114823','123521','130922','137936','152831', '160729','173334','180533','192136','201111','211619','249947','305830','366042','436845','516742','580650','645450','715041','782561', '871762','942658','106824','117021','123925','131823','138332','153025','162026','173536','180735','192439','201414','211821','251833', '310621','371843','445543','519950','580751','647858','720337','800941','871964','955465','107018','117122','125222','132017','138837', '153227','162329','173637','180937','193239','201818','211922','257542','314225','378857','454140', '523032', '585862','654350','725751', '803240','872562','959574','107422','117324','125424','133827','142828','153631','164030','173940','182739','194140','202719','212015', '257845','316633','381543','459453','525541','586460','654754','727553','812746','873968','966975']
nsub=len(subjlist)
s3 = boto3.client('s3')
listcon = ['WORKING_MEM_2BK_BODY', 'WORKING_MEM_2BK_FACE', 'WORKING_MEM_2BK_PLACE', 'WORKING_MEM_2BK_TOOL', 'WORKING_MEM_0BK_BODY', 'WORKING_MEM_0BK_FACE', 'WORKING_MEM_0BK_PLACE', 'WORKING_MEM_0BK_TOOL', 'WORKING_MEM_2BK', 'WORKING_MEM_0BK', 'WORKING_MEM_BODY', 'WORKING_MEM_FACE', 'WORKING_MEM_PLACE', 'WORKING_MEM_TOOL', 'GAMBLING_PUNISH', 'GAMBLING_REWARD','MOTOR_CUE', 'MOTOR_LF', 'MOTOR_LH', 'MOTOR_RF', 'MOTOR_RH', 'MOTOR_T', 'MOTOR_AVG',  'LANGUAGE_MATH', 'LANGUAGE_STORY',  'SOCIAL_RANDOM', 'SOCIAL_TOM', 'RELATIONAL_MATCH', 'RELATIONAL_REL', 'EMOTION_FACES', 'EMOTION_SHAPES']  

# Load results from previous analysis -  subjs are already pooled
# allresults is activation?
# topROI is the ranking of the most active ROIs
# DLPFtoproi is the ranking of the most active ROIs of the DLPFC



# For every sub, download the results and put all of them together
for sub in range(nsub):
    s3.download_file('smartontheinside', f'HCP_1200/{subjlist[sub]}/T1w/Diffusion.probtrackx2/{subjlist[sub]}_tractography_results_ROI.txt', f'/home/chiaracaldinelli/{subjlist[sub]}_tractography_results_ROI.txt')
    s3.download_file('smartontheinside', f'HCP_1200/{subjlist[sub]}/T1w/Diffusion.probtrackx2/{subjlist[sub]}_tractography_results_ROI.txt', f'/home/chiaracaldinelli/{subjlist[sub]}_tractography_results_VOXEL.txt')
    print(f'Downloading participant {subjlist[sub]}')
    a = pd.read_csv((f'/home/chiaracaldinelli/{subjlist[sub]}_tractography_results_ROI.txt'), delimiter=" ", header = None).to_dict()[0]
    print(a)

    data = np.load('DLPFCroi.npy')
    print(data.shape)
    data=np.mean(data,0)
    print(data.shape)
    rdm = np.corrcoef(data)
    print(rdm)
    # should give numcons * numcons matrix
    #if not then do rdm = np.corrcoef(X.T)


# For each contrast:
for contrast in listcon:
    # Create graph with activation by connections (26 DLPFC ROIs' activation by 26 DLPFC ROIs' tractography results)
    plt.figure()
    ax = plt.plot(x=, y=, data=df, color=".8", scale='area')
    ax = sns.stripplot(x=, y=, data=df, edgecolor="white", size=2, jitter=1) 
    plt.ylim(0, 0.65)
    plt.xlabel('')
    ax.set_ylabel("Activation by Connectivity", fontsize=16)
    plt.title('GVC')
    outFile = "RainViolinPlotBVCcorr.png"
    plt.savefig((os.path.join(path,'Plotpng')), dpi=200)
    print(("Figure saved as {0}".format(outFile)))

    # Create regression model with 26 ROIs and 1 
    result=sm.OLS(df.iloc[:,roi1][:np.size(matrix,0)],matrix).fit()
    allresults[r][int(df.columns[roi1])-1][int(df.columns[roi2])-1]=np.array(result.params)