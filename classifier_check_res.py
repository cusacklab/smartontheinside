import pandas as pd
import os
import matplotlib.pyplot as plt
from statsmodels.graphics.factorplots import interaction_plot
import numpy as np


alpha_values = [0.2, 0.4, 0.6, 0.8, 1.0]
l1_ratio_values = [0.2, 0.4, 0.6, 0.8, 1.0]

# Selection of contrasts - based on previous analysis
tasks_selected = ['tfMRI_WM', 'tfMRI_MOTOR', 'tfMRI_LANGUAGE', 'tfMRI_SOCIAL','tfMRI_EMOTION']

analysis_root = '/home/chiaracaldinelli'

m = np.zeros((len(tasks_selected),len(l1_ratio_values)))

for taskind, task in enumerate(tasks_selected):
    print(task)

    for hemi in ('L', 'R'):

        for alphaind, alpha in enumerate(alpha_values):
            for l1_ratioind, l1_ratio in enumerate(l1_ratio_values):

                df = pd.read_csv(os.path.join(analysis_root, f'classifier_results_alpha-{alpha}_l1ratio-{l1_ratio}/summary_N-20.csv'), index_col=False)
                df = df.loc[df['hemi'] == hemi]
                # print(dfL)

                # plt.figure()
                # fig,ax=plt.subplots(nrows=2, figsize=(10,8))
                # fig=interaction_plot(x=dfR['fold'], trace=dfR['task'], response=dfR['score'], ax=ax[0])
                # fig=interaction_plot(x=dfR['fold'], trace=dfR['task'], response=dfR['score'], ax=ax[1])
                # fig.tight_layout()
                # fig.set_figheight(9)
                # fig.set_figwidth(15)

                # # Folder for results of this analysis
                # folder = f'classifier_results_alpha-{alpha}_l1ratio-{l1_ratio}'
                # os.makedirs(os.path.join(analysis_root, folder), exist_ok=True) # Make folder if it doesn't already exist

                # plt.savefig((f'res_alpha_{alpha}_l1_ratio_{l1_ratio}.png'), bbox_inches='tight')
                # print(f'Figure saved as res_alpha_{alpha}_l1_ratio_{l1_ratio}.png')

            # Calculate average of the 20 folds and summarise it in a matrix
            y = (df.loc[df['task'] == task])
            print(y)
            y = y.loc['score']
            
            print('********************')
            print(f'taskind {taskind}')
            print(f'alpha {alphaind}')
            print(f'l1_ration {l1_ratioind}')
            m[alphaind,l1_ratioind] = y
            
            
            # print(mL)
            # print(mR)

            for hemi in ('L', 'R'):
                fig, ax = plt.subplots()
                im = ax.imshow(m)

                # Show all ticks and label them with the respective list entries
                # ax.set_xticks(np.arange(len(farmers)), labels=farmers)
                # ax.set_yticks(np.arange(len(vegetables)), labels=vegetables)

                # Rotate the tick labels and set their alignment.
                # plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
                #         rotation_mode="anchor")

                # Loop over data dimensions and create text annotations.
                # for i in range(len(vegetables)):
                #     for j in range(len(farmers)):
                #         text = ax.text(j, i, harvest[i, j],
                #                     ha="center", va="center", color="w")

                ax.set_title(f"{hemi} Hemisphere")
                fig.tight_layout()
                plt.show()
                plt.savefig(f'heatmap_{hemi}', bbox_inches='tight')