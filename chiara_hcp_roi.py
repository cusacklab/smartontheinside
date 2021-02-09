# To get ROI file wget https://www.dropbox.com/s/xppiw77mdtb5dls/ResultsRegions_ROI.dlabel.nii
import nibabel as nib
import numpy as np
import boto3

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
# Add 180 for the other hemisphere
roilist=[26, 67, 68, 70, 71, 73, 83, 84, 85, 86, 87, 96, 98]
# Selecting these task contrasts: 'tfMRI_WM_2BK','tfMRI_WM_0BK', 'tfMRI_WM_BODY', 'tfMRI_WM_FACE', 'tfMRI_WM_PLACE', 'tfMRI_WM_TOOL', 'tfMRI_GAMBLING_PUNISH',
#'tfMRI_GAMBLING_REWARD', 'tfMRI_MOTOR_CUE', 'tfMRI_MOTOR_LF', 'tfMRI_MOTOR_LH', 'tfMRI_MOTOR_RF', 'tfMRI_MOTOR_RH', 'tfMRI_MOTOR_T', 'tfMRI_LANGUAGE_MATH', 
#'tfMRI_LANGUAGE_STORY', 'tfMRI_SOCIAL_RANDOM', 'tfMRI_SOCIAL_TOM', 'tfMRI_RELATIONAL_MATCH', 'tfMRI_RELATIONAL_REL', 'tfMRI_EMOTION_FACES', 'tfMRI_EMOTION_SHAPES'
#taskcons=[8, 9, 14, 15, 16, 17, 30, 31, 36, 37, 38, 39, 40, 41, 62, 63, 68, 69, 80, 81] 
#these are all the folders, we need to select a few
taskcons=['PRE tfMRI_EMOTION', 'PRE tfMRI_GAMBLING', 'PRE tfMRI_LANGUAGE', 'PRE tfMRI_MOTOR', 'PRE tfMRI_RELATIONAL', 'PRE tfMRI_SOCIAL', 'PRE tfMRI_WM']

nsub=len(subjNums)
nroi=len(roilist)
ntaskcons=len(taskcons)

# add s3
#####       OPTION 1
s3 = boto3.resource('s3')
# bucket name is hcp-openaccess
obj = s3.Object(hcp-openaccess, ('%s'%(sub)+'_' %s(task)+'_level2_hp200_s2_MSMAll.dscalar.nii'))
body = obj.get()['Body'].read()

#####       OPTION 2
# If we use temp file then
task_img=nib.load(body)
task_dat=task_img.get_fdata()


for sub in nsub:
    for task in ntaskcons:
            (os.path.join(self.resultspth,'Activity.txt'))
    # Load fMRI task data, name of the file we need: 424939_tfMRI_MOTOR_level2_hp200_s2_MSMAll.dscalar.nii
    task_img=nib.load(obj)
        for roiind, roi in enumerate(nroi):
            sel=task_dat_surf[:, roi_dat == roi]
            meanact[:, roiind] = np.mean(sel, 1)[taskcons]


roi_img=nib.load('ResultsRegions_ROI.dlabel.nii')
roi_dat=roi_img.get_fdata().ravel()

# Find which vertices correspond to the cortex
task_surfmask=task_img.header.get_axis(1).surface_mask
task_dat_surf=task_dat[:,task_surfmask]

meanact=np.zeros((ntaskcons,nroi))



print(meanact)
print(meanact.shape)


