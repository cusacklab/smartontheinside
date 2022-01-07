import nibabel as nib
import numpy as np
from nibabel.gifti.gifti import GiftiDataArray

for hemi in ['L','R']:
    img=nib.load(f'ff.{hemi}.label.gii')
    img.print_summary()
    labels=img.labeltable.get_labels_as_dict()
    dat = img.agg_data('NIFTI_INTENT_LABEL')
    # DLPFC regions (check)
    frontalregs=[73,67,97,98,26,70,71,87,68,83,85,84,86]
    frontalregs.extend([x+180 for x in frontalregs])
    frontalregs.sort()
    mask=np.zeros(np.shape(dat))
    for reg in frontalregs:
        mask[dat==reg]=1
    # Remove labels...
    img.remove_gifti_data_array_by_intent('NIFTI_INTENT_LABEL')
    # ...and replace with mask
    img.add_gifti_data_array(GiftiDataArray(data=mask.astype('float32'), datatype='NIFTI_TYPE_FLOAT32', intent='NIFTI_INTENT_LABEL'))
    nib.save(img, f'frontal.{hemi}.label.gii')