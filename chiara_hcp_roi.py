# To get ROI file wget https://www.dropbox.com/s/xppiw77mdtb5dls/ResultsRegions_ROI.dlabel.nii
import nibabel as nib
import numpy as np
import boto3
import botocore

## Exploratory subjects from  Ito T, Hearne LJ, Cole MW (2020)
## We can validate this analysis on the validation subjects also from them
subjNums = ['178950','189450','199453','209228','220721','298455','356948','419239','499566','561444','618952','680452','757764','841349','908860',
            '103818','113922','121618','130619','137229','151829','158035','171633','179346','190031','200008','210112','221319','299154','361234',
            '424939','500222','570243','622236','687163','769064','845458','911849','104416','114217','122317','130720','137532','151930','159744',
            '172029','180230','191235','200614','211316','228434','300618','361941','432332','513130','571144','623844','692964','773257','857263',
            '926862','105014','114419','122822','130821','137633','152427','160123','172938','180432','192035','200917','211417','239944','303119',
            '365343','436239','513736','579665','638049','702133','774663','865363','930449','106521','114823','123521','130922','137936','152831',
            '160729','173334','180533','192136','201111','211619','249947','305830','366042','436845','516742','580650','645450','715041','782561',
            '871762','942658','106824','117021','123925','131823','138332','153025','162026','173536','180735','192439','201414','211821','251833',
            '310621','371843','445543','519950','580751','647858','720337','800941','871964','955465','107018','117122','125222','132017','138837',
            '153227','162329','173637','180937','193239','201818','211922','257542','314225','378857','454140','523032','585862','654350','725751',
            '803240','872562','959574','107422','117324','125424','133827','142828','153631','164030','173940','182739','194140','202719','212015',
            '257845','316633','381543','459453','525541','586460','654754','727553','812746','873968','966975']

# These are the DLPFC regions
roilist=[26, 67, 68, 70, 71, 73, 83, 84, 85, 86, 87, 96, 98, 206, 247, 148, 250, 251, 253, 264, 265, 266, 267, 276, 278]
#taskcons=[8, 9, 14, 15, 16, 17, 30, 31, 36, 37, 38, 39, 40, 41, 62, 63, 68, 69, 80, 81] 
#these are the tasks
taskcons=['tfMRI_EMOTION', 'tfMRI_GAMBLING', 'tfMRI_LANGUAGE', 'tfMRI_MOTOR', 'tfMRI_RELATIONAL', 'tfMRI_SOCIAL', 'tfMRI_WM']
#s3 = boto3.resource('s3')
#s3.Object('hcp-openaccess', 'HCP_1200/424939/MNINonLinear/Results/tfMRI_MOTOR/PRE tfMRI_MOTOR_hp200_s2_level2.feat/424939_tfMRI_MOTOR_level2_hp200_s2_MSMAll.dscalar.nii').download_file('/tmp/424939_tfMRI_MOTOR_level2_hp200_s2_MSMAll.dscalar.nii')
#obj = s3.Object('hcp-openaccess', 'HCP_1200/424939/MNINonLinear/Results/tfMRI_MOTOR/PRE tfMRI_MOTOR_hp200_s2_level2.feat/424939_tfMRI_MOTOR_level2_hp200_s2_MSMAll.dscalar.nii', 'objname')
#obj = s3.Object('s3://hcp-openaccess/HCP_1200/424939/MNINonLinear/Results/tfMRI_MOTOR/PRE tfMRI_MOTOR_hp200_s2_level2.feat/424939_tfMRI_MOTOR_level2_hp200_s2_MSMAll.dscalar.nii', 'try.nii')
s3 = boto3.client('s3')
obj = s3.download_file('hcp-openaccess', 'HCP_1200/424939/MNINonLinear/Results/tfMRI_MOTOR/tfMRI_MOTOR_hp200_s2_level2.feat/424939_tfMRI_MOTOR_level2_hp200_s2.dscalar.nii','testme.nii')
print(obj)  

#for sub in enumerate(subjNums): 
#    for con in enumerate(taskcons):
        # This was running:
        #obj = s3.download_file('hcp-openaccess', 'HCP_1200/424939/MNINonLinear/Results/tfMRI_MOTOR/tfMRI_MOTOR_hp200_s2_level2.feat/424939_tfMRI_MOTOR_level2_hp200_s2.dscalar.nii','testme.nii')
#        obj = s3.download_file('hcp-openaccess', f'/HCP_1200/{sub}/MNINonLinear/Results/{con}/{con}_hp200_s2_level2.feat/{sub}_{con}_level2_hp200_s2.dscalar.nii','testme.nii')

        #obj = s3.Object('s3://hcp-openaccess/HCP_1200/{sub}/MNINonLinear/Results/{con}/{con}_hp200_s2_level2.feat/{sub}_{con}_level2_hp200_s2.dscalar.nii', 'objname')  
        # Checking the previous command ran OK
        print(obj)
#        ts = obj.get()['TS'].read()
#        task_img=nib.load(ts)
#        task_dat=task_img.get_fdata()
#        task_img=nib.load(obj)
#        for roi in enumerate(roilist):
#            sel=task_dat_surf[:, roi_dat == roi]
#            meanact[:, roi] = np.mean(sel, 1)[taskcons]

#roi_img=nib.load('ResultsRegions_ROI.dlabel.nii')
#roi_dat=roi_img.get_fdata().ravel()

# Find which vertices correspond to the cortex
#task_surfmask=task_img.header.get_axis(1).surface_mask
#task_dat_surf=task_dat[:,task_surfmask]

#meanact=np.zeros((ntaskcons,nroi))

#print(meanact)
#print(meanact.shape)


