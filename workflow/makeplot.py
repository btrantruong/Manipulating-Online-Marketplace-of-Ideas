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
RES_PATH = os.path.join(ABS_PATH, "results")

all_configs = json.load(open(os.path.join(DATA_PATH,'all_configs.json'),'r'))
config_fpath = os.path.join(DATA_PATH,'all_configs.json')

PLOT_PATH = 'results/plots'


pprint = {'gamma':'$\\gamma$','theta': '$\\theta$', 'beta':'$\\beta$', 'phi': '$\phi$', 
        'quality': 'Relative Average Quality', 'discriminative_pow': 'Discriminative Power', 'diversity': 'Diversity'}
    
BETA = [0.0001, 0.0002, 0.0005, 0.001, 0.002, 0.005, 0.02, 0.05, 0.1, 0.2, 0.5]
GAMMA = [0.0001, 0.0002, 0.0005, 0.001, 0.002, 0.005, 0.02, 0.05, 0.1, 0.2, 0.5]
TARGETING = [None, 'hubs', 'partisanship', 'conservative', 'liberal', 'misinformation']
PHI_LIN = list(range(1,11))
THETA = [1,2,4,6,8,10,12,14]

heatmap_config = {'vary_thetagamma': {'x':'theta', 'y':'gamma', 'xvals':THETA, 'yvals':GAMMA},
'vary_phigamma': {'x':'phi', 'y':'gamma', 'xvals':PHI_LIN, 'yvals':GAMMA},
'vary_betagamma': {'x':'beta', 'y':'gamma', 'xvals':BETA, 'yvals':GAMMA}
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
    print('Drawing %s plot' %exp_type)
    _, all_results = fill_in_param(config_fpath, exp_type=exp_type)

    x = heatmap_config[exp_type]['x']
    y = heatmap_config[exp_type]['y']

    results = defaultdict(lambda: [])
    # for idx, yval in enumerate(heatmap_config[exp_type]['yvals']):
    #     for xval in heatmap_config[exp_type]['xvals']:
    #         if cell_type=='discriminative_pow':
    #             results[yval] += [np.mean(res[cell_type][0]) for res in all_results if res[x]==xval and res[y]==yval]
    #         else:
    #             results[yval] += [np.mean(res[cell_type]) for res in all_results if res[x]==xval and res[y]==yval]
    
    for idx, yval in enumerate(heatmap_config[exp_type]['yvals']):
        for xval in heatmap_config[exp_type]['xvals']:
            if cell_type=='discriminative_pow':
                vals = [res[cell_type][0] for res in all_results if res[x]==xval and res[y]==yval]
                results[yval] += [np.mean(vals) if len(vals)>0 else 0]
            else:
                vals = [res[cell_type] for res in all_results if res[x]==xval and res[y]==yval]
                results[yval] += [np.mean(vals) if len(vals)>0 else 0]

    data = np.array([row for row in results.values()])
    return data

def update_results(adict, newres_dict):
    measures = ['quality','diversity','discriminative_pow']
    # Append a dict with results from another run
    for m in measures:
        adict[m].extend(newres_dict[m])
    return adict

def fill_in_param(config_fpath, exp_type='vary_betagamma'):
    result_dir = RES_PATH
    res_dirs = [os.path.join(result_dir, i) for i in os.listdir(result_dir) if os.path.isdir(os.path.join(result_dir,i)) and exp_type in i]
    firstrun = res_dirs[0]
    respath = glob.glob('%s/*.json' %firstrun)
    resfiles = [i.split('%s/' %firstrun)[1].replace('.json','') for i in respath]

    #fill in other config
    all_configs = json.load(open(config_fpath,'r'))

    params = {}
    results = {}

    for file in resfiles: 
        if file in all_configs[exp_type].keys():
            params[file] = all_configs[exp_type][file]
            res = json.load(open(os.path.join(firstrun,'%s.json' %file),'r'))
            res = update_dict(res, params[file])
            nth_res = res
            for dir in res_dirs[1:]:
                paths = glob.glob('%s/*.json' %dir)
                nth_resfiles = [i.split('%s/' %dir)[1].replace('.json','') for i in paths]
                if file in nth_resfiles:
                    nth_run = json.load(open(os.path.join(dir,'%s.json' %file),'r'))
                    nth_res = update_results(res,nth_run)
            results[file] = nth_res
    
    all_results = results.values()
    return results, all_results

def lineplot_data(config_fpath=None, exp_type='vary_thetagamma', anchors=[('gamma', 0.01), ('gamma', 0.02)], 
                        x='beta', y='quality', relative=False):
    print('Drawing %s plot' %exp_type)
    results, _ = fill_in_param(config_fpath, exp_type=exp_type)
    
    multiline_data = []
    multiline_err = []
    for i,anchor in enumerate(anchors):
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
        ax.plot(*zip(*sorted(avg_data)), label='%s: %s' %(pprint[anchor[0]],anchor[1]) if anchor[1] is not None else 'None', marker=markers[idx])
    
    ax.set_xlabel(pprint[x])
    ax.set_ylabel(pprint[y])
    ax.legend()

def panel_plot(result_dir, config_fpath=None, exp_type= 'vary_thetagamma'):
    anchor_configs = {
        'vary_thetagamma': [('theta', val) for val in [1,6,14]],
        'vary_phigamma': [('phi', val) for val in [1,5,10]],
        'vary_betagamma': [('beta', val) for val in [0.001,0.05,0.1]]
    }
    xticks = {
        'vary_thetagamma': {'vals': THETA, 'label': pprint['theta']},
        'vary_phigamma': {'vals': PHI_LIN, 'label': pprint['phi']},
        'vary_betagamma': {'vals': BETA, 'label': pprint['beta']},
    }
    measurements  = ['quality', 'diversity', 'discriminative_pow']
    anchors = anchor_configs[exp_type]
    plots = [{'exp_type': exp_type, 'x': 'gamma', 'y': y} for y in measurements]
    lineplots = [{'exp_type': exp_type, 'anchors':anchors, 'x': 'gamma', 'y': y} for y in measurements]


    params = {'axes.labelsize': 10,'axes.titlesize':10,'legend.fontsize': 10, 'xtick.labelsize': 10, 'ytick.labelsize': 10}

    plt.rcParams.update(params)
    figure = plt.figure(figsize=(10, 10), facecolor='w')

    left=[1,3,5]
    right=[2,4,6]

    laxs = [figure.add_subplot(3,2,i) for i in left]

    for plot_specs,ax in zip(lineplots, laxs):
        line_data, _  = lineplot_data(config_fpath, **plot_specs)
        plotmulti_infosys(ax, line_data, anchors=anchors, 
                            x=plot_specs['x'], y=plot_specs['y'], log_flag=True)

    #TODO: Reduce tick size for betagamma
    # if exp_type=='vary_betagamma':
    #     ax.tick_params(axis='x', which='major', labelsize=5)
    #     ax.tick_params(axis='x', which='minor', labelsize=5)

    raxs = [figure.add_subplot(3,2,i) for i in right]
    for map_spec, ax, cell in zip(plots, raxs, measurements): 
        data = heatmap_data(result_dir, exp_type=exp_type, cell_type=cell)
        utils.draw_heatmap(ax, data, xticks[exp_type]['vals'], GAMMA, xticks[exp_type]['label'], pprint['gamma'], cmap, cell, vmax=None, vmin=None)

    figure.tight_layout() 
    plt.savefig(os.path.join(PLOT_PATH,'%s.png' %exp_type), dpi=100)

# panel_plot(RES_PATH, config_fpath, exp_type='vary_phigamma')
# panel_plot(RES_PATH, config_fpath, exp_type='vary_thetagamma')
panel_plot(RES_PATH, config_fpath, exp_type='vary_betagamma')
