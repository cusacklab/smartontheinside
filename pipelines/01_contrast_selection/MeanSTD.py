import numpy as np
import matplotlib.pyplot as plt
from numpy import random
import pandas as pd
import scipy.spatial.distance as ssd
import scipy.cluster.hierarchy as sch
import scipy.stats as stats
import pingouin as pg

indexDF = ['WORKING_MEM_2BK_BODY', 'WORKING_MEM_2BK_FACE', 'WORKING_MEM_2BK_PLACE', 'WORKING_MEM_2BK_TOOL', 'WORKING_MEM_0BK_BODY', 'WORKING_MEM_0BK_FACE', 'WORKING_MEM_0BK_PLACE', 'WORKING_MEM_0BK_TOOL', 'WORKING_MEM_2BK', 'WORKING_MEM_0BK', 'WORKING_MEM_2BK-0BK', 'WORKING_MEM_neg_2BK', 'WORKING_MEM_neg_0BK', 'WORKING_MEM_0BK-2BK', 'WORKING_MEM_BODY', 'WORKING_MEM_FACE', 'WORKING_MEM_PLACE', 'WORKING_MEM_TOOL', 'WORKING_MEM_BODY-AVG', 'WORKING_MEM_FACE-AVG', 'WORKING_MEM_PLACE-AVG', 'WORKING_MEM_TOOL-AVG', 'WORKING_MEM_neg_BODY', 'WORKING_MEM_neg_FACE', 'neg_PLACE', 'WORKING_MEM_neg_TOOL', 'WORKING_MEM_AVG-BODY', 'WORKING_MEM_AVG-FACE', 'WORKING_MEM_AVG-PLACE', 'WORKING_MEM_VG-TOOL', 'GAMBLING_PUNISH', 'GAMBLING_REWARD', 'GAMBLING_PUNISH-REWARD', 'GAMBLING_neg_PUNISH', 'GAMBLING_neg_REWARD', 'GAMBLING_REWARD-PUNISH', 'MOTOR_CUE', 'MOTOR_LF', 'MOTOR_LH', 'MOTOR_RF', 'MOTOR_RH', 'MOTOR_T', 'MOTOR_AVG', 'MOTOR_CUE-AVG', 'MOTOR_LF-AVG', 'MOTOR_LH-AVG', 'MOTOR_RF-AVG', 'MOTOR_RH-AVG', 'MOTOR_T-AVG', 'MOTOR_neg_CUE', 'MOTOR_neg_LF', 'MOTOR_neg_LH', 'MOTOR_neg_RF', 'MOTOR_neg_RH', 'MOTOR_neg_T', 'MOTOR_neg_AVG', 'MOTOR_AVG-CUE', 'MOTOR_AVG-LF', 'MOTOR_AVG-LH', 'MOTOR_AVG-RF', 'MOTOR_AVG-RH', 'MOTOR_AVG-T', 'LANGUAGE_MATH', 'LANGUAGE_STORY', 'LANGUAGE_MATH-STORY', 'LANGUAGE_STORY-MATH', 'LANGUAGE_neg_MATH', 'LANGUAGE_neg_STORY', 'SOCIAL_RANDOM', 'SOCIAL_TOM', 'SOCIAL_RANDOM-TOM', 'SOCIAL_neg_RANDOM', 'SOCIAL_neg_TOM', 'SOCIAL_TOM-RANDOM', 'RELATIONAL_MATCH', 'RELATIONAL_REL', 'RELATIONAL_MATCH-REL', 'RELATIONAL_REL-MATCH', 'RELATIONAL_neg_MATCH', 'RELATIONAL_neg_REL', 'EMOTION_FACES', 'EMOTION_SHAPES', 'EMOTION_FACES-SHAPES', 'EMOTION_neg_FACES', 'EMOTION_neg_SHAPES', 'EMOTION_SHAPES-FACES']   
indexDFnoneg = ['WORKING_MEM_2BK_BODY', 'WORKING_MEM_2BK_FACE', 'WORKING_MEM_2BK_PLACE', 'WORKING_MEM_2BK_TOOL', 'WORKING_MEM_0BK_BODY', 'WORKING_MEM_0BK_FACE', 'WORKING_MEM_0BK_PLACE', 'WORKING_MEM_0BK_TOOL', 'WORKING_MEM_2BK', 'WORKING_MEM_0BK', 'WORKING_MEM_BODY', 'WORKING_MEM_FACE', 'WORKING_MEM_PLACE', 'WORKING_MEM_TOOL', 'GAMBLING_PUNISH', 'GAMBLING_REWARD','MOTOR_CUE', 'MOTOR_LF', 'MOTOR_LH', 'MOTOR_RF', 'MOTOR_RH', 'MOTOR_T', 'MOTOR_AVG',  'LANGUAGE_MATH', 'LANGUAGE_STORY',  'SOCIAL_RANDOM', 'SOCIAL_TOM', 'RELATIONAL_MATCH', 'RELATIONAL_REL', 'EMOTION_FACES', 'EMOTION_SHAPES']   
subjlist = ['178950','189450','199453','209228','220721','298455','356948','419239','499566','561444','618952','680452','757764','841349','908860', '103818','113922','121618','130619','137229','151829','158035','171633','179346','190031','200008','210112','221319','299154','361234', '424939','500222','570243','622236','687163','769064','845458','911849','104416','114217','122317','130720','137532','151930','159744', '172029','180230','191235','200614','211316','228434','300618','361941','432332','513130','571144','623844','692964','773257','857263', '926862','105014','114419','122822','130821','137633','152427','160123','172938','180432','192035','200917','211417','239944','303119', '365343','436239','513736','579665','638049','702133','774663','865363','930449','106521','114823','123521','130922','137936','152831', '160729','173334','180533','192136','201111','211619','249947','305830','366042','436845','516742','580650','645450','715041','782561', '871762','942658','106824','117021','123925','131823','138332','153025','162026','173536','180735','192439','201414','211821','251833', '310621','371843','445543','519950','580751','647858','720337','800941','871964','955465','107018','117122','125222','132017','138837', '153227','162329','173637','180937','193239','201818','211922','257542','314225','378857','454140','523032','585862','654350','725751', '803240','872562','959574','107422','117324','125424','133827','142828','153631','164030','173940','182739','194140','202719','212015', '257845','316633','381543','459453','525541','586460','654754','727553','812746','873968','966975']
DLPFroilist = [26, 67, 68, 70, 71, 73, 83, 84, 85, 86, 87, 96, 98, 206, 247, 248, 250, 251, 253, 263, 264, 265, 266, 267, 276, 278]
DLPFroilistplot = ['26', '67', '68', '70', '71', '73', '83', '84', '85', '86', '87', '96', '98', '206', '247', '248', '250', '251', '253', '263', '264', '265', '266', '267', '276', '278']
data = np.load('DLPFCroi.npy')
print(data.shape)
data=np.mean(data,0)
print(data.shape)
rdm = np.corrcoef(data)
print(rdm)
# should give numcons * numcons matrix
#if not then do rdm = np.corrcoef(X.T)

