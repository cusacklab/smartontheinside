import boto3
import numpy as np
import msgpack_numpy as m
from sklearn.model_selection import LeaveOneOut
from sklearn.linear_model import ElasticNet, LinearRegression
from sklearn.model_selection import KFold
from sklearn.metrics import mean_squared_error, r2_score, explained_variance_score
from sklearn.model_selection import cross_val_score
from matplotlib import pyplot as plt
from scipy.stats import pearsonr
import pickle
import scipy
import os
import sys
import pandas as pd


assert len(sys.argv)>=3, 'Need to specify alpha and l1_ratio as parameters'
alpha = float(sys.argv[1])
l1_ratio = float(sys.argv[2])

# 1 for infant analysis, 0 for adult analysis
infants = 1

######### CHOOSE THESE OPTIONS:

# Subset of subjects for hyperparameter calculation?
hyperparameter_subjects = False
# Reload connectivity and activity data again to create summary numpy files? 
reload_data = False
# Scatter plots of individual fits
draw_scatter_plots = False


print(f'alpha {alpha} l1_ratio {l1_ratio}')

subjlist = ['178950','189450','199453','209228','220721','298455','356948','419239','499566','561444','618952','680452','757764','841349','908860','103818','113922','121618','130619','137229','151829','158035','171633','179346','190031','200008','210112','221319','299154','361234', '424939','500222','570243','622236','687163','769064','845458','911849','104416','114217','122317','130720','137532','151930','159744', '172029','180230','191235','200614','211316','228434','300618','361941','432332','513130','571144','623844','692964','773257','857263', '926862','105014','122822','130821','137633','152427','160123','172938','180432','192035','200917','211417','239944','303119', '365343','436239','513736','579665','638049','702133','774663','865363','930449','106521','114823','123521','130922','137936','152831', '160729','173334','180533','192136','201111','211619','249947','305830','366042','436845','516742','580650','645450','715041','782561', '871762','942658','106824','117021','123925','131823','138332','153025','162026','173536','180735','192439','201414','211821','251833', '310621','371843','445543','519950','580751','647858','720337','800941','871964','955465','107018','117122','125222','132017','138837', '153227','162329','173637','180937','193239','201818','211922','257542','314225','378857','454140','523032','585862', '654350','725751', '803240','872562','959574','107422','117324','125424','133827','142828','153631','164030','173940','182739','194140','202719','212015', '257845','316633','381543','459453','525541','586460','654754','727553','812746','873968','966975']
subjlist_infants = 

# Number of subjects to analyse? Put in "None" to use all subjects
sample_subjlist=20

if not sample_subjlist is None: 
    if hyperparameter_subjects: 
        subjlist = subjlist[:sample_subjlist] # subset of first subjects for hyperparamters 
    else: subjlist = subjlist[sample_subjlist:] # roll out to rest of subjects for hyperparamters

analysis_root = '/home/chiaracaldinelli'

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

