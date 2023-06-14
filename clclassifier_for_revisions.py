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


# assert len(sys.argv)>=3, 'Need to specify alpha and l1_ratio as parameters'
# alpha = float(sys.argv[1])
# l1_ratio = float(sys.argv[2])
alpha = 0.4
l1_ratio = 0.6

# 1 for infant analysis, 0 for adult analysis
infants = 0

######### CHOOSE THESE OPTIONS:

# Subset of subjects for hyperparameter calculation?
hyperparameter_subjects = False
# Reload connectivity and activity data again to create summary numpy files? 
reload_data = False
# Scatter plots of individual fits
draw_scatter_plots = False


print(f'alpha {alpha} l1_ratio {l1_ratio}')

subjlist = ['178950','189450','199453','209228','220721','298455','356948','419239','499566','561444','618952','680452','757764','841349','908860','103818','113922','121618','130619','137229','151829','158035','171633','179346','190031','200008','210112','221319','299154','361234', '424939','500222','570243','622236','687163','769064','845458','911849','104416','114217','122317','130720','137532','151930','159744', '172029','180230','191235','200614','211316','228434','300618','361941','432332','513130','571144','623844','692964','773257','857263', '926862','105014','122822','130821','137633','152427','160123','172938','180432','192035','200917','211417','239944','303119', '365343','436239','513736','579665','638049','702133','774663','865363','930449','106521','114823','123521','130922','137936','152831', '160729','173334','180533','192136','201111','211619','249947','305830','366042','436845','516742','580650','645450','715041','782561', '871762','942658','106824','117021','123925','131823','138332','153025','162026','173536','180735','192439','201414','211821','251833', '310621','371843','445543','519950','580751','647858','720337','800941','871964','955465','107018','117122','125222','132017','138837', '153227','162329','173637','180937','193239','201818','211922','257542','314225','378857','454140','523032','585862', '654350','725751', '803240','872562','959574','107422','117324','125424','133827','142828','153631','164030','173940','182739','194140','202719','212015', '257845','316633','381543','459453','525541','586460','654754','727553','812746','873968','966975']


