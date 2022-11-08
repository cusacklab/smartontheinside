from curses import def_prog_mode
from tkinter import Y
import boto3
import matplotlib.pyplot as plt
import numpy as np
import ptitprince as pt
import seaborn as sns
from matplotlib.colors import ListedColormap
import pandas as pd
from statsmodels.graphics.factorplots import interaction_plot 



subjlist = ['178950','189450','199453','209228','220721','298455','356948','419239','499566','561444','618952','680452','757764','841349','908860','103818','113922','121618','130619','137229','151829','158035','171633','179346','190031','200008','210112','221319','299154','361234', '424939','500222','570243','622236','687163','769064','845458','911849','104416','114217','122317','130720','137532','151930','159744', '172029','180230','191235','200614','211316','228434','300618','361941','432332','513130','571144','623844','692964','773257','857263', '926862','105014','122822','130821','137633','152427','160123','172938','180432','192035','200917','211417','239944','303119', '365343','436239','513736','579665','638049','702133','774663','865363','930449','106521','114823','123521','130922','137936','152831', '160729','173334','180533','192136','201111','211619','249947','305830','366042','436845','516742','580650','645450','715041','782561', '871762','942658','106824','117021','123925','131823','138332','153025','162026','173536','180735','192439','201414','211821','251833', '310621','371843','445543','519950','580751','647858','720337','800941','871964','955465','107018','117122','125222','132017','138837', '153227','162329','173637','180937','193239','201818','211922','257542','314225','378857','454140','523032','585862', '654350','725751', '803240','872562','959574','107422','117324','125424','133827','142828','153631','164030','173940','182739','194140','202719','212015', '257845','316633','381543','459453','525541','586460','654754','727553','812746','873968','966975']
nsub = len(subjlist)

# Selection of contrasts - based on previous analysis
taskcondict_selected_list = {'tfMRI_WM', 'tfMRI_MOTOR', 'tfMRI_LANGUAGE', 'tfMRI_SOCIAL', 'tfMRI_EMOTION'}

# Credentials for uploading data to the cusack lab s3
session = boto3.Session(profile_name='default')
s3 = session.client('s3')

for hemiind, hemi in enumerate(['R', 'L']):
    data_for_plot = np.zeros(((len(taskcondict_selected_list))*nsub,3))
    df = pd.DataFrame(data_for_plot, columns = (['Subject', 'Task', 'r2']))
    
    for taskind, task in enumerate(taskcondict_selected_list):
        
        # Download and load results from the classifier
        remotepath = (f'Results/classifier_results_{task}_2groups.npy')
        s3.download_file('smartontheinside', remotepath, f'/Users/chiara/classifier_results_{task}_2groups.npy')
        res = np.load(
        f'/Users/chiara/classifier_results_{task}_2groups.npy', allow_pickle=True).ravel()[0]
        res = pd.DataFrame(res[hemi])

        df.iloc[taskind*nsub:((taskind+1)*nsub),0] = subjlist
        df.iloc[taskind*nsub:((taskind+1)*nsub),1] = task
        df.iloc[taskind*nsub:((taskind+1)*nsub),2] = res

        res_avg = np.average(res)
        print(f' {hemi} Hemisphere: average for task {task} is {res_avg}')


        df.to_csv(f'/Users/chiara/results_for_plots_{hemi}_2groups.csv')  

        #dy="group"; dx="score"; ort="h"; pal = sns.color_palette(n_colors=1)



# PLOTS

# Read data as df
df_L = pd.read_csv('/Users/chiara/results_for_plots_L.csv')
df_R = pd.read_csv('/Users/chiara/results_for_plots_R.csv')

# plt.figure()
# sns.barplot(x = "group", y = "score", data = df, capsize= .1)
# plt.title("Figure P1\n Bar Plot")

# Divide the figure into 2
fig,ax=plt.subplots(nrows=2, figsize=(10,7))

fig=pt.half_violinplot(x=df_L['Task'], y=df_L['r2'], ax=ax[0])
fig=pt.half_violinplot(x=df_R['Task'], y=df_R['r2'], ax=ax[1])

ax[0].set_title('Left Hemisphere')
ax[1].set_title('Right Hemisphere')

ax[0].set_xlabel('')
ax[1].set_xlabel('')


plt.savefig(('/Users/chiara/Results_elastic_net_2group.png'), bbox_inches='tight')
#plt.figure()
plt.show()
