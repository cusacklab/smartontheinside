%% Based on script from Laura Cabral 
% Creates seed and targets for DLPFC
% Rhodri Cusack 2017-06-21

targetpath='/imaging/rcusack/laura_ffa_diffusion/rois';

% Regions
regs=[73 67 97 98 26 70 71 87 68 83 85 84 86];
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
Vseed.fname=fullfile(targetpath,'hcp_regions_frontal_seed.nii');
spm_write_vol(Vseed,Yseed);

Vtarget=V;
Vtarget.fname=fullfile(targetpath,'hcp_regions_frontal_target.nii');
spm_write_vol(Vtarget,Ytarget);

%% Do the reslicing for the new target file 

%should change to roi path (target directory here) did this manually
cd(targetpath)
spm_reslice(char('rhcp_regions_v4_seed.nii','hcp_regions_frontal_seed.nii','hcp_regions_frontal_target.nii'), struct('mean',0, 'which', 1, 'interp', 0))


