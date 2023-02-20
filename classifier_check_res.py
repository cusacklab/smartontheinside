import pandas as pd
import os
import matplotlib.pyplot as plt
from statsmodels.graphics.factorplots import interaction_plot
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable
import seaborn as sns
from statsmodels.graphics.factorplots import interaction_plot
import ptitprince as pt
from scipy.stats import kstest
import pingouin as pg
from scipy.stats import bootstrap
import numpy as np
import boto3
from scipy.stats import mannwhitneyu

infants  = 1 # 1 is infants, 0 is adults
alpha = 0.4
l1_ratio = 0.6

subjlist = ['178950','189450','199453','209228','220721','298455','356948','419239','499566','561444','618952','680452','757764','841349','908860','103818','113922','121618','130619','137229','151829','158035','171633','179346','190031','200008','210112','221319','299154','361234', '424939','500222','570243','622236','687163','769064','845458','911849','104416','114217','122317','130720','137532','151930','159744', '172029','180230','191235','200614','211316','228434','300618','361941','432332','513130','571144','623844','692964','773257','857263', '926862','105014','122822','130821','137633','152427','160123','172938','180432','192035','200917','211417','239944','303119', '365343','436239','513736','579665','638049','702133','774663','865363','930449','106521','114823','123521','130922','137936','152831', '160729','173334','180533','192136','201111','211619','249947','305830','366042','436845','516742','580650','645450','715041','782561', '871762','942658','106824','117021','123925','131823','138332','153025','162026','173536','180735','192439','201414','211821','251833', '310621','371843','445543','519950','580751','647858','720337','800941','871964','955465','107018','117122','125222','132017','138837', '153227','162329','173637','180937','193239','201818','211922','257542','314225','378857','454140','523032','585862', '654350','725751', '803240','872562','959574','107422','117324','125424','133827','142828','153631','164030','173940','182739','194140','202719','212015', '257845','316633','381543','459453','525541','586460','654754','727553','812746','873968','966975']

