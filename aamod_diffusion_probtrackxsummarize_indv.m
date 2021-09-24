% Get the results of probtrackx (diffusion space) of each participant and
% transform them to the MNI space.

function [aap resp]=aamod_probtrackxsummarize_indv(aap,task,subjind,sessind)

resp='';

switch task
    case 'report'
    case 'doit'
        fslext=aas_getfslext(aap);
        
        % Load seed ROI in individual diffusion space
        seedfn=aas_getfiles_bystream(aap,'diffusion_session',[subjind sessind],'tractography_seeds');
        if size(seedfn,1)~=1
            aas_log(aap,true,'Can only cope with a single seed');
        end;
        [Vmask,Ymask,allXYZ_MNI152]=aas_spm_vol(seedfn);
        Ymask=Ymask(:)~=0;
        roiXYZ_MNI152=allXYZ_MNI152(:,Ymask);
        maskind=find(Ymask);
        seeddim=sum(Ymask(:));
        
        % Summary files are written here
        dsesspth= aas_getpath_bydomain(aap,'diffusion_session',[subjind sessind]) ;
        
        targetlist={};
        ntarg=0;
        % Load up filenames for all splits and targets
        for splitind=1:aap.options.probtrackx.nsplits
            % Which targets were used for this split
            tl=load(aas_getfiles_bystream(aap,'diffusion_session_probtrackx',[subjind sessind splitind],'targetlist'));
            targetlist{splitind}=tl.targetlist_roinum;
            ntarg=max([ntarg,targetlist{splitind}]);
            s2d{splitind}=aas_getfiles_bystream(aap,'diffusion_session_probtrackx',[subjind sessind splitind],'seeds_to_diffusion_space');
        end;
        
        % For warping to MNI
        try
            seg_sn=aas_getfiles_bystream(aap,'subject',subjind,'normalisation_seg_sn');
        catch
            seg_sn=aas_getfiles_bystream(aap,'diffusion_session',[subjind sessind],'normalisation_seg_sn');
        end;
        seed2target=zeros(ntarg,seeddim);
        
        
        fns=cell(ntarg,1);
        fns_mni=cell(ntarg,1);
        
        for targind=1:ntarg
            aas_log(aap,false,sprintf('%d/%d ',targind,ntarg));
            
            % Load up the first one just to get the dimensions
            [V Y]=aas_spm_vol(deblank(s2d{1}(1,:)));
            Ytot=zeros(size(Y));
            
            % For this target, load up every split and add them together
            for splitind=1:aap.options.probtrackx.nsplits               
                % Find this target in the lists
                findtarg=find(targind==targetlist{splitind});
                if ~isempty(findtarg)
                    inpfn=deblank(s2d{splitind}(findtarg,:));
                    [V Y]=aas_spm_vol(inpfn);                   
                    Ytot=Ytot+Y;
                end;
            end;
            
            % Save summary image
            [pth nme ext]=aas_fileparts(inpfn);
            fns{targind}=fullfile(dsesspth,['sumacrosssplits_' nme '.nii']);
            V.fname=fns{targind};
            spm_write_vol(V,Ytot);
            
            seed2target(targind,:)=Ytot(Ymask);
            
            % Warp to MNI space
            % unzip
            [aap fns{targind}]=aas_gunzip(aap,fns{targind});
            % normalise
            spm_write_sn(fns{targind},seg_sn);
            
            % record
            fns_mni{targind}=fullfile(dsesspth,['wsumacrosssplits_' nme '.nii']);
            
        end;
        
        aap=aas_desc_outputs(aap,'diffusion_session',[subjind sessind],'seeds_to_diffusion_space',fns);
        aap=aas_desc_outputs(aap,'diffusion_session',[subjind sessind],'seeds_to_mni_space',fns_mni);
end

