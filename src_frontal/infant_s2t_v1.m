%% Reads in output of probtrackxsummarize, seed 2 target connections
% and summarizes

%% Split a number labelled map into regions

tbsspth='/imaging/rcusack/laura_ffa_diffusion/tbss_norm/FA';
roipth='/imaging/rcusack/laura_ffa_diffusion/rois/';

subjlist=[1003 1004 1005 1006 1007 1011 1012 1013 1017 1020 1024]; % no brain injury


if ~exist('subjtostartat','var')
    subjtostartat=1;
    s2t_infant_v1=[];
    s2t_rawhist_relab=[];
    s2t_rawhist=zeros(360,1);
    s2t_thissubj_relab=[];

    %% Target labels
    [Vaal_target Yaal_target]=aas_spm_vol(fullfile(roipth,'rhcp_regions_frontal_target.nii'));
    target_labels=unique(Yaal_target(~isnan(Yaal_target)));
    target_labels=setdiff(target_labels,0);

    % Seed labels
    [Vaal_seed Yaal_seed]=aas_spm_vol(fullfile(roipth,'rhcp_regions_frontal_seed.nii'));
    Yaal_seed(isnan(Yaal_seed))=0;
    mask=Yaal_seed(:)~=0;
    
    s2t_infant_v1=zeros(sum(mask),length(target_labels),length(subjlist));

end;


for subjind=subjtostartat:length(subjlist)
    subj=subjlist(subjind);
    sprintf('Subject %d\n',subj);
    
    % Find this subject's data
    bedpostpth=sprintf('/imaging/rcusack/leire_auditory_tractography/seeds/%d/Together/dtifit_rotatebvecs.bedpostX',subj);
    probtrackx2pth=fullfile(bedpostpth,'probtrackx2_hcp_frontal');
    
    %% Load probtrackx output
    Vs2t={};
    parfor labind=1:length(target_labels)
        [Vs2t{labind} Ys2t] =aas_spm_vol(fullfile(probtrackx2pth,sprintf('MNI_seeds_to_%d_hcp_frontal_%d.nii.gz',subj,target_labels(labind))));
        s2t_infant_v1(:,labind,subjind)=Ys2t(mask);
    end;  
    
end;



save /imaging/rcusack/laura_ffa_diffusion/summary_results_frontal/infant_s2t_v1.mat s2t_infant_v1