import numpy as np
import msgpack
import msgpack_numpy as m


#(1) take mean and standard error across subjects
#(2) find top 3 (?) activating regions within DLPFC
#(3) find top 3 (?) activating regions across rest of brain

subjlist = ['178950','189450','199453','209228','220721','298455','356948','419239','499566','561444','618952','680452','757764','841349','908860', '103818','113922','121618','130619','137229','151829','158035','171633','179346','190031','200008','210112','221319','299154','361234', '424939','500222','570243','622236','687163','769064','845458','911849','104416','114217','122317','130720','137532','151930','159744', '172029','180230','191235','200614','211316','228434','300618','361941','432332','513130','571144','623844','692964','773257','857263', '926862','105014','114419','122822','130821','137633','152427','160123','172938','180432','192035','200917','211417','239944','303119', '365343','436239','513736','579665','638049','702133','774663','865363','930449','106521','114823','123521','130922','137936','152831', '160729','173334','180533','192136','201111','211619','249947','305830','366042','436845','516742','580650','645450','715041','782561', '871762','942658','106824','117021','123925','131823','138332','153025','162026','173536','180735','192439','201414','211821','251833', '310621','371843','445543','519950','580751','647858','720337','800941','871964','955465','107018','117122','125222','132017','138837', '153227','162329','173637','180937','193239','201818','211922','257542','314225','378857','454140','523032','585862','654350','725751', '803240','872562','959574','107422','117324','125424','133827','142828','153631','164030','173940','182739','194140','202719','212015', '257845','316633','381543','459453','525541','586460','654754','727553','812746','873968','966975']
taskname = {'tfMRI_WM', 'tfMRI_GAMBLING', 'tfMRI_MOTOR', 'tfMRI_LANGUAGE', 'tfMRI_SOCIAL',  'tfMRI_EMOTION'}

# Load allresults
with open('sub-103818_roi.msgpack-numpy', 'rb') as f:
#with open(f'sub-{sublist[x]}_roi.msgpack-numpy', 'rb') as f:
    datallresultsa = msgpack.unpackb(f.read())
print(allresults)

# For each task
#Concatenate all subjects and all ROIs
allsubj={​taskname:np.hstack([subjdata[taskname] for subjname, subjdata in allresults.items()] for taskname, taskdata in subjdata[allresults.keys()[0])}​
print(allsubj)

#Get the mean
mnact = np.mean(allsubj, axis=1)
#Order them from the biggest (giving you the position, so we have the ROIs’ names)
sortedregions = np.argsort(mnact)
np.save(sortedregions, allow_pickle=True)


#DLPF regions
DLPFrois=[26, 67, 68, 70, 71, 73, 83, 84, 85, 86, 87, 96, 98, 206, 247, 148, 250, 251, 253, 264, 265, 266, 267, 276, 278]
#Select the right ROIs
for x in DLPFrois:
    
#Order them from the biggest (giving you the position, so we have the ROIs’ names)
sortedregionsDLPF = np.argsort(mnact)
np.save(sortedregions, allow_pickle=True)