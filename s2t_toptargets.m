numOfIC=3;

addpath(dropboxmatlab('FastICA_25'))

g=load('/imaging/rcusack/laura_ffa_diffusion/analysis_adult_v1/aamod_diffusion_probtrackxsummarize_group_00001/group_tractography_seed2target.mat');
hcppath='/imaging/rcusack/laura_ffa_diffusion/HCP_Files/Glasser_et_al_2016_HCP_MMP1.0_RVVG/HCP_PhaseTwo/Q1-Q6_RelatedParcellation210/MNINonLinear/fsaverage_LR32k';
tmppath='/imaging/rcusack/laura_ffa_diffusion/analysis_adult_v1/temp';
ntargroi=360; % number of target ROIs SHOULD BE 360!!
nsubj=size(g.seed2target,1)/ntargroi; % number of subjects
nseedvox=length(g.maskind);

seedreg_left=[7 163 22 18 153 154 160];
seedreg_both=[seedreg_left seedreg_left+180];
nseedreg=length(seedreg_both);

hemilab={'left','right'};

% Reshape to 3D matrix ntarg x nsubj x nseedvox 
s2t=reshape(g.seed2target,[ntargroi nsubj nseedvox]);

mntarget=mean(s2t,3);
sdtarget=std(s2t,[],3);