subjlist_infants =['sub-CC00549XX22', 'sub-CC00202XX04', 'sub-CC00720XX11', 'sub-CC00122XX07', 'sub-CC00071XX06', 'sub-CC00119XX12', 'sub-CC00207XX09', 'sub-CC00484XX15', 'sub-CC00590XX14', 'sub-CC00586XX18', 'sub-CC00467XX14', 'sub-CC00593XX17', 'sub-CC00344XX15', 'sub-CC00409XX13', 'sub-CC00168XX12', 'sub-CC00158XX10', 'sub-CC00613XX11', 'sub-CC00731XX14', 'sub-CC00198XX18', 'sub-CC00664XX13', 'sub-CC00397XX19', 'sub-CC00270XX07', 'sub-CC00252XX05', 'sub-CC00787XX21', 'sub-CC00223XX09', 'sub-CC00367XX13', 'sub-CC00183XX11', 'sub-CC00478XX17', 'sub-CC00540XX13', 'sub-CC00512XX09', 'sub-CC00476XX15', 'sub-CC00120XX05', 'sub-CC00164XX08', 'sub-CC00562XX10', 'sub-CC00194XX14', 'sub-CC00383XX13', 'sub-CC00440XX12', 'sub-CC00153XX05', 'sub-CC00170XX06', 'sub-CC00595XX19', 'sub-CC00744XX19', 'sub-CC00398XX20', 'sub-CC00547XX20','sub-CC00466BN13', 'sub-CC00258XX11', 'sub-CC00203XX05', 'sub-CC00500XX05', 'sub-CC00654XX11', 'sub-CC00073XX08', 'sub-CC00115XX08', 'sub-CC00070XX05', 'sub-CC00840XX16', 'sub-CC00089XX16', 'sub-CC00411XX07', 'sub-CC00184XX12', 'sub-CC00205XX07', 'sub-CC00337XX16', 'sub-CC00313XX08', 'sub-CC00107XX08', 'sub-CC00144XX13', 'sub-CC00585XX17', 'sub-CC00138XX15', 'sub-CC00850XX09', 'sub-CC00149XX18', 'sub-CC00193XX13', 'sub-CC00458XX13', 'sub-CC00201XX03', 'sub-CC00650XX07', 'sub-CC00508XX13', 'sub-CC00099AN18', 'sub-CC00078XX13', 'sub-CC00527XX16', 'sub-CC00150AN02', 'sub-CC00355XX09', 'sub-CC00454XX09', 'sub-CC00341XX12', 'sub-CC00343XX14', 'sub-CC00445XX17', 'sub-CC00116XX09', 'sub-CC00544XX17', 'sub-CC00450XX05', 'sub-CC00561XX09', 'sub-CC00548XX21', 'sub-CC00801XX09', 'sub-CC00060XX03', 'sub-CC00447XX19', 'sub-CC00377XX15', 'sub-CC00479XX18', 'sub-CC00473XX12', 'sub-CC00101XX02', 'sub-CC00481XX12', 'sub-CC00480XX11', 'sub-CC00502XX07', 'sub-CC00088XX15', 'sub-CC00766XX16', 'sub-CC00366XX12', 'sub-CC00757XX15', 'sub-CC00596XX20', 'sub-CC00536XX17', 'sub-CC00550XX06', 'sub-CC00221XX07', 'sub-CC00382XX12', 'sub-CC00178XX14', 'sub-CC00589XX21', 'sub-CC00068XX11', 'sub-CC00334XX13', 'sub-CC00486XX17', 'sub-CC00501XX06', 'sub-CC00455XX10', 'sub-CC00652XX09', 'sub-CC00528XX17', 'sub-CC00685XX18', 'sub-CC00649XX23', 'sub-CC00400XX04', 'sub-CC00094BN13', 'sub-CC00556XX12', 'sub-CC00199XX19', 
'sub-CC00507XX12', 'sub-CC00362XX08', 'sub-CC00236XX14', 'sub-CC00858XX17', 'sub-CC00555XX11', 'sub-CC00091XX10', 'sub-CC00110XX03', 'sub-CC00113XX06', 'sub-CC00558XX14', 'sub-CC00379XX17', 'sub-CC00466AN13', 'sub-CC00499XX22', 'sub-CC00096XX15', 'sub-CC00172BN08', 'sub-CC00399XX21', 'sub-CC00206XX08', 'sub-CC00143AN12', 'sub-CC00656XX13', 'sub-CC00298XX19', 'sub-CC00376XX14', 'sub-CC00219XX13', 'sub-CC00195XX15', 'sub-CC00483XX14', 'sub-CC00546XX19', 'sub-CC00306XX09']
   
   
subjlist_infants =['sub-CC00363XX09', 'sub-CC00066XX09', 'sub-CC00094AN13', 'sub-CC00583XX15', 'sub-CC00347XX18', 'sub-CC00254XX07', 'sub-CC00545XX18', 'sub-CC00532XX13', 'sub-CC00352XX06', 'sub-CC00172AN08', 'sub-CC00160XX04', 'sub-CC00553XX09', 'sub-CC00364XX10', 'sub-CC00189XX17', 'sub-CC00616XX14', 'sub-CC00097XX16', 'sub-CC00111XX04', 'sub-CC00320XX07', 'sub-CC00402XX06', 'sub-CC00587XX19', 'sub-CC00421BN09', 'sub-CC00622XX12', 'sub-CC00474XX13', 'sub-CC00852XX11', 'sub-CC00356XX10', 'sub-CC00824XX16', 'sub-CC00791XX17', 'sub-CC00843XX19', 'sub-CC00127XX12', 'sub-CC00439XX19', 'sub-CC00582XX14', 'sub-CC00693XX18', 'sub-CC00342XX13', 'sub-CC00257XX10', 'sub-CC00594XX18', 'sub-CC00209XX11', 'sub-CC00860XX11', 'sub-CC00272XX09', 'sub-CC00580XX12', 'sub-CC00130XX07', 'sub-CC00250XX03', 'sub-CC00879XX22', 'sub-CC00069XX12', 'sub-CC00441XX13', 'sub-CC00653XX10', 'sub-CC00534XX15', 'sub-CC00777XX19', 'sub-CC00080XX07', 'sub-CC00269XX14', 'sub-CC00669XX18', 'sub-CC00417XX13', 'sub-CC00329XX16', 'sub-CC00338BN17', 'sub-CC00416XX12', 'sub-CC00084XX11', 'sub-CC00171XX07', 'sub-CC00083XX10', 'sub-CC00408XX12', 'sub-CC00433XX13', 'sub-CC00734XX17', 'sub-CC00316XX11', 'sub-CC00504XX09', 'sub-CC00871XX14', 'sub-CC00410XX06', 'sub-CC00197XX17', 'sub-CC00180XX08', 'sub-CC00303XX06', 'sub-CC00542XX15', 'sub-CC00099BN18', 'sub-CC00457XX12', 'sub-CC00421AN09', 'sub-CC00647XX21', 'sub-CC00581XX13', 'sub-CC00639XX21', 'sub-CC00448XX20', 'sub-CC00114XX07', 'sub-CC00818XX18', 'sub-CC00314XX09', 'sub-CC00846XX22', 'sub-CC00308XX11', 'sub-CC00516XX13', 'sub-CC00412XX08', 'sub-CC00165XX09', 'sub-CC00292XX13', 'sub-CC00217XX11', 'sub-CC00428XX16', 'sub-CC00126XX11', 'sub-CC00260XX05', 'sub-CC00671XX12', 'sub-CC00568XX16', 'sub-CC00415XX11', 'sub-CC00564XX12', 'sub-CC00667XX16', 'sub-CC00174XX10', 'sub-CC00108XX09', 'sub-CC00106XX07', 'sub-CC00705XX12', 'sub-CC00552XX08', 'sub-CC00719XX18', 'sub-CC00592XX16', 'sub-CC00143BN12', 'sub-CC00247XX17', 'sub-CC00075XX10', 'sub-CC00497XX20', 'sub-CC00067XX10', 'sub-CC00268XX13', 'sub-CC00403XX07', 'sub-CC00324XX11', 'sub-CC00086XX13', 'sub-CC00371XX09', 'sub-CC00453XX08', 'sub-CC00853XX12', 'sub-CC00204XX06', 'sub-CC00074XX09', 'sub-CC00072XX07', 'sub-CC00349XX20', 'sub-CC00181XX09', 'sub-CC00438XX18', 'sub-CC00469XX16', 'sub-CC00413XX09', 'sub-CC00162XX06', 'sub-CC00799XX25', 'sub-CC00357XX11', 'sub-CC00255XX08', 'sub-CC00304XX07', 'sub-CC00470XX09', 'sub-CC00134XX11', 'sub-CC00150BN02', 'sub-CC00798XX24', 'sub-CC00117XX10', 'sub-CC00765XX15', 'sub-CC00145XX14', 'sub-CC00472XX11', 'sub-CC00793XX19', 'sub-CC00810XX10', 'sub-CC00348XX19', 'sub-CC00461XX08', 'sub-CC00434AN14', 'sub-CC00431XX11', 'sub-CC00577XX17', 'sub-CC00584XX16', 'sub-CC00675XX16', 'sub-CC00620XX10', 'sub-CC00822XX14', 'sub-CC00300XX03', 'sub-CC00607XX13', 'sub-CC00182XX10', 'sub-CC00146XX15', 'sub-CC00443XX15', 'sub-CC00451XX06', 'sub-CC00380XX10', 'sub-CC00513XX10', 'sub-CC00338AN17', 'sub-CC00286XX15', 'sub-CC00332XX11', 'sub-CC00102XX03', 'sub-CC00082XX09', 'sub-CC00498XX21', 'sub-CC00815XX15', 'sub-CC00079XX14', 'sub-CC00307XX10', 'sub-CC00446XX18', 'sub-CC00597XX21', 'sub-CC00179XX15', 'sub-CC00200XX02', 'sub-CC00157XX09', 'sub-CC00289XX18', 'sub-CC00065XX08', 'sub-CC00265XX10', 'sub-CC00062XX05', 'sub-CC00319XX14', 'sub-CC00520XX09', 'sub-CC00339XX18', 'sub-CC00424XX12', 'sub-CC00267XX12', 'sub-CC00131XX08', 'sub-CC00176XX12', 'sub-CC00103XX04', 'sub-CC00384XX14', 'sub-CC00378XX16', 'sub-CC00405XX09', 'sub-CC00588XX20', 'sub-CC00740XX15']
    # 'sub-CC00688XX21', # non andato

