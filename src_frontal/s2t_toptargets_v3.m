%numOfIC=3;
%addpath(dropboxmatlab('FastICA_25'))  If we need ICA (not in current
%analysis pipeline)

addpath(dropboxmatlab('xmltree-2.0'));

%% Load up data produced by adult_s2t_v1, other paths
g=load('/imaging/rcusack/laura_ffa_diffusion/summary_results_frontal/adult_s2t_v1.mat');
hcppath='/imaging/rcusack/laura_ffa_diffusion/HCP_Files/Glasser_et_al_2016_HCP_MMP1.0_RVVG/HCP_PhaseTwo/Q1-Q6_RelatedParcellation210/MNINonLinear/fsaverage_LR32k';
% Load the temporary file path, changed for this analysis not to overwrite
% the files from the previous analysis
tmppath='/imaging/rcusack/laura_ffa_diffusion/analysis_adult_v1/temp_toptarget_v4';
%Load the path to find the ROI's
roipth='/imaging/rcusack/laura_ffa_diffusion/rois';
 

%% Set up useful parameters
%Find the number of sujects
nsubj=size(g.s2t_adult_v1,3);
nseedvox=size(g.s2t_adult_v1,1);
ntargroi=346;

%% Define targets and seeds
% This is where we are defining the seed regions
seedreg_left=[73 67 97 98 26 70 71 87 68 83 85 84 86];
seedreg_both=[seedreg_left seedreg_left+180];
nseedreg=length(seedreg_both);

hemilab={'left','right'};
figpth='/imaging/rcusack/laura_ffa_diffusion/figs_frontal_v1';
mkdir(figpth)

% Region labels
% THIS IS WRONG AT THE MOMENT- NEEDS TO BE A LABELLED IMAGE THAT HAS THE
% DIFFERENT SEED REGIONS MARKED. COULD JUST BE AN IMAGE WITH ALL 360REGIONS
% IN. BUT, NEEDS TO BE IN THE RIGHT SPACE (SAME AS THE FOLLOWING IMAGE)

% We made a resliced image on April 18th, 2017. Using the Ventral Visual
% Stream_v3 script.

[Vhcp_regions Yhcp_regions allXYZ]=aas_spm_vol(fullfile(roipth,'rhcp_regions_frontal_seed.nii'));

%Load this to be able to get the maskind
[Vhcp_seed Yhcp_seed]=aas_spm_vol(fullfile(roipth,'rhcp_regions_frontal_seed.nii'));

% Rearrange order of dimensions
s2t=permute(g.s2t_adult_v1,[2 3 1]); %gives [ntargroi x nsubj xnseedvox]
 
%[ttval ttsortind]=sort(mean(mntarget,2),'descend');
% I took out a whole lot of stuff here which was earlier window on the data


%% Classification FFC vs other loocv across subjects
a2a={};

seedregionlist=seedreg_left;
seedregionlabel={seedreg_left(:)};

[mesh_white mesh_inflated]=mesh_render_preload(hcppath);

diary(fullfile(figpth,'trainadult_testadult_diary.txt'));

maskind=find(Yhcp_seed(:)==1);

for seedregionind=1:length(seedregionlist)
    
    s2t_perm=permute(s2t,[3 2 1]);
    isnonzero=any(sum(s2t_perm,1),2); % only voxels regions that have non-zero connections in at least one subject
    s2t_perm=s2t_perm(:,:,isnonzero);
    
    fprintf('Train adult test adult, classification for %s\n',seedregionlabel{seedregionind});
    ax=0;
    el=90;
    for hemiind=1:2
        figh=figure('Position',[0 0 1024 1024]);
        
        fprintf('Hemisphere %s\n',hemilab{hemiind});
        hemitargetoffset=(hemiind-1)*180;
        % target region
        isffc=Yhcp_regions(maskind)==seedregionlist(seedregionind)+hemitargetoffset;
        labels=repmat(isffc,[1 nsubj]);
        
        % A bit clumsy - write out 3D volume of labels
        if ~exist(tmppath,'dir')
            mkdir(tmppath)
        end
        
        Yout=zeros(size(Yhcp_regions));
        Yout(maskind)=1+isffc;
        %is this correct?
        Vout=Vhcp_regions;
        Vout.fname=fullfile(tmppath,'class_labels.nii');
        spm_write_vol(Vout,Yout);
        
        hax=subplot(4,4,1,'Parent',figh);
        axes(hax);
        mesh_render(Vout,mesh_white,mesh_inflated);
        title(seedregionlabel{seedregionind});
        
        for subjind=1:nsubj
            hax=subplot(4,4,subjind+1,'Parent',figh);
            axes(hax);
            
            othersubj=setdiff(1:nsubj,subjind);
            trainset=s2t_perm(:,othersubj,:);
            testset=s2t_perm(:,subjind,:);
            trainlabels=labels(:,othersubj);
            testlabels=labels(:,subjind);
            [myclass,myerr,myposterior,mylogp,mycoef] =classify(squeeze(testset),reshape(trainset,[nseedvox*(nsubj-1) sum(isnonzero)]),trainlabels(:));

            hits=mean(myclass(testlabels==1));
            fa=mean(myclass(testlabels==0));
            fprintf('Subject %d correct %f hits %f fa %f d-prime %f\n',subjind,mean(myclass==testlabels),hits,fa,norminv(hits)-norminv(fa));
          
            
            % A bit clumsy - write out 3D volume of labels
            Yout=zeros(size(Yhcp_regions));
            Yout(maskind)=1+myclass;
            Vout=Vhcp_regions; %changed from V
            Vout.fname=fullfile(tmppath,'class_labels.nii');
            spm_write_vol(Vout,Yout);
            
            mesh_render(Vout,mesh_white,mesh_inflated);
            title(sprintf('S%d',subjind));
            
            a2a_seedresults{seedregionind,subjind,hemiind}=[];
            a2a_seedresults{seedregionind,subjind,hemiind}.myclass=myclass;
            a2a_seedresults{seedregionind,subjind,hemiind}.testlabels=testlabels;
            a2a_seedresults{seedregionind,subjind,hemiind}.hits=hits;
            a2a_seedresults{seedregionind,subjind,hemiind}.fa=fa;
            a2a_seedresults{seedregionind,subjind,hemiind}.mycoef=mycoef;
            
        end;
        
        print(fullfile(figpth,sprintf('trainadult_testadult_classification_%s_%s.pdf',seedregionlabel{seedregionind},hemilab{hemiind})),'-dpdf')

    end;
end;

save('/imaging/rcusack/laura_ffa_diffusion/summary_results_frontal/adult_s2t_v1.mat','s2t','a2a_seedresults')

diary off



