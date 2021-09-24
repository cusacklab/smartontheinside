%% Split a number labelled map into regions

tbsspth='/imaging/rcusack/laura_ffa_diffusion/tbss_norm/FA';
roipth='/imaging/rcusack/laura_ffa_diffusion/rois/';

subjlist=[1007	1003 1020 1011	1004	1006	1005	1024	1017	1012	1013]; % no brain injury

s2t_infant=[];
s2t_rawhist_relab=[];
s2t_rawhist=zeros(360,1);
s2t_thissubj_relab=[];

g_adult=load('/imaging/rcusack/laura_ffa_diffusion/analysis_adult_v1/aamod_diffusion_probtrackxsummarize_group_00001/group_tractography_seed2target.mat');
nvox=length(g_adult.maskind);

%% Target labels
[Vaal Yaal]=aas_spm_vol(fullfile(roipth,'rhcp_regions_v4_target.nii'));    
labels=unique(Yaal(~isnan(Yaal)));
labels=setdiff(labels,0);
    
 
for subjind=1:length(subjlist)
    subj=subjlist(subjind);
    sprintf('Subject %d\n',subj);
    
    bedpostpth=sprintf('/imaging/rcusack/leire_auditory_tractography/seeds/%d/Together/dtifit_rotatebvecs.bedpostX',subj);
    probtrackx2pth=fullfile(bedpostpth,'probtrackx2_hcp');
    
    %% Unpack images
    Vs2t={};
     parfor labind=1:length(labels)
            [Vs2t{labind} Ys2t] =aas_spm_vol(fullfile(probtrackx2pth,sprintf('MNI_seeds_to_%d_hcp_v4_%d.nii.gz',subj,labels(labind))),true);
            s2t_rawhist_relab(labind)=sum(Ys2t(:));
     end;
     
    %% Sample images
    sample=[];
    for x=-1:0
        for y=-1:0
            for z=-1:0
                sample(end+1,:)=[x y z];
            end;
        end;
    end;
%    sample=[0 0 0];
    
    Vsp=Vs2t{1};
    Ysp=zeros(Vs2t{1}.dim);
    
    co=Vs2t{1}.mat\[g_adult.allXYZ(:,g_adult.maskind); ones(1,size(g_adult.maskind,1))];
    s2t_thissubj_relab=zeros(nvox,length(labels),size(sample,1));
    for sampleind=1:size(sample,1)
        for labind=1:length(labels)
            fprintf('.');
            Ysp(sub2ind(size(Ysp),co(1,:)'+sample(sampleind,1),co(2,:)'+sample(sampleind,2),co(3,:)'+sample(sampleind,3)))=1;
            s2t_thissubj_relab(:,labind,sampleind)=spm_sample_vol(Vs2t{labind},co(1,:)+sample(sampleind,1),co(2,:)+sample(sampleind,2),co(3,:)+sample(sampleind,3),0);
        end;
    end;
    
    % Delete files so we don't run out of memory
     for labind=1:length(labels)
        delete(Vs2t{labind}.fname);
     end;
    
    [pth nme ext]=fileparts(Vsp.fname);
    Vsp.fname=fullfile(pth,'sample_positions.nii');
    spm_write_vol(Vsp,Ysp);

    %% Summarize
    s2t_rawhist=zeros(360,1);
    s2t_thissubj=zeros(size(s2t_thissubj_relab,1),360);
    s2t_rawhist(labels)=s2t_rawhist_relab;
    s2t_thissubj(:,labels)=sum(s2t_thissubj_relab,3);
    fprintf('...done\n');
    figure(50); 
    scatter(s2t_rawhist,sum(s2t_thissubj,1))
    
    s2t_infant(:,:,subjind)=s2t_thissubj;
end;

save /imaging/rcusack/laura_ffa_diffusion/summary_results/infant_s2t.mat s2t_infant