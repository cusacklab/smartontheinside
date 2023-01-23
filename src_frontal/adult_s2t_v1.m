%% Reads in output of probtrackxsummarize, seed 2 target connections
% and summarizes

%% Split a number labelled map into regions

tbsspth='/imaging/rcusack/laura_ffa_diffusion/tbss_norm_adult/FA';
roipth='/imaging/rcusack/laura_ffa_diffusion/rois/';

subjlist=[9001 9002 9003 9005 9007 9008 9009 9010 9011 9012 9013 9014 9015 9016];

if ~exist('subjtostartat','var')
    subjtostartat=1;
    s2t_adult_v1=[];
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
    
    s2t_adult_v1=zeros(sum(mask),length(target_labels),length(subjlist));

end;


for subjind=subjtostartat:length(subjlist)
    subj=subjlist(subjind);
    sprintf('Subject %d\n',subj);
    
    % Find this subject's data
    prebedpth='/imaging/rcusack/laura_ffa_diffusion/analysis_adult_v1/aamod_diffusion_bedpostx_00001';
    fullsubjdir=dir(fullfile(prebedpth,sprintf('*%d*',subj)));
    bedpostpth=sprintf('/imaging/rcusack/laura_ffa_diffusion/analysis_adult_v1/aamod_diffusion_bedpostx_00001/%s/diffusion.bedpostX', fullsubjdir.name);
    probtrackx2pth=sprintf('/imaging/rcusack/laura_ffa_diffusion/analysis_adult_v1/probtrackx2_hcp_frontal_FANorm/%s',fullsubjdir.name);
    
    %% Load probtrackx output
    Vs2t={};
    parfor labind=1:length(target_labels)
        [Vs2t{labind} Ys2t] =aas_spm_vol(fullfile(probtrackx2pth,sprintf('MNI_seeds_to_%d_hcp_frontal_%d.nii.gz',subj,target_labels(labind))));
        s2t_adult_v1(:,labind,subjind)=Ys2t(mask);
    end;  
    
end;
%s2t_adult_v1 is voxels (686*8) x target roi x nsubj


save /imaging/rcusack/laura_ffa_diffusion/summary_results_frontal/adult_s2t_v1.mat s2t_adult_v1