ntask = len(taskcondict_selected)
nsub = len(subjlist)
nsub_infants = len(subjlist_infants
                   
# Credentials for uploading data to the cusack lab s3
s3 = boto3.client('s3')
session = boto3.Session(profile_name='default')

nseedvox = {'L': 2207, 'R': 2185}
ntarg = 360

if reload_data:
    ################################################
    ############ Load connectivity data ############
    ################################################

    conn_for_classifier = {}

    for hemiind, hemi in enumerate(['R', 'L']):
        # right hemi has 786600, but left has 794520
        conn_for_classifier[hemi] = np.zeros((nsub, nseedvox[hemi], ntarg))
        print(f'Working on tractography data, {hemi} hemisphere')

        if infants == 1;

            for subind, sub in enumerate(subjlist_infants):
                conn = []
                print(f'Working on infant subject {sub} tractography data, {hemi} hemisphere')

                remotepath_conn = (
                    f'infant_tractography/{sub}_tractography_results_VOXEL.npy')
                s3.download_file('smartontheinside', remotepath_conn,
                                os.path.join(analysis_root, f'{sub}_tractography_results_VOXEL_{hemi}.npy'))
                tract = np.load(
                    os.path.join(analysis_root, f'{sub}_tractography_results_VOXEL_{hemi}.npy'), allow_pickle=True)

                for target_roi in range(1, 361):  # For every target ROI (334 in total?)
                conn_for_classifier[hemi][subind, :,
                                        target_roi - 1] = tract[target_roi, :]
       
       
        else:
            for subind, sub in enumerate(subjlist):
                conn = []
                print(f'Working on subject {sub} tractography data, {hemi} hemisphere')
                else:

                remotepath_conn = (
                    f'Results/{sub}_tractography_results_VOXEL_{hemi}.npy')
                s3.download_file('smartontheinside', remotepath_conn,
                                os.path.join(analysis_root, f'{sub}_tractography_results_VOXEL_{hemi}.npy'))
                tract = np.load(
                    os.path.join(analysis_root, f'{sub}_tractography_results_VOXEL_{hemi}.npy'), allow_pickle=True)

                for target_roi in range(1, 361):  # For every target ROI (334 in total?)
                    conn_for_classifier[hemi][subind, :,
                                            target_roi - 1] = tract[target_roi, :]

    np.save(os.path.join(analysis_root, f'conn_for_classifier_N-{nsub}.npy'), conn_for_classifier)
    s3.upload_file(os.path.join(analysis_root, f'conn_for_classifier_N-{nsub}.npy'),
                'smartontheinside', f'Results/conn_for_classifier_N-{nsub}.npy')


    ############################################
    ############ Load activity data ############
    ############################################


    # # for each of the selected tasks
    # for task, taskcons in taskcondict_selected.items():
    #     act_for_classifier = {}

    #     # for each hemisphere
    #     for hemiind, hemi in enumerate(['R', 'L']):
    #         act_for_classifier[hemi] = np.zeros((nsub, nseedvox[hemi]))

    #         # For each subject
    #         for subind, sub in enumerate(subjlist):
    #             print(
    #                 f'Working on subject {sub} activation data, {hemi} hemisphere', {task})
    #             remotepath_act = (f'Results/{task}_{sub}_{hemi}_tfmri.npy')
    #             s3.download_file('smartontheinside', remotepath_act,
    #                             os.path.join(analysis_root, f'{task}_{sub}_{hemi}_tfmri.npy'))
    #             data_act = np.load(
    #                 os.path.join(analysis_root, f'{task}_{sub}_{hemi}_tfmri.npy'), allow_pickle=True)
    #             act_for_classifier[hemi][subind, :] = data_act

    #     np.save(os.path.join(analysis_root, f'act_for_classifier_{task}_N-{nsub}.npy'), act_for_classifier)
    #     s3.upload_file(os.path.join(analysis_root, f'act_for_classifier_{task}_N-{nsub}.npy'),
    #                     'smartontheinside', f'Results/act_for_classifier_N-{nsub}.npy')


####################################
############ CLASSIFIER ############
####################################

# Download connections for classifier
# remotepath_conn = (f'Results/conn_for_classifier.npy')
# s3.download_file('smartontheinside', remotepath_conn, f'/home/ubuntu/conn_for_classifier.npy')
conn_for_classifier = np.load(
    os.path.join(analysis_root, f'conn_for_classifier_N-{nsub}.npy'), allow_pickle=True).ravel()[0]

# Create dataframe for results
res = pd.DataFrame()

# Load up activations for all of the tasks
act_for_classifier = {}
for task, taskcons in taskcondict_selected.items():
    # Download activations for classifier
    # remotepath_act = (f'Results/act_for_classifier.npy')
    #s3.download_file('smartontheinside', remotepath_act, f'/home/ubuntu/conn_for_classifier.npy')
    act_for_classifier[task] = np.load(
        os.path.join(analysis_root, f'act_for_classifier_{task}_N-{nsub}.npy'), allow_pickle=True).ravel()[0]


# Set up lists to store predictions for each task and hemi
pred = {'L':[], 'R':[]}
all_pred = {x:pred for x in taskcondict_selected}


# Run classification for each task
for task, taskcons in taskcondict_selected.items():
    if hyperparameter_subjects: 
        folder = f'classifier_results_alpha-{alpha}_l1ratio-{l1_ratio}' 
    else: 
        folder = f'final_parameters_classifier_results_alpha-{alpha}_l1ratio-{l1_ratio}'

    os.makedirs(os.path.join(analysis_root, folder), exist_ok=True) # Make folder if it doesn't already exist

    for hemiind, hemi in enumerate(['R', 'L']):
        X = conn_for_classifier[hemi]

        # z-score activation for target task and hemisphere
        y = scipy.stats.zscore( act_for_classifier[task][hemi], axis=1) # Across vertices within each subject

        score = []  

        # dict with lists for each comparison task
        all_corr = {comparison_task:[] for comparison_task in act_for_classifier }
        

        # Leave one out elastic net
        loo = LeaveOneOut()
        loo.get_n_splits(X)

        for train_index, test_index in loo.split(X):

            X_train, X_test = X[train_index, :, :], X[test_index, :, :]
            y_train, y_test = y[train_index, :], y[test_index, :]

            nsub_train = len(train_index)
            nsub_test = len(test_index)

            # Reshape to collapse subject and seed voxel dimensions as rows
            X_train = np.reshape(X_train, [nsub_train * nseedvox[hemi], ntarg])
            X_test = np.reshape(X_test, [nsub_test * nseedvox[hemi], ntarg])
            y_train = np.reshape(y_train, [nsub_train * nseedvox[hemi], 1])
            y_test = np.reshape(y_test, [nsub_test * nseedvox[hemi], 1])

            # Define model
            if alpha==0:
                model = LinearRegression()
            else:
                model = ElasticNet(alpha = alpha, l1_ratio=l1_ratio, random_state=42) 

            # Train
            model.fit(X_train, y_train)
            # Test
            sc = model.score(X_test, y_test)
            sp = model.get_params

            # Get predicted activity 
            y_estimate = model.predict(X_test)
            
            # save predicted values
            all_pred[task][hemi].append(y_estimate)
 
            # correlate predicted activity for this task against true activity for each of the tasks
            for comparison_task in act_for_classifier:

                c = pearsonr(act_for_classifier[comparison_task][hemi][test_index,:].ravel(), y_estimate)
                c_ext = c[0]
                all_corr[comparison_task].append(c_ext)

                res = pd.concat((res, pd.DataFrame([
                    {'algorithm': 'ElasticNet', 'alpha': alpha, 'l1_ratio': l1_ratio,
                    'task': task, 'hemi': hemi, 'fold': test_index[0],
                    'comparison_task':comparison_task, 
                    'pearson': c[0], 'score':sc}
                    ])))

            if draw_scatter_plots:
                # Draw scatter plot
                plt.figure()
                plt.scatter(y_test, y_estimate)
                plt.title(f'r={c[0]} p={c[1]}')
                plt.savefig(f'scatter_{task}_{hemi}_{test_index[0]}.png')

            score.append(sc)

        print(f'Folder {folder} task {task} hemi {hemi} score {np.mean(score)} pearson {np.mean(all_corr[task])}')
        # Save results with pickle   
        with open(os.path.join(analysis_root, folder, f'{task}_subject_loo_N-{nsub}.pickle'), 'wb') as f:
            pickle.dump(res, f)


    # Save summary of results with pickle
    with open(os.path.join(analysis_root, folder, f'{task}_subject_loo_N-{nsub}.pickle'), 'wb') as f:
        pickle.dump(res, f)
    
    s3.upload_file(os.path.join(analysis_root, folder, f'{task}_subject_loo_N-{nsub}.pickle'), 
        'smartontheinside', 
        os.path.join('Results', folder, f'{task}_subjectloo_N-{nsub}.pickle'))

# Save predictions
with open(os.path.join(analysis_root, folder, f'predictions_N-{nsub}.pickle'), 'wb') as f:
    pickle.dump(all_pred, f)

s3.upload_file(os.path.join(analysis_root, folder, f'predictions_N-{nsub}.pickle'), 
    'smartontheinside', 
    os.path.join('Results', folder, f'predictions_N-{nsub}.pickle'))

# Dump data frame
res.to_csv(os.path.join(analysis_root, folder, f'summary_N-{nsub}.csv'))
s3.upload_file(os.path.join(analysis_root,  folder,f'summary_N-{nsub}.csv'), 
    'smartontheinside', 
    os.path.join('Results', folder, f'summary_N-{nsub}.csv'))

print(f'Finished with alpha {alpha} l1_ratio {l1_ratio}')
        