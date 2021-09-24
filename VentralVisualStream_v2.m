%Region numbers for the Ventral Visual Stream
%V8 Region 7 in the left and 187 in the right 
%VVC Region 163 in the left and 343 in the right
%PIT Region 22 in the left and 202 in the right
%FFC Region 18 in the left and 198 in the right
%VMVA1 Region 153 in the left and 333 in the right
%VMVA2 Region 154 in the left and 334 in the right
%VMVA3 Region 160 in the left and 340 in the right 

%This version makes the files with just a 1 (true) saved for the seed
%region

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
    Yseed(Y==regs(regind))=1;
    % Remove this region as a target
    Ytarget(Y==regs(regind))=0;
end;

Vseed=V;
Vseed.fname=fullfile(targetpath,'hcp_regions_v4_seed.nii');
spm_write_vol(Vseed,Yseed);

Vtarget=V;
Vtarget.fname=fullfile(targetpath,'hcp_regions_v4_target.nii');
spm_write_vol(Vtarget,Ytarget);



