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

% Load target
V=spm_vol(fullfile(targetpath,'hcp_regions_target.nii'));
Y=spm_read_vols(V);

ci=ft_read_cifti('Q1-Q6_RelatedParcellation210_tfMRI_ALLTASKS_level3_hp200_s2_MSMAll_2_d41_WRN_DeDrift_L.CorticalAreas_dil_Group.pscalar.nii');

Yseed=zeros(size(Y));
Ytarget=Y;


for regind=1:length(regs)
    % Add this to seed mask
    Yseed(Y==regs(regind))=ci.tfmri_wm_face_avg(regs(regind));
end;

cd '/home/lcabral/Dropbox/'

V.fname='hcp_regions_contrast_seed.nii';

spm_write_vol(V,Yseed);



