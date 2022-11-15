import pandas as pd


alpha_values = [0.2, 0.4, 0.8]
l1_ratio_values = [0.2, 0.4, 0.8]

analysis_root = '/home/chiaracaldinelli'

for alpha in alpha_values:
    for l1_ratio l1_ratio_values:
        
        df = pd.read_csv(os.path.join(analysis_root, f'classifier_results_alpha-{alpha}_l1ratio-{l1_ratio}.npy'))
        print(df)
