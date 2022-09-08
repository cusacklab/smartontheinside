import boto3
import nibabel as nib
import numpy as np 

#We'll need to load both the .label. file, 
#which tells you which vertices belong to which ROI, 
#and the 360 .shape. files for each subject. 
#I suggest you then pick out all the seed voxels (i.e., frontal ROIs) 
#and (a) make an average of the shape for each frontal ROI 
#[i.e., nsubj * 334 targets * 26 frontal ROIs] ; 
#(b) record the seed voxel values for each subject [
#    i.e., nsubj * 334 targets * nseedvoxels]


# Download using boto3
#session = boto3.session.Session()
#client = session.client('s3')
s3 = boto3.client('s3')
subjlist = ['178950','189450','199453','209228','220721','298455','356948','419239','499566','561444','618952','680452','757764','841349','908860', '103818','113922','121618','130619','137229','151829','158035','171633','179346','190031','200008','210112','221319','299154','361234', '424939','500222','570243','622236','687163','769064','845458','911849','104416','114217','122317','130720','137532','151930','159744', '172029','180230','191235','200614','211316','228434','300618','361941','432332','513130','571144','623844','692964','773257','857263', '926862','105014','114419','122822','130821','137633','152427','160123','172938','180432','192035','200917','211417','239944','303119', '365343','436239','513736','579665','638049','702133','774663','865363','930449','106521','114823','123521','130922','137936','152831', '160729','173334','180533','192136','201111','211619','249947','305830','366042','436845','516742','580650','645450','715041','782561', '871762','942658','106824','117021','123925','131823','138332','153025','162026','173536','180735','192439','201414','211821','251833', '310621','371843','445543','519950','580751','647858','720337','800941','871964','955465','107018','117122','125222','132017','138837', '153227','162329','173637','180937','193239','201818','211922','257542','314225','378857','454140','523032','585862','654350','725751', '803240','872562','959574','107422','117324','125424','133827','142828','153631','164030','173940','182739','194140','202719','212015', '257845','316633','381543','459453','525541','586460','654754','727553','812746','873968','966975']
nsub=len(subjlist)

######################################################################################################
# Load both the .label. file (vertices corresponding to ROI) and the 360 .shape files for each subject
######################################################################################################

roi_res = {'L':None, 'R':None} 
vox_res = {'L':None, 'R':None} 

for hemiind, hemi in enumerate(['L','R']):
    img=nib.load(f'ff.{hemi}.label.gii') # Load label file
    #img.print_summary()
    labels=img.labeltable.get_labels_as_dict()
    dat = img.agg_data('NIFTI_INTENT_LABEL')
    frontalregs_left=[73,67,97,98,26,70,71,87,68,83,85,84,86] # Select all the seed voxels in the DLPFC regions
    frontalregs_left.sort()
    roi_res[hemi] = np.zeros((nsub, 334, 26)) # Prepare the output file for the avg for each frontal ROI (L and R, nsubj * 334 targets * 26 frontal ROIs)
    for sub in subjlist:
        for target_roi in (1, 360): # Load ROI file and calculate average
            remotepath = f'HCP_1200/{sub}/T1w/Diffusion.probtrackx2/{hemi}/seeds_to_ROI.{target_roi}.shape.gii'
            print(remotepath)
            s3.download_file('smartontheinside', remotepath, f'/Users/chiara/seeds_to_ROI.{target_roi}.shape.gii')
            img_s2t = nib.load(f'/Users/chiara/seeds_to_ROI.{target_roi}.shape.gii')
            img_s2t = nib.load(remotepath, f'/Users/chiara/ROI.{target_roi}.shape.gii')  # Load results from tractography
            dat_s2t = img_s2t.agg_data()
            all_seed_values=[]
            roi_frontal_right=[x+180 for x in frontalregs_left]
            for seed_roi in roi_frontal_right: # check if 1-180 is left
                seed_values=dat_s2t[labels==(seed_roi)]
                #roi_res[hemiind][sub,:,target_roi] = np.mean(seed_values)
                all_seed_values.extend(seed_values)

            if vox_res[hemi] is None:
                vox_res[hemiind] = np.zeros((nsub, 334, len(all_seed_values))) # Average seed voxels for each subject (L and R, nsubj * 334 targets * nseedvoxels)

            vox_res[hemi][sub, target_roi, :] = all_seed_values
        print(vox_res)