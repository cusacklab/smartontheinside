Chiara Caldinelli and Rhodri Cusack
caldinec@tcd.it 

Code used to run this analysis is the following.

I - Data was obtained from the HCP S3, using a subset of 1200 subject release, it was downloaded from S3 AWS (REF). Only a selection of contrasts was downloaded, in particular all the negative contrasts were excluded from selection. The full list of contrasts used for this analysis is the following:
A rdm analysis was performed and the contrasts with the most different pattern of activation were recorded. These contrasts were: Emotion, Language - Story, Motor - Average, contrast Social - TOM, Working Memory - 2-back.
Code used for this analysis: 
docker-hcp/roi_extract_one_subject.py
docker-hcp/hcp_example.py docker-hcp/MeanSTD.py

II - ROI masks were created
Code used for this analysis: makerois.py

III - A tractography analysis was performed.
Code used for this analysis: smartontheinside/slurm_3_run_tractograpy.sh

IV - Results were summarised in plots.
Code used for this analysis: pool_sub.py

V - Results from tractography were transformed from volume to surface
Code used for this analysis: slurm_3_summarise_res.sh

VI - Files containing time series for each selected fMRI were downloaded from the HCP S3 (1200 dataset) and summarised for each subject. 
Code used for this analysis: extract_conn_act.py

VII - A matrix containing activation during each of the selected fMRI tasks (nsub * nDLPFCvoxels), and ra matrix results from tractography (nsub * nDLPFCvoxels * ntarget_regions) were created. A classifier model was built using elastic net.
Code used for this analysis: classifier.py