subjlist_infants =['sub-CC00549XX22', 'sub-CC00202XX04', 'sub-CC00720XX11', 'sub-CC00122XX07', 'sub-CC00071XX06', 'sub-CC00119XX12', 'sub-CC00207XX09', 'sub-CC00484XX15', 'sub-CC00590XX14', 'sub-CC00586XX18', 'sub-CC00467XX14', 'sub-CC00593XX17', 'sub-CC00344XX15', 'sub-CC00409XX13', 'sub-CC00168XX12', 'sub-CC00158XX10', 'sub-CC00613XX11', 'sub-CC00731XX14', 'sub-CC00198XX18', 'sub-CC00664XX13', 'sub-CC00397XX19', 'sub-CC00270XX07', 'sub-CC00252XX05', 'sub-CC00787XX21', 'sub-CC00223XX09', 'sub-CC00367XX13', 'sub-CC00183XX11', 'sub-CC00478XX17', 'sub-CC00540XX13', 'sub-CC00512XX09', 'sub-CC00476XX15', 'sub-CC00120XX05', 'sub-CC00164XX08', 'sub-CC00562XX10', 'sub-CC00194XX14', 'sub-CC00383XX13', 'sub-CC00440XX12', 'sub-CC00153XX05', 'sub-CC00170XX06', 'sub-CC00595XX19', 'sub-CC00744XX19', 'sub-CC00398XX20', 'sub-CC00547XX20','sub-CC00466BN13', 'sub-CC00258XX11', 'sub-CC00203XX05', 'sub-CC00500XX05', 'sub-CC00654XX11', 'sub-CC00073XX08', 'sub-CC00115XX08', 'sub-CC00070XX05', 'sub-CC00840XX16', 'sub-CC00089XX16', 'sub-CC00411XX07', 'sub-CC00184XX12', 'sub-CC00205XX07', 'sub-CC00337XX16', 'sub-CC00313XX08', 'sub-CC00107XX08', 'sub-CC00144XX13', 'sub-CC00585XX17', 'sub-CC00138XX15', 'sub-CC00850XX09', 'sub-CC00149XX18', 'sub-CC00193XX13', 'sub-CC00458XX13', 'sub-CC00201XX03', 'sub-CC00650XX07', 'sub-CC00508XX13', 'sub-CC00099AN18', 'sub-CC00078XX13', 'sub-CC00527XX16', 'sub-CC00150AN02', 'sub-CC00355XX09', 'sub-CC00454XX09', 'sub-CC00341XX12', 'sub-CC00343XX14', 'sub-CC00445XX17', 'sub-CC00116XX09', 'sub-CC00544XX17', 'sub-CC00450XX05', 'sub-CC00561XX09', 'sub-CC00548XX21', 'sub-CC00801XX09', 'sub-CC00060XX03', 'sub-CC00447XX19', 'sub-CC00377XX15', 'sub-CC00479XX18', 'sub-CC00473XX12', 'sub-CC00101XX02', 'sub-CC00481XX12', 'sub-CC00480XX11', 'sub-CC00502XX07', 'sub-CC00088XX15', 'sub-CC00766XX16', 'sub-CC00366XX12', 'sub-CC00757XX15', 'sub-CC00596XX20', 'sub-CC00536XX17', 'sub-CC00550XX06', 'sub-CC00221XX07', 'sub-CC00382XX12', 'sub-CC00178XX14', 'sub-CC00589XX21', 'sub-CC00068XX11', 'sub-CC00334XX13', 'sub-CC00486XX17', 'sub-CC00501XX06', 'sub-CC00455XX10', 'sub-CC00652XX09', 'sub-CC00528XX17', 'sub-CC00685XX18', 'sub-CC00649XX23', 'sub-CC00400XX04', 'sub-CC00094BN13', 'sub-CC00556XX12', 'sub-CC00199XX19', 
'sub-CC00507XX12', 'sub-CC00362XX08', 'sub-CC00236XX14', 'sub-CC00858XX17', 'sub-CC00555XX11', 'sub-CC00091XX10', 'sub-CC00110XX03', 'sub-CC00113XX06', 'sub-CC00558XX14', 'sub-CC00379XX17', 'sub-CC00466AN13', 'sub-CC00499XX22', 'sub-CC00096XX15', 'sub-CC00172BN08', 'sub-CC00399XX21', 'sub-CC00206XX08', 'sub-CC00143AN12', 'sub-CC00656XX13', 'sub-CC00298XX19', 'sub-CC00376XX14', 'sub-CC00219XX13', 'sub-CC00195XX15', 'sub-CC00483XX14', 'sub-CC00546XX19', 'sub-CC00306XX09']


# Selection of contrasts - based on previous analysis
tasks_selected = ['tfMRI_WM', 'tfMRI_MOTOR', 'tfMRI_LANGUAGE', 'tfMRI_SOCIAL','tfMRI_EMOTION']

analysis_root = '/home/chiaracaldinelli'



# Credentials for downloading data from the cusack lab s3
s3 = boto3.client('s3')
session = boto3.Session(profile_name='default')

def bootstrap_replicate_1d(data, func):

    """Generate bootstrap replicate of 1D data."""
    bs_sample = np.random.choice(data, len(data))

    return func(bs_sample)


def draw_bs_reps(data, func, size=1):
    """Draw bootstrap replicates."""

    # Initialize array of replicates: bs_replicates
    bs_replicates = np.empty(size)

    # Generate replicates
    for i in range(size):
        bs_replicates[i] = bootstrap_replicate_1d(data, func)

    return bs_replicates
    
def bootstrap_compare_two_groups(group1, group2):

    # Compute mean of all groups
    mean_two_groups = np.mean(np.concatenate((group1,group2), axis=0))

    # Generate shifted arrays
    within_shifted = within - np.mean(group1) + mean_two_groups
    across_shifted = across - np.mean(group2) + mean_two_groups 

    # Compute 10,000 bootstrap replicates from shifted arrays
    bs_replicates_within = draw_bs_reps(within_shifted, np.mean, size=10000)
    bs_replicates_across = draw_bs_reps(across_shifted, np.mean, size=10000)

    # Get replicates of difference of means: bs_replicates
    bs_replicates = bs_replicates_within - bs_replicates_across

    # Compute and print p-value: p
    empirical_diff_means = np.mean(group1) - np.mean(group2)
    p = np.sum(bs_replicates >= np.mean(empirical_diff_means)) / 10000
    print('p-value =', p)

    return


