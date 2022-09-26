from audioop import avg
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
import scipy.stats
import pickle
from numpy import mean
from numpy import std
import msgpack
import msgpack_numpy as m
from sklearn.linear_model import Ridge
#from sklearn.datasets import make_classification
#from sklearn.model_selection import cross_val_score
#from sklearn.model_selection import RepeatedStratifiedKFold
#from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import train_test_split
from sklearn.linear_model import ElasticNet
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedKFold
from numpy import absolute





### POOL SUBJECTS
subjlist = ['103818']
#subjlist = ['178950','189450','199453','209228','220721','298455','356948','419239','499566','561444','618952','680452','757764','841349','908860', '103818','113922','121618','130619','137229','151829','158035','171633','179346','190031','200008','210112','221319','299154','361234', '424939','500222','570243','622236','687163','769064','845458','911849','104416','114217','122317','130720','137532','151930','159744', '172029','180230','191235','200614','211316','228434','300618','361941','432332','513130','571144','623844','692964','773257','857263', '926862','122822','130821','137633','152427','160123','172938','180432','192035','200917','239944','303119', '365343','436239','513736','579665','638049','702133','774663','865363','930449','106521','114823','123521','130922','137936','152831', '160729','173334','180533','192136','201111','211619','249947','305830','366042','436845','516742','580650','645450','715041','782561', '871762','942658','106824','117021','123925','131823','138332','153025','162026','173536','180735','192439','201414','211821','251833', '310621','371843','445543','519950','580751','647858','720337','800941','871964','955465','107018','117122','125222','132017','138837', '153227','162329','173637','180937','193239','201818','211922','257542','314225','378857','454140', '523032', '585862','654350','725751', '803240','872562','959574','107422','117324','125424','133827','142828','153631','164030','173940','182739','194140','202719','212015', '257845','316633','381543','459453','525541','586460','654754','727553','812746','873968','966975']
#'105014', '114419', 
nsub=len(subjlist)
s3 = boto3.client('s3')
DLPFroilist = ['26', '67', '68', '70', '71', '73', '83', '84', '85', '86', '87', '96', '98', '206', '247', '248', '250', '251', '253', '263', '264', '265', '266', '267', '276', '278']

taskcondictnoneg = {
    'tfMRI_WM': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 14, 15, 16, 17], # 0 2BK_BODY, 1 2BK_FACE, 2 2BK_PLACE, 3 2BK_TOOL, 4 0BK_BODY, 5 0BK_FACE, 6 0BK_PLACE, 7 0BK_TOOL, 8 2BK, 9 0BK, 10 2BK-0BK, 11 neg_2BK, 12 neg_0BK, 13 0BK-2BK, 14 BODY, 15 FACE, 16 PLACE, 17 TOOL, 18 BODY-AVG, 19 FACE-AVG, 20 PLACE-AVG, 21 TOOL-AVG, 22 neg_BODY, 23 neg_FACE, 24 neg_PLACE, 25 neg_TOOL, 26 AVG-BODY, 27 AVG-FACE, 28 AVG-PLACE, 29 VG-TOOL
    'tfMRI_GAMBLING': [0, 1],     # PUNISH, REWARD, PUNISH-REWARD, neg_PUNISH, neg_REWARD, REWARD-PUNISH
    'tfMRI_MOTOR': [0, 1, 2, 3, 4, 5, 6],  # 0 CUE, 1 LF, 2 LH, 3 RF, 4 RH, 5 T, 6 AVG, 7 CUE-AVG, 8 LF-AVG, 9 LH-AVG, 10 RF-AVG, 11 RH-AVG, 12 T-AVG, 13 neg_CUE, 14 neg_LF, 15 neg_LH, 16 neg_RF, 17 neg_RH, 18 neg_T, 19 neg_AVG, 20 AVG-CUE, 21 AVG-LF, 22 AVG-LH, 23 AVG-RF, 24 AVG-RH, 25 AVG-T
    'tfMRI_LANGUAGE': [0, 1],     # MATH, STORY, MATH-STORY, STORY-MATH, neg_MATH, neg_STORY
    'tfMRI_SOCIAL': [0, 1],     # RANDOM, TOM, RANDOM-TOM, neg_RANDOM, neg_TOM, TOM-RANDOM
    'tfMRI_RELATIONAL':[0, 1],   # MATCH, REL, MATCH-REL, REL-MATCH, neg_MATCH, neg_REL
    'tfMRI_EMOTION': [0, 1],     # FACES, SHAPES, FACES-SHAPES, neg_FACES, neg_SHAPES, SHAPES-FACES
    }

taskconseldict = {
    'tfMRI_WM': [8], # 8 2BK
    'tfMRI_MOTOR': [6],  # 6 AVG
    'tfMRI_LANGUAGE': [1],     # STORY
    'tfMRI_SOCIAL': [1],     # TOM
    'tfMRI_EMOTION': [1],     # FACES
    }


nvox = 59412
ntask = len(taskcondictnoneg)
nsub=len(subjlist)
session = boto3.session.Session()
client = session.client('s3')
s3 = boto3.client('s3')

# Load connectivity data
conn =     

s3.upload_file(f'/Users/chiara/{subjlist[sub]}_tractography_results_VOXEL_L.npy', 'smartontheinside', f'HCP_1200/{subjlist[sub]}/T1w/Diffusion.probtrackx2/{subjlist[sub]}_tractography_results_VOXEL_L.npy')
s3.upload_file(f'/Users/chiara/{subjlist[sub]}_tractography_results_VOXEL_R.npy', 'smartontheinside', f'HCP_1200/{subjlist[sub]}/T1w/Diffusion.probtrackx2/{subjlist[sub]}_tractography_results_VOXEL_R.npy')


# Load activity data
act = 


############ CLASSIFIER ############


# define model
model = ElasticNet(alpha=1.0, l1_ratio=0.5)
# define model evaluation method
cv = RepeatedKFold(n_splits=10, n_repeats=3, random_state=1)
# evaluate model
scores = cross_val_score(model, act, conn, scoring='neg_mean_absolute_error', cv=cv, n_jobs=-1)
# force scores to be positive
scores = absolute(scores)
print('Mean MAE: %.3f (%.3f)' % (mean(scores), std(scores)))


'''''
for sub in range(nsub):

    X_train, X_test, y_train, y_test = train_test_split(act, conn, test_size=0.25 , random_state=1)

    model = Ridge(alpha=1.0)
    model.fit(act, conn)
    para = model.get_params
    print(model.coef_)
    print(model.coef_.shape)
    model.get_params()
    
    predictors = X_train.columns
    
    coef = Series(model.coef_.flatten(),predictors).sort_values()
    plt.figure(figsize=(10,8))
    coef.plot(kind='bar', title='Model Coefficients')
    plt.show()
'''''