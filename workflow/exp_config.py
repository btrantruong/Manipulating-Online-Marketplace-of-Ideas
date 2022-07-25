""" Config for the first set of exps (vary phi&gamma; vary beta&gamma, vary theta&gamma)"""
import os
print(os.getcwd())
import infosys.utils as utils
import infosys.config_values as configs
import numpy as np 
import os 
import json 

#DEBUG
# ABS_PATH = ''
# DATA_PATH = os.path.join(ABS_PATH, "data_")

ABS_PATH = '/N/slate/baotruon/marketplace'
DATA_PATH = os.path.join(ABS_PATH, "data")

all_exps = {}

def make_exps():
    # Varying beta gamma target: (use to init net)
    all_exps["vary_network"] = {}
    
    for idx, beta in enumerate(configs.BETA):
        for jdx,gamma in enumerate(configs.GAMMA):
            for kdx,target in enumerate(configs.TARGETING):
                cf = {'beta': beta, 'gamma':gamma, 'targeting_criterion': target}
                config = utils.update_dict(cf, configs.default_net)
                
                config_name = '%s%s%s' %(idx,jdx, kdx)
                all_exps["vary_network"][config_name] = config
                if utils.make_sure_dir_exists(DATA_PATH, 'vary_network'):
                    fp = os.path.join(DATA_PATH, 'vary_network','%s.json' %config_name)
                    json.dump(config,open(fp,'w'))
    assert len(all_exps["vary_network"]) == len(configs.BETA) * len(configs.GAMMA)*len(configs.TARGETING)


    #compare strategies
    all_exps["compare_strategies"] = {}
    for idx, strategy in enumerate(configs.COMPARE_TARGETING):
        cf = {'beta':configs.DEFAULT_BETA, 'gamma':configs.DEFAULT_GAMMA, 'targeting_criterion': strategy}
        config = utils.update_dict(cf, configs.default_net)

        config_name = '%s' %str(strategy)
        all_exps["compare_strategies"][config_name] = config
        
        if utils.make_sure_dir_exists(DATA_PATH, 'compare_strategies'):
            fp = os.path.join(DATA_PATH, 'compare_strategies','%s.json' %config_name)
            json.dump(config,open(fp,'w'))


    #vary beta & gamma
    all_exps["vary_betagamma"] = {}
    for idx,beta in enumerate(configs.BETA):
        for jdx,gamma in enumerate(configs.GAMMA):
            cf = {'beta':beta, 'gamma':gamma, 'targeting_criterion': configs.DEFAULT_STRATEGY}
            config = utils.update_dict(cf, configs.default_infosys)

            config_name = '%s%s' %(idx,jdx)
            all_exps["vary_betagamma"][config_name] = config
            
            if utils.make_sure_dir_exists(DATA_PATH, 'vary_betagamma'):
                fp = os.path.join(DATA_PATH, 'vary_betagamma','%s.json' %config_name)
                json.dump(config,open(fp,'w'))

    #vary theta & phi
    all_exps["vary_thetaphi"] = {}
    for idx,theta in enumerate(configs.THETA):
        for jdx,phi in enumerate(configs.PHI_LIN):
            cf = {'theta':theta, 'phi':phi}
            config = utils.update_dict(cf, configs.default_infosys)

            config_name = '%s%s' %(idx,jdx)
            all_exps["vary_thetaphi"][config_name] = config
            
            if utils.make_sure_dir_exists(DATA_PATH, 'vary_thetaphi'):
                fp = os.path.join(DATA_PATH, 'vary_thetaphi','%s.json' %config_name)
                json.dump(config,open(fp,'w'))


    #Varying phi gamma:
    all_exps["vary_phigamma"] = {}
    for idx, phi in enumerate(configs.PHI_LIN):
        for jdx,gamma in enumerate(configs.GAMMA):
            cf = {'phi': phi, 'gamma':gamma}
            config = utils.update_dict(cf, configs.default_infosys)
            
            config_name = '%s%s' %(idx,jdx)
            all_exps["vary_phigamma"][config_name] = config
            
            if utils.make_sure_dir_exists(DATA_PATH, 'vary_phigamma'):
                fp = os.path.join(DATA_PATH, 'vary_phigamma','%s.json' %config_name)
                json.dump(config,open(fp,'w'))


    #Varying theta gamma:
    all_exps["vary_thetagamma"] = {}
    for idx, theta in enumerate(configs.THETA):
        for jdx,gamma in enumerate(configs.GAMMA):
            cf = {'theta':theta, 'gamma':gamma}
            config = utils.update_dict(cf, configs.default_infosys)
            
            config_name = '%s%s' %(idx,jdx)
            all_exps["vary_thetagamma"][config_name] = config
            
            if utils.make_sure_dir_exists(DATA_PATH, 'vary_thetagamma'):
                fp = os.path.join(DATA_PATH, 'vary_thetagamma','%s.json' %config_name)
                json.dump(config,open(fp,'w'))


    fp = os.path.join(DATA_PATH, 'all_configs.json')
    json.dump(all_exps,open(fp,'w'))

if __name__=='__main__':
    make_exps()
