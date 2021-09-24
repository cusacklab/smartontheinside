numOfIC=3;

addpath(dropboxmatlab('FastICA_25'))

g=load('/imaging/rcusack/laura_ffa_diffusion/analysis_adult_v1/aamod_diffusion_probtrackxsummarize_group_00001/group_tractography_seed2target.mat');

ntargroi=359; % number of target ROIs
nsubj=size(g.seed2target,1)/ntargroi; % number of subjects
nseedvox=size(g.seed2target,2);

% Reshape to 3D matrix ntarg x nsubj x nseedvox 
s2t=reshape(g.seed2target,[ntargroi nsubj nseedvox]);


% Run ICA
s2t_samples=reshape(s2t,[ntargroi nsubj*nseedvox]);
[icasig, A, W] = fastica(s2t_samples,'numOfIC',numOfIC);


figure(10);
imagesc(A);
title('Mixing matrix A');

xc=g.allXYZ(1,g.maskind);
yc=g.allXYZ(2,g.maskind);
cm=colormap('jet');

%% Show ICs for each individual
figure(11)
colind=round(64*((icasig/3)+0.5));
colind(colind<1)=1;
colind(colind>64)=64;

for icacomp=1:numOfIC
    for subj=1:nsubj
        offset=(subj-1)*nseedvox;
        subplot(numOfIC,nsubj,subj+(icacomp-1)*nsubj);
        scatter(xc,yc,1,cm(colind(icacomp,(1:nseedvox)+offset),:));
    end;
end;