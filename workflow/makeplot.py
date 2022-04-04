# Code to plot 1 line
from matplotlib import cm 

import matplotlib.pyplot as plt
import csv
import numpy as np 
import glob 
import json
import os
from matplotlib import cm
import infosys.utils as utils 
from collections import defaultdict
cmap = cm.get_cmap('inferno', 10)

ABS_PATH = ''
DATA_PATH = os.path.join(ABS_PATH, "data")

all_configs = json.load(open(os.path.join(DATA_PATH,'all_configs.json'),'r'))

RES_PATH = 'results/vary_thetagamma_2runs'
PLOT_PATH = 'results/plots'
result_dir = RES_PATH
exp_type = 'vary_thetagamma'

pprint = {'gamma':'$\\gamma$','theta': '$\\theta$', 'beta':'$\\beta$', 'phi': '$phi$', 
        'quality': 'Relative Average Quality', 'discriminative_pow': 'Discriminative Power', 'diversity': 'Diversity'}
    
BETA = [0.0001, 0.0002, 0.0005, 0.001, 0.002, 0.005, 0.02, 0.05, 0.1, 0.2, 0.5]
GAMMA = [0.0001, 0.0002, 0.0005, 0.001, 0.002, 0.005, 0.02, 0.05, 0.1, 0.2, 0.5]
TARGETING = [None, 'hubs', 'partisanship', 'conservative', 'liberal', 'misinformation']
PHI_LIN = list(range(1,11))
THETA = [1,2,4,6,8,10,12,14]
heatmap_config = {'vary_thetagamma': {'x':'theta', 'y':'gamma', 'xvals':THETA, 'yvals':GAMMA},
'vary_phigamma': {'x':'gamma', 'y':'phi', 'xvals':GAMMA, 'yvals':PHI_LIN},
'vary_betagamma': {'x':'gamma', 'y':'beta', 'xvals':GAMMA, 'yvals':BETA}
}

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


def heatmap_data(result_dir, exp_type='vary_thetagamma', cell_type='quality'):
    #2D array for plotting data 
    respath = glob.glob('%s/*.json' %result_dir)
    resfiles = [i.split('%s/' %result_dir)[1].replace('.json','') for i in respath]

    all_results = [json.load(open(os.path.join(result_dir,'%s.json' %file),'r')) for file in resfiles]

    x = heatmap_config[exp_type]['x']
    y = heatmap_config[exp_type]['y']

    results = defaultdict(lambda: [])
    for yval in heatmap_config[exp_type]['yvals']:
        for xval in heatmap_config[exp_type]['xvals']:
            if cell_type=='discriminative_pow':
                results[yval] += [np.mean(res[cell_type][0]) for res in all_results if res[x]==xval and res[y]==yval]
            else:
                results[yval] += [np.mean(res[cell_type]) for res in all_results if res[x]==xval and res[y]==yval]
            
    data = np.array([row for row in results.values()])
    return data


def lineplot_data(result_dir, config_fpath=None, exp_type='vary_thetagamma', anchors=[('gamma', 0.01), ('gamma', 0.02)], 
                        x='beta', y='quality', relative=False):
    respath = glob.glob('%s/*.json' %result_dir)
    resfiles = [i.split('%s/' %result_dir)[1].replace('.json','') for i in respath]

    if config_fpath is not None:
        #fill in other config
        all_configs = json.load(open(config_fpath,'r'))

        params = {}
        for file in resfiles: 
            params[file] = all_configs[exp_type][file]
    
    multiline_data = []
    multiline_err = []
    for i,anchor in enumerate(anchors):
        results = {}
        for file in resfiles: 
            res = json.load(open(os.path.join(result_dir,'%s.json' %file),'r'))
            results[file] = update_dict(res, params[file])
        data = []
        for info in results.values():
            if info[anchor[0]]==anchor[1]:
                if y=='discriminative_pow':
                    data += [(info[x], info[y][0])] #since discrinminative_pow is a tuple of (tau,p_val)
                else:
                    data += [(info[x], info[y])] 
