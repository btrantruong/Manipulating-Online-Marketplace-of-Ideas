""" Config for the first set of exps (vary phi&gamma; vary beta&gamma, vary theta&gamma)"""
import os
print(os.getcwd())
import infosys.utils as utils
import infosys.final_configs as configs
import numpy as np 
import os 
import json 

def make_exps(saving_dir, default_net_config, default_infosys_config):
    all_exps = {}

    # Varying beta gamma target: (use to init net)
    all_exps["vary_network"] = {}
    
    for idx, beta in enumerate(configs.BETA):
        for jdx,gamma in enumerate(configs.GAMMA):
            for kdx,target in enumerate(configs.TARGETING):
                cf = {'beta': beta, 'gamma':gamma, 'targeting_criterion': target}
                config = utils.update_dict(cf, default_net_config)
                config = utils.update_dict(config, default_infosys_config)

                config_name = f'{idx}{jdx}{kdx}'
                all_exps["vary_network"][config_name] = config
                if utils.make_sure_dir_exists(saving_dir, 'vary_network'):
                    fp = os.path.join(saving_dir, 'vary_network',f'{config_name}.json')
                    json.dump(config,open(fp,'w'))
    assert len(all_exps["vary_network"]) == len(configs.BETA) * len(configs.GAMMA)*len(configs.TARGETING)


    #compare strategies
    all_exps["compare_strategies"] = {}
    for idx, strategy in enumerate(configs.TARGETING):
        cf = {'beta':configs.DEFAULT_BETA, 'gamma':configs.DEFAULT_GAMMA, 'targeting_criterion': strategy}
        config = utils.update_dict(cf, default_net_config)

        config_name = f'{str(strategy)}'
        all_exps["compare_strategies"][config_name] = config
        
        if utils.make_sure_dir_exists(saving_dir, 'compare_strategies'):
            fp = os.path.join(saving_dir, 'compare_strategies', f'{config_name}.json')
            json.dump(config,open(fp,'w'))


    #vary beta & gamma, keep constant targeting strategy 
    all_exps["vary_betagamma"] = {}
    for idx,beta in enumerate(configs.BETA):
        for jdx,gamma in enumerate(configs.GAMMA):
            cf = {'beta':beta, 'gamma':gamma, 'targeting_criterion': configs.DEFAULT_STRATEGY}
            config = utils.update_dict(cf, default_infosys_config)

            config_name = f'{idx}{jdx}'
            all_exps["vary_betagamma"][config_name] = config
            
            if utils.make_sure_dir_exists(saving_dir, 'vary_betagamma'):
                fp = os.path.join(saving_dir, 'vary_betagamma', f'{config_name}.json')
                json.dump(config,open(fp,'w'))


    #vary theta & phi
    all_exps["vary_thetaphi"] = {}
    for idx,theta in enumerate(configs.THETA):
        for jdx,phi in enumerate(configs.PHI_LIN):
            cf = {'theta':theta, 'phi':phi}
            config = utils.update_dict(cf, default_infosys_config)

            config_name = f'{idx}{jdx}'
            all_exps["vary_thetaphi"][config_name] = config
            
            if utils.make_sure_dir_exists(saving_dir, 'vary_thetaphi'):
                fp = os.path.join(saving_dir, 'vary_thetaphi', f'{config_name}.json')
                json.dump(config,open(fp,'w'))


    #Varying theta beta:
    all_exps["vary_thetabeta"] = {}
    for idx, theta in enumerate(configs.THETA):
        for jdx,beta in enumerate(configs.BETA):
            cf = {'theta':theta, 'beta':beta}
            config = utils.update_dict(cf, default_infosys_config)
            
            config_name = f'{idx}{jdx}'
            all_exps["vary_thetabeta"][config_name] = config
            
            if utils.make_sure_dir_exists(saving_dir, 'vary_thetabeta'):
                fp = os.path.join(saving_dir, 'vary_thetabeta', f'{config_name}.json')
                json.dump(config,open(fp,'w'))



    fp = os.path.join(saving_dir, 'all_configs.json')
    json.dump(all_exps,open(fp,'w'))
    print(f'Finish saving config to {fp}')

if __name__=='__main__':
    #DEBUG
    ABS_PATH = ''
    # saving_dir = os.path.join(ABS_PATH, "data_hi")

    # ABS_PATH = '/N/slate/baotruon/marketplace'

    # exps results in newpipeline/results/final*
    saving_dir = os.path.join(ABS_PATH, "config_final")
    make_exps(saving_dir, configs.default_net, configs.infosys_default)