if infants == 1:
    nsub = 183
    folder = f'/home/chiaracaldinelli/final_parameters_classifier_results_alpha-{alpha}_l1ratio-{l1_ratio}_infants'
    folder_results_classifier = f'final_parameters_classifier_results_alpha-{alpha}_l1ratio-{l1_ratio}_infants'
    os.makedirs(os.path.join(folder, folder_results_classifier), exist_ok=True) # Make folder if it doesn't already exist

else:
    nsub = 155
    folder = f'final_parameters_classifier_results_alpha-{alpha}_l1ratio-{l1_ratio}'
    folder_results_classifier = f'final_parameters_classifier_results_alpha-{alpha}_l1ratio-{l1_ratio}'
    os.makedirs(os.path.join(folder, folder_results_classifier), exist_ok=True) # Make folder if it doesn't already exist


for hemiind, hemi in enumerate(['R', 'L']):

    df = pd.read_csv(os.path.join(folder, f'summary_N-{nsub}.csv'), index_col=False)
    print(df)

    for taskind, task in enumerate(tasks_selected): 

        # Bootstrap
        #convert array to sequence
        data = df.loc[df['task'] == task]
        print(data)

        data = df['pearson'] 
        print(data)
        data = (data,)

        #calculate 95% bootstrapped confidence interval for median
        bootstrap_ci = bootstrap(data, np.median, confidence_level=0.99,
                                random_state=1, method='percentile')

        #view 95% boostrapped confidence interval
        print(f'task: {task} {bootstrap_ci.confidence_interval}')



    # Jitter and rain for score
    f, ax = plt.subplots(figsize=(7, 5))
    ax = pt.half_violinplot( x = df['task'], y = df['score'], data = df, bw = .2, cut = 0.,
                            scale = "area", width = .6, inner = None)
    ax = sns.stripplot( x = df['task'], y = df['score'], data = df, edgecolor = "white",
                        size = 3, jitter = 1, zorder = 0)
    plt.ylim(-0.25, 0.30)
    plt.title(f"{hemi} hemisphere")
    plt.savefig(os.path.join(folder, f'summarise_res_classifier_score_{hemi}.png'), bbox_inches='tight')
    print(f'Figure saved as summarise_res_score_{hemi}.png')
    

    # Jitter and rain for pearson
    f, ax = plt.subplots(figsize=(7, 5))
    ax = pt.half_violinplot( x = df['task'], y = df['pearson'], data = df, bw = .2, cut = 0.,
                            scale = "area", width = .6, inner = None)
    ax = sns.stripplot( x = df['task'], y = df['pearson'], data = df, edgecolor = "white",
                        size = 3, jitter = 1, zorder = 0)
    plt.title(f"{hemi} hemisphere")
    # plt.ylim(-0.20, 0.40)
    x = np.arange(0, 10, 0.1)

    plt.savefig(os.path.join(folder, f'summarise_res_classifier_pearson_{hemi}.png'), bbox_inches='tight')
    print(f'Figure saved as summarise_res_pearson_{hemi}.png')


    table = pd.pivot_table(df, values=['pearson', 'score'], index=['hemi', 'task'],
                    aggfunc={'pearson': [np.mean, np.std, min, max],
                             'score': [np.mean, np.std, min, max]})
    print(table)




# RESULTS  OF CORRELATION BETWEEN PREDICTED VALUES AND VALUES FROM CLASSIFICATION
# Check if tasks are different 

