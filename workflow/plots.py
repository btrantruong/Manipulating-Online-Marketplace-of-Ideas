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
from make_exp_config import THETA, GAMMA, PHI_LIN, BETA
cmap = cm.get_cmap('inferno', 10)

pprint = {'gamma':'$\\gamma$','theta': '$\\theta$', 'beta':'$\\beta$', 'phi': '$\phi$', 
        'quality': 'Relative Average Quality', 'discriminative_pow': 'Discriminative Power', 'diversity': 'Diversity'}

def update_results(adict, newres_dict):
    measures = ['quality','diversity','discriminative_pow']
    # Append a dict with results from another run
    for m in measures:
        adict[m].extend(newres_dict[m])
    return adict

def combine_results(res_dir, res_folders):
    # Input: result folder where each .json file contains the results & parameters for an experiment.
    # Structure: dict: {'param': param_val, "quality": [0.11], "diversity": [5.77], "discriminative_pow": [[0.83, 0.0]]}
    # Each measurement is a list of results over multiple runs. 
    # Output: a dict {exp_name: {dict of measurement}}

    res_paths = [os.path.join(res_dir, f) for f in res_folders]

    run1 = res_paths[0]
    file_paths =  glob.glob('%s/*.json' %run1)
    file_names = [i.split('%s/' %run1)[1].replace('.json','') for i in file_paths]
    res = [json.load(open(respath,'r')) for respath in file_paths]
    all_results = { expname: res for expname, res in zip(file_names, res)}
    
    for expname, results in all_results.items():
        for dir_path in res_paths[1:]:
            path = os.path.join(dir_path, '%s.json' %expname)
            if utils.make_sure_file_exists(path):
                nth_run = json.load(open(path,'r'))
                all_results[expname] = update_results(all_results[expname],nth_run)

    return all_results


def val2expname(all_results, all_configs, value = ('theta', 1), exp_type='vary_thetagamma'):
    #TODO: Might not need this later if we rewrite func to make config
    # return parameter and results data 
    # get exps whose parameter matches a specific value, 

    config = all_configs[exp_type]
    param, val = value
    results = []
    
    for expname,params in config.items():
        if params[param]==val: 
            res = all_results[expname]
            results += [utils.update_dict(res, params)] #fill in missing params with config
    return results


def lineplot_data(all_results, all_configs, exp_type='vary_thetagamma', line_name='gamma', line_values=[0.01, 0.02], 
                    x_name='beta', y_name='quality'):

    assert (line_name in exp_type) and (x_name in exp_type) 
    multiline_data = [] #list of tuple, data=[(x1,y1, err2), (x2,y2, err2)] - y is the average over multiple runs 

    #TODO: Relative data compared to targeting 
    for line_val in line_values:
        data = val2expname(all_results, all_configs, value = (line_name, line_val), exp_paramstype=exp_type)
        
        x = [results[x_name] for results in data] #array of 
        if y_name =='discriminative_pow':
            y = [results[y_name][0] for results in data] #since discrinminative_pow is a tuple of (tau,p_val)
        else:
            y = [results[y_name] for results in data]
        

        y_avg = [np.mean(yval) for yval in y]
        y_err = [np.std(yval) for yval in y]

        x_y_err = zip(*sorted(zip(x, y_avg, y_err))) # sort data based on x, results in a zip object

        multiline_data += [x_y_err] 
    
    return multiline_data


def draw_lines(ax, data, line_values, line_name='beta',x_name='beta', y_name='quality', log_x=True):
    # Input: data=[(x1,y1, err2), (x2,y2, err2)], line_name='beta', line_value=[b1, b2]
    # Data: list of zip objects 
    assert len(data)==len(line_values)

    markers=list('.s*o^v<>+x')
    if log_x is True: ax.set_xscale('log')

    for idx, linedata in enumerate(data):
        x, y, y_err = linedata
        #TODO: simplify pprint
        ax.plot(x,y, marker=markers[idx], label='%s: %s' %(pprint[line_name], line_values[idx]) if line_values[idx] is not None else 'None')
        ax.fill_between(x, np.subtract(np.array(y), np.array(y_err)), np.add(np.array(y), np.array(y_err)), alpha=0.3)

        ax.set_xlabel(pprint[x_name])
        ax.set_ylabel(pprint[y_name])
        ax.legend()
    
    return 