# Number of subjects to analyse? Put in "None" to use all subjects
sample_subjlist=20

if not sample_subjlist is None: 
    if hyperparameter_subjects: 
        subjlist = subjlist[:sample_subjlist] # subset of first subjects for hyperparamters 
    else: subjlist = subjlist[sample_subjlist:] # roll out to rest of subjects for hyperparamters

analysis_root = f'/home/{os.getlogin()}'

DLPFroilist = ['26', '67', '68', '70', '71', '73', '83', '84', '85', '86', '87', '97', '98',
               '206', '247', '248', '250', '251', '253', '263', '264', '265', '266', '267', '277', '278']

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
nsub_infants = len(subjlist_infants)      

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

        if infants == 1:
            # right hemi has 786600, but left has 794520
            conn_for_classifier[hemi] = np.zeros((nsub_infants, nseedvox[hemi], ntarg))
            print(f'Working on tractography data, {hemi} hemisphere')
            
            
        
            for subind, sub in enumerate(subjlist_infants):
                conn = []
                print(f'Working on infant subject {sub} tractography data, {hemi} hemisphere')
                
                remotepath_conn = (
                    f'Results/{sub}_infants_tractography_results_VOXEL_{hemi}.npy')
                s3.download_file('smartontheinside', remotepath_conn,
                                os.path.join(analysis_root, f'/home/{os.getlogin()}/{sub}_infants_tractography_results_VOXEL_{hemi}.npy'))
                tract = np.load(
                    os.path.join(analysis_root, f'{sub}_infants_tractography_results_VOXEL_{hemi}.npy'), allow_pickle=True)
                print(tract)
                y = tract[3, :]
                print(y)
                
                for target_roi in range(1, 361):  # For every target ROI (334 in total?)
                    conn_for_classifier[hemi][subind, :,
                                        target_roi - 1] = tract[target_roi, :]
        
       
        else:

            conn_for_classifier[hemi] = np.zeros((nsub, nseedvox[hemi], ntarg))
                
            print(f'Working on tractography data, {hemi} hemisphere')

            for subind, sub in enumerate(subjlist):
                conn = []
                print(f'Working on subject {sub} tractography data, {hemi} hemisphere')

                remotepath_conn = (
                    f'Results/{sub}_tractography_results_VOXEL_{hemi}.npy')
                s3.download_file('smartontheinside', remotepath_conn,
                                os.path.join(analysis_root, f'{sub}_tractography_results_VOXEL_{hemi}.npy'))
                tract = np.load(
                    os.path.join(analysis_root, f'{sub}_tractography_results_VOXEL_{hemi}.npy'), allow_pickle=True)

                for target_roi in range(1, 361):  # For every target ROI (334 in total?)
                    conn_for_classifier[hemi][subind, :,
                                            target_roi - 1] = tract[target_roi, :]


    if infants == 1:
        np.save(os.path.join(analysis_root, f'results/conn_for_classifier_N-{nsub_infants}_infants.npy'), conn_for_classifier)
        s3.upload_file(os.path.join(analysis_root, f'results/conn_for_classifier_N-{nsub_infants}_infants.npy'),
                'smartontheinside', f'infant_classifier/conn_for_classifier_N-{nsub_infants}_infants.npy')
    else:
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





