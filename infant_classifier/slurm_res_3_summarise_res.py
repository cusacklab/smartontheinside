import boto3
import nibabel as nib
import numpy as np 
import os
from os.path import exists as file_exists
import pandas as pd
import os
import tempfile
  


#We'll need to load both the .label. file, 
#which tells you which vertices belong to which ROI, 
#and the 360 .shape. files for each subject. 
#I suggest you then pick out all the seed voxels (i.e., frontal ROIs) 
#and (a) make an average of the shape for each frontal ROI 
#[i.e., nsubj * 334 targets * 26 frontal ROIs] ; 
#(b) record the seed voxel values for each subject [
#    i.e., nsubj * 334 targets * nseedvoxels]


# Download using boto3
# s3 = boto3.client('s3')
infants = 1

if infants==1:                
    subjlist =['sub-CC00549XX22', 'sub-CC00202XX04', 'sub-CC00720XX11', 'sub-CC00122XX07', 'sub-CC00071XX06', 'sub-CC00119XX12', 'sub-CC00207XX09', 'sub-CC00484XX15', 'sub-CC00590XX14', 'sub-CC00586XX18', 'sub-CC00467XX14', 'sub-CC00593XX17', 'sub-CC00344XX15', 'sub-CC00409XX13', 'sub-CC00168XX12', 'sub-CC00158XX10', 'sub-CC00613XX11', 'sub-CC00731XX14', 'sub-CC00198XX18', 'sub-CC00664XX13', 'sub-CC00397XX19', 'sub-CC00270XX07', 'sub-CC00252XX05', 'sub-CC00787XX21', 'sub-CC00223XX09', 'sub-CC00367XX13', 'sub-CC00183XX11', 'sub-CC00478XX17', 'sub-CC00540XX13', 'sub-CC00512XX09', 'sub-CC00476XX15', 'sub-CC00120XX05', 'sub-CC00164XX08', 'sub-CC00562XX10', 'sub-CC00194XX14', 'sub-CC00383XX13', 'sub-CC00440XX12', 'sub-CC00153XX05', 'sub-CC00170XX06', 'sub-CC00595XX19', 'sub-CC00744XX19', 'sub-CC00398XX20', 'sub-CC00547XX20','sub-CC00466BN13', 'sub-CC00258XX11', 'sub-CC00203XX05', 'sub-CC00500XX05', 'sub-CC00654XX11', 'sub-CC00073XX08', 'sub-CC00115XX08', 'sub-CC00070XX05', 'sub-CC00840XX16', 'sub-CC00089XX16', 'sub-CC00411XX07', 'sub-CC00184XX12', 'sub-CC00205XX07', 'sub-CC00337XX16', 'sub-CC00313XX08', 'sub-CC00107XX08', 'sub-CC00144XX13', 'sub-CC00585XX17', 'sub-CC00138XX15', 'sub-CC00850XX09', 'sub-CC00149XX18', 'sub-CC00193XX13', 'sub-CC00458XX13', 'sub-CC00201XX03', 'sub-CC00650XX07', 'sub-CC00508XX13', 'sub-CC00099AN18', 'sub-CC00078XX13', 'sub-CC00527XX16', 'sub-CC00150AN02', 'sub-CC00355XX09', 'sub-CC00454XX09', 'sub-CC00341XX12', 'sub-CC00343XX14', 'sub-CC00445XX17', 'sub-CC00116XX09', 'sub-CC00544XX17', 'sub-CC00450XX05', 'sub-CC00561XX09', 'sub-CC00548XX21', 'sub-CC00801XX09', 'sub-CC00060XX03', 'sub-CC00447XX19', 'sub-CC00377XX15', 'sub-CC00479XX18', 'sub-CC00473XX12', 'sub-CC00101XX02', 'sub-CC00481XX12', 'sub-CC00480XX11', 'sub-CC00502XX07', 'sub-CC00088XX15', 'sub-CC00766XX16', 'sub-CC00366XX12', 'sub-CC00757XX15', 'sub-CC00596XX20', 'sub-CC00536XX17', 'sub-CC00550XX06', 'sub-CC00221XX07', 'sub-CC00382XX12', 'sub-CC00178XX14', 'sub-CC00589XX21', 'sub-CC00068XX11', 'sub-CC00334XX13', 'sub-CC00486XX17', 'sub-CC00501XX06', 'sub-CC00455XX10', 'sub-CC00652XX09', 'sub-CC00528XX17', 'sub-CC00685XX18', 'sub-CC00649XX23', 'sub-CC00400XX04', 'sub-CC00094BN13', 'sub-CC00556XX12', 'sub-CC00199XX19', 'sub-CC00507XX12', 'sub-CC00362XX08', 'sub-CC00236XX14', 'sub-CC00858XX17', 'sub-CC00555XX11', 'sub-CC00091XX10', 'sub-CC00110XX03', 'sub-CC00113XX06', 'sub-CC00558XX14', 'sub-CC00379XX17', 'sub-CC00466AN13', 'sub-CC00499XX22', 'sub-CC00096XX15', 'sub-CC00172BN08', 'sub-CC00399XX21', 'sub-CC00206XX08', 'sub-CC00143AN12', 'sub-CC00656XX13', 'sub-CC00298XX19', 'sub-CC00376XX14', 'sub-CC00219XX13', 'sub-CC00195XX15', 'sub-CC00483XX14', 'sub-CC00546XX19', 'sub-CC00306XX09', 'sub-CC00363XX09', 'sub-CC00066XX09', 'sub-CC00094AN13', 'sub-CC00583XX15', 'sub-CC00347XX18', 'sub-CC00254XX07', 'sub-CC00545XX18', 'sub-CC00532XX13', 'sub-CC00352XX06', 'sub-CC00172AN08', 'sub-CC00160XX04', 'sub-CC00553XX09', 'sub-CC00364XX10', 'sub-CC00189XX17', 'sub-CC00616XX14', 'sub-CC00097XX16', 'sub-CC00111XX04', 'sub-CC00320XX07', 'sub-CC00402XX06', 'sub-CC00587XX19', 'sub-CC00421BN09', 'sub-CC00622XX12', 'sub-CC00474XX13', 'sub-CC00852XX11', 'sub-CC00356XX10', 'sub-CC00824XX16', 'sub-CC00791XX17', 'sub-CC00843XX19', 'sub-CC00127XX12', 'sub-CC00439XX19', 'sub-CC00582XX14', 'sub-CC00693XX18', 'sub-CC00342XX13', 'sub-CC00257XX10', 'sub-CC00594XX18', 'sub-CC00209XX11', 'sub-CC00860XX11', 'sub-CC00272XX09', 'sub-CC00580XX12', 'sub-CC00130XX07', 'sub-CC00250XX03', 'sub-CC00879XX22', 'sub-CC00069XX12', 'sub-CC00441XX13', 'sub-CC00653XX10', 'sub-CC00534XX15', 'sub-CC00777XX19', 'sub-CC00080XX07', 'sub-CC00269XX14', 'sub-CC00669XX18', 'sub-CC00417XX13', 'sub-CC00329XX16', 'sub-CC00338BN17', 'sub-CC00416XX12', 'sub-CC00084XX11', 'sub-CC00171XX07', 'sub-CC00083XX10', 'sub-CC00408XX12', 'sub-CC00433XX13', 'sub-CC00734XX17', 'sub-CC00316XX11', 'sub-CC00504XX09', 'sub-CC00871XX14', 'sub-CC00410XX06', 'sub-CC00197XX17', 'sub-CC00180XX08', 'sub-CC00303XX06', 'sub-CC00542XX15', 'sub-CC00099BN18', 'sub-CC00457XX12', 'sub-CC00421AN09', 'sub-CC00647XX21', 'sub-CC00581XX13', 'sub-CC00639XX21', 'sub-CC00448XX20', 'sub-CC00114XX07', 'sub-CC00818XX18', 'sub-CC00314XX09', 'sub-CC00846XX22', 'sub-CC00308XX11', 'sub-CC00516XX13', 'sub-CC00412XX08', 'sub-CC00165XX09', 'sub-CC00292XX13', 'sub-CC00217XX11', 'sub-CC00428XX16', 'sub-CC00126XX11', 'sub-CC00260XX05', 'sub-CC00671XX12', 'sub-CC00568XX16', 'sub-CC00415XX11', 'sub-CC00564XX12', 'sub-CC00667XX16', 'sub-CC00174XX10', 'sub-CC00108XX09', 'sub-CC00106XX07', 'sub-CC00705XX12', 'sub-CC00552XX08', 'sub-CC00719XX18', 'sub-CC00592XX16', 'sub-CC00143BN12', 'sub-CC00247XX17', 'sub-CC00075XX10', 'sub-CC00497XX20', 'sub-CC00067XX10', 'sub-CC00268XX13', 'sub-CC00403XX07', 'sub-CC00324XX11', 'sub-CC00086XX13', 'sub-CC00371XX09', 'sub-CC00453XX08', 'sub-CC00853XX12', 'sub-CC00204XX06', 'sub-CC00074XX09', 'sub-CC00072XX07', 'sub-CC00349XX20', 'sub-CC00181XX09', 'sub-CC00438XX18', 'sub-CC00469XX16', 'sub-CC00413XX09', 'sub-CC00162XX06', 'sub-CC00799XX25', 'sub-CC00357XX11', 'sub-CC00255XX08', 'sub-CC00304XX07', 'sub-CC00470XX09', 'sub-CC00134XX11', 'sub-CC00150BN02', 'sub-CC00798XX24', 'sub-CC00117XX10', 'sub-CC00765XX15', 'sub-CC00145XX14', 'sub-CC00472XX11', 'sub-CC00793XX19', 'sub-CC00810XX10', 'sub-CC00348XX19', 'sub-CC00461XX08', 'sub-CC00434AN14', 'sub-CC00431XX11', 'sub-CC00577XX17', 'sub-CC00584XX16', 'sub-CC00675XX16', 'sub-CC00620XX10', 'sub-CC00822XX14', 'sub-CC00300XX03', 'sub-CC00607XX13', 'sub-CC00182XX10', 'sub-CC00146XX15', 'sub-CC00443XX15', 'sub-CC00451XX06', 'sub-CC00380XX10', 'sub-CC00513XX10', 'sub-CC00338AN17', 'sub-CC00286XX15', 'sub-CC00332XX11', 'sub-CC00102XX03', 'sub-CC00082XX09', 'sub-CC00498XX21', 'sub-CC00815XX15', 'sub-CC00079XX14', 'sub-CC00307XX10', 'sub-CC00446XX18', 'sub-CC00597XX21', 'sub-CC00179XX15', 'sub-CC00200XX02', 'sub-CC00157XX09', 'sub-CC00289XX18', 'sub-CC00065XX08', 'sub-CC00265XX10', 'sub-CC00062XX05', 'sub-CC00319XX14', 'sub-CC00520XX09', 'sub-CC00339XX18', 'sub-CC00424XX12', 'sub-CC00267XX12', 'sub-CC00131XX08', 'sub-CC00176XX12', 'sub-CC00103XX04', 'sub-CC00384XX14', 'sub-CC00378XX16', 'sub-CC00405XX09', 'sub-CC00588XX20', 'sub-CC00740XX15']
    # 'sub-CC00688XX21', # non andato
    
    else:
    subjlist = ['178950','189450','199453']

