%% Reads in output of probtrackxsummarize, seed 2 target connections
% and summarizes

%% Split a number labelled map into regions

tbsspth='/imaging/rcusack/laura_ffa_diffusion/tbss_norm_adult/FA';
roipth='/imaging/rcusack/laura_ffa_diffusion/rois/';

% subjlist=[1007	1003 1020 1011	1004	1006	1005	1024	1017	1012	1013]; % no brain injury

subjlist=[9001 9002 9003 9005 9007 9008 9009 9010 9011 9012 9013 9014 9015 9016];

s2t_adult_v1=[];
s2t_rawhist_relab=[];
s2t_rawhist=zeros(360,1);
s2t_thissubj_relab=[];

g_adult=load('/imaging/rcusack/laura_ffa_diffusion/analysis_adult_v1/aamod_diffusion_probtrackxsummarize_group_00001/group_tractography_seed2target.mat');
nvox=length(g_adult.maskind);

%% Target labels
[Vaal_target Yaal_target]=aas_spm_vol(fullfile(roipth,'rhcp_regions_v4_target.nii'));
target_labels=unique(Yaal_target(~isnan(Yaal_target)));
target_labels=setdiff(target_labels,0);

% Seed labels
[Vaal_seed Yaal_seed]=aas_spm_vol(fullfile(roipth,'rhcp_regions_v4_seed.nii'));


for subjind=1:length(subjlist)
    subj=subjlist(subjind);
    sprintf('Subject %d\n',subj);
    
    % Find this subject's data
    prebedpth='/imaging/rcusack/laura_ffa_diffusion/analysis_adult_v1/aamod_diffusion_bedpostx_00001';
    fullsubjdir=dir(fullfile(prebedpth,sprintf('*%d*',subj)));
    %fullsubjdir=dir(fullfile(bedpostpth,sprintf('*%d*',subj)));
    bedpostpth=sprintf('/imaging/rcusack/laura_ffa_diffusion/analysis_adult_v1/aamod_diffusion_bedpostx_00001/%s/diffusion.bedpostX', fullsubjdir.name);
    probtrackx2pth=sprintf('/imaging/rcusack/laura_ffa_diffusion/analysis_adult_v1/probtrackx2_hcp_FANorm/%s',fullsubjdir.name);
    
    %% Load probtrackx output
    Vs2t={};
    parfor labind=1:length(target_labels)
        [Vs2t{labind} Ys2t] =aas_spm_vol(fullfile(probtrackx2pth,sprintf('MNI_seeds_to_%d_hcp_v4_%d.nii.gz',subj,target_labels(labind))),true);
        s2t_adult_v1(:,labind,subjind)=Ys2t(Yaal_seed(:)==1);
    end;  
    
end;
%s2t_adutlt_v1 is voxels (686*8) x target roi x nsubj


save /imaging/rcusack/laura_ffa_diffusion/temp_summary_results/adult_s2t_v1.mat s2t_adult_v1