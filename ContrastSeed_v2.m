%% Written by Laura Cabral and Rhodri Cusack March 2017

%This script will attempt to load the contrasts from the HCP data to
%identify what labels in the ventral visual stream are part of the FFA, PPA
%and LOC

targetpath='/imaging/rcusack/laura_ffa_diffusion/rois';
addpath '/home/lcabral/Dropbox';
addpath '/imaging/rcusack/laura_ffa_diffusion/HCP_Files/Glasser_et_al_2016_HCP_MMP1.0_RVVG/HCP_PhaseTwo/Q1-Q6_RelatedParcellation210/MNINonLinear/Results/tfMRI_ALLTASKS/'

% Regions
regs=[7 163 22 18 153 154 160];

%Right now let's just work on one hemisphere, then we can loop around
%regs=[regs regs+180];
for hemi = 1:2
if hemi== 1
        ci=ft_read_cifti('Q1-Q6_RelatedParcellation210_tfMRI_ALLTASKS_level3_hp200_s2_MSMAll_2_d41_WRN_DeDrift_L.CorticalAreas_dil_Group.pscalar.nii');
        for regind=1:length(regs)
            value_roi(regind,1)=regs(regind);
            %change contrast here
            value_roi(regind,2)=ci.tfmri_wm_tool_avg(regs(regind));
        end
elseif hemi==2
       ci=ft_read_cifti('Q1-Q6_RelatedParcellation210_tfMRI_ALLTASKS_level3_hp200_s2_MSMAll_2_d41_WRN_DeDrift_R.CorticalAreas_dil_Group.pscalar.nii');
        for regind=1:length(regs)
            value_roi(regind+7,1)=regs(regind);
            %change contrast here
            value_roi(regind+7,2)=ci.tfmri_wm_tool_avg(regs(regind));
        end       
end
end
bar(value_roi(:,2))

labels=[regs regs+180];

set(gca,'XTick',[1:14])
set(gca,'XTickLabel',labels);

figpath= '/home/lcabral/Dropbox/';

print(fullfile(figpath,'toolBar.pdf'),'-dpdf');
