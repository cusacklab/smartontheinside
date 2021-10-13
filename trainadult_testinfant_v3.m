%% This is a new version of the script, created April 18th to train/test on the new data

%V3 created after Rhodri suggested I combine scripts s2t_toptarget and
%trainadult_testinfant_v2.m 

%% constants
% HCP path
hcppath='/imaging/rcusack/laura_ffa_diffusion/HCP_Files/Glasser_et_al_2016_HCP_MMP1.0_RVVG/HCP_PhaseTwo/Q1-Q6_RelatedParcellation210/MNINonLinear/fsaverage_LR32k';
hemilab={'left','right'}; %timeseries
g=load('/imaging/rcusack/laura_ffa_diffusion/temp_summary_results/adult_s2t_v1.mat'); %matrix subj x target ROI x seed ROI
hcppath='/imaging/rcusack/laura_ffa_diffusion/HCP_Files/Glasser_et_al_2016_HCP_MMP1.0_RVVG/HCP_PhaseTwo/Q1-Q6_RelatedParcellation210/MNINonLinear/fsaverage_LR32k'; %timeseries - repeated?
tmppath='/imaging/rcusack/laura_ffa_diffusion/analysis_adult_v1/temp_toptarget_v3'; %top ROIs
figpth='/imaging/rcusack/laura_ffa_diffusion/figs_v3'; %results' plots output
%Load the path to find the ROI's
roipth='/imaging/rcusack/laura_ffa_diffusion/rois';

figweights=figure('Position',[0 0 768 768]);

%% FFC train adult, test infant
load /imaging/rcusack/laura_ffa_diffusion/temp_summary_results/adult_s2t_v3.mat  % from s2t_toptargets_v3
load /imaging/rcusack/laura_ffa_diffusion/temp_summary_results/infant_s2t_v2.mat % from infant_s2t_v2

%% Add the xmltree path
%addpath(dropboxmatlab('xmltree-2.0')) %% this is a rhodri path, won't work
%when I run the analysis from my space. 
addpath('/home/lcabral/Dropbox//Matlab_Tools/xmltree-2.0');

%% Standard setting up of useful parameters
nsubj=size(s2t,2);
nsubj_infant=size(s2t_infant_v2,3);
nseedvox=size(s2t,3);
ntargroi=346; %% IS THIS CORRECT SHOULD THIS BE 360???

%% Define targets and seeds
% This is where we are defining the seed regions
seedreg_left=[7 163 22 18 153 154 160];
seedreg_both=[seedreg_left seedreg_left+180];
nseedreg=length(seedreg_both);

%Load this to be able to get the maskind
[Vhcp_seed Yhcp_seed]=aas_spm_vol(fullfile(roipth,'rhcp_regions_v4_seed.nii'));

%Load this to get the labeled seed regions
[Vhcp_regions Yhcp_regions allXYZ]=aas_spm_vol(fullfile(roipth,'rhcp_regions_v5_seed.nii'));

%% Centres of ROIs
V=spm_vol('/imaging/rcusack/laura_ffa_diffusion/rois/rhcp_regions_target.nii'); %is this going to be in the wrong space? I changed it to the resliced image
[Yregionlabs XYZ]=spm_read_vols(V);

%% Classification with loo cross-validation across subjects
a2i_seedresults={};

[mesh_white mesh_inflated]=mesh_render_preload(hcppath);

s2t_perm=permute(s2t,[3 2 1]);
isnonzero=any(sum(s2t_perm,1),2); % non zero in every subject
s2t_perm=s2t_perm(:,:,isnonzero);

s2t_infant_perm=permute(s2t_infant_v2,[1 3 2]);
s2t_infant_perm=s2t_infant_perm(:,:,isnonzero);

maskind=find(Yhcp_seed(:)==1);

diary(fullfile(figpth,'trainadult_testinfant_diary.txt')); %keep track of what was run

fprintf('Train adult test infant\n');
ax=0;
el=90;

%Here we're defining which regions are the target regions for this analysis
seedregionlist=[18 160 154];
seedregionlabel={'faces','places','tools'};

for seedregionind=1:length(seedregionlist)
 
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
        
        for subjind=1:nsubj_infant
            hax=subplot(4,4,subjind+1,'Parent',figh);
            axes(hax);
            
            %all adults are the training set
            othersubj=1:nsubj;
            trainset=s2t_perm(:,othersubj,:);
            
            %Infant in the current loop is the test set
            testset=s2t_infant_perm(:,subjind,:);
            
            trainlabels=labels(:,othersubj);
            testlabels=labels(:,subjind);
            %took out the nsubj-1 in the line below. We are no longer using
            %cross validation 
            [myclass,myerr,myposterior,mylogp,mycoef] =classify(squeeze(testset),reshape(trainset,[nseedvox*(nsubj) sum(isnonzero)]),trainlabels(:));

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
            
            a2i_seedresults{seedregionind,subjind,hemiind}=[];
            a2i_seedresults{seedregionind,subjind,hemiind}.myclass=myclass;
            a2i_seedresults{seedregionind,subjind,hemiind}.testlabels=testlabels;
            a2i_seedresults{seedregionind,subjind,hemiind}.hits=hits;
            a2i_seedresults{seedregionind,subjind,hemiind}.fa=fa;
            a2i_seedresults{seedregionind,subjind,hemiind}.mycoef=mycoef;
            
        end
        
        print(fullfile(figpth,sprintf('trainadult_testinfant_classification_%s_%s.pdf',seedregionlabel{seedregionind},hemilab{hemiind})),'-dpdf')

    end
end


%         %% Weights rendered
%         figure(25+seedregionind);
%         clf
%         Yout=zeros(size(Yregionlabs));
%         isnonzeroind=find(isnonzero);
%         for nonzeroind=1:length(isnonzeroind)
%             Yout(Yregionlabs==isnonzeroind(nonzeroind))=mycoef(2,1).linear(nonzeroind)/2;
%         end;
%         Vout=V;
%         Vout.fname=fullfile(tmppath,sprintf('%s_weights_labels.nii',seedregionlabel{seedregionind}));
%         spm_write_vol(Vout,Yout);
%         
%         h=subplot(3,2,hemiind,'Parent', figweights);
%         axes(h)
%         mesh_render_continuous(Vout,mesh_white,mesh_inflated,[90 0]);
%         
%         
%         h=subplot(3,2,2+hemiind,'Parent', figweights);
%         axes(h)
%         mesh_render_continuous(Vout,mesh_white,mesh_inflated,[270 0]);
%         
%         h=subplot(3,2,4+hemiind,'Parent', figweights);
%         axes(h)
%         mesh_render_continuous(Vout,mesh_white,mesh_inflated,[0 -90]);
%         
%         print(fullfile(figpth,sprintf('trainadult_weights_%s_%s.pdf',seedregionlabel{seedregionind},hemilab{hemiind})),'-dpdf')
%         
%     end;
% end;

%This is the wrong path, I copied the file, but have changed it in case we
%run it again.
%save('/imaging/rcusack/laura_ffa_diffusion/summary_results/trainadult_testinfant_v3.mat','a2i_seedresults')

save('/imaging/rcusack/laura_ffa_diffusion/temp_summary_results/trainadult_testinfant_v3.mat','a2i_seedresults')
    
diary off
