import pandas as pd
import os
import matplotlib.pyplot as plt
from statsmodels.graphics.factorplots import interaction_plot
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable
import seaborn as sns
from statsmodels.graphics.factorplots import interaction_plot
import ptitprince as pt

alpha_values = [0.4]
l1_ratio_values = [0.6]

# Selection of contrasts - based on previous analysis
tasks_selected = ['tfMRI_WM', 'tfMRI_MOTOR', 'tfMRI_LANGUAGE', 'tfMRI_SOCIAL','tfMRI_EMOTION']

analysis_root = '/home/chiaracaldinelli'


folder = f'smartontheinside/smartontheinside/results/classifier_tune_parameters'
os.makedirs(os.path.join(analysis_root, folder), exist_ok=True) # Make folder if it doesn't already exist

for hemiind, hemi in enumerate(['R', 'L']):

    df = pd.read_csv(os.path.join(analysis_root, f'final_parameters_classifier_results_alpha-{alpha_values[0]}_l1ratio-{l1_ratio_values[0]}/summary_N-155.csv'), index_col=False)
    df = df.loc[df['hemi'] == hemi]

    plt.figure()
    fig,ax=plt.subplots(nrows=2, figsize=(10,8))

    # Jitter and rain for score
    f, ax = plt.subplots(figsize=(7, 5))
    ax = pt.half_violinplot( x = df['task'], y = df['score'], data = df, bw = .2, cut = 0.,
                            scale = "area", width = .6, inner = None)
    ax = sns.stripplot( x = df['task'], y = df['score'], data = df, edgecolor = "white",
                        size = 3, jitter = 1, zorder = 0)
    plt.title(f"{hemi} hemisphere")
    plt.ylim(-0.20, 0.25)
    x = np.arange(0, 10, 0.1)

    plt.savefig(os.path.join(analysis_root, folder, f'summarise_res__classifier_score_{hemi}.png'), bbox_inches='tight')
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

    plt.savefig(os.path.join(analysis_root, folder, f'summarise_res_classifier_pearson_{hemi}.png'), bbox_inches='tight')
    print(f'Figure saved as summarise_res_pearson_{hemi}.png')

    # table = pd.pivot_table(df, values=['pearson', 'M score'], index=['hemi', 'task'],
    #         aggfunc={'pearson': np.mean,
    #                  'pearson': np.std,
    #                  'score': np.mean,
    #                  'pearson': np.std})

    # print(df.describe)

