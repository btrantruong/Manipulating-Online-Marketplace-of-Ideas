# Code to plot 1 line
# TODO: handle when result files are empty
from matplotlib import cm 

import matplotlib.pyplot as plt
import numpy as np 
import glob 
import json
import os
import sys
from matplotlib import cm
import infosys.utils as utils 
from collections import defaultdict
from infosys.config_values import THETA, GAMMA, PHI_LIN, BETA

""" make a panel - resulting plot has 3 rows, 2 cols
    line plot (left) and heatmap (right) for 3 up to measurements 'quality', 'diversity', 'discriminative_pow' 
"""


pprint = {'gamma':'$\\gamma$','theta': '$\\theta$', 'beta':'$\\beta$', 'phi': '$\phi$', 
        'quality': 'Relative Average Quality', 'discriminative_pow': 'Discriminative Power', 'diversity': 'Diversity'}

def update_results(adict, newres_dict):
    measures = ['quality','diversity','discriminative_pow']
    # Append a dict with results from another run
    for m in measures:
        adict[m].extend(newres_dict[m])
    return adict

def combine_results(res_dir, res_folders, prefix=None):
    # Input: result folder where each .json file contains the results & parameters for an experiment.
    # Structure: dict: {'param': param_val, "quality": [0.11], "diversity": [5.77], "discriminative_pow": [[0.83, 0.0]]}
    # Each measurement is a list of results over multiple runs. 
    # Prefix filters out the exp of interest, e.g: 'None' or 'hubs' exps
    # Output: a dict {exp_name: {dict of measurement}}

    res_paths = [os.path.join(res_dir, f) for f in res_folders]

    run1 = res_paths[0]
    file_paths =  glob.glob('%s/*.json' %run1)
    file_names = [i.split('%s/' %run1)[1].replace('.json','') for i in file_paths]
    if prefix is not None:
        file_names = [f for f in file_names if prefix in f]
    
    all_results = { fname: json.load(open(os.path.join(run1, '%s.json' %fname), 'r')) for fname in file_names}
    
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
        data = val2expname(all_results, all_configs, value = (line_name, line_val), exp_type=exp_type)
        
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

    # plt.gca().set_prop_cycle(plt.rcParams["axes.prop_cycle"] + plt.cycler(marker=list('.s*o^v<>+x')))
   
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

#TODO: update combine_results() for scatter
def plot_scatter(ax, exp_name, data_path, result_path, folders, exp_prefix=None, y_name='quality'):

    lineplot_config = {
        'vary_thetagamma': {'line_name':'theta', 'line_values':[1,6,14], 'x_name':'gamma', 'y_name': y_name},
        'vary_phigamma': {'line_name':'phi', 'line_values':[1,5,10], 'x_name':'gamma', 'y_name': y_name},
        'vary_betagamma': {'line_name':'beta', 'line_values':[0.001,0.05,0.1], 'x_name':'gamma', 'y_name': y_name}
    }
    config = lineplot_config[exp_name]

    all_configs = json.load(open(os.path.join(data_path,'all_configs.json'),'r'))
    all_results = combine_results(result_path, folders, prefix=exp_prefix)

    multiline_data = lineplot_data(all_results, all_configs, exp_type=exp_name, **utils.remove_illegal_kwargs(config, lineplot_data))

    draw_lines(ax, multiline_data, **utils.remove_illegal_kwargs(config, draw_lines))
    # plt.tight_layout()
    return

def heatmap_data(result_path, folders, exp_prefix=None, cell_type='quality', x_name='theta', y_name='gamma', xvals =THETA, yvals=GAMMA):
    # all_results: a dict {exp_name: {dict of measurement}}

    all_results = combine_results(result_path, folders, prefix=exp_prefix)

    results = defaultdict(lambda: []) #each key is a row of yvals. to be converted to a 2-D array later
    
    for idx, yval in enumerate(yvals):  
        for xval in xvals:
            cell_res = [res for res in all_results.values() if res[x_name]==xval and res[y_name]==yval] #result for one exp
            # Handle the cells (param combo) for which we don't have results yet
            if len(cell_res)==1:
                exp_res, = cell_res
                #vals is list of results over multiple runs
                vals = exp_res[cell_type] if cell_type!='discriminative_pow' else exp_res[cell_type][0] 
            else:
                vals =[0] #if we don't have results yet

            results[yval] += [np.mean(vals) if len(vals)>0 else 0] #Fill 0 for exps that haven't finished running yet

    data = np.array([row for row in results.values()])
    return data


