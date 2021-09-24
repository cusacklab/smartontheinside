% Get diffusion data streams to apply probtractx.
% Probtrackx repetitively samples from the distributions on voxel-wise
% principal diffusion directions, each time computing a streamline through
% these local samples to generate a probabilistic streamline or a sample
% from the distribution on the location of the true streamline.
% By taking many such samples FDT is able to build up the posterior
% distribution on the streamline location or the connectivity distribution.

function [aap resp]=aamod_diffusion_probtrackx(aap,task,subjind,sessind,splitind)
global aaworker
resp='';

switch task
    case 'report'
    case 'doit'
        % Launch all of the bedpost jobs
        fslext=aas_getfslext(aap);
        
        % Rename diffusion_data input
        %diffusion_data=aas_getfiles_bystream(aap,'diffusion_session',[subjind sessind],'diffusion_data');
        %[pth nme ext]=aas_fileparts(diffusion_data);
        %movefile(diffusion_data,fullfile(pth,['data' fslext]));
        
        % Paths
        dsesspth= aas_getpath_bydomain(aap,'diffusion_session',[subjind sessind]);
        bedpostpath=[dsesspth '.bedpostX'];
        
        psesspth= aas_getpath_bydomain(aap,'diffusion_session_probtrackx',[subjind sessind splitind]);
        
        makesplitsacrossrois=aap.tasklist.currenttask.settings.makesplitsacrossrois;
        
        % If we've been ask to make splits across ROIs, then pick relevant
        % ROIs for this split
        if makesplitsacrossrois
            % Target and seed images are the same with this option, just
            % pick ROIs 
            targets=aas_getfiles_bystream(aap,'diffusion_session',[subjind sessind],'tractography_seeds'); 
            % Overall targets and seeds ROI set is the same set in the scenario           
            if length(aap.options.probtrackx.seedroirange)~=aap.options.probtrackx.nsplits
                aas_log(aap,true,sprintf('WARNING: Expected same number of ROIs in seed range (length(aap.options.probtrackx.seedroirange)) as number of splits (aap.options.probtrackx.nsplits), but got %d and %d respectively.',length(aap.options.probtrackx.seedroirange),aap.options.probtrackx.nsplits))
            end;

            % No parallelisation across streamlines
            nstreamlines=aap.tasklist.currenttask.settings.totalstreamlines;
        else
            % Parallelise across streamlines
             targets=aas_getfiles_bystream(aap,'diffusion_session',[subjind sessind],'tractography_targets');
            nstreamlines=round(aap.tasklist.currenttask.settings.totalstreamlines/aap.options.probtrackx.nsplits);
            
        end;
        
        %% Need to make a list of target files
        targetmaskfn=fullfile(psesspth,'target_mask_list.txt');
        fid=fopen(targetmaskfn,'w');
        
