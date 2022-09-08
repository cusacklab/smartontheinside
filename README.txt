Chiara Caldinelli and Rhodri Cusack
caldinec@tcd.it 

Code used to run this analysis is the following.

I STEP:
extract_activation.py
I will pull data from HCP S3, using a subset of 1200 subject release. It will pull data from a selection of contrasts and save a file for each subject.

II STEP:
pool_sub.py
This is taking into consideration all ROIs and calculating the most active per each contrast.

III STEP:
classification.py