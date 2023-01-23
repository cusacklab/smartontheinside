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
nsubj_adult=size(s2t_adult.s2t_adult_v1,3);
nsubj_infant=size(s2t_infant.s2t_infant_v1,3);
ncons=size(hcpcons.value_roi,3);

figure(11);

for ind=1:nsubj_adult
    subplot(nsubj_adult,1,ind)
    imagesc(r2t_adult(:,:,ind));
end;

%% Scramble data as check
scrambledata='none'; % none | seeds | targets

switch(scrambledata)
    case 'targets'
        fprintf('Scrambling data to check stats\n');
        for subjind=1:nsubj_adult
            r2t_adult(:,:,subjind)=r2t_adult(:,randperm(ntarg),subjind);
        end;
        for subjind=1:nsubj_infant
            r2t_infant(:,:,subjind)=r2t_infant(:,randperm(ntarg),subjind);
        end;
    case 'seeds'
        for subjind=1:nsubj_adult
            r2t_adult(:,:,subjind)=r2t_adult(randperm(nreg),:,subjind);
        end;
        for subjind=1:nsubj_infant
            r2t_infant(:,:,subjind)=r2t_infant(randperm(nreg),:,subjind);
        end;
    case 'none'
end;


%% Predict activity from connectivity (ridge regression)
mean_rho_ridge=[];
rho_ridge_adult=[];
fit_adult=[];
klist=5;
for kind=1:length(klist)
    % Within adults
    t_stats=reshape(permute(hcpcons.value_roi,[2 1 3]),[26 ncons]);
    for subjind=1:nsubj_adult
        others=setdiff(1:nsubj_adult,subjind);
        mn_others=mean(r2t_adult(:,:,others),3);
        for conind=1:ncons
            b(:,conind,subjind)=ridge(t_stats(:,conind),mn_others,klist(kind));
            fit_adult(:,subjind,conind)=zscore(r2t_adult(:,:,subjind)*b(:,conind,subjind));
            rho_ridge_adult(subjind,conind)=corr(t_stats(:,conind),fit_adult(:,subjind,conind));
        end;
    end;
    mean_rho_ridge(kind)=mean(rho_ridge_adult(:));
    
    figure(13)
    for conind=1:ncons
        subplot(3,3,conind)
        scatter(zscore(mean(fit_adult(:,:,conind),2)),zscore(t_stats(:,conind)));
        xlim([-3 3])
        ylim([-3 3]);
    end;
    
    % Adult to infants
    mn_adult=mean(r2t_adult,3);
    for subjind=1:nsubj_infant
        for conind=1:ncons
            b_infant(:,conind,subjind)=ridge(t_stats(:,conind),mn_adult,klist(kind));
            fit_infant(:,subjind,conind)=zscore(r2t_infant(:,:,subjind)*b_infant(:,conind,subjind));
            rho_ridge_infant(subjind,conind)=corr(t_stats(:,conind),fit_infant(:,subjind,conind));
        end;
    end;
    
    figure(14)
    for conind=1:ncons
        subplot(3,3,conind)
        scatter(zscore(mean(fit_infant(:,:,conind),2)),zscore(t_stats(:,conind)));
        xlim([-3 3])
        ylim([-3 3]);
    end;
    
    % Bar plot comparisons
    figure(15)
    clf
    hold off
    errorbar(mean(rho_ridge_adult),std(rho_ridge_adult)/sqrt(nsubj_adult));
    hold on
    errorbar(mean(rho_ridge_infant),std(rho_ridge_infant)/sqrt(nsubj_infant));
    legend({'adult','infant'})
    ylim([-1 1]);
    set(gca,'XTickLabel',hcpcons.cons)
    
    figure(17); 
    subplot 311; 
    bar(zscore(t_stats(:,1))); 
    ylim([-3 3]);
    subplot 312; 
    bar(zscore(mean(fit_adult(:,:,1),2))); 
    ylim([-3 3]);
    subplot 313; 
    bar(zscore(mean(fit_infant(:,:,1),2)));
    ylim([-3 3]);
    
    %% Save data
    save(fullfile(summarypath,'compare_connectivity_and_contrasts.mat'),'fit_adult','fit_infant','rho_ridge_infant','rho_ridge_adult','t_stats','seeds');
    
    
    
end