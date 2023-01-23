%% Compares connectivity and activity on a region-by-region basis
% The fitting has a problem with the number of dimensions as we only have
% 26 activity values (one per region) but 334 connections per region.
% The regularisation solution here is to pick the single best predicting

function compare_connectivity_and_contrasts

% Paths
summarypath='/imaging/rcusack/laura_ffa_diffusion/summary_results_frontal';
roipth='/imaging/rcusack/laura_ffa_diffusion/rois';

%% Main data sources
s2t_adult=load(fullfile(summarypath,'adult_s2t_v1.mat'));
s2t_infant=load(fullfile(summarypath,'infant_s2t_v1.mat'));
hcpcons=load(fullfile(summarypath,'hcp_contrasts.mat'));

%% Load seed labels
[Vaal_seed Yaal_seed]=aas_spm_vol(fullfile(roipth,'rhcp_regions_frontal_seed.nii'));
Yaal_seed(isnan(Yaal_seed))=0;
seeds=setdiff(unique(Yaal_seed(:)),0);
frontal_labels=Yaal_seed(Yaal_seed~=0);
nreg=length(seeds);

%% Summarise connectivity by HCP region
for seedind=1:nreg
    r2t_adult(seedind,:,:)=sum(s2t_adult.s2t_adult_v1(frontal_labels==seeds(seedind),:,:));
    r2t_infant(seedind,:,:)=sum(s2t_infant.s2t_infant_v1(frontal_labels==seeds(seedind),:,:));
end;

ntarg=size(s2t_adult.s2t_adult_v1,2);
nsubj=size(s2t_adult.s2t_adult_v1,3);
ncons=size(hcpcons.value_roi,3);

figure(11);

for ind=1:nsubj
    subplot(nsubj,1,ind)
    imagesc(r2t_adult(:,:,ind));
end;


%% Predict activity from connectivity (top correlating)
figure(12)
for subjind=1:nsubj
    others=setdiff(1:nsubj,subjind);
    mn_others=mean(r2t_adult(:,:,others),3);
    t_stats=reshape(permute(hcpcons.value_roi,[2 1 3]),[26 ncons]);
    %[A,B,r]=canoncorr(t_stats,mn_others);
    cc=corr(t_stats,mn_others);
    [mx ind]=max(cc')
    for conind=1:ncons
        rho(subjind,conind)=corr(t_stats(:,conind),r2t_adult(:,conind,subjind));
    end;
end;

%% Predict activity from connectivity (ridge regression)
mean_rho_ridge=[];
fit=[];
klist=5;
for kind=1:length(klist)
    t_stats=reshape(permute(hcpcons.value_roi,[2 1 3]),[26 ncons]);
    for subjind=1:nsubj
        others=setdiff(1:nsubj,subjind);
        mn_others=mean(r2t_adult(:,:,others),3);
        for conind=1:ncons
            b(:,conind,subjind)=ridge(t_stats(:,conind),mn_others,klist(kind));
            %            b(:,conind,subjind)=regress(t_stats(:,conind),mn_others);
            fit(:,subjind,conind)=zscore(r2t_adult(:,:,subjind)*b(:,conind,subjind));
            rho_ridge(subjind,conind)=corr(t_stats(:,conind),fit(:,subjind,conind));
        end;
    end;
    mean_rho_ridge(kind)=mean(rho_ridge(:));
    
    figure(13)
    for conind=1:ncons
        subplot(3,3,conind)
        scatter(mean(fit(:,:,conind),2),t_stats(:,conind));
        xlim([-3 3])
        ylim([-25 25]);
    end;
end