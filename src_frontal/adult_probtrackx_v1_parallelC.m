%% Split a number labelled map into regions
% This applies TBSS normalization to diffusion tractography data for
% classification
%  Rhodri Cusack 2017-06-02: HCP DLPFC

tbsspth='/imaging/rcusack/laura_ffa_diffusion/tbss_norm_adult/FA';
roipth='/imaging/rcusack/laura_ffa_diffusion/rois/';

subjlist=[9001 9002 9003 9005 9007 9008 9009 9010 9011 9012 9013 9014 9015 9016];

tic

s2t=[];
% Following already run for Laura's project
% 
% for subjind=1:length(subjlist)
%     subj=subjlist(subjind);
%     fprintf('Working on invwarp %d... ',subj);
%     
%      cmd=[sprintf('invwarp -w %s/%d_dti_FA_FA_to_target_warp ',tbsspth, subj) ...
%             sprintf(' -r /usr/share/fsl/data/standard/FMRIB58_FA_1mm') ...
%             sprintf(' -o %s/%d_dti_FA_target_to_FA_invwarp ',tbsspth,subj ) ...
%           ];
%         system(cmd);
%    
% end    
for subjind=9:11
    subj=subjlist(subjind);
    fprintf('Working on %d... ',subj);
    
    %% Back transform ROIs
    fprintf('applywarp ');
    roilist={'rhcp_regions_frontal_seed.nii','rhcp_regions_frontal_target.nii'};
    for roiind=1:length(roilist)
       
        cmd=[sprintf('applywarp -i %s ',fullfile(roipth,roilist{roiind})) ...
            sprintf(' -w %s/%d_dti_FA_target_to_FA_invwarp ',tbsspth,subj) ...
            sprintf(' -r %s/%d_dti_FA_FA ',tbsspth,subj) ...
            sprintf(' -o %s/%d_%s ',tbsspth,subj,roilist{roiind}) ...
            ' --interp=nn'];
        system(cmd);
    end;
    
    %% Split target masks and write text file
    fprintf('split masks ');
    [Vaal Yaal]=aas_spm_vol(fullfile(tbsspth,sprintf('%d_rhcp_regions_frontal_target.nii.gz',subj)));
    
    targetmaskfn=fullfile(tbsspth,sprintf('%d_frontal_target_masks.txt',subj));
    fid=fopen(targetmaskfn,'w');
    
    labels=unique(Yaal(~isnan(Yaal)));
    labels=setdiff(labels,0);
    
    for ind=1:length(labels)
        Vaal.fname=fullfile(tbsspth,sprintf('%d_hcp_frontal_%d.nii',subj,labels(ind)));
        spm_write_vol(Vaal,Yaal==labels(ind));
        fprintf(fid,'%s\n',Vaal.fname);
    end;
    fclose(fid)
    
    %% Run probtrackx2
    fprintf('probtrackx2 ');
    prebedpth='/imaging/rcusack/laura_ffa_diffusion/analysis_adult_v1/aamod_diffusion_bedpostx_00001';
    fullsubjdir=dir(fullfile(prebedpth,sprintf('*%d*',subj)));
    bedpostpth=sprintf('/imaging/rcusack/laura_ffa_diffusion/analysis_adult_v1/aamod_diffusion_bedpostx_00001/%s/diffusion.bedpostX', fullsubjdir.name);
    tbssroot=sprintf('%s/%d',tbsspth,subj);
    probtrackx2pth=sprintf('/imaging/rcusack/laura_ffa_diffusion/analysis_adult_v1/probtrackx2_hcp_frontal_FANorm/%s',fullsubjdir.name);
    fprintf('Probtrackx2pth %s\n',probtrackx2pth);
    cmd=['probtrackx2 --onewaycondition -P 5000 --forcedir --opd --os2t ' ...
        sprintf('--rseed=%d -s %s ',round(toc),fullfile(bedpostpth,'merged')) ...
        sprintf('--dir=%s ',probtrackx2pth) ...
        sprintf('-m %s_dti_FA_FA_mask ',tbssroot) ...
        sprintf('--targetmasks=%s ',targetmaskfn) ...
        sprintf(' -x %s_rhcp_regions_frontal_seed.nii.gz',tbssroot) ...
        ' -o fdt_paths_hcp_rhodri'];
    
    system(cmd);
    
    
    %% Warp to standard space
    for labind=1:length(labels)
        cmd=[sprintf('applywarp -i %s',fullfile(probtrackx2pth,sprintf('seeds_to_%d_hcp_frontal_%d',subj,labels(labind)))) ...
            sprintf(' -w %s/%d_dti_FA_FA_to_target_warp ',tbsspth,subj) ...
            ' -r /usr/share/fsl/data/standard/FMRIB58_FA_1mm ' ...
            sprintf(' -o %s ',fullfile(probtrackx2pth,sprintf('MNI_seeds_to_%d_hcp_frontal_%d',subj,labels(labind)))) ...
            ' --interp=nn'];
        system(cmd);
    end;
    
    %% Find the biggest
    fprintf('find the biggest ');
    cmd=sprintf('find_the_biggest %s/MNI_seeds_to_%d_hcp_frontal_* %s/MNI_hcp_frontal_%d_biggest',probtrackx2pth,subj,probtrackx2pth,subj);
    system(cmd);
    
end;

