# Code to plot 1 line
from matplotlib import cm 
import matplotlib.pyplot as plt
import numpy as np 
import glob 
import json
import os
import infosys.utils as utils 

ABS_PATH = ''
DATA_PATH = os.path.join(ABS_PATH, "data")

all_configs = json.load(open(os.path.join(DATA_PATH,'all_configs.json'),'r'))

RES_PATH = 'results/vary_thetaphi_1runs'


def update_results(adict, newres_dict):
    measures = ['quality','diversity','discriminative_pow']
    # Append a dict with results from another run
    for m in measures:
        adict[m].extend(newres_dict[m])
    return adict
    
def plotmulti_infosys(result_dir, exp_type='vary_betagamma', anchors=[('gamma', 0.01), ('gamma', 0.02)], 
                        x='beta', y='quality', log_flag=False, relative=True):
    respath = glob.glob('%s/*.json' %result_dir)
    resfiles = [i.split('%s/' %result_dir)[1].replace('.json','') for i in respath]

    fixed_param = None #because we're varying both theta and phi, we need to fix 1 param to draw line plot
    if x == 'theta':
        fixed_param = [('phi',2), ('phi',4), ('phi',8)]
    elif x == 'phi':
        fixed_param = [('theta',2), ('theta',6), ('theta',12)]

    #fill in other config
    params = {}
    for file in resfiles: 
        params[file] = all_configs[exp_type][file]
    
    results = {}
    for file in resfiles: 
        #2run results
        res = json.load(open(os.path.join(result_dir,'%s.json' %file),'r'))
        results[file] = res
        
    for plot_no,fixed in enumerate(fixed_param):
        #plt config
        colormap = cm.get_cmap('inferno', 10)
        colors = [colormap(i) for i in range(10)]
        plt.gca().set_prop_cycle(plt.rcParams["axes.prop_cycle"] + plt.cycler(marker=list('.s*o^v<>+x')))
        if log_flag: plt.xscale('log')
        #get None baseline:
        none_data = []
        for info in results.values():
            if info[anchors[0][0]]==None and info[fixed[0]]==fixed[1]:
                # if x in info.keys() and y in info.keys():
                if y=='discriminative_pow':
                    none_data += [(info[x], info[y][0])]
                else:
                    none_data += [(info[x], info[y])] 
        none_avg = []
        noney_err = []
        for xval,yval in none_data:
            none_avg += [(xval, np.mean(yval))]
            noney_err += [np.std(yval)]
        baseline_x, baseline = zip(*sorted(none_avg))

        for i,anchor in enumerate(anchors):
            data = []
            for info in results.values():
                if info[anchor[0]]==anchor[1] and info[fixed[0]]==fixed[1]:
                    # if x in info.keys() and y in info.keys():
                    if y=='discriminative_pow':
                        data += [(info[x], info[y][0])]
                    else:
                        data += [(info[x], info[y])] 
        
            avg_data = []
            y_err = []
            for xval,yval in data:
                avg_data += [(xval, np.mean(yval))]
                y_err += [np.std(yval)]

            # plt.errorbar(*zip(*sorted(avg_data)), yerr=y_err, fmt='v', color=colors(i),
            #          ecolor='lightgray', elinewidth=3, capsize=0, label=anchor[1])
            # plt.errorbar(*zip(*sorted(avg_data)), yerr=y_err, elinewidth=3, capsize=0, label=anchor[1] if anchor[1] is not None else 'None')
            
            xvals, yvals = zip(*sorted(avg_data))
            y_relative = np.divide(np.array(yvals),np.array(baseline))
            assert baseline_x==xvals
            # xvals = zip
            if relative:
                plt.plot(xvals, y_relative,label=anchor[1])
            else:
                plt.plot(xvals, yvals,label=anchor[1])
            # plt.plot(*zip(*sorted(avg_data)),label=anchor[1])
        
        plt.title('Avg quality Ratio for different strategies (%s=%s)' %(pprint[fixed[0]], fixed[1]) if relative is True else 'Avg quality for different strategies')
        plt.xlabel(pprint[x], fontsize=16)
        plt.ylabel(pprint[y], fontsize=16)
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
        plt.ylim(0.5,2)
        plt.legend()
        plt.savefig(os.path.join(result_dir, '%s%s_%s%s.png' %(x,y, fixed[0], fixed[1])), dpi=300)
        # plt.show()
        plt.clf()

BETA = [0.0001, 0.0002, 0.0005, 0.001, 0.002, 0.005, 0.02, 0.05, 0.1, 0.2, 0.5]
GAMMA = [0.0001, 0.0002, 0.0005, 0.001, 0.002, 0.005, 0.02, 0.05, 0.1, 0.2, 0.5]
TARGETING = [None, 'hubs', 'partisanship', 'conservative', 'liberal', 'misinformation']
THETAPHI_TARGETING = ['hubs', 'partisanship', 'misinformation']
PHI_LIN = list(range(1,11))
THETA = [1,2,4,6,8,10,12,14]

pprint = {'gamma':'$\gamma$','theta': '$\\theta$', 'beta':'$\\beta$', 'phi': '$\phi$', 
        'quality': 'Relative Average Quality', 'discriminative_pow': 'Discriminative Power', 'diversity': 'Diversity'}

anchors = [('targeting_criterion', val) for val in THETAPHI_TARGETING]
plots = [{'exp_type': 'vary_thetaphi', 'anchors': anchors, 'x': 'phi', 'y':'quality','log_flag':True},
        {'exp_type': 'vary_thetaphi', 'anchors': anchors, 'x': 'theta', 'y':'quality','log_flag':True}
        ]
for plot_spec in plots:
    plotmulti_infosys(RES_PATH, **plot_spec)