#         data = [(info[x], info[y]) for info in results.values() if info[anchor[0]]==anchor[1]]
        

        avg_data = []
        y_err = []
        for xval,yval in data:
            if relative is True:
                baseline = 0.5
                avg_data += [(xval, np.mean(yval)/baseline)]
            else:
                avg_data += [(xval, np.mean(yval))]
            y_err += [np.std(yval)]

        multiline_data+= [avg_data] #list of lists, each list is a line
        multiline_err += [y_err]
    return multiline_data, multiline_err


def plotmulti_infosys(ax, data, anchors=[('gamma', 0.01), ('gamma', 0.02)], 
                        x='beta', y='quality', log_flag=False):
    
    markers=list('.s*o^v<>+x')
    for idx,avg_data in enumerate(data):
        anchor = anchors[idx]
        # plt.gca().set_prop_cycle(plt.rcParams["axes.prop_cycle"] + plt.cycler(marker=list('.s*o^v<>+x')))
        if log_flag: ax.set_xscale('log')
        # plt.errorbar(*zip(*sorted(avg_data)), yerr=y_err, elinewidth=3, capsize=0, label=anchor[1] if anchor[1] is not None else 'None')
        ax.plot(*zip(*sorted(avg_data)), label=anchor[1] if anchor[1] is not None else 'None', marker=markers[idx])
    
    ax.set_xlabel(pprint[x])
    ax.set_ylabel(pprint[y])
    # ax.set_ylim(bottom=0)
    ax.legend()
    # plt.savefig(os.path.join(result_dir, '%s%s.png' %(x,y)), dpi=300)
    # # plt.show()
    # plt.clf()
    
anchors = [('theta', val) for val in [1,6,14]]
plots = [{'exp_type': 'vary_thetagamma', 'anchors': anchors, 'x': 'gamma', 'y':'quality'},
        {'exp_type': 'vary_thetagamma', 'anchors': anchors, 'x': 'gamma', 'y':'discriminative_pow'},
        {'exp_type': 'vary_thetagamma', 'anchors': anchors, 'x': 'gamma', 'y':'diversity'},
        ]

# plotmulti_infosys(RES_PATH, exp_type='vary_thetagamma', anchors=anchors, x='gamma', y='quality',log_flag=True)
params = {'axes.labelsize': 10,'axes.titlesize':10,'legend.fontsize': 10, 'xtick.labelsize': 10, 'ytick.labelsize': 10}

plt.rcParams.update(params)
figure = plt.figure(figsize=(10, 10), facecolor='w')

ax1 = figure.add_subplot(321)
ax2 = figure.add_subplot(323)
ax3 = figure.add_subplot(325)

ax4 = figure.add_subplot(322)
ax5 = figure.add_subplot(324)
ax6 = figure.add_subplot(326)

axs = [ax1, ax2, ax3]

for plot_spec,ax in zip(plots,axs):
    line_data, _  = lineplot_data(RES_PATH,config_fpath='data/all_configs.json', **plot_spec)
    plotmulti_infosys(ax, line_data, anchors=anchors, 
                        x='beta', y='quality', log_flag=False)
axs_ = [ax4, ax5, ax6]
maps = [{'exp_type': 'vary_thetagamma', 'x': 'gamma', 'y':'quality'},
        {'exp_type': 'vary_thetagamma', 'x': 'gamma', 'y':'discriminative_pow'},
        {'exp_type': 'vary_thetagamma', 'anchors': anchors, 'x': 'gamma', 'y':'diversity'},
        ]

cells = ['quality', 'discriminative_pow', 'diversity']
for map_spec,ax, cell in zip(maps, axs_, cells): 
    data = heatmap_data(result_dir, exp_type='vary_thetagamma', cell_type=cell)
    utils.draw_heatmap(ax, data, THETA, GAMMA, '$\\theta$', '$\gamma$', cmap, cell, vmax=None, vmin=None)

figure.tight_layout() 
plt.savefig(os.path.join(PLOT_PATH,'thetagamma.png'), dpi=100)
# plt.show()