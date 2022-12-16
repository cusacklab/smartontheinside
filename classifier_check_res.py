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


alpha = 0.4
l1_ratio = 0.6

# Selection of contrasts - based on previous analysis
tasks_selected = ['tfMRI_WM', 'tfMRI_MOTOR', 'tfMRI_LANGUAGE', 'tfMRI_SOCIAL','tfMRI_EMOTION']

analysis_root = '/home/chiaracaldinelli'

folder_results_classifier = f'final_parameters_classifier_results_alpha-{alpha}_l1ratio-{l1_ratio}'
os.makedirs(os.path.join(analysis_root, folder_results_classifier), exist_ok=True) # Make folder if it doesn't already exist

# Credentials for downloading data from the cusack lab s3
s3 = boto3.client('s3')
session = boto3.Session(profile_name='default')




for hemiind, hemi in enumerate(['R', 'L']):
    print(f'{hemi} hemisphere')

    # Download and load predicted values
    remotepath = (os.path.join('Results', folder_results_classifier, f'predictions_N-155.pickle'))
    print(remotepath)
    s3.download_file('smartontheinside', remotepath, os.path.join(analysis_root, f'predictions_N-155.pickle'))


    df = pd.read_csv(os.path.join(analysis_root, folder_results_classifier, f'summary_N-155.csv'))
    print(df)
    print(df.groupby(['task','comparison_task']).mean())


    matrix = df['pearson']
    matrix= matrix.reshape((5,5))
    plt.imshow(matrix)
    # Make empty matrix to compare pred to real values
    m = np.zeros((5,5))

    for taskind, task in enumerate(tasks_selected): 

        # Download and load true values
        remotepath = (os.path.join('Results', folder_results_classifier, f'{task}_subjectloo_N-155.pickle'))
        print(remotepath)
        s3.download_file('smartontheinside', remotepath, os.path.join(analysis_root, f'{task}_subjectloo_N-155.pickle'))

        df_true = pd.read_pickle(os.path.join(analysis_root, f'{task}_subjectloo_N-155.pickle'))
        # print(df_true)
        df_true = df_true.loc[df_true['hemi'] == hemi]

        # Load predicted values - pred is a dict 
        df_pred = pd.read_pickle(os.path.join(analysis_root, f'predictions_N-155.pickle'))
        # print(df_pred) 


        # # Bootstrap
        # #convert array to sequence
        # data = df['pearson'] 
        # data = (data,)

        # #calculate 95% bootstrapped confidence interval for median
        # bootstrap_ci = bootstrap(data, np.median, confidence_level=0.99,
        #                         random_state=1, method='percentile')

        #view 95% boostrapped confidence interval
        # print(f'task: {task} {bootstrap_ci.confidence_interval}')

        # Calculate mean for true values for each task
        df_pred = df_pred[task]
        df_pred = df_pred[hemi]
        print(len(df_pred))
        list_avg_pred = []
        for p in range(0, 154):
            list_avg_pred.append(np.mean(df_pred[p]))
            # Calculate mean for pred values for each task for each hemi
            print(list_avg_pred)
        m[taskind,] = np.mean(list_avg_pred)


    plt.figure()
    fig,ax=plt.subplots(nrows=2, figsize=(10,8))

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

    score = df['score']
    for task in tasks_selected:
        print(f'{hemi} hemisphere - score')
        print(f'Normality test for {task}')
        print(kstest(score, 'norm'))

    pearson = df['pearson']
    for task in tasks_selected:
        print(f'{hemi} hemisphere - pearson')
        print(f'Normality test for {task}')
        print(kstest(pearson, 'norm'))

    # ANOVA
    aov=pg.anova(dv='score', between='task', data=df, detailed=True).round(3)
    print('ANOVA for score')
    print(aov)

    # ANOVA
    aov=pg.anova(dv='pearson', between='task', data=df, detailed=True).round(3)
    print('ANOVA for pearson')
    print(aov)