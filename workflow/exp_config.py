""" Config for the first set of exps (vary phi&gamma; vary beta&gamma, vary theta&gamma)"""
import os
print(os.getcwd())
import infosys.utils as utils
import infosys.config_values as configs
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
                
                config_name = '%s%s%s' %(idx,jdx, kdx)
                all_exps["vary_network"][config_name] = config
                if utils.make_sure_dir_exists(saving_dir, 'vary_network'):
                    fp = os.path.join(saving_dir, 'vary_network','%s.json' %config_name)
                    json.dump(config,open(fp,'w'))
    assert len(all_exps["vary_network"]) == len(configs.BETA) * len(configs.GAMMA)*len(configs.TARGETING)


    #compare strategies
    all_exps["compare_strategies"] = {}
    for idx, strategy in enumerate(configs.COMPARE_TARGETING):
        cf = {'beta':configs.DEFAULT_BETA, 'gamma':configs.DEFAULT_GAMMA, 'targeting_criterion': strategy}
        config = utils.update_dict(cf, default_net_config)

        config_name = '%s' %str(strategy)
        all_exps["compare_strategies"][config_name] = config
        
        if utils.make_sure_dir_exists(saving_dir, 'compare_strategies'):
            fp = os.path.join(saving_dir, 'compare_strategies','%s.json' %config_name)
            json.dump(config,open(fp,'w'))


    #vary beta & gamma
    all_exps["vary_betagamma"] = {}
    for idx,beta in enumerate(configs.BETA):
        for jdx,gamma in enumerate(configs.GAMMA):
            cf = {'beta':beta, 'gamma':gamma, 'targeting_criterion': configs.DEFAULT_STRATEGY}
            config = utils.update_dict(cf, default_infosys_config)

            config_name = '%s%s' %(idx,jdx)
            all_exps["vary_betagamma"][config_name] = config
            
            if utils.make_sure_dir_exists(saving_dir, 'vary_betagamma'):
                fp = os.path.join(saving_dir, 'vary_betagamma','%s.json' %config_name)
                json.dump(config,open(fp,'w'))

    #vary theta & phi
    all_exps["vary_thetaphi"] = {}
    for idx,theta in enumerate(configs.THETA):
        for jdx,phi in enumerate(configs.PHI_LIN):
            cf = {'theta':theta, 'phi':phi}
            config = utils.update_dict(cf, default_infosys_config)

            config_name = '%s%s' %(idx,jdx)
            all_exps["vary_thetaphi"][config_name] = config
            
            if utils.make_sure_dir_exists(saving_dir, 'vary_thetaphi'):
                fp = os.path.join(saving_dir, 'vary_thetaphi','%s.json' %config_name)
                json.dump(config,open(fp,'w'))


    #Varying phi gamma:
    all_exps["vary_phigamma"] = {}
    for idx, phi in enumerate(configs.PHI_LIN):
        for jdx,gamma in enumerate(configs.GAMMA):
            cf = {'phi': phi, 'gamma':gamma}
            config = utils.update_dict(cf, default_infosys_config)
            
            config_name = '%s%s' %(idx,jdx)
            all_exps["vary_phigamma"][config_name] = config
            
            if utils.make_sure_dir_exists(saving_dir, 'vary_phigamma'):
                fp = os.path.join(saving_dir, 'vary_phigamma','%s.json' %config_name)
                json.dump(config,open(fp,'w'))


    #Varying theta gamma:
    all_exps["vary_thetagamma"] = {}
    for idx, theta in enumerate(configs.THETA):
        for jdx,gamma in enumerate(configs.GAMMA):
            cf = {'theta':theta, 'gamma':gamma}
            config = utils.update_dict(cf, default_infosys_config)
            
            config_name = '%s%s' %(idx,jdx)
            all_exps["vary_thetagamma"][config_name] = config
            
            if utils.make_sure_dir_exists(saving_dir, 'vary_thetagamma'):
                fp = os.path.join(saving_dir, 'vary_thetagamma','%s.json' %config_name)
                json.dump(config,open(fp,'w'))


    # Convergence criteria: rho and epsilon
    all_exps["convergence_rhoepsilon"] = {}
    for idx, rho in enumerate(configs.RHO):
        for jdx,epsilon in enumerate(configs.EPSILON):
            cf = {'rho':rho, 'epsilon':epsilon}
            config = utils.update_dict(cf, default_infosys_config)
            
            config_name = '%s%s' %(idx,jdx)
            all_exps["convergence_rhoepsilon"][config_name] = config
            
            if utils.make_sure_dir_exists(saving_dir, "convergence_rhoepsilon"):
                fp = os.path.join(saving_dir, "convergence_rhoepsilon",'%s.json' %config_name)
                json.dump(config,open(fp,'w'))


    fp = os.path.join(saving_dir, 'all_configs.json')
    json.dump(all_exps,open(fp,'w'))
    print('Finish saving config to %s' %fp)

if __name__=='__main__':
    #DEBUG
    # ABS_PATH = ''
    # saving_dir = os.path.join(ABS_PATH, "data_hi")

    ABS_PATH = '/N/slate/baotruon/marketplace'
    
    # exps in newpipeline/results
    # saving_dir = os.path.join(ABS_PATH, "data")
    # make_exps(saving_dir, configs.default_net, configs.default_infosys)
    
    # exps in hiepsilon
    # saving_dir = os.path.join(ABS_PATH, "data_hiepsilon")
    # make_exps(saving_dir, configs.default_net, configs.infosys_hiepsilon)

    # exps low epsilon
    # saving_dir = os.path.join(ABS_PATH, "data_lowepsilon")
    # make_exps(saving_dir, configs.default_net, configs.infosys_lowepsilon)

    # exp_type: convergence_rhoepsilon
    # Results stored in /N/slate/baotruon/marketplace/newpipeline/results/convergence_criteria
    # saving_dir = os.path.join(ABS_PATH, "data_convergence")
    # make_exps(saving_dir, configs.default_net, configs.default_infosys)

    # exps in convergence_largerho
    saving_dir = os.path.join(ABS_PATH, "data_convergence_largerho")
    make_exps(saving_dir, configs.default_net, configs.default_infosys)