############################################################
######################## CLASSIFIER ########################
########### train on adults, test on avg adults ############
############################################################

print('Running classifier for revisions')

#     (1) Train the model on all of the adults
#     (2) Predict activity on average adult
#     (3) Test in existing way using adult contrast maps (as everything here is in the adult space)

conn_for_classifier_infants = np.load(
            os.path.join(analysis_root, f'/home/chiaracaldinelli/conn_for_classifier_N-{nsub}.npy'), allow_pickle=True).ravel()[0]
conn_for_classifier = np.load(
            os.path.join(analysis_root, f'conn_for_classifier_N-{nsub}.npy'), allow_pickle=True).ravel()[0]

# Download connections for classifier
# remotepath_conn = (f'Results/conn_for_classifier.npy')
# s3.download_file('smartontheinside', remotepath_conn, f'/home/ubuntu/conn_for_classifier.npy')

# Create dataframe for results
res = pd.DataFrame()

# Load up activations for all of the tasks
act_for_classifier = {}
for task, taskcons in taskcondict_selected.items():
    # Download activations for classifier
    remotepath_act = (f'Results/act_for_classifier.npy')
    # s3.download_file('smartontheinside', remotepath_act, f'/home/chiaracaldinelli/conn_for_classifier.npy')
    act_for_classifier[task] = np.load(
        os.path.join(analysis_root, f'act_for_classifier_{task}_N-{nsub}.npy'), allow_pickle=True).ravel()[0]

# Set up lists to store predictions for each task and hemi
pred = {'L':[], 'R':[]}
all_pred = {x:pred for x in taskcondict_selected}

if os.getlogin()=='ubuntu':
    folder = f'/home/ubuntu/final_parameters_classifier_results_alpha-{alpha}_l1ratio-{l1_ratio}_infants'             