def plot_heatmap(ax, exp_name, result_path, folders, exp_prefix=None, title=None, cell_type='quality', cbar_max=1, cbar_min=0):
    cmap = cm.get_cmap('inferno', 10)
    heatmap_config = {'vary_thetagamma': {'x_name':'theta', 'y_name':'gamma', 'xvals':THETA, 'yvals':GAMMA},
                        'vary_phigamma': {'x_name':'phi', 'y_name':'gamma', 'xvals':PHI_LIN, 'yvals':GAMMA},
                        'vary_betagamma': {'x_name':'beta', 'y_name':'gamma', 'xvals':BETA, 'yvals':GAMMA},
                        'vary_thetaphi': {'x_name':'theta', 'y_name':'phi', 'xvals':THETA, 'yvals':PHI_LIN}
                        }
    config = heatmap_config[exp_name]
    data = heatmap_data(result_path, folders= folders, exp_prefix=exp_prefix, cell_type=cell_type, **config)
    
    
    xticks = heatmap_config[exp_name]['xvals']
    yticks = heatmap_config[exp_name]['yvals']
    xlabel = pprint[heatmap_config[exp_name]['x_name']] #pretty print
    ylabel = pprint[heatmap_config[exp_name]['y_name']]
    if title is None:
        title = pprint[cell_type]
    utils.draw_heatmap(ax, data, xticks, yticks, xlabel, ylabel, cmap, title, vmax=cbar_max, vmin=cbar_min)
    # plt.tight_layout()
    return

def plot_panel(exp_name, data_path, results_path, folders, measurements  = ['quality', 'diversity', 'discriminative_pow'], plot_fpath=None):
    # line plot (left) and heatmap (right) for 3 up to measurements 'quality', 'diversity', 'discriminative_pow'
    # resulting plot has 3 rows, 2 cols
    params = {'axes.labelsize': 10,'axes.titlesize':10,'legend.fontsize': 10, 'xtick.labelsize': 10, 'ytick.labelsize': 10}

    plt.rcParams.update(params)

    nrows = len(measurements)
    ncols = 2 #2 plots on each row

    figure = plt.figure(figsize=(nrows*6, ncols*4), facecolor='w')

    left = range(1,nrows*ncols, ncols) # left=[1,3,5]
    right = range(2,nrows*ncols+1, ncols) # right=[2,4,6]
    laxs = [figure.add_subplot(nrows, ncols, i) for i in left]
    
    for measure, ax in zip(measurements, laxs):
        plot_scatter(ax, exp_name, data_path, results_path, folders, y_name=measure)

    raxs = [figure.add_subplot(nrows, ncols, i) for i in right]
    
    for measure, ax in zip(measurements, raxs):
        plot_heatmap(ax, exp_name, RES_PATH, folders, cell_type=measure)

    figure.tight_layout()
    if plot_fpath is not None:
        plt.savefig(os.path.join(plot_fpath), dpi=200)
    else:
        figure.show()
    return 

if __name__=="__main__":
    logger = utils.get_logger(__name__)
    logger.info('WORKING DIR: %s' %(os.getcwd()))
   
    # LOCAL 
    # ABS_PATH = ''
    # exp_name=sys.argv[1]
    # plot_folder=sys.argv[4]
    
    ABS_PATH = '/N/slate/baotruon/marketplace'
    DATA_PATH = os.path.join(ABS_PATH, "data")
    RES_PATH = os.path.join(ABS_PATH, "results")

    folders = ['vary_thetagamma_2runs', 'vary_thetagamma_3runs']
    exp_name = 'vary_thetagamma'

    PLOT_DIR = os.path.join(ABS_PATH,'plots',exp_name)
    utils.make_sure_dir_exists(PLOT_DIR, '')
    plot_fpath = os.path.join(PLOT_DIR, 'panel.png')

    plot_panel(exp_name, DATA_PATH, RES_PATH, folders, measurements  = ['quality', 'diversity'], plot_fpath=plot_fpath)

    
    # Single plot:
    # figure, ax = plt.subplots(figsize=(10, 6), facecolor='w')
    # plot_scatter(ax, exp_name, DATA_PATH, RES_PATH, folders)
    # plot_heatmap(ax, exp_name, RES_PATH, folders, cell_type='quality')