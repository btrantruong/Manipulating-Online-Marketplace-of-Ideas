import json
import infosys.utils as utils 
import igraph as ig
import os
import collections
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pickle as pkl
import collections
import sys
from  scipy.stats import entropy
from scipy.special import entr

hub_verbose = utils.read_json_compressed('data/igraph/results.json.gz')
print('')

# import json 
# import os 

# def get_exp_network_map(config_fname, gamma=0.005):
#     exp_configs = json.load(open(config_fname,'r'))
#     EXPS = list(exp_configs['vary_thetaphi'].keys()) #keys are name of exp, format: '{targeting}_{thetaidx}{phiidx}' 

#     # map available network in `vary_targetgamma` corresponding with the exp
#     # networks from `vary_targetgamma` has format: '{targeting}{gamma}'
#     GAMMA = [0.0001, 0.0002, 0.0005, 0.001, 0.002, 0.005, 0.02, 0.05, 0.1, 0.2, 0.5]
#     TARGETING = [None, 'hubs', 'partisanship', 'conservative', 'liberal', 'misinformation']

#     EXP_NETWORK = {}

#     # need to match with default_targeting
#     for exp in EXPS:
#         if 'none' in exp:
#             networkname = '%s%s' %(TARGETING.index(None), GAMMA.index(gamma))
#         else: 
#             networkname = '%s%s' %(TARGETING.index(exp.split('_')[0]), GAMMA.index(gamma))
#         EXP_NETWORK[exp] = networkname

#     return EXP_NETWORK

# gamma=0.005
# config_fname= os.path.join('data', 'all_configs.json')
# exp2network = get_exp_network_map(config_fname, float(gamma))
# print('')