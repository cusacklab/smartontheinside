%% Written by Laura Cabral and Rhodri Cusack March 2017

% Laura Cabral 2017
% Rhodri Cusack 2017-06-21

%This script will attempt to load the contrasts from the HCP data to
%identify what labels in the ventral visual stream are part of the FFA, PPA
%and LOC
summarypath='/imaging/rcusack/laura_ffa_diffusion/summary_results_frontal';
targetpath='/imaging/rcusack/laura_ffa_diffusion/rois';
addpath '/home/lcabral/Dropbox';
addpath '/imaging/rcusack/laura_ffa_diffusion/HCP_Files/Glasser_et_al_2016_HCP_MMP1.0_RVVG/HCP_PhaseTwo/Q1-Q6_RelatedParcellation210/MNINonLinear/Results/tfMRI_ALLTASKS/'
addpath(dropboxmatlab('cifti-matlab'))

% Regions
% Just one hemisphere
regs=sort([73 67 97 98 26 70 71 87 68 83 85 84 86]);
regsperhemi=length(regs);


% Not quite sure about tfmri_gambling_reward - check workbench file
cons={'tfmri_wm_2bk_0bk','tfmri_gambling_reward','tfmri_motor_cue','tfmri_language_math','tfmri_language_story','tfmri_language_story_math','tfmri_social_tom_random','tfmri_relational_match'};

%Right now let's just work on one hemisphere, then we can loop around
%regs=[regs regs+180];
value_roi=[];
for hemi = 1:2
    if hemi== 1
        ci=ft_read_cifti('Q1-Q6_RelatedParcellation210_tfMRI_ALLTASKS_level3_hp200_s2_MSMAll_2_d41_WRN_DeDrift_L.CorticalAreas_dil_Group.pscalar.nii');
    elseif hemi==2
        ci=ft_read_cifti('Q1-Q6_RelatedParcellation210_tfMRI_ALLTASKS_level3_hp200_s2_MSMAll_2_d41_WRN_DeDrift_R.CorticalAreas_dil_Group.pscalar.nii');
    end
    for regind=1:regsperhemi
        for conind=1:length(cons)
            %change contrast here
            value_roi(hemi,regind,conind)=ci.(cons{conind})(regs(regind));
        end
    end;
end

%% Save summary
save(fullfile(summarypath,'hcp_contrasts.mat'),'value_roi','cons');

%% Graph up
figure(10);
subplot 211
bar(squeeze(value_roi(1,:,:)))
title('left');
set(gca,'XTick',[1:regsperhemi])
set(gca,'XTickLabel',regs);

subplot 212
bar(squeeze(value_roi(2,:,:)))
title('right');
set(gca,'XTick',[1:regsperhemi])
set(gca,'XTickLabel',regs+180);

% figpath= '/home/lcabral/Dropbox/';
% 
% print(fullfile(figpath,'toolBar.pdf'),'-dpdf');