plt.figure()
# Show matrix plot
ax = plt.gca()
# Major ticks
ax.set_xticks(np.arange(0, len(indexDFnoneg), 1))
ax.set_yticks(np.arange(0, len(indexDFnoneg), 1))
# Labels for major ticks
ax.set_xticklabels(indexDFnoneg, fontsize=6)
ax.set_yticklabels(indexDFnoneg, fontsize=6)
plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
         rotation_mode="anchor")
rdm = (rdm + 1) / 2
#plt.imshow(rdm)
plt.savefig(('rdmnoneg.png'), bbox_inches='tight')
plt.close()


plt.figure()
fig,ax = plt.subplots(figsize=(10,10))
dend = sch.dendrogram(sch.linkage(rdm, method='ward'), 
    ax=ax, 
    labels=indexDFnoneg, 
    orientation='right'
    )
plt.xlim(0,20)
y = [0,20]
plt.xticks(np.arange(min(y), max(y)+1, 1.0))
plt.savefig(('rdm-hie_noneg.png'), bbox_inches='tight')
plt.close()


# Create bar plots for each selected contrast

listcon = ['EMOTION_SHAPES', 'SOCIAL_TOM', 'WORKING_MEM_2BK', 'MOTOR_AVG', 'LANGUAGE_STORY']
datapersub = np.load('DLPFCroi.npy')
con8=np.zeros((176, 26))
for q in range(len(indexDFnoneg)):
    if indexDFnoneg[q]=='EMOTION_SHAPES' or indexDFnoneg[q]=='SOCIAL_TOM' or indexDFnoneg[q]=='WORKING_MEM_2BK' or indexDFnoneg[q]=='MOTOR_AVG' or indexDFnoneg[q]=='LANGUAGE_STORY':
        x=data[q,:] 
        plt.figure()
        plt.bar(DLPFroilistplot, x, color=['black', 'red', 'green', 'blue', 'cyan', 'red', 'yellow', 'black', 'blue', 'orange', 'black', 'red', 'green', 'blue', 'cyan', 'red', 'yellow', 'black', 'blue', 'orange', 'black', 'red', 'green', 'blue', 'cyan', 'red'])
        #plt.stem(DLPFroilistplot, x)
        plt.title(indexDFnoneg[q])
        plt.style.use('seaborn-pastel')
        plt.tick_params(axis='x', labelsize=6)
        plt.savefig(('barplot%s'%(indexDFnoneg[q]) + '.png'), bbox_inches='tight')
        plt.close()
        print('Saved plot')
        np.append(con8, datapersub[:,q,:], axis=1)
        print(datapersub[:,q,:])
        s = datapersub[:,q,:]
        np.savetxt('%s'%indexDFnoneg[q] + '.txt', datapersub[:,q,:])
        print('Saved %s'%indexDFnoneg[q] + '.txt')
        
    else:
        print('con')


