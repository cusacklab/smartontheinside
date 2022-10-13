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
from sklearn.linear_model import ElasticNet
from sklearn.datasets import make_regression


#subjlist = ['199453', '189450', '220721', '298455']
#subjlist = [ '103818', '942658', '106521', '178950', '122317']
subjlist = [ '199453', '209228', '114419', '178950','189450', '220721','298455','356948','419239','499566','561444','618952','680452','757764','841349','908860', '103818','113922','121618','130619','137229','151829','158035','171633','179346','190031','200008','210112','221319','299154','361234', '424939','500222','570243','622236','687163','769064','845458','911849','104416', '114217','122317','130720','137532','151930','159744', '172029','180230','191235','200614','211316','228434','300618','361941','432332','513130','571144','623844','692964','773257','857263', '926862','122822','130821','137633','152427','160123','172938','180432','192035','200917','239944','303119', '365343','436239','513736','579665','638049','702133','774663','865363','930449','106521','114823','123521','130922','137936','152831', '160729','173334','180533','192136','201111','211619','249947','305830','366042','436845','516742','580650','645450','715041','782561', '871762','942658','106824','117021','123925','131823','138332','153025','162026','173536', '180735','192439','201414','211821','251833', '310621','371843','445543','519950','580751','647858','720337','800941','871964','955465','107018','117122','125222','132017','138837', '153227','162329','173637','180937','193239','201818','211922','257542','314225','378857','454140', '523032', '585862','654350','725751', '803240','872562','959574','107422','117324','125424','133827','142828','153631','164030','173940','182739','194140','202719','212015', '257845','316633','381543','459453','525541','586460','654754','727553','812746','873968', '966975', '105014', '114419', '199453', '209228']
nsub = len(subjlist)
s3 = boto3.client('s3')
DLPFroilist = ['26', '67', '68', '70', '71', '73', '83', '84', '85', '86', '87', '96', '98',
               '206', '247', '248', '250', '251', '253', '263', '264', '265', '266', '267', '276', '278']

# Selection of contrasts - based on previous analysis
taskcondict_selected = {
    'tfMRI_WM': [8],  # 8 2BK
    'tfMRI_MOTOR': [6],  # 6 AVG
    'tfMRI_LANGUAGE': [1],  # STORY
    'tfMRI_SOCIAL': [1],     # TOM
    'tfMRI_EMOTION': [1]     # SHAPES
}

nvox = 59412
ntask = len(taskcondict_selected)
nsub = len(subjlist)

# Credentials for uploading data to the cusack lab s3
session = boto3.Session(profile_name='default')
s3 = session.client('s3')

nseedvox = {'L': 2207, 'R': 2185}
ntarg = 360

################################################
############ Load connectivity data ############
################################################

conn_for_classifier = {}

for hemiind, hemi in enumerate(['R', 'L']):
    # right hemi has 786600, but left has 794520
    conn_for_classifier[hemi] = np.zeros((nsub, nseedvox[hemi], ntarg))

    for subind, sub in enumerate(subjlist):
        conn = []
        print(f'Working on subject {sub}, {hemi} hemisphere')

        remotepath_conn = (
            f'HCP_1200/{sub}/T1w/Diffusion.probtrackx2/{sub}_tractography_results_VOXEL_{hemi}.npy')
        s3.download_file('smartontheinside', remotepath_conn,
                         f'/Users/chiara/{sub}_tractography_results_VOXEL_{hemi}.npy')
        tract = np.load(
            f'/Users/chiara/{sub}_tractography_results_VOXEL_{hemi}.npy', allow_pickle=True)

        for target_roi in range(1, 361):  # For every target ROI (334 in total?)
            conn_for_classifier[hemi][subind, :,
                                      target_roi - 1] = tract[target_roi, :]

np.save(f'/Users/chiara/conn_for_classifier.npy', conn_for_classifier)
s3.upload_file(f'/Users/chiara/conn_for_classifier.npy',
               'smartontheinside', f'Results/conn_for_classifier.npy')


############################################
############ Load activity data ############
############################################

act_for_classifier = {}
for hemiind, hemi in enumerate(['R', 'L']):
    act_for_classifier[hemi] = np.zeros((nsub, nseedvox[hemi]))

    for subind, sub in enumerate(subjlist):
        act = []

        for task, taskcons in taskcondict_selected.items():
            print(
                f'Working on subject {sub} activation data, {hemi} hemisphere', {task})
            remotepath_act = (f'Results/{task}_{sub}_{hemi}_tfmri.npy')
            s3.download_file('smartontheinside', remotepath_act,
                             f'/Users/chiara/{task}_{sub}_{hemi}_tfmri.npy')
            data_act = np.load(
                f'/Users/chiara/{task}_{sub}_{hemi}_tfmri.npy', allow_pickle=True)
            act_for_classifier[hemi][subind, :] = data_act

np.save(f'/Users/chiara/act_for_classifier.npy', act_for_classifier)
s3.upload_file(f'/Users/chiara/act_for_classifier.npy',
               'smartontheinside', f'Results/act_for_classifier.npy')


####################################
############ CLASSIFIER ############
####################################

# Flatten out the first two dimensions like this
#xtrain = np.reshape(xtrain, [(nsubj-1)*nseedvox, ntargetroi])


# Download and load data for classifier
# remotepath_conn = (f'Results/conn_for_classifier.npy')
#s3.download_file('smartontheinside', remotepath_conn, f'/Users/chiara/conn_for_classifier.npy')
conn_for_classifier = np.load(
    f'/Users/chiara/conn_for_classifier.npy', allow_pickle=True).ravel()[0]

# remotepath_act = (f'Results/act_for_classifier.npy')
#s3.download_file('smartontheinside', remotepath_act, f'/Users/chiara/conn_for_classifier.npy')
act_for_classifier = np.load(
    f'/Users/chiara/act_for_classifier.npy', allow_pickle=True).ravel()[0]

res = {}

for hemiind, hemi in enumerate(['R', 'L']):
    print
    X = conn_for_classifier[hemi]
    y = act_for_classifier[hemi]

    # Leave one out elastic net
    loo = LeaveOneOut()
    loo.get_n_splits(X)
    print(loo)

    #print('X shape is:')
    # print(X.shape)
    #print('y shape is:')
    # print(y.shape)

    score = []

    for train_index, test_index in loo.split(X):
        print("TRAIN:", train_index, "TEST:", test_index)
        # X.shape=[nsub,nseedvox,ntarg]

        X_train, X_test = X[train_index, :, :], X[test_index, :, :]
        y_train, y_test = y[train_index, :], y[test_index, :]

        nsub_train = nsub-1
        nsub_test = 1

        # Reshape to collapse subject and seed voxel dimensions as rows
        X_train = np.reshape(X_train, [nsub_train * nseedvox[hemi], ntarg])
        X_test = np.reshape(X_test, [nsub_test * nseedvox[hemi], ntarg])
        y_train = np.reshape(y_train, [nsub_train * nseedvox[hemi], 1])
        y_test = np.reshape(y_test, [nsub_test * nseedvox[hemi], 1])

        # Define model
        model = ElasticNet(alpha=1.0, l1_ratio=0.5, random_state=0)

        # Train
        m = model.fit(X_train, y_train)
        m.coef_
        m.intercept_

        # Test
        m.predict(X_train)
        m.predict(X_test)

        # evaluate model
        sc = m.score(X_test, y_test)
        score.append(sc)
        print(sc)
        res[hemi] = score
