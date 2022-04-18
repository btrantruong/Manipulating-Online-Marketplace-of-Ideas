""" Config for the first set of exps (vary phi&gamma; vary beta&gamma, vary theta&gamma)"""
import os
print(os.getcwd())
import infosys.utils as utils

import numpy as np 
import os 
import json 


# ABS_PATH = ''
ABS_PATH = '/N/slate/baotruon/marketplace'
DATA_PATH = os.path.join(ABS_PATH, "data")
follower_network = 'follower_network.gml'
mode = 'igraph'

#Default:alpha (15), beta (0.01), gamma (0.001), phi (1), theta (1)

BETA = [0.0001, 0.0002, 0.0005, 0.001, 0.002, 0.005, 0.02, 0.05, 0.1, 0.2, 0.5]
GAMMA = [0.0001, 0.0002, 0.0005, 0.001, 0.002, 0.005, 0.02, 0.05, 0.1, 0.2, 0.5]
TARGETING = [None, 'hubs', 'partisanship', 'conservative', 'liberal', 'misinformation']
PHI_LIN = list(range(1,11))
THETA = [1,2,4,6,8,10,12,14]
# DEBUG
# BETA = [0.1, 0.02]
# GAMMA = [0.1, 0.02]
# PHI_LIN = list(range(1,3))
# TARGETING = [None, 'hubs']
# THETA = [2,8]
#!TODO: Change back epsilon in default params! 

# PHI_LOG = [2,4,8,16,32]

# default_infosys = {
#     'trackmeme': True,
#     'verbose': False,
#     'epsilon': 0.01,
#     'mu': 0.5,
#     'phi': 1,
#     'alpha': 15,
#     'theta': 1
# }

all_exps = {}
## DEFAULT 
default_infosys = {
    'trackmeme': True,
    'verbose': False,
    'epsilon': 0.001,
    'mu': 0.5,
    'phi': 1,
    'alpha': 15,
    'theta': 1
}

default_net = {'verbose':False, 'targeting_criterion':None, 'human_network': follower_network, 'beta': 0.01, 'gamma': 0.001}

#gamma is 0.01 for the range in which targeting has some effect
default_targeting = {'verbose':False, 'targeting_criterion':None, 'human_network': follower_network, 'beta': 0.01, 'gamma': 0.01}

#DEBUG
# default_net = {'verbose':False, 'targeting_criterion':None, "human_network": None, "n_humans": 10}


def update_dict_with_default(adict, default_dict):
    #only update the dictionary if key doesn't exist
    # use to fill out the rest of the params we're not interested in

    for k,v in default_dict.items():
        if k not in adict.keys():
            adict.update({k:v})
    return adict
    
def make_exps():
    # Varying beta gamma: (use to init net)
    all_exps["vary_betagamma"] = {}
    for idx, beta in enumerate(BETA):
        for jdx,gamma in enumerate(GAMMA):
            cf = {'beta': beta, 'gamma':gamma}
            config = update_dict_with_default(cf, default_net)
            if beta ==0.02:
                config_name = 'gamma%s' %gamma
            else:
                config_name = '%s%s' %(idx,jdx)
            all_exps["vary_betagamma"][config_name] = config
            
            if utils.make_sure_dir_exists(DATA_PATH, 'vary_betagamma'):
                fp = os.path.join(DATA_PATH, 'vary_betagamma','%s.json' %config_name)
                json.dump(config,open(fp,'w'))

        #Add an additional default file for info sys
        fp = os.path.join(DATA_PATH, 'vary_betagamma','default_infosys.json')
        json.dump(default_infosys,open(fp,'w'))


    all_exps["vary_targetgamma"] = {}
    for idx, target in enumerate(TARGETING):
        for jdx,gamma in enumerate(GAMMA):
            cf = {'targeting_criterion': target, 'gamma':gamma}
            config = update_dict_with_default(cf, default_net)

            if target is None and gamma==0.001:
                config_name = 'default'
            else:
                config_name = '%s%s' %(idx,jdx)
            all_exps["vary_targetgamma"][config_name] = config
            
            if utils.make_sure_dir_exists(DATA_PATH, 'vary_targetgamma'):
                fp = os.path.join(DATA_PATH, 'vary_targetgamma','%s.json' %config_name)
                json.dump(config,open(fp,'w'))

        #Add an additional default file for info sys
        fp = os.path.join(DATA_PATH, 'vary_targetgamma','default_infosys.json')
        json.dump(default_infosys,open(fp,'w'))


    #vary theta & phi for each targeting strategy
    all_exps["vary_thetaphi"] = {}
    for idx, target in enumerate(TARGETING):
        for jdx,theta in enumerate(THETA):
            for kdx,phi in enumerate(PHI_LIN):
                cf = {'targeting_criterion': target, 'theta':theta, 'phi':phi}
                config = update_dict_with_default(cf, default_targeting)

                config_name = '%s_%s%s' %(target,jdx, kdx) if target is not None else 'none_%s%s' %(jdx, kdx)
                all_exps["vary_thetaphi"][config_name] = config
                
                if utils.make_sure_dir_exists(DATA_PATH, 'vary_thetaphi'):
                    fp = os.path.join(DATA_PATH, 'vary_thetaphi','%s.json' %config_name)
                    json.dump(config,open(fp,'w'))

        #Add an additional default file for info sys
        fp = os.path.join(DATA_PATH, 'vary_thetaphi','default_infosys.json')
        json.dump(default_infosys,open(fp,'w'))


    #Varying phi gamma:
    all_exps["vary_phigamma"] = {}
    for idx, phi in enumerate(PHI_LIN):
        for jdx,gamma in enumerate(GAMMA):
            cf = {'phi': phi, 'gamma':gamma, 'graph_gml': 'network_gamma%s.gml' %gamma}
            config = update_dict_with_default(cf, default_infosys)
            
            config_name = '{}{}_gamma{}'.format(idx,jdx, gamma)
            all_exps["vary_phigamma"][config_name] = config
            
            if utils.make_sure_dir_exists(DATA_PATH, 'vary_phigamma'):
                fp = os.path.join(DATA_PATH, 'vary_phigamma','%s.json' %config_name)
                json.dump(config,open(fp,'w'))

    #Varying theta gamma:
    all_exps["vary_thetagamma"] = {}
    for idx, theta in enumerate(THETA):
        for jdx,gamma in enumerate(GAMMA):
            cf = {'theta':theta, 'gamma':gamma, 'graph_gml': 'network_gamma%s.gml' %gamma}
            config = update_dict_with_default(cf, default_infosys)
            
            config_name = '{}{}_gamma{}'.format(idx,jdx, gamma)
            all_exps["vary_thetagamma"][config_name] = config
            
            if utils.make_sure_dir_exists(DATA_PATH, 'vary_thetagamma'):
                fp = os.path.join(DATA_PATH, 'vary_thetagamma','%s.json' %config_name)
                json.dump(config,open(fp,'w'))


    fp = os.path.join(DATA_PATH, 'all_configs.json')
    json.dump(all_exps,open(fp,'w'))

if __name__=='__main__':
    make_exps()