def plot_scatter(data_path, result_path, plot_specs):
    folders = plot_specs['folders']
    all_configs = json.load(open(os.path.join(data_path,'all_configs.json'),'r'))
    all_results = combine_results(result_path, folders)

    params = {'axes.labelsize': 10,'axes.titlesize':10,'legend.fontsize': 10, 'xtick.labelsize': 10, 'ytick.labelsize': 10}

    plt.rcParams.update(params)
    plt.gca().set_prop_cycle(plt.rcParams["axes.prop_cycle"] + plt.cycler(marker=list('.s*o^v<>+x')))
    figure, ax = plt.subplots(figsize=(10, 10), facecolor='w')

    multiline_data = lineplot_data(all_results, all_configs, **utils.remove_illegal_kwargs(plot_specs, lineplot_data))

    draw_lines(ax, multiline_data, **utils.remove_illegal_kwargs(plot_specs, draw_lines))


def heatmap_data(result_path, folders, cell_type='quality', x_name='theta', y_name='gamma', xvals =THETA, yvals=GAMMA):
    # all_results: a dict {exp_name: {dict of measurement}}

    all_results = combine_results(result_path, folders)

    results = defaultdict(lambda: []) #each key is a row of yvals. to be converted to a 2-D array later
    
    for idx, yval in enumerate(yvals):  
        for xval in xvals:
            exp_res  = [res for res in all_results.values() if res[x_name]==xval and res[y_name]==yval][0] #result for one exp
            
            if cell_type=='discriminative_pow':
                vals = exp_res[cell_type][0] #list of results over multiple runs
            else:
                vals = exp_res[cell_type]
            
            results[yval] += [np.mean(vals) if len(vals)>0 else 0] #Fill 0 for exps that haven't finished running yet

    data = np.array([row for row in results.values()])
    return data


def plot_heatmap(ax, exp_name, result_path, folders, cell_type='quality'):
    heatmap_config = {'vary_thetagamma': {'x_name':'theta', 'y_name':'gamma', 'xvals':THETA, 'yvals':GAMMA},
                        'vary_phigamma': {'x_name':'phi', 'y_name':'gamma', 'xvals':PHI_LIN, 'yvals':GAMMA},
                        'vary_betagamma': {'x_name':'beta', 'y_name':'gamma', 'xvals':BETA, 'yvals':GAMMA}
                        }
    config = heatmap_config[exp_name]
    data = heatmap_data(result_path, folders= folders, cell_type=cell_type, **config)
    
    
    xticks = heatmap_config[exp_name]['xvals']
    yticks = heatmap_config[exp_name]['yvals']
    xlabel = pprint[heatmap_config[exp_name]['x_name']] #pretty print
    ylabel = pprint[heatmap_config[exp_name]['y_name']]
    title = pprint[cell_type]
    utils.draw_heatmap(ax, data, xticks, yticks, xlabel, ylabel, cmap, title, vmax=None, vmin=None)
    return


ABS_PATH = ''
DATA_PATH = os.path.join(ABS_PATH, "data")
RES_PATH = os.path.join(ABS_PATH, "results")

lineplot_config = {
    'vary_thetagamma': 
    {   'folders':['vary_thetagamma_2runs', 'vary_thetagamma_3runs'],
        'exp_type':'vary_thetagamma', 'line_name':'theta', 'line_values':[1,6,14], 'x_name':'gamma', 'y_name':'quality' }
}



# heatmap_config = {'vary_thetagamma': {'x_name':'theta', 'y_name':'gamma', 'xvals':THETA, 'yvals':GAMMA},
# 'vary_phigamma': {'x_name':'phi', 'y_name':'gamma', 'xvals':PHI_LIN, 'yvals':GAMMA},
# 'vary_betagamma': {'x_name':'beta', 'y_name':'gamma', 'xvals':BETA, 'yvals':GAMMA}
# }

# figure, ax = plt.subplots(figsize=(10, 10), facecolor='w')

# xticks = {
#         'vary_thetagamma': {'vals': THETA, 'label': pprint['theta']},
#         'vary_phigamma': {'vals': PHI_LIN, 'label': pprint['phi']},
#         'vary_betagamma': {'vals': BETA, 'label': pprint['beta']},
#     }

# data = heatmap_data(RES_PATH, folders= ['vary_thetagamma_2runs', 'vary_thetagamma_3runs'], cell_type='quality', x_name='theta', y_name='gamma', xvals =THETA, yvals=GAMMA)
# xticks = heatmap_config['vary_thetagamma']['xvals']
# yticks = heatmap_config['vary_thetagamma']['yvals']
# xlabel = pprint['theta'] #pprint xname
# ylabel = pprint['gamma'] #pprint xname
# utils.draw_heatmap(ax, data, xticks, yticks, xlabel, ylabel, cmap, 'quality', vmax=None, vmin=None)


# print('')