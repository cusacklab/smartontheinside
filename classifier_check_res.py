import pandas as pd
import os


alpha_values = [0.2, 0.4, 0.8]
l1_ratio_values = [0.2, 0.4, 0.8]

analysis_root = '/Users/chiara/smartontheinside'

for alpha in alpha_values:
    for l1_ratio in l1_ratio_values:
        
        df = pd.read_csv(os.path.join(analysis_root, f'classifier_results_alpha-{alpha}_l1ratio-{l1_ratio}/summary_N-20.csv'))
        print(df)



