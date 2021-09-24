%

function [aap resp]=aamod_diffusion_probtrackxsummarize_group(aap,task)

resp='';

switch task
    case 'report'
    case 'doit'
        fslext=aas_getfslext(aap);
        sessind=1;  
        % Load seed ROI in individual diffusion space
%        fprintf('MASKFN TEMPORARILY HARD CODED\n');
%        maskfn='/imaging/rcusack/laura_ffa_diffusion/rois/hcp_regions_target.nii';
        maskfn=aas_getfiles_bystream(aap,'diffusion_session',[1 sessind],'tractography_seeds_mni');
        % Reslice into space of seeds
        s2t=aas_getfiles_bystream(aap,'diffusion_session',[1 sessind],'seeds_to_mni_space');
        
        % Select regions if seedroirange specifies?
        if ~isempty(aap.options.probtrackx.seedroirange)
            V=spm_vol(maskfn);
            Y=spm_read_vols(V);
            Ysel=zeros(size(Y));
            for ind=1:length(aap.options.probtrackx.seedroirange)
                Ysel(Y==aap.options.probtrackx.seedroirange(ind))=1;
            end;
            [pth nme ext]=fileparts(V.fname);
            maskfn=fullfile(aas_getpath_bydomain(aap,'study',[]),['sel_' nme ext]);
            V.fname=maskfn;
            spm_write_vol(V,Ysel);
        end;
        
        spm_reslice(strvcat(s2t,maskfn));
        [pth nme ext]=aas_fileparts(maskfn);
        maskfn_r=fullfile(pth,['r' nme ext]);
        
        [Vmask Ymask allXYZ]=aas_spm_vol(maskfn_r);
        Ymask=Ymask(:)>0.1;
        maskind=find(Ymask(:));
        seeddim=sum(Ymask(:));
        
              
        rowoffset=0;
        nsubj=length(aap.acq_details.subjects);
        for subjind=1:nsubj
            s2t=aas_getfiles_bystream(aap,'diffusion_session',[subjind sessind],'seeds_to_mni_space');
            if subjind==1
                ntarg=size(s2t,1);
                seed2target=zeros(ntarg*nsubj,seeddim);
            else
                if size(s2t,1)~=ntarg
                    aas_log(aap,true,sprintf('All seeds_to_mni_space must have same number of targets but subject %d differs.',subjind));
                end;
            end;
            
            for targind=1:ntarg
                [V Y]=aas_spm_vol(s2t(targind,:));
                seed2target(targind+rowoffset,:)=Y(Ymask);
            end;
            rowoffset=rowoffset+ntarg;
        end;
        
        seedroirange=aap.options.probtrackx.seedroirange;
        s2tfn=fullfile(aas_getstudypath(aap),'group_tractography_seed2target.mat');
        save(s2tfn,'seed2target','maskind','allXYZ','maskfn','seedroirange');
        aap=aas_desc_outputs(aap,'study',[],'seed2target',s2tfn);
end

