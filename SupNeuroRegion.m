%Written by Laura Cabral and Rhodri Cusack
%January, 2017
%This script will load in the supplematry neuroanatomical results and will
%attempt to assemble them into a form that we can use to define the VVC. 

%add the path to the dropbox folder that contains the sup neuro results 
addpath '/home/lcabral/Dropbox/Glasser_et_al_2016_HCP_MMP1.0_RVVG_SupNeuro/HCP_PhaseTwo/Q1-Q6_RelatedParcellation210/MNINonLinear/fsaverage_LR32k'
addpath '/home/lcabral/Dropbox/Glasser_et_al_2016_HCP_MMP1.0_RVVG/HCP_PhaseTwo/Q1-Q6_RelatedParcellation210/MNINonLinear/fsaverage_LR32k'

%Load in the file that looks like it has the files that we need. This file
%has both of the left hemisphere and thr right hemisphere in one file 
ci_supneuro=ft_read_cifti('ResultsRegions_ROI.dlabel.nii');

for hemisphere = 1:2
    
    if hemisphere == 1
        %Load the main targert labels into matlab
        ci_main=ft_read_cifti('Q1-Q6_RelatedParcellation210.L.CorticalAreas_dil_Colors.32k_fs_LR.dlabel.nii');
        
        %assign the sup neuro lables to the matrix 
        region_label(1:32492,1)=ci_supneuro.x1(1:32492,1);
        
        %assign the main labels to the matrix
        region_label(1:32492,2)=ci_main.x1(1:32492,1);
        
    elseif hemisphere ==2
        %Load the targert labels into matlab
        ci_main=ft_read_cifti('Q1-Q6_RelatedParcellation210.R.CorticalAreas_dil_Colors.32k_fs_LR.dlabel.nii');
        
        region_label(32493:64984,1)=ci_supneuro.x1(32493:64984,1);
        region_label(32493:64984,2)=ci_main.x1(1:32492,1);
       
    end
end

save('region_label','region_label')


        
        
        
        
        
        
        

        