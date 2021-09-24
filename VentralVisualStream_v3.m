%Region numbers for the Ventral Visual Stream
%V8 Region 7 in the left and 187 in the right 
%VVC Region 163 in the left and 343 in the right
%PIT Region 22 in the left and 202 in the right
%FFC Region 18 in the left and 198 in the right
%VMVA1 Region 153 in the left and 333 in the right
%VMVA2 Region 154 in the left and 334 in the right
%VMVA3 Region 160 in the left and 340 in the right 

%April 18th, 2017. This version of the script makes target and seed regions
%that don't just have 1 (true) in their place. They are labeled. 

targetpath='/imaging/rcusack/laura_ffa_diffusion/rois';

% Regions
regs=[7 163 22 18 153 154 160];
regs=[regs regs+180];

% Load target
V=spm_vol(fullfile(targetpath,'hcp_regions_target.nii'));
Y=spm_read_vols(V);

Yseed=zeros(size(Y));
Ytarget=Y;

for regind=1:length(regs)
    % Add this to seed mask
    Yseed(Y==regs(regind))=regs(regind);
    % Remove this region as a target
    Ytarget(Y==regs(regind))=0;
end

Vseed=V;
Vseed.fname=fullfile(targetpath,'hcp_regions_v5_seed.nii');
spm_write_vol(Vseed,Yseed);

Vtarget=V;
Vtarget.fname=fullfile(targetpath,'hcp_regions_v5_target.nii');
spm_write_vol(Vtarget,Ytarget);

%% Do the reslicing for the new target file 

%should change to roi path (target directory here) did this manually

spm_reslice(char('rhcp_regions_v4_seed.nii','hcp_regions_v5_seed.nii'), struct('mean',0, 'which', 2, 'interp', 0))


