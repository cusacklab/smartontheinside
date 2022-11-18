import pandas as pd
import os
import matplotlib.pyplot as plt
from statsmodels.graphics.factorplots import interaction_plot
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable


alpha_values = [0.1, 1.0, 10.0, 100.0]
l1_ratio_values = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]

# Selection of contrasts - based on previous analysis
tasks_selected = ['tfMRI_WM', 'tfMRI_MOTOR', 'tfMRI_LANGUAGE', 'tfMRI_SOCIAL','tfMRI_EMOTION']

analysis_root = '/home/chiaracaldinelli'
# code_folder = '/home/chiaracaldinelli/smartontheinside/smartontheinside'
m = np.zeros(((len(alpha_values)),(len(l1_ratio_values))))

for hemiind, hemi in enumerate(['R', 'L']):
    # Make composite figures
    # fig, ax = plt.subplots(ncols=2, nrows=5)
    fig, ax = plt.subplots(2, 5)

    for alphaind, alpha in enumerate(alpha_values):
        for l1_ratioind, l1_ratio in enumerate(l1_ratio_values):
            for taskind, task in enumerate(tasks_selected):

                folder = f'smartontheinside/smartontheinside/results/classifier_tune_parameters'
                os.makedirs(os.path.join(analysis_root, folder), exist_ok=True) # Make folder if it doesn't already exist

                df = pd.read_csv(os.path.join(analysis_root, f'classifier_results_alpha-{alpha}_l1ratio-{l1_ratio}/summary_N-20.csv'), index_col=False)
                df = df.loc[df['hemi'] == hemi]
                # print(dfL)
                print(df)
                table = pd.pivot_table(df, values=['pearson', 'score'], index=['hemi', 'task'],
                    aggfunc={'pearson': np.mean,
                             'score': np.mean})
                
                # file = open(os.path.join(analysis_root, folder, f'classifier_res.txt'),'a')
                # file.write(f"\n Results for alpha = {alpha} and l1_ratio = {l1_ratio}")
                # file.write(f"\n {table}")
                # file.close()

                print(table)

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
                y = (df.loc[df['task'] == task]['score'])
                m[alphaind,l1_ratioind] = y.mean()
            
                # fig, ax = plt.subplots()
                # Compose figure
                im = ax[hemiind][taskind].imshow(m)
                # im = ax.imshow(m)

                # plt.figure()
                # fig,ax=plt.subplots(ncols=2, nrows=5, figsize=(10,8))
                # im = ax.imshow(m)
                # fig=interaction_plot(x=dfR['fold'], trace=dfR['task'], response=dfR['score'], ax=ax[0])
                # fig=interaction_plot(x=dfR['fold'], trace=dfR['task'], response=dfR['score'], ax=ax[1])

                # Show all ticks and label them with the respective list entries
                ax[hemiind][taskind].set_xticks(np.arange(len(alpha_values)), labels=alpha_values)
                ax[hemiind][taskind].set_yticks(np.arange(len(l1_ratio_values)), labels=l1_ratio_values)
                plt.xlabel('l1 ratio')
                plt.ylabel('alpha')
                # Rotate the tick labels and set their alignment.
                plt.setp(ax[hemiind][taskind].get_xticklabels(), rotation=45, ha="right",
                        rotation_mode="anchor")

                # create an Axes on the right side of ax. The width of cax will be 5%
                # of ax and the padding between cax and ax will be fixed at 0.05 inch.
                divider = make_axes_locatable(ax[hemiind][taskind])
                cax = divider.append_axes("right", size="5%", pad=0.05)
                plt.colorbar(im, cax=cax)
                plt.tight_layout()

            
                plt.show()

                ax[hemiind][taskind].set_title(f"{hemi} Hemisphere - {task}")
                fig.tight_layout()
                # plt.show()
# plt.savefig(os.path.join(analysis_root, folder, f'heatmap_{hemi}_{task}'), bbox_inches='tight')
plt.savefig(os.path.join(analysis_root, folder, f'heatmap.png'), bbox_inches='tight')