nsub=len(subjlist)
print(nsub)

s3 = boto3.resource('s3')
bucket = s3.Bucket('smartontheinside')


# Found that many subjects had problem with transformation. So I am selecting only the subject with transformation done and running the code only with them.
 
list_subj_with_transformations = []



  

# for sub in subjlist:
#     path = f'infant_tractography/{sub}/T1w/Diffusion.probtrackx2/L/seeds_to_ROI.360.shape.gii'
#     def IsObjectExists(path):
#         for object_summary in bucket.objects.filter(Prefix=path):
#             return True
#         return False

#     if(IsObjectExists(path)):
#         list_subj_with_transformations.append(sub)
#         print(f'Transformation done for {sub}')
#     else:
#         print(f'Transformation NOT done for {sub}')

# print(list_subj_with_transformations)
# print(len(list_subj_with_transformations))




######################################################################################################
# Load both the .label. file (vertices corresponding to ROI) and the 360 .shape files for each', 'subject
######################################################################################################

# roi_res = np.zeros(2, 334, 26) # 0 is right and 1 is left
# df = pd.DataFrame(data=roi_res)
roi_res = {}
vox_res = {0:None, 1:None}

frontalregs_right=[73,67,96,98,26,70,71,87,68,83,85,84,86] # All the ROIs in the right DLPFC regions

