import nibabel as nib
import numpy as np
from nibabel.gifti.gifti import GiftiDataArray

# DLPFC regions
frontalregs=[73,67,97,98,26,70,71,87,68,83,85,84,86]
frontalregs.extend([x+180 for x in frontalregs])
frontalregs.sort()
# All the other regions
regs = list(range(1,361))
regs = [x for x in regs if not x in frontalregs]
print(regs)

for hemi in ['L','R']:
    # *********************
    # ***** DLFC MASK *****
    # *********************
    imgDLPFC=nib.load(f'ff.{hemi}.label.gii')
    imgDLPFC.print_summary()
    labels=imgDLPFC.labeltable.get_labels_as_dict()
    datDLPFC = imgDLPFC.agg_data('NIFTI_INTENT_LABEL')
    maskDLPFC=np.zeros(np.shape(datDLPFC))
    for reg in frontalregs:
        maskDLPFC[datDLPFC==reg]=1
    # Remove labels...
    imgDLPFC.remove_gifti_data_array_by_intent('NIFTI_INTENT_LABEL')
    # ...and replace with mask
    imgDLPFC.add_gifti_data_array(GiftiDataArray(data=maskDLPFC.astype('float32'), datatype='NIFTI_TYPE_FLOAT32', intent='NIFTI_INTENT_LABEL'))
    nib.save(imgDLPFC, f'/Users/chiara/smartontheinside/Rois/frontal.{hemi}.label.gii')

    # ************************************************
    # ***** ALL THE BRAIN OTHER THAN DLFC'S MASK *****
    # ************************************************
    imgNOT_DLPFC=nib.load(f'ff.{hemi}.label.gii')
    imgNOT_DLPFC.print_summary()
    imgNOT_DLFClabels=imgNOT_DLPFC.labeltable.get_labels_as_dict()
    datNOT_DLPFC = imgNOT_DLPFC.agg_data('NIFTI_INTENT_LABEL')
    maskNOT_DLPFC=np.zeros(np.shape(datNOT_DLPFC))
    for r in regs:
        maskNOT_DLPFC[datNOT_DLPFC==reg]=1
    # Remove labels...
    imgNOT_DLPFC.remove_gifti_data_array_by_intent('NIFTI_INTENT_LABEL')
    # ...and replace with mask
    imgNOT_DLPFC.add_gifti_data_array(GiftiDataArray(data=maskNOT_DLPFC.astype('float32'), datatype='NIFTI_TYPE_FLOAT32', intent='NIFTI_INTENT_LABEL'))
    nib.save(imgNOT_DLPFC, f'/Users/chiara/smartontheinside/Rois/NOT_frontal.{hemi}.label.gii')
    
    # *******************************************
    # ***** EACH ROI OTHER THAN DLFC'S MASK *****
    # *******************************************
    for q in regs: 
        img=nib.load(f'ff.{hemi}.label.gii')
        img.print_summary()
        labels=img.labeltable.get_labels_as_dict()
        dat = img.agg_data('NIFTI_INTENT_LABEL')
        mask=np.zeros(np.shape(dat))
        if q > 180: 
            mask[dat==q]=1
            # Remove labels...
            img.remove_gifti_data_array_by_intent('NIFTI_INTENT_LABEL')
            # ...and replace with mask
            img.add_gifti_data_array(GiftiDataArray(data=mask.astype('float32'), datatype='NIFTI_TYPE_FLOAT32', intent='NIFTI_INTENT_LABEL'))
            nib.save(img, f'/Users/chiara/smartontheinside/Rois/ROI.{q}.{hemi}.label.gii')
        else:
            mask[dat==q]=1
            # Remove labels...
            img.remove_gifti_data_array_by_intent('NIFTI_INTENT_LABEL')
            # ...and replace with mask
            img.add_gifti_data_array(GiftiDataArray(data=mask.astype('float32'), datatype='NIFTI_TYPE_FLOAT32', intent='NIFTI_INTENT_LABEL'))
            nib.save(img, f'/Users/chiara/smartontheinside/Rois/ROI.{q}.{hemi}.label.gii')
