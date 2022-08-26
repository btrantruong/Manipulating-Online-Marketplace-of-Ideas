import infosys.utils as utils
import infosys.config_values as configs
import os
### Varying thetaphi on networks of different targeting strategies
import json 

ABS_PATH = ''
DATA_PATH = os.path.join(ABS_PATH, "data")
CONFIG_PATH = os.path.join(ABS_PATH, "data_rhoepsilon")

config_fname = os.path.join(ABS_PATH, "data_rhoepsilon", 'all_configs.json')
exp_type = 'compare_strategies'
vary_params = "vary_network"
STRATEGIES = configs.COMPARE_TARGETING
# exp_no is the same as network name (unique network config)
all_networks = json.load(open(config_fname,'r'))[vary_params]

COMPARE_EXPS = {exp: params for exp, params in all_networks.items() if params['targeting_criterion'] in STRATEGIES}
EXPS = list(COMPARE_EXPS.keys())
sim_num = 1
mode='igraph'
print('')