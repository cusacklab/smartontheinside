import pandas as pd
import os
import matplotlib.pyplot as plt
from statsmodels.graphics.factorplots import interaction_plot

alpha_values = [0.2, 0.4, 0.8]
l1_ratio_values = [0.2, 0.4, 0.8]

analysis_root = '/Users/chiara/smartontheinside'

for alpha in alpha_values:
    for l1_ratio in l1_ratio_values:
        
        df = pd.read_csv(os.path.join(analysis_root, f'classifier_results_alpha-{alpha}_l1ratio-{l1_ratio}/summary_N-20.csv'), index_col=False)

        dfL = df.loc[df['hemi'] == 'L']
        dfR = df.loc[df['hemi'] == 'R']
        
        print(dfL)
        print(dfR)

        fold = (dfL['fold'])
        print(fold)
        print(dfL['task'])
        print(dfL['score'])

        # plt.figure()
        fig,ax=plt.subplots(nrows=2, figsize=(10,8))
        fig=interaction_plot(x=dfR['fold'], trace=dfR['task'], response=dfR['score'], ax=ax[0])
        fig=interaction_plot(x=dfR['fold'], trace=dfR['task'], response=dfR['score'], ax=ax[1])
        fig.tight_layout()
        fig.set_figheight(9)
        fig.set_figwidth(15)

        plt.savefig((f'res_alpha_{alpha}_l1_ratio_{l1_ratio}.png'), bbox_inches='tight')