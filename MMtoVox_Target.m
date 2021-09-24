%Written By Laura Cabral and Rhodri Cusack
%Novemeber, 2016
%This script is used to make the target regions. 

%set n here, find the number of verticies
N=32492;

%path stuff that's specific to this experiment, not in startup file
cd '/imaging/rcusack/laura_ffa_diffusion/analysis_adult_v1/aamod_norm_write_diffusion_session_00001/2014_04_01_9002/diffusion'
addpath '/home/lcabral/Dropbox/Glasser_et_al_2016_HCP_MMP1.0_RVVG/HCP_PhaseTwo/Q1-Q6_RelatedParcellation210/MNINonLinear/fsaverage_LR32k'

%load our FA image so we can get the mat file that will help convert the mm
%to voxels
V=spm_vol('wdti_FA.nii');

for hemisphere= 1:2

if hemisphere == 1
    %Load the targert labels into matlab
    ci=ft_read_cifti('Q1-Q6_RelatedParcellation210.L.CorticalAreas_dil_Colors.32k_fs_LR.dlabel.nii');

    %load the gifti file that gives us the coordinates in mm for the HCP 
    g=gifti('Q1-Q6_RelatedParcellation210.L.white_MSMAll_2_d41_WRN_DeDrift.32k_fs_LR.surf.gii');
    
    Yout=zeros(V.dim);

else
    %Load the targert labels into matlab
    ci=ft_read_cifti('Q1-Q6_RelatedParcellation210.R.CorticalAreas_dil_Colors.32k_fs_LR.dlabel.nii');

    %load the gifti file that gives us the coordinates in mm for the HCP 
    g=gifti('Q1-Q6_RelatedParcellation210.R.white_MSMAll_2_d41_WRN_DeDrift.32k_fs_LR.surf.gii');
  
end


%We are going to convert every vertex to voxels


for vertind = 1:N

    %need augmented vectors with a set of ones in the final column/row, so it is 4xN or Nx4 in size

    Cmm=(g.vertices(vertind,:))';
    
    Cmm(4,1)=1;
   
    Cvox=V.mat\Cmm;
    
    Cvox=round(Cvox);
    
    Cvox=Cvox';
    
    if hemisphere ==1
        Yout(Cvox(1),Cvox(2),Cvox(3))=(ci.x1(vertind,1));
    else
        Yout(Cvox(1),Cvox(2),Cvox(3))=(ci.x1(vertind,1)+180);
    end    
 

end


end

%commented this because it's part of the script used to make the seed
%region i.e. thresholding etc. not needed for the target regions
% Yout=double(Yout>0.4);
% 

cd '/home/lcabral/Dropbox/'

V.fname='hcp_regions_target.nii';

spm_write_vol(V,Yout);


