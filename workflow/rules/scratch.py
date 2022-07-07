import os 
import json 
ABS_PATH = ''
# ABS_PATH = '/N/u/baotruon/Carbonate/marketplace'
DATA_PATH = os.path.join(ABS_PATH, "data")

print(os.getcwd())
exp_configs = json.load(open('data/all_configs.json','r'))
anchor_gamma = 0.001 #change to 0.001
RES_DIR = os.path.join(ABS_PATH, "results", "vary_thetagamma", "gamma%s" %str(anchor_gamma))
EXPS = list([name for name in exp_configs['vary_thetagamma'].keys()])
EXPS = list([name for name in exp_configs['vary_thetagamma'].keys() if 'gamma%s' %anchor_gamma in name])
NAMES = [tuple(expname.split('_')) for expname in EXPS] # turn "07_gamma0.05" to ('07', 'gamma0.05')
exp_nos, gs = zip(*NAMES) #example: exp_nos[i]=00, gs[i]=gamma0.01
print('')