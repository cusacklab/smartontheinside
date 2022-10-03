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
import numpy as np
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
from sklearn.model_selection import LeaveOneOut





### POOL SUBJECTS
subjlist = ['123521', '942658'] # cancella questo perche e doppio
#subjlist = ['103818', '178950','189450','199453','209228','220721','298455','356948','419239','499566','561444','618952','680452','757764','841349','908860', '103818','113922','121618','130619','137229','151829','158035','171633','179346','190031','200008','210112','221319','299154','361234', '424939','500222','570243','622236','687163','769064','845458','911849','104416','114217','122317','130720','137532','151930','159744', '172029','180230','191235','200614','211316','228434','300618','361941','432332','513130','571144','623844','692964','773257','857263', '926862','122822','130821','137633','152427','160123','172938','180432','192035','200917','239944','303119', '365343','436239','513736','579665','638049','702133','774663','865363','930449','106521','114823','123521','130922','137936','152831', '160729','173334','180533','192136','201111','211619','249947','305830','366042','436845','516742','580650','645450','715041','782561', '871762','942658','106824','117021','123925','131823','138332','153025','162026','173536','180735','192439','201414','211821','251833', '310621','371843','445543','519950','580751','647858','720337','800941','871964','955465','107018','117122','125222','132017','138837', '153227','162329','173637','180937','193239','201818','211922','257542','314225','378857','454140', '523032', '585862','654350','725751', '803240','872562','959574','107422','117324','125424','133827','142828','153631','164030','173940','182739','194140','202719','212015', '257845','316633','381543','459453','525541','586460','654754','727553','812746','873968','966975']
#'105014', '114419', 
nsub=len(subjlist)
s3 = boto3.client('s3')
DLPFroilist = ['26', '67', '68', '70', '71', '73', '83', '84', '85', '86', '87', '96', '98', '206', '247', '248', '250', '251', '253', '263', '264', '265', '266', '267', '276', '278']

# Selection of contrasts - based on previous analysis
taskcondict_selected = {
        'tfMRI_WM': [8], # 8 2BK
        'tfMRI_MOTOR': [6],  # 6 AVG
        'tfMRI_LANGUAGE': [1],     #  STORY
        'tfMRI_SOCIAL': [1],     # TOM
        'tfMRI_EMOTION': [1]     # SHAPES
        }

nvox = 59412
ntask = len(taskcondict_selected)
nsub=len(subjlist)

# Credentials for uploading data to the cusack lab s3
session = boto3.Session(profile_name='default')
s3 = session.client('s3')



################################################
############ Load connectivity data ############
################################################

for hemiind, hemi in enumerate(['R','L']):
    conn_for_classifier = np.zeros((nsub,786600))
    
    for subind, sub in enumerate(subjlist):
        conn = []
        print(f'Working on subject {sub} connectivity data, {hemi} hemisphere')
        remotepath = (f'HCP_1200/{sub}/T1w/Diffusion.probtrackx2/{sub}_tractography_results_VOXEL_R.npy')
        s3.download_file('smartontheinside', remotepath, f'/Users/chiara/{sub}_tractography_results_VOXEL_R.npy')
        tract = np.load(f'/Users/chiara/{sub}_tractography_results_VOXEL_R.npy', allow_pickle=True)

        for target_roi in range(1, 361): # For every target ROI (334 in total)
            conn.extend(tract[target_roi, :])
            print(len(conn))
        conn_for_classifier[subind,:] = conn
    np.save(f'/Users/chiara/conn_for_classifier_{hemi}.npy', conn_for_classifier)



############################################
############ Load activity data ############
############################################

for task, taskcons in taskcondict_selected.items():
    for subind, sub in enumerate(subjlist):

        print(f'Working on task {task} fMRI data')
        act = []
        act_for_classifier = np.zeros((nsub,4400))
        remotepath = (f'Results/{task}_timeseries.npy')
        #s3.download_file('smartontheinside', remotepath, f'/Users/chiara/{task}_{sub}_timeseries.npy')
        x = np.load(f'/Users/chiara/{task}_{sub}_timeseries.npy', allow_pickle=True)
        x = np.ravel(x)[0]

        for kind, k in enumerate(x.keys()):
            act.extend(x[k])
            #print(len(x[k]))
            #act[kind, :] = x[k]
        act_for_classifier[subind,:] = act
        #print(act_for_classifier.shape)
        #print(act_for_classifier)

    # copia i risulati di ogni soggetto dentro act_for_classifier: ogni riga sara' un soggetto
    np.save(f'/Users/chiara/{task}_for_classifier.npy', act)



####################################
############ CLASSIFIER ############
####################################




for hemiind, hemi in enumerate(['R','L']):
    conn_for_classifier = np.load(f'/Users/chiara/conn_for_classifier_{hemi}.npy', allow_pickle=True)

    X = conn_for_classifier
    y = act_for_classifier 

    loo = LeaveOneOut()
    loo.get_n_splits(X)
    print(loo)

    for train_index, test_index in loo.split(X):
        print("TRAIN:", train_index, "TEST:", test_index)
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]
        print(X_train, X_test, y_train, y_test)


        # define model
        model = ElasticNet(alpha=1.0, l1_ratio=0.5)
        # define model evaluation method
        cv = RepeatedKFold(n_splits=2, n_repeats=3, random_state=1)
        # evaluate model
        scores = cross_val_score(model, y, X, scoring='neg_mean_absolute_error', cv=cv, n_jobs=-1)
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