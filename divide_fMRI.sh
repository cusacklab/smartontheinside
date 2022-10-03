#!/bin/bash


for subj in 172938 180432 192035 200917 211417 239944 303119 365343 436239 513736 579665 638049 702133 774663 865363 930449 106521 114823 123521 130922 137936 152831 160729 173334 180533 192136 201111 211619 249947 305830 366042 436845 516742 580650 645450 715041 782561 871762 942658 106824 117021 123925 131823 138332 153025 162026 173536 180735 192439 201414 211821 251833 310621 371843 445543 519950 580751 647858 720337 800941 871964 955465 107018 117122 125222 132017 138837 153227 162329 173637 180937 193239 201818 211922 257542 314225 378857 454140 523032 585862 654350 725751 803240 872562 959574 107422 117324 125424 133827 142828 153631 164030 173940 182739 194140 202719 212015 257845 316633 381543 459453 525541 586460 654754 727553 812746 873968 966975; do


    for task in 'tfMRI_WM' 'tfMRI_MOTOR' 'tfMRI_LANGUAGE' 'tfMRI_SOCIAL' 'tfMRI_EMOTION'; do

        # Get functional data from HCP
        aws s3 cp s3://hcp-openaccess/HCP_1200/${subj}/MNINonLinear/Results/${task}/${task}_hp200_s2_level2_MSMAll.feat/${subj}_${task}_level2_hp200_s2_MSMAll.dscalar.nii /home/chiaracaldinelli/${subj}_${task}_level2_hp200_s2_MSMAll.dscalar.nii --profile hcp
        
        # Split file into left and right 
        wb_command -cifti-separate /home/chiaracaldinelli/${subj}_${task}_level2_hp200_s2_MSMAll.dscalar.nii COLUMN  -metric CORTEX_LEFT /home/chiaracaldinelli/${subj}_${task}_m1_L.func.gii
        wb_command -cifti-separate /home/chiaracaldinelli/${subj}_${task}_level2_hp200_s2_MSMAll.dscalar.nii COLUMN  -metric CORTEX_RIGHT /home/chiaracaldinelli/${subj}_${task}_m1_R.func.gii  

        # Push new files to s3
        aws s3 cp /home/chiaracaldinelli/${subj}_${task}_m1_L.func.gii s3://smartontheinside/Results/${subj}_${task}_m1_L.func.gii
        aws s3 cp /home/chiaracaldinelli/${subj}_${task}_m1_R.func.gii s3://smartontheinside/Results/${subj}_${task}_m1_R.func.gii

        # Remove local files
        rm /home/chiaracaldinelli/${subj}_${task}_level2_hp200_s2_MSMAll.dscalar.nii
        rm /home/chiaracaldinelli/${subj}_${task}_m1_L.func.gii 
        rm /home/chiaracaldinelli/${subj}_${task}_m1_R.func.gii


    done
done