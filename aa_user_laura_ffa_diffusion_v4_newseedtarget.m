% Automatic analysis user script

% Some manual intervention needed for optimal performance
%  eddy is super memory hungry, so I set NUM_SLOTS=4 in
%  /etc/condor/condor_config.local
%  bedpost likes lots of threads so I let it default to the number of cores
%

addpath('/imaging/rcusack/laura_ffa_diffusion/src/');

% Diffusion
aap=aarecipe('aap_tasklist_laura_ffa_diffusion_v4_newseedtarget.xml');

aap.options.wheretoprocess='localsingle';
%aap.options.wheretoprocess='matlab_pct';

% DEFINE STUDY SPECIFIC PARAMETERS
aap.options.aa_minver='5.0.0';

% Where to put the analyzed data
aap.acq_details.root = '/imaging/rcusack/laura_ffa_diffusion';
aap.directory_conventions.analysisid='analysis_adult_v1';
aap.directory_conventions.rawdatadir='/imaging/HesterD/AdultLullabies/rawdata/';

% Standard stuff, could go in local config file
aap.options.autoidentifyfieldmaps=false;
aap.directory_conventions.T1template='/imaging/software/spm12/canonical/avg305T1.nii';
aap.directory_conventions.dicomfilter='*.IMA';
aap.directory_conventions.subject_directory_format=3;
aap.options.NIFTI4D=true;

%use interp command to change to nearest neighbour
aap.tasksettings.aamod_norm_write_diffusion_session.interp=0;


% The topup table. See comments in aamod_diffusion_topup for explanation
aap.tasksettings.aamod_diffusion_topup.topuptable.topuprow{1}=[1 0 0 0.0749];  % RL
aap.tasksettings.aamod_diffusion_topup.topuptable.topuprow{2}=[-1 0 0 0.0749]; % LR


% Fixes a problem with long paths in csh
aap.directory_conventions.fslshell='bash';

% Add subjects
% First diffusion session number refers to series with RL encoding, second LR
aap=aas_addsubject(aap,'2014_03_29_9001','2014_03_29_9001','diffusion',{[8 11]});
aap=aas_addsubject(aap,'2014_04_01_9002','2014_04_01_9002','diffusion',{[7 10]});
aap=aas_addsubject(aap,'2014_04_01_9003','2014_04_01_9003','diffusion',{[6 9]});
aap.tasksettings.aamod_norm_noss_diffusion_session.subject(end+1) = struct('name', '2014_04_01_9003', 'affineStartingEstimate', [-1.5 -16 39 0.25 0 0]);

aap=aas_addsubject(aap,'2014_04_02_9005','2014_04_02_9005','diffusion',{[6 9]});
%aap=aas_addsubject(aap,'2014_04_02_9006','2014_04_02_9006','diffusion',{[6
%9]}); % LAURA TO WORK OUT WHY THIS FAILS FOR NUMBER OF SEEDS!
% aap.tasksettings.aamod_norm_noss_diffusion_session.subject(end+1) = struct('name', '2014_04_02_9006', 'affineStartingEstimate', [-2 -20 -9 0.27 0 0]);
aap.tasksettings.aamod_norm_noss_diffusion_session.subject(end+1) = struct('name', '2014_04_02_9006', 'affineStartingEstimate', [5 -39 -68 0.25 0 0]);

aap=aas_addsubject(aap,'2014_04_02_9007','2014_04_02_9007','diffusion',{[6 9]});
aap=aas_addsubject(aap,'2014_04_03_9008','2014_04_03_9008','diffusion',{[6 9]});
aap=aas_addsubject(aap,'2014_04_03_9009','2014_04_03_9009','diffusion',{[6 9]});
aap=aas_addsubject(aap,'2014_04_03_9010','2014_04_03_9010','diffusion',{[6 9]});
aap=aas_addsubject(aap,'2014_04_04_9011','2014_04_04_9011','diffusion',{[7 10]});
aap=aas_addsubject(aap,'2014_04_04_9012','2014_04_04_9012','diffusion',{[6 9]});
aap=aas_addsubject(aap,'2014_04_10_9013','2014_04_10_9013','diffusion',{[6 9]});
aap=aas_addsubject(aap,'2014_04_10_9014','2014_04_10_9014','diffusion',{[6 9]});
aap=aas_addsubject(aap,'2014_04_11_9015','2014_04_11_9015','diffusion',{[7 10]});
aap=aas_addsubject(aap,'2014_04_11_9016','2014_04_11_9016','diffusion',{[6 9]});


% Just a few subjects for testing?
%aap.acq_details.subjects=aap.acq_details.subjects(1:5);

% Scan directory, not needed any more
% fn=dir('/imaging/HesterD/AdultLullabies/rawdata/2014*');
% for fnind=1:length(fn)
%     aap=aas_addsubject(aap,fn(fnind).name,fn(fnind).name,'diffusion',{[8 11]});
% end;

% One diffusion session
aap=aas_add_diffusion_session(aap,'diffusion');

% add the command about normalization: no idea if this is the right place
aap.spm.defaults.normalise.write.interp=0;

% Restrict number of workers as eddy takes a lot of memory
aap.options.aaparallel.numberofworkers=8;

aap.directory_conventions.fslsetup='FSL_DIR=/usr/share/fsl/5.0; . ${FSL_DIR}/etc/fslconf/fsl.sh; PATH=${FSL_DIR}/bin:${PATH}; FSLPARALLEL=condor; export FSL_DIR PATH FSLPARALLEL;';

% No longer leave-one-out splits
aap.options.probtrackx.nsplits=1; 

% No longer splitting across ROIs
aap.tasksettings.aamod_diffusion_probtrackx.makesplitsacrossrois=false;

% Hard links don't work on ssc-rt-scanner
aap.directory_conventions.linktype='hard';

% DO PROCESSING
aa_doprocessing(aap);


