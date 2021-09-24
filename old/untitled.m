roipth='/imaging/rcusack/laura_ffa_diffusion/rois';

V=spm_vol(fullfile(roipth,'hcp_regions_target.nii'));
Y=spm_read_vols(V);
mx=max(Y(:));
