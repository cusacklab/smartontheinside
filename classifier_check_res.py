import pandas as pd
import os
import matplotlib.pyplot as plt
from statsmodels.graphics.factorplots import interaction_plot
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable
import seaborn as sns
from statsmodels.graphics.factorplots import interaction_plot
import ptitprince as pt
from scipy.stats import kstest
import pingouin as pg
from scipy.stats import bootstrap
import numpy as np
import boto3
from scipy.stats import mannwhitneyu


alpha = 0.4
l1_ratio = 0.6

subjlist = ['178950','189450','199453','209228','220721','298455','356948','419239','499566','561444','618952','680452','757764','841349','908860','103818','113922','121618','130619','137229','151829','158035','171633','179346','190031','200008','210112','221319','299154','361234', '424939','500222','570243','622236','687163','769064','845458','911849','104416','114217','122317','130720','137532','151930','159744', '172029','180230','191235','200614','211316','228434','300618','361941','432332','513130','571144','623844','692964','773257','857263', '926862','105014','122822','130821','137633','152427','160123','172938','180432','192035','200917','211417','239944','303119', '365343','436239','513736','579665','638049','702133','774663','865363','930449','106521','114823','123521','130922','137936','152831', '160729','173334','180533','192136','201111','211619','249947','305830','366042','436845','516742','580650','645450','715041','782561', '871762','942658','106824','117021','123925','131823','138332','153025','162026','173536','180735','192439','201414','211821','251833', '310621','371843','445543','519950','580751','647858','720337','800941','871964','955465','107018','117122','125222','132017','138837', '153227','162329','173637','180937','193239','201818','211922','257542','314225','378857','454140','523032','585862', '654350','725751', '803240','872562','959574','107422','117324','125424','133827','142828','153631','164030','173940','182739','194140','202719','212015', '257845','316633','381543','459453','525541','586460','654754','727553','812746','873968','966975']
nsubj = 155

# Selection of contrasts - based on previous analysis
tasks_selected = ['tfMRI_WM', 'tfMRI_MOTOR', 'tfMRI_LANGUAGE', 'tfMRI_SOCIAL','tfMRI_EMOTION']

analysis_root = '/home/chiaracaldinelli'

folder_results_classifier = f'final_parameters_classifier_results_alpha-{alpha}_l1ratio-{l1_ratio}'
os.makedirs(os.path.join(analysis_root, folder_results_classifier), exist_ok=True) # Make folder if it doesn't already exist

# Credentials for downloading data from the cusack lab s3
s3 = boto3.client('s3')
session = boto3.Session(profile_name='default')

def bootstrap_replicate_1d(data, func):

    """Generate bootstrap replicate of 1D data."""
    bs_sample = np.random.choice(data, len(data))

    return func(bs_sample)


def draw_bs_reps(data, func, size=1):
    """Draw bootstrap replicates."""

    # Initialize array of replicates: bs_replicates
    bs_replicates = np.empty(size)

    # Generate replicates
    for i in range(size):
        bs_replicates[i] = bootstrap_replicate_1d(data, func)

    return bs_replicates
    

    # Using np.empty(), initialize an array called bs_replicates of size size to hold all of the bootstrap replicates.
    # Write a for loop that ranges over size and computes a replicate using bootstrap_replicate_1d(). Refer to the exercise description above to see the function signature of bootstrap_replicate_1d(). Store the replicate in the appropriate index of bs_replicates.