else:
    folder = f'/home/{os.getlogin()}/final_parameters_classifier_results_alpha-{alpha}_l1ratio-{l1_ratio}_infants'     
os.makedirs(os.path.join(analysis_root, folder), exist_ok=True) # Make folder if it doesn't already exist


# Run classification for each task
for task, taskcons in taskcondict_selected.items():

    for hemiind, hemi in enumerate(['R', 'L']):
        X_adult = conn_for_classifier[hemi]
        X_infant = conn_for_classifier_infants[hemi]

        # z-score activation for target task and hemisphere
        y = scipy.stats.zscore( act_for_classifier[task][hemi], axis=1 ) # Across vertices within each subject
        score = []  

        # dict with lists for each comparison task
        all_corr = {comparison_task:[] for comparison_task in act_for_classifier }

        # Define model
        if alpha==0:
            model = LinearRegression()
        else:
            model = ElasticNet(alpha = alpha, l1_ratio=l1_ratio, random_state=42) 

        # Reshape to collapse subject and seed voxel dimensions as rows
        X_adult = np.reshape(X_adult, [nsub * nseedvox[hemi], ntarg])
        y_adult = np.reshape(y, [nsub * nseedvox[hemi], 1])
        # X_infant = np.reshape(X_infant, [nsub_infants * nseedvox[hemi], ntarg])


        # Train
        model.fit(X_adult, y_adult)

        y_adult_mean = np.mean(y, axis=0)
        # y_adult_mean.reshape(1, -1)


        for one_infant in range(nsub):
            X_test = (X_infant[one_infant,:,:])
            # X_infant = np.reshape(X_infant, [nsub_infants * nseedvox[hemi], ntarg])
            # X_test = X_infant[one_infant, :, :].reshape(1,-1)

            # Test
            sc = model.score(X_test, y_adult_mean)
            sp = model.get_params

            # Get predicted activity
            y_estimate = model.predict(X_test)

            # save predicted values
            all_pred[task][hemi].append(y_estimate)

            # correlate predicted activity for this task against true activity for each of the tasks
            for comparison_task in act_for_classifier:

                y_comparison = scipy.stats.zscore( act_for_classifier[comparison_task][hemi], axis=1 ) # Across vertices within each subject
                y_comparison_mean = np.mean(y_comparison, axis=0)
                c = pearsonr(y_comparison_mean, y_estimate)

                c_ext = c[0]
                all_corr[comparison_task].append(c_ext)
                res = pd.concat((res, pd.DataFrame([
                    {'algorithm': 'ElasticNet', 'alpha': alpha, 'l1_ratio': l1_ratio,
                    'task': task, 'hemi': hemi, 'fold': one_infant,
                    'comparison_task': comparison_task, 
                    'pearson': c[0], 'score':sc}
                    ])))

            score.append(sc)

        print(f'Folder {folder} task {task} hemi {hemi} score {np.mean(score)} pearson {np.mean(all_corr[task])}')
        # Save results with pickle   

        with open((f'/home/{os.getlogin()}/{task}_subject_N-{nsub}_infants.pickle'), 'wb') as f:
            pickle.dump(res, f)


    # Save summary of results with pickle
    with open(f'/home/{os.getlogin()}/{task}_subject_N-{nsub}_revisions.pickle', 'wb') as f:
        pickle.dump(res, f)

    s3.upload_file(f'/home/{os.getlogin()}/{task}_subject_N-{nsub}_revisions.pickle', 
        'smartontheinside', 
        f'{task}_subject_N-{nsub}_revisions.pickle')

# Save predictions
with open(f'/home/{os.getlogin()}/predictions_N-{nsub}_revisions.pickle', 'wb') as f:
    pickle.dump(all_pred, f)

s3.upload_file(f'/home/{os.getlogin()}/predictions_N-{nsub}_revisions.pickle', 
    'smartontheinside', 
    f'/home/{os.getlogin()}/predictions_N-{nsub}_revisions.pickle')

# Dump data frame
res.to_csv(f'/home/{os.getlogin()}/summary_N-{nsub}_revisions.csv')
s3.upload_file(f'/home/{os.getlogin()}/summary_N-{nsub}_revisions.csv', 
    'smartontheinside', 
    f'/home/{os.getlogin()}/summary_N-{nsub}_revisions.csv')

print(f'Finished with alpha {alpha} l1_ratio {l1_ratio} for infant classifier')
