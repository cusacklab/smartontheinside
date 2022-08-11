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
from sklearn.datasets import make_classification
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis






### POOL SUBJECTS
subjlist = ['178950','189450','199453','209228','220721','298455','356948','419239','499566','561444','618952','680452','757764','841349','908860', '103818','113922','121618','130619','137229','151829','158035','171633','179346','190031','200008','210112','221319','299154','361234', '424939','500222','570243','622236','687163','769064','845458','911849','104416','114217','122317','130720','137532','151930','159744', '172029','180230','191235','200614','211316','228434','300618','361941','432332','513130','571144','623844','692964','773257','857263', '926862','122822','130821','137633','152427','160123','172938','180432','192035','200917','239944','303119', '365343','436239','513736','579665','638049','702133','774663','865363','930449','106521','114823','123521','130922','137936','152831', '160729','173334','180533','192136','201111','211619','249947','305830','366042','436845','516742','580650','645450','715041','782561', '871762','942658','106824','117021','123925','131823','138332','153025','162026','173536','180735','192439','201414','211821','251833', '310621','371843','445543','519950','580751','647858','720337','800941','871964','955465','107018','117122','125222','132017','138837', '153227','162329','173637','180937','193239','201818','211922','257542','314225','378857','454140', '523032', '585862','654350','725751', '803240','872562','959574','107422','117324','125424','133827','142828','153631','164030','173940','182739','194140','202719','212015', '257845','316633','381543','459453','525541','586460','654754','727553','812746','873968','966975']
#'105014', '114419', 
nsub=len(subjlist)
s3 = boto3.client('s3')
DLPFroilistplot = ['26', '67', '68', '70', '71', '73', '83', '84', '85', '86', '87', '96', '98', '206', '247', '248', '250', '251', '253', '263', '264', '265', '266', '267', '276', '278']
# create df for con

# create df for act


array_r = np.zeros([360, 13, nsub])
array_l = np.zeros([360, 13, nsub])

# Load activation results
session = boto3.session.Session()
client = session.client('s3')
allresults={}



# For every sub, download the results
for sub in range(nsub):
    # Download files connectivity
    s3.download_file('smartontheinside', f'HCP_1200/{subjlist[sub]}/T1w/Diffusion.probtrackx2/{subjlist[sub]}_tractography_results_ROI.npy', f'/home/chiaracaldinelli/{subjlist[sub]}_tractography_results_VOXEL.npy')
    print(f'Downloading participant {subjlist[sub]}')
    # Load results
    x = np.load(f'/home/chiaracaldinelli/{subjlist[sub]}_tractography_results_VOXEL.npy',allow_pickle=True)
    x = np.ravel(x)[0]
    # Create an array to load the results for each hemisphere
    r = (x['R'])
    array_r[:,:,sub] = r
    l = (x['L'])
    array_l[:,:,sub] = l
    print(l)
    print(l.shape)
    os.remove(f'/home/chiaracaldinelli/{subjlist[sub]}_tractography_results_VOXEL.npy')

    # Load activation results
    load allresults.py
    allresults[sub] = x_rec

    #for hemi in L R:
    #   for DLPFC_ROI:
    #        for


############ CLASSIFICATION ############

# define model
model = LinearDiscriminantAnalysis()
# define model evaluation method
cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=1)
# evaluate model
scores = cross_val_score(model, X, y, scoring='accuracy', cv=cv, n_jobs=-1)
# summarize result
print('Mean Accuracy: %.3f (%.3f)' % (mean(scores), std(scores)))