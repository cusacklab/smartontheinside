import pandas as pd
import os
import matplotlib.pyplot as plt
from statsmodels.graphics.factorplots import interaction_plot
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable


# alpha_values = [0.1, 1.0, 10.0, 100.0]
alpha_values = [0.1, 0.2, 0.4, 0.8, 1.6, 3.2, 6.4, 12.8, 25.6, 51.2]
l1_ratio_values = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]

# alpha_values = [0.1, 1.0]
# l1_ratio_values = [0.0, 0.2]

# Selection of contrasts - based on previous analysis
tasks_selected = ['tfMRI_WM', 'tfMRI_MOTOR', 'tfMRI_LANGUAGE', 'tfMRI_SOCIAL','tfMRI_EMOTION']

analysis_root = '/home/chiaracaldinelli'
# code_folder = '/home/chiaracaldinelli/smartontheinside/smartontheinside'
m = np.zeros(((len(alpha_values)),(len(l1_ratio_values))))


# Make composite figures
plt.figure()
fig,ax=plt.subplots(ncols=2, nrows=5, figsize=(10,8))

for hemiind, hemi in enumerate(['R', 'L']):
    for taskind, task in enumerate(tasks_selected):

        for alphaind, alpha in enumerate(alpha_values):
            for l1_ratioind, l1_ratio in enumerate(l1_ratio_values):

                folder = f'smartontheinside/smartontheinside/results/classifier_tune_parameters'
                os.makedirs(os.path.join(analysis_root, folder), exist_ok=True) # Make folder if it doesn't already exist

                df = pd.read_csv(os.path.join(analysis_root, f'classifier_results_alpha-{alpha}_l1ratio-{l1_ratio}/summary_N-20.csv'), index_col=False)
                df = df.loc[df['hemi'] == hemi]
                table = pd.pivot_table(df, values=['pearson', 'score'], index=['hemi', 'task'],
                    aggfunc={'pearson': np.mean,
                             'score': np.mean})
                # print(table)
                
                # file = open(os.path.join(analysis_root, folder, f'classifier_res.txt'),'a')
                # file.write(f"\n Results for alpha = {alpha} and l1_ratio = {l1_ratio}")
                # file.write(f"\n {table}")
                # file.close()


                # Calculate average of the 20 folds and summarise it in a matrix
                y = (df.loc[df['task'] == task]['score'])
                m[alphaind,l1_ratioind] = y.mean()
            
        # Compose figure
        # im = ax[taskind][hemiind].imshow(m)
        im = ax[taskind][hemiind].imshow(m)

        # # Show all ticks and label them with the respective list entries 
        ax[taskind][hemiind].set_yticks(np.arange(len(alpha_values)), labels=alpha_values, fontsize=4)
        ax[taskind][hemiind].set_xticks(np.arange(len(l1_ratio_values)), labels=l1_ratio_values, fontsize=4)
        plt.xlabel('l1 ratio', fontsize=5)
        plt.ylabel('alpha', fontsize=5)

        # Rotate the tick labels and set their alignment.
        plt.setp(ax[taskind][hemiind].get_xticklabels(), rotation=45, ha="right",
                rotation_mode="anchor")

        # create an Axes on the right side of ax. The width of cax will be 5%
        # of ax and the padding between cax and ax will be fixed at 0.05 inch.
        divider = make_axes_locatable(ax[taskind][hemiind])
        cax = divider.append_axes("right", size="5%", pad=0.05)
        plt.colorbar(im, cax=cax)
        plt.tight_layout()

        plt.show()

        ax[taskind][hemiind].set_title(f"{hemi} Hemi - {task}", fontsize=8)
        fig.tight_layout()
        # plt.show()

plt.savefig(os.path.join(analysis_root, folder, f'heatmap.png'), bbox_inches='tight')
print(f'Figure saved as heatmap.png')

# plt.savefig(os.path.join(analysis_root, folder, f'heatmap_alpha-{alpha}_l1_ratio-{l1_ratio}.png'), bbox_inches='tight')