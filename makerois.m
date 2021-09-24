roipth='/imaging/rcusack/laura_ffa_diffusion/rois';

V=spm_vol(fullfile(roipth,'hcp_regions_target.nii'));
Y=spm_read_vols(V);
mx=max(Y(:));
for ind=1:mx
    Vseed=V;
    Yseed=Y;
    Vseed.fname=fullfile(roipth,sprintf('hcp_regions_%d.nii',ind));
    Yseed(Yseed~=ind)=0;
    spm_write_vol(Vseed,Yseed);
end;

