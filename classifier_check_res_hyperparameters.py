import pandas as pd
import os
import matplotlib.pyplot as plt
from statsmodels.graphics.factorplots import interaction_plot
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable
import boto3


alpha_values = [0.1, 0.2, 0.4, 0.8, 1.6, 3.2, 6.4, 12.8, 25.6, 51.2]
l1_ratio_values = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]

# Selection of contrasts - based on previous analysis
tasks_selected = ['tfMRI_WM', 'tfMRI_MOTOR', 'tfMRI_LANGUAGE', 'tfMRI_SOCIAL','tfMRI_EMOTION']

analysis_root = '/home/chiaracaldinelli'
# code_folder = '/home/chiaracaldinelli/smartontheinside/smartontheinside'
m = np.zeros(((len(alpha_values)),(len(l1_ratio_values))))

# Credentials for downloading data from the cusack lab s3
s3 = boto3.client('s3')
session = boto3.Session(profile_name='default')


# Make composite figures
plt.figure()
fig,ax=plt.subplots(ncols=2, nrows=5, figsize=(8,10))

for hemiind, hemi in enumerate([ 'L', 'R']):
    for taskind, task in enumerate(tasks_selected):

        for alphaind, alpha in enumerate(alpha_values):
            for l1_ratioind, l1_ratio in enumerate(l1_ratio_values):

                # Download results of parameters tuning
                remotepath_conn = (f'Results/classifier_results_alpha-{alpha_values[alphaind]}_l1ratio-{l1_ratio_values[l1_ratioind]}/summary_N-20.csv')

                # s3.download_file('smartontheinside', remotepath_conn, f'/home/chiaracaldinelli/summary_N-20_alpha-{alpha_values[alphaind]}_l1ratio-{l1_ratio_values[l1_ratioind]}.csv')

                folder = f'smartontheinside/smartontheinside/results/classifier_tune_parameters'
                os.makedirs(os.path.join(analysis_root, folder), exist_ok=True) # Make folder if it doesn't already exist

                df = pd.read_csv(os.path.join(f'/home/chiaracaldinelli/summary_N-20_alpha-{alpha_values[alphaind]}_l1ratio-{l1_ratio_values[l1_ratioind]}.csv'), index_col=False)
                df = df.loc[df['hemi'] == hemi]
                table = pd.pivot_table(df, values=['pearson', 'score'], index=['hemi', 'task'],
                    aggfunc={'pearson': np.mean,
                             'score': np.mean})


                # Calculate average of the 20 folds and summarise it in a matrix
                y = (df.loc[df['task'] == task]['score'])
                m[alphaind,l1_ratioind] = y.mean()
        
        # Compose figure
        im = ax[taskind][hemiind].imshow(m, cmap='PiYG', vmin=-0.06, vmax=0.06, aspect='auto')
        # Show all ticks and label them with the respective list entries 
        ax[taskind][hemiind].set_yticks(np.arange(len(alpha_values)), labels=alpha_values, fontsize=6)
        ax[taskind][hemiind].set_xticks(np.arange(len(l1_ratio_values)), labels=l1_ratio_values, fontsize=6)

        # Rotate the tick labels and set their alignment.
        plt.setp(ax[taskind][hemiind].get_xticklabels(), rotation=45, ha="right",
                rotation_mode="anchor")

        # create an Axes on the right side of ax. The width of cax will be 5%
        # of ax and the padding between cax and ax will be fixed at 0.05 inch.
        divider = make_axes_locatable(ax[taskind][hemiind])

        # ax[taskind][hemiind].set_title(f"{hemi} Hemi - {task}", fontsize=8)


plt.tight_layout()
plt.subplots_adjust(bottom=0.3, right=1, top=1)
cax = plt.axes([0.85, 0.1, 0.05, 0.1])
#plt.xlabel('l1 ratio', fontsize=8)
#plt.ylabel('alpha', fontsize=8)
plt.colorbar(im, cax=cax)
plt.show()



plt.savefig( f'/home/chiaracaldinelli/smartontheinside/smartontheinside/heatmap.png', bbox_inches='tight')
print(f'Figure saved as heatmap.png')