frontalregs_right.sort() #  1-180 is right, 181-360 is left
frontalregs_left=[x+180 for x in frontalregs_right]
frontalregs_left.sort()

s3 = boto3.client('s3')
# finished sub sub-sub-CC00071XX06
# finished sub sub-sub-CC00071XX06

for sub in subjlist:
    print(f"Starting with {sub}")
    for hemiind, hemi in enumerate(['R','L']):
        img=nib.load(f'/home/chiaracaldinelli/smartontheinside/smartontheinside/parcellations_and_masks/ff.{hemi}.label.gii') # Load label file 
        labels=img.labeltable.get_labels_as_dict()
        dat = img.agg_data('NIFTI_INTENT_LABEL') # dat contains ROI and voxels' coordinates
        roi_res[hemiind] = np.zeros((334, 13)) # Prepare the output file for the avg for each frontal ROI (L and R, nsubj * 334 targets * 26 frontal ROIs)
        all_seed_values=[]
        all_seed_values = np.array(all_seed_values)

        for target_roi in range(1, 361): # For every target ROI (334 in total)
            if not target_roi in frontalregs_right:
                if not target_roi in frontalregs_left:
                    # print(target_roi)
                    if infants==1:


                        remotepath = f'infant_tractography/{sub}/T1w/Diffusion.probtrackx2/{hemi}/seeds_to_ROI.{target_roi}.shape.gii'
                        print(remotepath)
                        s3.download_file('smartontheinside', remotepath, f'/home/chiaracaldinelli/infant_classifier/{sub}_seeds_to_ROI.{target_roi}.shape.gii')
                        img_s2t = nib.load(f'/home/chiaracaldinelli/infant_classifier/{sub}_seeds_to_ROI.{target_roi}.shape.gii') 
                    else:
                        remotepath = f'HCP_1200/{sub}/T1w/Diffusion.probtrackx2/{hemi}/seeds_to_ROI.{target_roi}.shape.gii'
                        s3.download_file('smartontheinside', remotepath, f'/home/chiaracaldinelli/{sub}_seeds_to_ROI.{target_roi}.shape.gii')
                        img_s2t = nib.load(f'/home/chiaracaldinelli/{sub}_seeds_to_ROI.{target_roi}.shape.gii') 

                    print(f'Downloading file {remotepath}')

                        
                    dat_s2t = img_s2t.agg_data() # dat_s2t has tractography results
                    for seed_roi in range(len(frontalregs_right)): # for every ROI in the DLPFC
                        if hemiind == 0:
                            seed_values=dat_s2t[dat==(frontalregs_right[seed_roi])]
                        else:
                            seed_values=dat_s2t[dat==(frontalregs_left[seed_roi])]
                        print('this is seed values')
                        print(len(seed_values))
                        print(seed_values)
                        roi_res[hemiind][:,seed_roi] = np.mean(seed_values) # avg and copy res to roi_res

                        all_seed_values = np.append(all_seed_values, seed_values)
                        # print('this is all seed values')
                        # print(all_seed_values)

        if vox_res[hemiind] is None:
            vox_res[hemiind] = np.zeros((360, len(all_seed_values))) # Record seed voxels for each subject (L and R, nsubj * 334 targets * nseedvoxels)
            all_seed_values =  vox_res[hemiind][target_roi-1, :] # Careful: ROI 1 will be in position 0
        if file_exists(f'/home/chiaracaldinelli/infant_classifier/{sub}_seeds_to_ROI.{target_roi}.shape.gii'):
            os.remove(f'/home/chiaracaldinelli/infant_classifier/{sub}_seeds_to_ROI.{target_roi}.shape.gii')
        if file_exists(f'/home/chiaracaldinelli/infant_classifier/{sub}_seeds_to_ROI.{target_roi}.shape.gii'):
            os.remove(f'/home/chiaracaldinelli/infant_classifier/{sub}_seeds_to_ROI.{target_roi}.shape.gii')


    arr_vox0 = vox_res[0]
    arr_vox1 = vox_res[1]
    print(arr_vox0.shape)
    print(arr_vox1.shape)
    arr_roi0 = roi_res[0]
    arr_roi1 = roi_res[1]
    print(arr_roi0.shape)
    print(arr_roi1.shape)
    print(roi_res)

    # open file for writing
    if infants==1:
        f = open(f'/home/chiaracaldinelli/infant_classifier/{sub}_infant_tractography_results_ROI.txt',"w")

    else:
        f = open(f'/home/chiaracaldinelli/smartontheinside/{sub}_tractography_results_ROI.txt',"w")
    f.write( str(roi_res) )
    f.close()

    print(f"Finished with {sub}")


    if infants==1:
        
        np.save((f'/home/chiaracaldinelli/infant_classifier/{sub}_infant_tractography_results_ROI.npy'), roi_res)
        np.save((f'/home/chiaracaldinelli/infant_classifier/{sub}_infant_tractography_results_VOXEL.npy'), vox_res)

        s3.upload_file(f'/home/chiaracaldinelli/infant_classifier/{sub}_infant_tractography_results_ROI.npy', 'smartontheinside', f'infant_tractography/{sub}_tractography_results_ROI.npy')
        s3.upload_file(f'/home/chiaracaldinelli/infant_classifier/{sub}_infant_tractography_results_VOXEL.npy', 'smartontheinside', f'infant_tractography/{sub}_tractography_results_VOXEL.npy')

        os.remove(f'/home/chiaracaldinelli/infant_classifier/{sub}_infant_tractography_results_ROI.npy')
        os.remove(f'/home/chiaracaldinelli/infant_classifier/{sub}_infant_tractography_results_VOXEL.npy')

    else:

        np.save((f'/home/chiaracaldinelli/smartontheinside/{sub}_tractography_results_ROI.npy'), roi_res)
        np.save((f'/home/chiaracaldinelli/{sub}_tractography_results_VOXEL.npy'), vox_res)

        s3.upload_file(f'/home/chiaracaldinelli/{sub}_tractography_results_ROI.npy', 'smartontheinside', f'HCP_1200/{sub}/T1w/Diffusion.probtrackx2/{sub}_tractography_results_ROI.npy')
        s3.upload_file(f'/home/chiaracaldinelli/{sub}_tractography_results_VOXEL.npy', 'smartontheinside', f'HCP_1200/{sub}/T1w/Diffusion.probtrackx2/{sub}_tractography_results_VOXEL.npy')

        os.remove(f'/home/chiaracaldinelli/{sub}_tractography_results_ROI.npy')
        os.remove(f'/home/chiaracaldinelli/{sub}_tractography_results_VOXEL.npy')
