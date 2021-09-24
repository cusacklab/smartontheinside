
%set n here, find the number of verticies


N=32492;

%path stuff that's specific to this experiment, not in startup file
cd '/imaging/rcusack/laura_ffa_diffusion/analysis_adult_v1/aamod_norm_write_diffusion_session_00001/2014_04_01_9002/diffusion/'
addpath /home/lcabral/Dropbox/Glasser_et_al_2016_HCP_MMP1.0_RVVG/HCP_PhaseTwo/Q1-Q6_RelatedParcellation210/MNINonLinear/fsaverage_LR32k/
addpath /home/lcabral/Dropbox/Glasser_et_al_2016_HCP_MMP1.0_RVVG/HCP_PhaseTwo/Q1-Q6_RelatedParcellation210/MNINonLinear/Results/tfMRI_ALLTASKS/


%load in the cifti file that will give us the labels for the regions
ci=ft_read_cifti('Q1-Q6_RelatedParcellation210_tfMRI_ALLTASKS_level3_beta_hp200_s2_MSMAll_2_d41_WRN_DeDrift_norm.dscalar.nii');

left_labels=ci.tfmri_emotion_faces_shapes(ci.brainstructure==1);

%load the gifti file that gives us the coordinates in mm for the HCP 
g=gifti('Q1-Q6_RelatedParcellation210.R.white_MSMAll_2_d41_WRN_DeDrift.32k_fs_LR.surf.gii');

%load our FA image so we can get the mat file that will help convert the mm
%to voxels
V=spm_vol('wdti_FA.nii');

Yout=zeros(V.dim);

%We are going to convert every vertex to voxels

for vertind = 1:N

    %need augmented vectors with a set of ones in the final column/row, so it is 4xN or Nx4 in size

    Cmm=(g.vertices(vertind,:))';
    
    Cmm(4,1)=1;
   
    Cvox=V.mat\Cmm;
    
    Cvox=round(Cvox);
    
    Cvox=Cvox';
      
    Yout(Cvox(1),Cvox(2),Cvox(3))=left_labels(vertind,1);
 

end

Yout=double(Yout>0.4);

Ylab=spm_bwlabel(Yout,6);

%Yout(Ylab==2)=1;

Yout=double(Ylab==2);

%V.fname='hcp_regions2.nii';

cd '/home/lcabral/Dropbox/'

V.fname='hcp_regions_threshold.nii';

spm_write_vol(V,Yout);