figure(10);
subplot 311
imagesc(mntarget');
subplot 312
imagesc(sdtarget');
subplot 313
seedrr=zeros(ntargroi,1);
seedrr(seedreg_both)=1;
imagesc(seedrr');

[ttval ttsortind]=sort(mean(mntarget,2),'descend');

%% Show targets for each individual
xc=g.allXYZ(1,g.maskind);
yc=g.allXYZ(2,g.maskind);
zc=g.allXYZ(3,g.maskind);
cm=colormap('jet');

figure(11)
s2t_z=s2t/1000;
colind=round(64*s2t_z);
%colind=round(64*((s2t_z/3)+0.5));
colind(colind<1)=1;
colind(colind>64)=64;

numOftt=1;
for ttind=1:numOftt
    for subj=1:nsubj
         subplot(numOftt,nsubj,subj+(ttind-1)*nsubj);
        scatter3(xc,yc,zc,1,cm(colind(ttsortind(ttind),subj,:),:));
        axis off
    end;
end;


%% Average components across subjects
figure(12);
clf
s2t_mnsubj=squeeze(mean(s2t_z,2));
colind=round(64*s2t_mnsubj);
%colind=round(64*((s2t_z/3)+0.5));
colind(colind<1)=1;
colind(colind>64)=64;
for ttind=1:numOftt
        subplot(4,4,ttind);
        scatter3(g.allXYZ(1,:),g.allXYZ(2,:),g.allXYZ(3,:),0.5,[0.8 0.8 0.8]);
        hold on
        scatter3(xc,yc,zc,1,cm(colind(ttsortind(ttind),:),:));
        axis off
end;


%% Region to region connectivities
V=spm_vol('/imaging/rcusack/laura_ffa_diffusion/rois/hcp_regions_target.nii');
[Y XYZ]=spm_read_vols(V);
coreg=[];
for regind=1:ntargroi
    coreg(:,regind)=mean(XYZ(:,Y==regind),2);
end;
figure(13); 
clf


for seedind=1:6
    subplot(3,2,seedind);
    scatter3(coreg(1,:),coreg(2,:),coreg(3,:),1+seedrr*5,'filled')
    hold on
    axis off
    axis equal
    view(0,90);
    voxinseed=Y(g.maskind)==seedreg_both(seedind);
    for targind=1:ntargroi
        linewidth=mean(0.001+s2t_mnsubj(targind,voxinseed))*10;
        if linewidth>0.1
        plot3(coreg(1,[seedreg_both(seedind) targind]),coreg(2,[seedreg_both(seedind) targind]),coreg(3,[seedreg_both(seedind) targind]),'k','LineWidth',linewidth);
        end;
    end
end;

%% Seed to target distance plot

dist=[];
for seedvoxind=1:size(s2t_mnsubj,2)
    for targind=1:ntargroi
        dist(targind,seedvoxind)=sqrt(sum((coreg(:,targind)-g.allXYZ(:,g.maskind(seedvoxind))).^2));
    end;
end;

figure(14);
scatter(dist(:),s2t_mnsubj(:))

%% Connectivity patterns of regions
figure(15);
for hemiind=1:2
    hemitargetoffset=(hemiind-1)*180;
    for seedind=1:length(seedreg_left)
        voxinseed=Y(g.maskind)==hemitargetoffset+seedreg_left(seedind);
        targdist=mean(s2t_mnsubj((1:180)+hemitargetoffset,voxinseed),2);
        subplot(length(seedreg_left),2,(seedind-1)*2+hemiind)
        bar(targdist);
        title(sprintf('seed %d',seedreg_left(seedind)+hemitargetoffset));
    end;
end;
    
%% FFC vs other loo across subjects

fshemilab={'L','R'};
clear mesh_white
clear mesh_inflated
for hemiind_rend=1:2
mesh_white{hemiind_rend}=gifti(fullfile(hcppath,sprintf('Q1-Q6_RelatedParcellation210.%s.white_MSMAll_2_d41_WRN_DeDrift.32k_fs_LR.surf.gii',fshemilab{hemiind_rend})));
mesh_inflated{hemiind_rend}=gifti(fullfile(hcppath,sprintf('Q1-Q6_RelatedParcellation210.%s.inflated_MSMAll_2_d41_WRN_DeDrift.32k_fs_LR.surf.gii',fshemilab{hemiind_rend})));
end;

s2t_perm=permute(s2t,[3 2 1]);
isnonzero=any(sum(s2t_perm,1),2); % non zero in every subject
s2t_perm=s2t_perm(:,:,isnonzero);

fprintf('FFC vs. non-FFC\n');
figure(20);
clf
ax=0;
el=90;
for hemiind=1:2
    
    fprintf('Hemisphere %s\n',hemilab{hemiind});
    hemitargetoffset=(hemiind-1)*180;
    % FFC
    isffc=Y(g.maskind)==18+hemitargetoffset;
    labels=repmat(isffc,[1 nsubj]);
    subplot(2,nsubj+1,1+(hemiind-1)*(nsubj+1));
    hold off
    scatter3(coreg(1,:),coreg(2,:),coreg(3,:),1,'r','filled');
    hold on
    scatter3(g.allXYZ(1,g.maskind(~isffc)),g.allXYZ(2,g.maskind(~isffc)),g.allXYZ(3,g.maskind(~isffc)),1,'y','filled');
    scatter3(g.allXYZ(1,g.maskind(isffc)),g.allXYZ(2,g.maskind(isffc)),g.allXYZ(3,g.maskind(isffc)),1,'k','filled');
    axis equal
    axis off
    view(ax,el);
    for subjind=1:nsubj
        subplot(4,nsubj+1,subjind+1+(hemiind-1)*(nsubj+1));

        othersubj=setdiff(1:nsubj,subjind);
        trainset=s2t_perm(:,othersubj,:);
        testset=s2t_perm(:,subjind,:);
        trainlabels=labels(:,othersubj);
        testlabels=labels(:,subjind);
        myclass=classify(squeeze(testset),reshape(trainset,[nseedvox*(nsubj-1) sum(isnonzero)]),trainlabels(:));
        fprintf('Subject %d correct %f\n',subjind,mean(myclass==testlabels));
        
%         hold off
%         scatter3(coreg(1,:),coreg(2,:),coreg(3,:),1,'r','filled');
%         hold on
%         scatter3(g.allXYZ(1,g.maskind(~class)),g.allXYZ(2,g.maskind(~class)),g.allXYZ(3,g.maskind(~class)),1,'y','filled');
%         scatter3(g.allXYZ(1,g.maskind(class==1)),g.allXYZ(2,g.maskind(class==1)),g.allXYZ(3,g.maskind(class==1)),1,'k','filled');
%         axis equal
%         axis off
    
        % A bit clumsy - write out 3D volume of labels
        mkdir(tmppath)
        Yout=zeros(size(Y));
        Yout(g.maskind)=1+myclass;
        Vout=V;
        Vout.fname=fullfile(tmppath,'class_labels.nii');
        spm_write_vol(Vout,Yout);
        
        for hemiind_rend=1:2
            % Sample back in as surface
            co=Vout.mat\double([mesh_white{hemiind_rend}.vertices' ; ones(1,size(mesh_white{hemiind_rend}.vertices,1))]);
            vertclass=round(spm_sample_vol(Vout,co(1,:),co(2,:),co(3,:),1));
            cdata=0.25*ones(size(mesh_white{hemiind_rend}.vertices,1),3);
            cdata(vertclass==1,3)=1; 
            cdata(vertclass==2,1)=1; 
            axis equal
            axis off

            hp = patch(struct('Parent',gca,'vertices',mesh_inflated{hemiind_rend}.vertices,'faces',mesh_inflated{hemiind_rend}.faces, ...
                'edgecolor','none','FaceColor','interp','FaceVertexCdata',cdata));

        end;
        view(0,-90);
        camlight;
        camlight(-80,-10);
        material([0.5 0.5 0.3]);
    end;
end;





