import pandas as pd 
import numpy as np


df = pd.read_csv('participants.tsv', sep='\t')
print(df)

# Select preterm babies and save the codes in a txt file
df_preterm = df.loc[df['birth_age'] < 37]
print(df_preterm.describe())

# Write the codes of brabies born preterm into a list and then save it in a txt file
codes_preterm = df_preterm['pparticipant_id']
codes_preterm = codes_preterm.tolist()
print(codes_preterm)

file = open('preterm_list.txt','w')
for baby in codes_preterm:
	file.write(baby+"\n")
file.close()


# Select only term babies
df = df.loc[df['birth_age'] >= 37]
print(df)

df_male = df.loc[df['gender'] == 'Male']
print('Describe males')
print(df_male.describe())

df_female = df.loc[df['gender'] == 'Female']
print('Describe females')
print(df_female.describe())