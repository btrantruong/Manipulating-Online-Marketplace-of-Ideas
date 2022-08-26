import os 
import json 
import infosys.utils as utils 
import infosys.config_values as configs
ABS_PATH = ''
CONFIG_PATH = os.path.join(ABS_PATH, "config_final")
DATA_PATH = os.path.join(ABS_PATH, "data")


config_fname = os.path.join(CONFIG_PATH, 'all_configs.json')
exp_type = "vary_beta"
# get network names corresponding to the strategy
EXPS = json.load(open(config_fname,'r'))[exp_type]

EXP_NOS = list(EXPS.keys())
EXP2NET = {exp_name: utils.netconfig2netname(config_fname, net_cf) for exp_name, net_cf in EXPS.items()}
sim_num = 2
mode='igraph'