%        If just one image, assume its a labelled map 
        targetlist={};
        targetlist_roinum=[];

        if size(targets,1)==1
            V=spm_vol(deblank(targets));
            Y=spm_read_vols(V);
            l=unique(Y(~isnan(Y(:))));
            l=setdiff(l,0);
                       
            for labind=1:length(l)
                V.fname=fullfile(psesspth,sprintf('roi_%d.nii',l(labind)));
                Yroi=Y==l(labind);
                if sum(Yroi(:))==0
                    aas_log(aap,false,sprintd('No ROI in labelled map with index %d from aap.options.probtrackx.seedroirange ', l(labind)));
                end;
                spm_write_vol(V,Yroi);
                if makesplitsacrossrois && l(labind)==aap.options.probtrackx.seedroirange(splitind) 
                    seedfn=V.fname;
                else
                    % Add to target list
                    fprintf(fid,'%s\n',V.fname);
                    targetlist{end+1}=V.fname;
                    targetlist_roinum(end+1)=l(labind);
                end;
            end;
            
            if ~makesplitsacrossrois
                seedfn=aas_getfiles_bystream(aap,'diffusion_session',[subjind sessind],'tractography_seeds');
            end;
            
        else
            % otherwise one input file per target
            for targetind=1:size(targets,1)
                fprintf(fid,'%s\n',deblank(targets(targetind,:)));
                targetlist{end+1}=deblank(targets(targetind,:));
            end;
            seedfn=aas_getfiles_bystream(aap,'diffusion_session',[subjind sessind],'tractography_seeds');
        end;
        fclose(fid);
        
        % Remove bet_ from start of bet_nofid_brain_mask etc as bedpost
        % doesn't like this
        betmaskfns=aas_getfiles_bystream(aap,'diffusion_session',[subjind sessind], 'BETmask');
        
        nodif_brain_mask=betmaskfns(1,:);  % top row
        %[pth nme ext]=aas_fileparts(nodif_brain_mask);
        %  if strcmp(nme(1:4),'bet_')
        % nme=nme(5:end);
        %  end;
        % nodif_fn=fullfile(pth, [nme ext]);
        
        
        
        
        

        cmd='probtrackx2';
        cmd=[cmd sprintf(' -x %s',seedfn)];
        cmd=[cmd ' -l --onewaycondition --omatrix2'];
        cmd=[cmd sprintf(' -c 0.2 -S 2000 --steplength=0.5 -P %d --fibthresh=0.01 --distthresh=0.0 --sampvox=0.0 --forcedir --opd --os2t --rseed=%d',nstreamlines,floor(toc))];
        cmd=[cmd sprintf(' --target2=%s',aas_getfiles_bystream(aap,'diffusion_session',[subjind sessind],'dti_FA'))];
        cmd=[cmd sprintf(' -s %s',fullfile(bedpostpath,'merged'))];
        cmd=[cmd sprintf(' -m %s', nodif_brain_mask)];
        cmd=[cmd sprintf(' --dir=%s',fullfile(psesspth,'logdir'))];
        cmd=[cmd sprintf(' --targetmasks=%s',targetmaskfn)]
        
        % Do the task
        [s w]=aas_runfslcommand(aap,cmd);
        if s
           aas_log(aap,true,sprintf('Error executing\n  %s\nof\n%s',cmd,w));
        end
        
        % Check the output is there
        [pth nme ext]=fileparts(targetlist{end});
        if ~exist(fullfile(psesspth,'logdir',sprintf('seeds_to_%s%s',nme,ext)),'file')
            aas_log(aap,true,sprintf('Missing output for\n  %s\n',cmd));
        end;
        
        % Write output streams
        fns={};
        for targetind=1:length(targetlist)
            [pth nme ext]=fileparts(targetlist{targetind});
            fns{targetind}=fullfile(psesspth,'logdir',sprintf('seeds_to_%s%s',nme,ext));
        end;
        
        targetlistfn=fullfile(psesspth,'target_list.mat');
        save(targetlistfn,'targetlist','targetlist_roinum');
        
        aap=aas_desc_outputs(aap, 'diffusion_session_probtrackx',[subjind sessind splitind],'seeds_to_diffusion_space',fns);
        
        aap=aas_desc_outputs(aap, 'diffusion_session_probtrackx',[subjind sessind splitind],'fdt_matrix2',{fullfile(psesspth,'logdir','fdt_matrix2.dot'),fullfile(psesspth,'logdir','tract_space_coords_for_fdt_matrix2'),  fullfile(psesspth,'logdir','coords_for_fdt_matrix2')});
        aap=aas_desc_outputs(aap, 'diffusion_session_probtrackx',[subjind sessind splitind],'fdt_paths',fullfile(psesspth,'logdir',['fdt_paths' fslext]));
        aap=aas_desc_outputs(aap, 'diffusion_session_probtrackx',[subjind sessind splitind],'lookup_tractspace_fdt_matrix2',fullfile(psesspth,'logdir',['lookup_tractspace_fdt_matrix2' fslext]));
        aap=aas_desc_outputs(aap, 'diffusion_session_probtrackx',[subjind sessind splitind],'probtrackx_log',fullfile(psesspth,'logdir','probtrackx.log' ));
        aap=aas_desc_outputs(aap, 'diffusion_session_probtrackx',[subjind sessind splitind],'waytotal',fullfile(psesspth,'logdir','waytotal' ));
        aap=aas_desc_outputs(aap, 'diffusion_session_probtrackx',[subjind sessind splitind],'targetlist',targetlistfn);
       
end