for hemiind, hemi in enumerate(['R', 'L']):
    print(f'{hemi} hemisphere')

    # Load values
    df = pd.read_csv(os.path.join(folder, f'summary_N-{nsub}.csv'))
    df = df.loc[df['hemi'] == hemi]
    print(df)

    ######### PLOT MATRIX WITH PREDICTED AND TRUE VALUES #########
    
    df_mean = (df.groupby(['task','comparison_task']).mean())
    matrix = df_mean['pearson']
    matrix = matrix.to_frame()
    matrix = matrix.to_numpy()
    matrix= np.reshape(matrix, (5,5))

    plt.imshow(matrix)

    plt.figure()
    # Show matrix plot
    ax = plt.gca()
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
            rotation_mode="anchor")
    # Major ticks
    ax.set_xticks(np.arange(0, len(tasks_selected), 1))
    ax.set_yticks(np.arange(0, len(tasks_selected), 1))
    # Labels for major ticks
    ax.set_xticklabels(tasks_selected, fontsize=6)
    ax.set_yticklabels(tasks_selected, fontsize=6)

    plt.imshow(matrix)

    plt.colorbar()    
    plt.savefig((f'matrix_{hemi}_hemisphere.png'), bbox_inches='tight')
    plt.close()

    # Make empty matrix to compare within to across tasks
    # First column is within, second is across
    if infants == 1:
        comp = np.zeros((182,2))
    else:
        comp = np.zeros((154,2))
        
    comp_same_task = np.zeros((nsub,len(tasks_selected)))

    for subj in range(nsub-1):
 
        df_one_sub = df.loc[df['fold'] == subj]

        within = []
        across = []

        for index, row in df_one_sub.iterrows():

            if row['task'] == row['comparison_task']:
                within.append(row['pearson'])
            else:
                across.append(row['pearson'])

            # Calculate average of the participants for each task correlated to itself
            for taskind, task in enumerate(tasks_selected):
                if row['task'] == task and row['comparison_task'] == task:

                    comp_same_task[subj-1,taskind] = row['pearson']
            
        comp[subj,0] = np.mean(within)
        comp[subj,1] = np.mean(across)

    

    # take mean for within and across
    # (1) for each subject calculate two values - the within task (average of leading diagonal) and the across tasks (average of values off the leading diagonal). We can then do bootstrapping of the difference to see if they're different
    # for within, pick rows where task == comparison taks, then groupby subject and take mean. For across tasks, pick rows where task ~= comparison task, group by subject and mean
    # Then get one difference value per subject and bootstrap them using the bootstrap command

    within = comp[:,0] 
    across = comp[:,1]
    print(f'Mean and SD for within, {hemi} hemisphere:')
    print(np.mean(within))
    print(np.std(within))
    print(f'Mean and SD for across, {hemi} hemisphere:')
    print(np.mean(across))
    print(np.std(across))

    # res = mannwhitneyu(within, across, method="exact")
    # print('************************************************************')
    # print('Results Mann Whitney')
    # print(res)

    # ************* USE BOOTSTRAP TO CHECK IF THE 2 GROUPS (ACROSS AND WITHIN) ARE DIFFERENT *************
    #  
    # 
    # Compute the mean of all forces (from forces_concat) using np.mean().
    # Generate shifted data sets for both force_a and force_b such that the mean of each is the mean of the concatenated array of impact forces.
    # Generate 10,000 bootstrap replicates of the mean each for the two shifted arrays.
    # Compute the bootstrap replicates of the difference of means by subtracting the replicates of the shifted impact force of Frog B from those of Frog A.
    # Compute and print the p-value from your bootstrap replicates.

    # Compare the diagonal VS all the other tasks
    print('T test for within and across:')
    bootstrap_compare_two_groups(within, across)

    # Compare each task VS ech task
    for group1 in range(len(tasks_selected)):
        print(f'Mean and SD for {tasks_selected[group1]}, {hemi} hemisphere:')
        print(np.mean(comp_same_task[group1,:]))
        print(np.std(comp_same_task[group1,:]))

        for group2 in range(len(tasks_selected)):
            
            print(f'T test between {tasks_selected[group1]} and {tasks_selected[group2]}, {hemi} hemisphere:')
            bootstrap_compare_two_groups(comp_same_task[group1,:], comp_same_task[group2,:])





