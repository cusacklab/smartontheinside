import pandas as pd 
import numpy as np




df = pd.read_csv('participants.tsv', sep='\t')
print(df)



# Select only term babies
df = df.loc[df['birth_age'] >= 37]
print(df)

# check that only term babies are included 
term = df['birth_age']
print(np.amin(term))

df_male = df.loc[df['gender'] == 'Male']
print('Describe males')
print(df_male.describe())

df_female = df.loc[df['gender'] == 'Female']
print('Describe females')
print(df_female.describe())


# # Mean birth age and birth weight
# table = pd.pivot_table(df, values=['birth_age', 'birth_weight'],
#                     columns=['gender'], aggfunc=np.mean)
# print(table)

# # St dev birth age and birth weight
# table = pd.pivot_table(df, values=['birth_age', 'birth_weight'],
#                     columns=['gender'], aggfunc=np.std)
# print(table)
