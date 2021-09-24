%% This is a new version of the script, created April 18th to train/test on the new data

%this version is scratch. Real version of the script is _v3

%% constants
% HCP path
hcppath='/imaging/rcusack/laura_ffa_diffusion/HCP_Files/Glasser_et_al_2016_HCP_MMP1.0_RVVG/HCP_PhaseTwo/Q1-Q6_RelatedParcellation210/MNINonLinear/fsaverage_LR32k';
hemilab={'L','R'};
g=load('/imaging/rcusack/laura_ffa_diffusion/temp_summary_results/adult_s2t_v1.mat');
hcppath='/imaging/rcusack/laura_ffa_diffusion/HCP_Files/Glasser_et_al_2016_HCP_MMP1.0_RVVG/HCP_PhaseTwo/Q1-Q6_RelatedParcellation210/MNINonLinear/fsaverage_LR32k';
tmppath='/imaging/rcusack/laura_ffa_diffusion/analysis_adult_v1/temp_toptarget_v3';

%ntargroi=360; % number of target ROIs SHOULD BE 360!!
%nsubj=size(g.seed2target,1)/ntargroi; % number of subjects
%nseedvox=length(g.maskind);

figpth='/imaging/rcusack/laura_ffa_diffusion/figs_v3';


%% FFC train adult, test infant

load /imaging/rcusack/laura_ffa_diffusion/temp_summary_results/adult_s2t_v3.mat  % from s2t_toptargets_v3
load /imaging/rcusack/laura_ffa_diffusion/temp_summary_results/infant_s2t_v2.mat % from infant_s2t_v2

%% Add the xmltree path
%addpath(dropboxmatlab('xmltree-2.0')) %% this is a rhodri path, won't work
%when I run the analysis from my space. 

addpath('/home/lcabral/Dropbox//Matlab_Tools/xmltree-2.0');

%% Standard 

nsubj=size(g.s2t_adult_v1,3);
nseedvox=size(g.s2t_adult_v1,1);
ntargroi=346; %% IS THIS CORRECT SHOULD THIS BE 360???

%% Centres of ROIs
V=spm_vol('/imaging/rcusack/laura_ffa_diffusion/rois/rhcp_regions_target.nii'); %is this going to be in the wrong space? I changed it to the resliced image
[Yregionlabs XYZ]=spm_read_vols(V);
coreg=[];
for regind=1:ntargroi
    coreg(:,regind)=mean(XYZ(:,Yregionlabs==regind),2);
end;

%% Classification with loo cross-validation across subjects
a2i_seedresults={};

[mesh_white mesh_inflated]=mesh_render_preload(hcppath);

s2t_perm=permute(s2t,[3 2 1]);
isnonzero=any(sum(s2t_perm,1),2); % non zero in every subject
s2t_perm=s2t_perm(:,:,isnonzero);

s2t_infant_perm=permute(s2t_infant,[1 3 2]);
s2t_infant_perm=s2t_infant_perm(:,:,isnonzero);

diary(fullfile(figpth,'trainadult_testinfant_diary.txt'));

fprintf('Train adult test infant\n');
ax=0;
el=90;

figweights=figure('Position',[0 0 768 768]);

seedregionlist=[18 160 154];
seedregionlabel={'faces','places','tools'};