# Run ANOVA between contrasts to see if they are different
index_df_con = ['roi26', 'roi67', 'roi68', 'roi70', 'roi71', 'roi73', 'roi83', 'roi84', 'roi85', 'roi86', 'roi87', 'roi96', 'roi98', 'roi206', 'roi247', 'roi248', 'roi250', 'roi251', 'roi253', 'roi263', 'roi264', 'roi265', 'roi266', 'roi267', 'roi276', 'roi278', 'Contrasts']
anova_dict = {}
anova_df = pd.DataFrame(anova_dict)
for p in range(len(listcon)):
    df_con = pd.read_csv('%s'%(listcon[p]) + '.txt', sep=" ", header=None)
    dict_roi_con = {"Activation": df_con[0].tolist(), "ROI": [index_df_con[0]]*df_con[0].shape[0]}
    for i in range(1, 26):
        dict_roi_con["ROI"] = dict_roi_con["ROI"] + [index_df_con[i]]*df_con[i].shape[0]
        dict_roi_con["Activation"] = dict_roi_con["Activation"] + df_con[i].tolist()
    df_roi_con = pd.DataFrame(dict_roi_con)
    df_roi_con['Contrast'] = listcon[p]
    anova_df = pd.concat([anova_df, df_roi_con], axis=0, ignore_index=True)

# ANOVA
aov=pg.anova(dv="Activation", between=['ROI', 'Contrast'], data=anova_df, detailed=True).round(3)
print(aov)

# Create 2 dfs for each hemisphere
list_hem1 = ['ROI 26', 'ROI 67', 'ROI 68', 'ROI 70', 'ROI 71', 'ROI 73', 'ROI 83', 'ROI 84', 'ROI 85', 'ROI 86', 'ROI 87', 'ROI 96', 'ROI 98']
dict_hem1 = {}
hem1 = pd.DataFrame(dict_hem1)
for i in list_hem1: 
    df_hem1 = anova_df[(anova_df['ROI'] == i)]
    hem1 = pd.concat([hem1, df_hem1], axis=0, ignore_index=True)
    print('this is hemi')
    print(hem1)

list_hem2 = ['ROI206', 'ROI247', 'ROI248', 'ROI250', 'ROI251', 'ROI253', 'ROI263', 'ROI264', 'ROI265', 'ROI266', 'ROI267', 'ROI276', 'ROI278']
dict_hem2 = {}
hem2 = pd.DataFrame(dict_hem2)
for r in list_hem2: 
    print(r)
    df_hem2 = anova_df[(anova_df['ROI'] == r)]
    hem2 = pd.concat([hem2, df_hem2], axis=0, ignore_index=True)


from statsmodels.graphics.factorplots import interaction_plot 
fig,ax=plt.subplots(nrows=2, figsize=(10,8))
fig=interaction_plot(x=hem1['ROI'], trace=hem1['Contrast'], response=hem1['Activation'], ax=ax[0])
fig=interaction_plot(x=hem2['ROI'], trace=hem2['Contrast'], response=hem2['Activation'], ax=ax[1])

fig=interaction_plot(x=anova_df['ROI'], trace=anova_df['Contrast'], response=anova_df['Activation'], ax=ax)
fig.tight_layout()
# fig.set_figheight(9)
# fig.set_figwidth(15)

plt.savefig(('anova.png'), bbox_inches='tight')