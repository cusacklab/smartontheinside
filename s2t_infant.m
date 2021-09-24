subjlist=[1007	1003 1020 1011	1004	1006	1005	1024	1017	1012	1013]; % no brain injury

s2t=[];

for subjind=1:nsubj
    subj=subjlist(subjind);
    fprintf('Subj %d ',subj);
    bedpostpth=sprintf('/imaging/rcusack/leire_auditory_tractography/seeds/%d/Together/dtifit_rotatebvecs.bedpostX',subj);
    probtrackx2pth=fullfile(bedpostpth,'probtrackx2_hcp');
    s2tfns=dir(fullfile(probtrackx2pth,'s2t*.mat'));
    if ~isempty(s2tfns)
        s2t_onesubj=load(fullfile(probtrackx2pth,s2tfns(1).name));
        fprintf('Loaded\n');
    else
        fprintf('%s not found\n');
    end;
    
    s2t(:,:,subjind)=s2t_onesubj.s2t_thissubj;
end;
   
%% Target distribution collapsed across seeds
figure(30);
imagesc(squeeze(sum(s2t,1))');

figure(31)
imagesc(mean(s2t,3));