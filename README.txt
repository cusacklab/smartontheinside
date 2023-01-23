Chiara Caldinelli and Rhodri Cusack
caldinec@tcd.it 

Code used to run this analysis is the following.


******************* ADULT ANALYSIS *******************

I - Data was obtained from the HCP S3, using a subset of 1200 subject release, it was downloaded from S3 AWS (REF). Only a selection of contrasts was downloaded, in particular all the negative contrasts were excluded from selection. The full list of contrasts used for this analysis is the following:
A rdm analysis was performed and the contrasts with the most different pattern of activation were recorded. These contrasts were: Emotion, Language - Story, Motor - Average, contrast Social - TOM, Working Memory - 2-back.
Code used for this analysis: docker-hcp/roi_extract_one_subject.py and docker-hcp/hcp_example.py docker-hcp/MeanSTD.py

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



******************* INFANT ANALYSIS *******************

VIII - Images from the dHCP diffusion pipeline were registered to the Glasser parcellation in order to run tractography.
Code used for this analysis: hcp2dhcp.sh

IX - Infant tractography was run using slurm. 
Code used for this analysis: slurm_1_infant_tractography.sh, slurm_2_infant_tractography.sh, infant_tractography.sh.
Output is at s3://smartontheinside/infant_tractography/$SUBJ/Diffusion.probtrackx2/

X - The results of the tractography analysis were transformed into surface adult space
Code used for this analysis: slurm_res_1_summarise_results_infants.sh, slurm_res_2_summarise_infants.sh, slurm_res_2_summarise_infants.sh,
Output is at s3://smartontheinside/infant_tractography/${SUBJ}/T1w/Diffusion.probtrackx2/${hemi}
Output of apply warp (seed2target.nii --> label40weeks.nii): ${tmp_dir}/T1w/Diffusion.probtrackx2/${hem}/seed2target_40weeks_${SUBJ}_${roi}.nii.gz
Output of ants (label 40 weeks .nii --> dhcp template40weeks): ${tmp_dir}/T1w/Diffusion.probtrackx2/${hem}/seed2target_template_40weeks__${SUBJ}_${roi}.nii.gz
Output of wb_command (volume to surface): ${tmp_dir}/T1w/Diffusion.probtrackx2/${hem}/seeds_to_ROI.${roi}.shape.giiOutput of wb_command (volume to surface): 

XI - The tractography results in adult surface space were then organised in python matrices
Code used for this analysis: slurm_res_summarise_res_PANDAS.py.py
