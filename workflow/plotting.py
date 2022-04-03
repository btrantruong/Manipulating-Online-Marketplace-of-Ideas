# Code to plot 1 line
from matplotlib import cm 

import matplotlib.pyplot as plt
import csv
import numpy as np 
import glob 
import json
import os
from matplotlib import cm 

ABS_PATH = ''
DATA_PATH = os.path.join(ABS_PATH, "data")

all_configs = json.load(open(os.path.join(DATA_PATH,'all_configs.json'),'r'))

RES_PATH = 'results/vary_targetgamma_2runs'

def update_dict(adict, default_dict,fill_na=True):
    #only update the dictionary if key doesn't exist
    # use to fill out the rest of the params we're not interested in
    # Fill NaN value if it exists in another dict
    for k,v in default_dict.items():
        if k not in adict.keys():
            adict.update({k:v})
        if fill_na is True and adict[k] is None:
            adict.update({k:v})
    return adict

def plotmulti_infosys(result_dir, exp_type='vary_betagamma', anchors=[('gamma', 0.01), ('gamma', 0.02)], 
                        x='beta', y='quality', log_flag=False, relative=False):
    respath = glob.glob('%s/*.json' %result_dir)
    resfiles = [i.split('%s/' %result_dir)[1].replace('.json','') for i in respath]

    #fill in other config
    params = {}
    for file in resfiles: 
        params[file] = all_configs[exp_type][file]
    
    colormap = cm.get_cmap('inferno', 10)
    colors = [colormap(i) for i in range(10)]
    plt.gca().set_prop_cycle(plt.rcParams["axes.prop_cycle"] + plt.cycler(marker=list('.s*o^v<>+x')))
    if log_flag: plt.xscale('log')
    for i,anchor in enumerate(anchors):
        results = {}
        for file in resfiles: 
            res = json.load(open(os.path.join(result_dir,'%s.json' %file),'r'))
            results[file] = update_dict(res, params[file])
        # print(results)
        data = []
        for info in results.values():
            if info[anchor[0]]==anchor[1]:
                # if x in info.keys() and y in info.keys():
                if y=='discriminative_pow':
                    data += [(info[x], info[y][0])]
                else:
                    data += [(info[x], info[y])] #TODO: x and y got modified when we come to here some how! (instead of 'beta' it becomes 0.001)
#             print(info)
#         data = [(info[x], info[y]) for info in results.values() if info[anchor[0]]==anchor[1]]
        
        avg_data = []
        y_err = []
        print(y_err)
        for xval,yval in data:
            if relative is True:
                baseline = 0.5
                avg_data += [(xval, np.mean(yval)/baseline)]
            else:
                avg_data += [(xval, np.mean(yval))]
            y_err += [np.std(yval)]

        # plt.errorbar(*zip(*sorted(avg_data)), yerr=y_err, fmt='v', color=colors(i),
        #          ecolor='lightgray', elinewidth=3, capsize=0, label=anchor[1])
        # plt.errorbar(*zip(*sorted(avg_data)), yerr=y_err, elinewidth=3, capsize=0, label=anchor[1] if anchor[1] is not None else 'None')
        plt.plot(*zip(*sorted(avg_data)),label=anchor[1] if anchor[1] is not None else 'None')
                 
    plt.xlabel(pprint[x], fontsize=16)
    plt.ylabel(pprint[y], fontsize=16)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.ylim(bottom=0)
    plt.legend()
    plt.savefig(os.path.join(result_dir, '%s%s.png' %(x,y)), dpi=300)
    # plt.show()
    plt.clf()

BETA = [0.0001, 0.0002, 0.0005, 0.001, 0.002, 0.005, 0.02, 0.05, 0.1, 0.2, 0.5]
GAMMA = [0.0001, 0.0002, 0.0005, 0.001, 0.002, 0.005, 0.02, 0.05, 0.1, 0.2, 0.5]
TARGETING = [None, 'hubs', 'partisanship', 'conservative', 'liberal', 'misinformation']
PHI_LIN = list(range(1,11))
THETA = [1,2,4,6,8,10,12,14]

pprint = {'gamma':'$\gamma$','theta': '$\theta$', 'beta':'$\beta$', 'phi': '$phi$', 
        'quality': 'Relative Average Quality', 'discriminative_pow': 'Discriminative Power', 'diversity': 'Diversity'}
anchors = [('targeting_criterion', val) for val in TARGETING]
plots = [{'exp_type': 'vary_targetgamma', 'anchors': anchors, 'x': 'gamma', 'y':'quality','log_flag':True},
        {'exp_type': 'vary_targetgamma', 'anchors': anchors, 'x': 'gamma', 'y':'discriminative_pow','log_flag':False, 'relative':False},
        {'exp_type': 'vary_targetgamma', 'anchors': anchors, 'x': 'gamma', 'y':'diversity','log_flag':False, 'relative':False},
        ]
# plotmulti_infosys(RES_PATH, exp_type='vary_targetgamma', anchors=anchors, x='gamma', y='quality',log_flag=True)
for plot_spec in plots:
    plotmulti_infosys(RES_PATH, **plot_spec)