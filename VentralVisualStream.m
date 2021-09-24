%Region numbers for the Ventral Visual Stream
%V8 Region 7 in the left and 187 in the right 
%VVC Region 163 in the left and 343 in the right
%PIT Region 22 in the left and 202 in the right
%FFC Region 18 in the left and 198 in the right
%VMVA1 Region 153 in the left and 333 in the right
%VMVA2 Region 154 in the left and 334 in the right
%VMVA3 Region 160 in the left and 340 in the right 

targetpath='/imaging/rcusack/laura_ffa_diffusion/rois';
seedpath='/imaging/rcusack/laura_ffa_diffusion/src';

V=spm_vol(fullfile(targetpath,'hcp_regions_target.nii'));
Y=spm_read_vols(V);

Vseed=V;
Yseed=Y;
Vseed.fname=fullfile(seedpath,'hcp_seed_VVS.nii');

Yseed(Yseed~= 7 |187 | 163 | 343 | 22 | 202 | 18 | 198 | 153 | 333 | 154 | 334 | 160 | 340)=0;


spm_write_vol(Vseed,Yseed);