for hemiind, hemi in enumerate(['R', 'L']):
    print(f'{hemi} hemisphere')

    # Load values
    df = pd.read_csv(os.path.join(analysis_root, folder_results_classifier, f'summary_N-155.csv'))
    df = df.loc[df['hemi'] == hemi]
    print(df)

    ######### PLOT MATRIX WITH PREDICTED AND TRUE VALUES #########
    
    df_mean = (df.groupby(['task','comparison_task']).mean())
    matrix = df_mean['pearson']
    matrix = matrix.to_frame()
    matrix = matrix.to_numpy()
    matrix= np.reshape(matrix, (5,5))

    plt.imshow(matrix)

    plt.figure()
    # Show matrix plot
    ax = plt.gca()
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
            rotation_mode="anchor")
    # Major ticks
    ax.set_xticks(np.arange(0, len(tasks_selected), 1))
    ax.set_yticks(np.arange(0, len(tasks_selected), 1))
    # Labels for major ticks
    ax.set_xticklabels(tasks_selected, fontsize=6)
    ax.set_yticklabels(tasks_selected, fontsize=6)

    plt.imshow(matrix)

    plt.colorbar()    
    plt.savefig((f'matrix_{hemi}_hemisphere.png'), bbox_inches='tight')
    plt.close()

    # Make empty matrix to compare within to across tasks
    # First column is within, second is across
    comp = np.zeros((155,2))

    for subj in range(nsubj-1):
        df_one_sub = df.loc[df['fold'] == subj]

        within = []
        across = []

        for index, row in df_one_sub.iterrows():

            if row['task'] == row['comparison_task']:
                within.append(row['pearson'])
            else:
                across.append(row['pearson'])

        comp[subj,0] = np.mean(within)
        comp[subj,1] = np.mean(across)

    print(comp)

    

    # take mean for within and across
    # (1) for each subject calculate two values - the within task (average of leading diagonal) and the across tasks (average of values off the leading diagonal). We can then do bootstrapping of the difference to see if they're different
    # for within, pick rows where task == comparison taks, then groupby subject and take mean. For across tasks, pick rows where task ~= comparison task, group by subject and mean
    # Then get one difference value per subject and bootstrap them using the bootstrap command

    within = comp[:,0] 
    across = comp[:,1]
    print(f'Mean and SD for within, {hemi} hemisphere:')
    print(np.mean(within))
    print(np.std(within))
    print(f'Mean and SD for across, {hemi} hemisphere:')
    print(np.mean(across))
    print(np.std(across))

    res = mannwhitneyu(within, across, method="exact")
    print('************************************************************')
    print('Results Mann Whitney')
    print(res)

    # ************* USE BOOTSTRAP TO CHECK IF THE 2 GROUPS (ACROSS AND WITHIN) ARE DIFFERENT *************
    #  
    # 
    # Compute the mean of all forces (from forces_concat) using np.mean().
    # Generate shifted data sets for both force_a and force_b such that the mean of each is the mean of the concatenated array of impact forces.
    # Generate 10,000 bootstrap replicates of the mean each for the two shifted arrays.
    # Compute the bootstrap replicates of the difference of means by subtracting the replicates of the shifted impact force of Frog B from those of Frog A.
    # Compute and print the p-value from your bootstrap replicates.

    # Compute mean of all groups
    mean_within_across = np.mean(np.concatenate((comp[:,0],comp[:,1]), axis=0))

    # Generate shifted arrays
    within_shifted = within - np.mean(within) + mean_within_across
    across_shifted = across - np.mean(across) + mean_within_across 

    # Compute 10,000 bootstrap replicates from shifted arrays
    bs_replicates_within = draw_bs_reps(within_shifted, np.mean, size=10000)
    bs_replicates_across = draw_bs_reps(across_shifted, np.mean, size=10000)

    # Get replicates of difference of means: bs_replicates
    bs_replicates = bs_replicates_within - bs_replicates_across

    # Compute and print p-value: p
    empirical_diff_means = np.mean(within) - np.mean(across)
    p = np.sum(bs_replicates >= np.mean(empirical_diff_means)) / 10000
    print('p-value =', p)

    # NOW separate bootstrap for each cell on the leading diagonal (5 separate bootstraps) against which we can then test 
    # individual other comparisons. Some tasks I think will be completely distinguishable from every other task; 
    # some will be a bit distinct, and WM not at all 




'''''''''
    for taskind, task in enumerate(tasks_selected): 

        # # Bootstrap
        # #convert array to sequence
        # data = df['pearson'] 
        # data = (data,)

        # #calculate 95% bootstrapped confidence interval for median
        # bootstrap_ci = bootstrap(data, np.median, confidence_level=0.99,
        #                         random_state=1, method='percentile')

        #view 95% boostrapped confidence interval
        print(f'task: {task} {bootstrap_ci.confidence_interval}')



    # Jitter and rain for score
    f, ax = plt.subplots(figsize=(7, 5))
    ax = pt.half_violinplot( x = df['task'], y = df['score'], data = df, bw = .2, cut = 0.,
                            scale = "area", width = .6, inner = None)
    ax = sns.stripplot( x = df['task'], y = df['score'], data = df, edgecolor = "white",
                        size = 3, jitter = 1, zorder = 0)
    plt.ylim(-0.25, 0.30)
    plt.title(f"{hemi} hemisphere")
    
    plt.savefig(os.path.join(analysis_root, f'smartontheinside/smartontheinside/results/classifier_results/summarise_res_classifier_score_{hemi}.png'), bbox_inches='tight')
    print(f'Figure saved as summarise_res_score_{hemi}.png')

    # Jitter and rain for pearson
    f, ax = plt.subplots(figsize=(7, 5))
    ax = pt.half_violinplot( x = df['task'], y = df['pearson'], data = df, bw = .2, cut = 0.,
                            scale = "area", width = .6, inner = None)
    ax = sns.stripplot( x = df['task'], y = df['pearson'], data = df, edgecolor = "white",
                        size = 3, jitter = 1, zorder = 0)
    plt.title(f"{hemi} hemisphere")
    # plt.ylim(-0.20, 0.40)
    x = np.arange(0, 10, 0.1)

    plt.savefig(os.path.join(analysis_root, f'smartontheinside/smartontheinside/results/classifier_results/summarise_res_classifier_pearson_{hemi}.png'), bbox_inches='tight')
    print(f'Figure saved as summarise_res_pearson_{hemi}.png')


    table = pd.pivot_table(df, values=['pearson', 'score'], index=['hemi', 'task'],
                    aggfunc={'pearson': [np.mean, np.std, min, max],
                             'score': [np.mean, np.std, min, max]})
    print(table)
'''''''''