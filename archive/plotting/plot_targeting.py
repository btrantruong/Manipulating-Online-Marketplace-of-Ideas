from matplotlib import cm 
import gzip
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
'vary_betagamma': {'x':'beta', 'y':'gamma', 'xvals':BETA, 'yvals':GAMMA},
'vary_thetaphi': {'x':'theta', 'y':'phi', 'xvals':THETA, 'yvals':PHI_LIN}
}

xticks = {
        'vary_thetagamma': {'vals': THETA, 'label': pprint['theta']},
        'vary_phigamma': {'vals': PHI_LIN, 'label': pprint['phi']},
        'vary_betagamma': {'vals': BETA, 'label': pprint['beta']},
        'vary_thetaphi': {'vals': THETA, 'label': pprint['theta']},
    }

def read_raw_data(result_dir, exp_type='vary_thetaphi', file_prefix='none'):
    #prefix: the targeting strategy, used to filter results specific to that targeting strategy 
    res_dirs = [os.path.join(result_dir, i) for i in os.listdir(result_dir) if os.path.isdir(os.path.join(result_dir,i)) and exp_type in i]
    firstrun=res_dirs[0]
    print(res_dirs)
    respath = glob.glob('%s/%s*.json' %(firstrun, file_prefix))
    resfiles = [i.split('%s/' %firstrun)[1].replace('.json','') for i in respath]
    print(resfiles)
    #fill in other config
    all_configs = json.load(open(config_fpath,'r'))

    params = {}
    results = {}
    #TODO: simplify this!! 
    for file in resfiles: 
    #     print(file)
        if file in all_configs[exp_type].keys():
            params[file] = all_configs[exp_type][file]
#             print(params)
            fpath = os.path.join(firstrun,'%s.json' %file)
            res = json.load(open(fpath,'r'))

            if res is not None:
                res = utils.update_dict(res, params[file])

                results[file] = res

    all_results = results.values()
    return all_results, results


def get_heatmap_data(all_results, exp_type='vary_thetaphi', cell_type='quality'):
#     results: dict of exp_name - {dict of params + list of qualities across runs}

    x = heatmap_config[exp_type]['x']
    y = heatmap_config[exp_type]['y']

    results = defaultdict(lambda: [])
    for idx, yval in enumerate(heatmap_config[exp_type]['yvals']):
        for xval in heatmap_config[exp_type]['xvals']:
            if cell_type=='discriminative_pow':
                #Fill 0 for exps that haven't finished running yet
                vals = [res[cell_type][0] for res in all_results if res[x]==xval and res[y]==yval]
                results[yval] += [np.mean(vals) if len(vals)>0 else 0] #change else back to 0
            else:
                vals = [res[cell_type] for res in all_results if res[x]==xval and res[y]==yval]
                results[yval] += [np.mean(vals) if len(vals)>0 else 0]

    data = np.array([row for row in results.values()])
    return data


def compare_targeting_heatmap(exp_type='vary_thetaphi', cell_type='quality', prefixes=['none','misinformation']):
    plt.clf()
    figure, (ax1, ax2) = plt.subplots(1,2, figsize=(10, 5), facecolor='w')
    for ax, prefix in zip([ax1,ax2], prefixes):
        _, all_results = read_raw_data(RES_PATH, exp_type=exp_type, file_prefix=prefix)
        data= get_heatmap_data(all_results, exp_type=exp_type, cell_type=cell_type)
        utils.draw_heatmap(ax, data, xticks[exp_type]['vals'], PHI_LIN, xticks[exp_type]['label'], pprint['phi'], cmap, cell_type, vmax=None, vmin=None)
        ax.set_title('%s targeting' %prefix)
    figure.tight_layout()
    if utils.make_sure_dir_exists(RES_PATH, 'plots'):
        plt.savefig(os.path.join(RES_PATH, 'plots', '%s%s_.png' %(prefixes[0], prefixes[1])), dpi=300)
    plt.show()

compare_targeting_heatmap(exp_type='vary_thetaphi', cell_type='quality', prefixes=['none','misinformation'])