for seedregionind=1:length(seedregionlist)
    fprintf('Seed region %s\n',seedregionlabel{seedregionind});
    for hemiind=1:2
        figh=figure('Position',[0 0 768 1024]);
        fprintf('Hemisphere %s\n',hemilab{hemiind});
        hemitargetoffset=(hemiind-1)*180;
        seedregion=seedregionlist(seedregionind)+hemitargetoffset;
        
        disttotarget=sum((coreg(:,isnonzero)-repmat(coreg(:,seedregion),[1 sum(isnonzero)])).^2).^0.5;
        
        % FFC
        isffc=Yregionlabs(g.maskind)==seedregion;
        trainlabels=repmat(isffc,[1 nsubj]);
        
        % A bit clumsy - write out 3D volume of labels
        if ~exist(tmppath,'dir')
            mkdir(tmppath)
        end;
        Yout=zeros(size(Yregionlabs));
        Yout(g.maskind)=1+isffc;
        Vout=V;
        Vout.fname=fullfile(tmppath,'class_labels.nii');
        spm_write_vol(Vout,Yout);
        
        subplot(4,3,1);
        mesh_render(Vout,mesh_white,mesh_inflated);
        title(seedregionlabel{seedregionind});
        
        for subjind=1:nsubj_infant
            
            subplot(4,3,subjind+1,'Parent',figh);
            
            othersubj=1:nsubj; % all adults
            
            trainset=s2t_perm(:,othersubj,:);
            
            testset=s2t_infant_perm(:,subjind,:);
            
            trainlabels=trainlabels;
            testlabels=isffc;
            [myclass,myerr,myposterior,mylogp,mycoef] =classify(squeeze(testset),reshape(trainset,[nseedvox*nsubj sum(isnonzero)]),trainlabels(:));
            hits=mean(myclass(testlabels==1));
            fa=mean(myclass(testlabels==0));

            
            fprintf('Subject %d correct %f hits %f fa %f d-prime %f\n',subjind,mean(myclass==testlabels),hits,fa,norminv(hits)-norminv(fa));
            
            a2i_seedresults{seedregionind,subjind,hemiind}=[];
            a2i_seedresults{seedregionind,subjind,hemiind}.myclass=myclass;
            a2i_seedresults{seedregionind,subjind,hemiind}.testlabels=testlabels;
            a2i_seedresults{seedregionind,subjind,hemiind}.hits=hits;
            a2i_seedresults{seedregionind,subjind,hemiind}.fa=fa;
            a2i_seedresults{seedregionind,subjind,hemiind}.mycoef=mycoef;
   
            % A bit clumsy - write out 3D volume of labels
            if ~exist(tmppath,'dir')
                mkdir(tmppath)
            end;
            Yout=zeros(size(Yregionlabs));
            Yout(g.maskind)=1+myclass;
            Vout=V;
            Vout.fname=fullfile(tmppath,'class_labels_infants.nii');
            spm_write_vol(Vout,Yout);
            
            mesh_render(Vout,mesh_white,mesh_inflated);
            title(sprintf('S%d',subjind));
            
        end;

        print(fullfile(figpth,sprintf('trainadult_testinfant_classification_%s_%s.pdf',seedregionlabel{seedregionind},hemilab{hemiind})),'-dpdf')

        %% Weights rendered
        figure(25+seedregionind);
        clf
        Yout=zeros(size(Yregionlabs));
        isnonzeroind=find(isnonzero);
        for nonzeroind=1:length(isnonzeroind)
            Yout(Yregionlabs==isnonzeroind(nonzeroind))=mycoef(2,1).linear(nonzeroind)/2;
        end;
        Vout=V;
        Vout.fname=fullfile(tmppath,sprintf('%s_weights_labels.nii',seedregionlabel{seedregionind}));
        spm_write_vol(Vout,Yout);
        
        h=subplot(3,2,hemiind,'Parent', figweights);
        axes(h)
        mesh_render_continuous(Vout,mesh_white,mesh_inflated,[90 0]);
        
        
        h=subplot(3,2,2+hemiind,'Parent', figweights);
        axes(h)
        mesh_render_continuous(Vout,mesh_white,mesh_inflated,[270 0]);
        
        h=subplot(3,2,4+hemiind,'Parent', figweights);
        axes(h)
        mesh_render_continuous(Vout,mesh_white,mesh_inflated,[0 -90]);
        
        print(fullfile(figpth,sprintf('trainadult_weights_%s_%s.pdf',seedregionlabel{seedregionind},hemilab{hemiind})),'-dpdf')
        
    end;
end;
    
save('/imaging/rcusack/laura_ffa_diffusion/summary_results/trainadult_testinfant_v2.mat','a2i_seedresults')
    
diary off
