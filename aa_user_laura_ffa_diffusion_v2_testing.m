% Automatic analysis user script

% Some manual intervention needed for optimal performance
%  eddy is super memory hungry, so I set NUM_SLOTS=4 in
%  /etc/condor/condor_config.local
%  bedpost likes lots of threads so I let it default to the number of cores
% 

% Diffusion
aap=aarecipe('aap_tasklist_laura_ffa_diffusion_v1.xml');

aap.options.wheretoprocess='localsingle';

% DEFINE STUDY SPECIFIC PARAMETERS
aap.options.aa_minver='5.0.0';

% Where to put the analyzed data
aap.acq_details.root = '/imaging/rcusack/laura_ffa_diffusion';
aap.directory_conventions.analysisid='analysis_adult_v2_testing';
aap.directory_conventions.rawdatadir='/imaging/HesterD/AdultLullabies/rawdata/';

% Standard stuff, could go in local confi file
aap.options.autoidentifyfieldmaps=false;
aap.directory_conventions.T1template='/imaging/software/spm12/canonical/avg305T1.nii';
aap.directory_conventions.dicomfilter='*.IMA';
aap.directory_conventions.subject_directory_format=3;
aap.options.NIFTI4D=true;

% The topup table. See comments in aamod_diffusion_topup for explanation
aap.tasksettings.aamod_diffusion_topup.topuptable.topuprow{1}=[1 0 0 0.0749];  % RL
aap.tasksettings.aamod_diffusion_topup.topuptable.topuprow{2}=[-1 0 0 0.0749]; % LR

% Fixes a problem with long paths in csh
aap.directory_conventions.fslshell='bash';

% Add subjects
%    First diffusion session number refers to series with RL encoding, second LR
aap=aas_addsubject(aap,'2014_03_29_9001','2014_03_29_9001','diffusion',{[8 11]});
% aap=aas_addsubject(aap,'2014_04_01_9002','2014_04_01_9002','diffusion',{[7 10]});
% aap=aas_addsubject(aap,'2014_04_01_9003','2014_04_01_9003','diffusion',{[6 9]});
% aap=aas_addsubject(aap,'2014_04_01_9004','2014_04_01_9004','diffusion',{[8 11]});
% aap=aas_addsubject(aap,'2014_04_02_9005','2014_04_02_9005','diffusion',{[6 9]});
% aap=aas_addsubject(aap,'2014_04_02_9006','2014_04_02_9006','diffusion',{[6 9]});
% aap=aas_addsubject(aap,'2014_04_02_9007','2014_04_02_9007','diffusion',{[6 9]});
% aap=aas_addsubject(aap,'2014_04_03_9008','2014_04_03_9008','diffusion',{[6 9]});
% aap=aas_addsubject(aap,'2014_04_03_9009','2014_04_03_9009','diffusion',{[6 9]});
% aap=aas_addsubject(aap,'2014_04_03_9010','2014_04_03_9010','diffusion',{[6 9]});
% aap=aas_addsubject(aap,'2014_04_04_9011','2014_04_04_9011','diffusion',{[7 10]});
% aap=aas_addsubject(aap,'2014_04_04_9012','2014_04_04_9012','diffusion',{[6 9]});
% aap=aas_addsubject(aap,'2014_04_10_9013','2014_04_10_9013','diffusion',{[6 9]});
% aap=aas_addsubject(aap,'2014_04_10_9014','2014_04_10_9014','diffusion',{[6 9]});
% aap=aas_addsubject(aap,'2014_04_11_9015','2014_04_11_9015','diffusion',{[7 10]});
% aap=aas_addsubject(aap,'2014_04_11_9016','2014_04_11_9016','diffusion',{[6 9]});

% Scan directory, not needed any more
% fn=dir('/imaging/HesterD/AdultLullabies/rawdata/2014*');
% for fnind=1:length(fn)    
%     aap=aas_addsubject(aap,fn(fnind).name,fn(fnind).name,'diffusion',{[8 11]}); 
% end;

% One diffusion session
aap=aas_add_diffusion_session(aap,'diffusion');

% Restrict number of workers as eddy takes a lot of memory
aap.options.aaparallel.numberofworkers=4;

aap.directory_conventions.fslsetup='FSL_DIR=/usr/share/fsl/5.0; . ${FSL_DIR}/etc/fslconf/fsl.sh; PATH=${FSL_DIR}/bin:${PATH}; FSLPARALLEL=condor; export FSL_DIR PATH FSLPARALLEL;';
% DO PROCESSING
aa_doprocessing(aap);

