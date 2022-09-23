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


    # #vary beta & gamma, keep constant targeting strategy 
    # all_exps["vary_betagamma"] = {}
    # for idx,beta in enumerate(configs.BETA):
    #     for jdx,gamma in enumerate(configs.GAMMA):
    #         cf = {'beta':beta, 'gamma':gamma, 'targeting_criterion': configs.DEFAULT_STRATEGY}
    #         config = utils.update_dict(cf, default_infosys_config)

    #         config_name = f'{idx}{jdx}'
    #         all_exps["vary_betagamma"][config_name] = config
            
    #         if utils.make_sure_dir_exists(saving_dir, 'vary_betagamma'):
    #             fp = os.path.join(saving_dir, 'vary_betagamma', f'{config_name}.json')
    #             json.dump(config,open(fp,'w'))


    # #vary theta & phi
    # all_exps["vary_thetaphi"] = {}
    # for idx,theta in enumerate(configs.THETA):
    #     for jdx,phi in enumerate(configs.PHI_LIN):
    #         cf = {'theta':theta, 'phi':phi}
    #         config = utils.update_dict(cf, default_infosys_config)

    #         config_name = f'{idx}{jdx}'
    #         all_exps["vary_thetaphi"][config_name] = config
            
    #         if utils.make_sure_dir_exists(saving_dir, 'vary_thetaphi'):
    #             fp = os.path.join(saving_dir, 'vary_thetaphi', f'{config_name}.json')
    #             json.dump(config,open(fp,'w'))


    # #Varying theta beta:
    # all_exps["vary_thetabeta"] = {}
    # for idx, theta in enumerate(configs.THETA):
    #     for jdx,beta in enumerate(configs.BETA):
    #         cf = {'theta':theta, 'beta':beta}
    #         config = utils.update_dict(cf, default_net_config)
    #         config = utils.update_dict(config, default_infosys_config)
            
    #         config_name = f'{idx}{jdx}'
    #         all_exps["vary_thetabeta"][config_name] = config
            
    #         if utils.make_sure_dir_exists(saving_dir, 'vary_thetabeta'):
    #             fp = os.path.join(saving_dir, 'vary_thetabeta', f'{config_name}.json')
    #             json.dump(config,open(fp,'w'))


    # # 09102022:
    # # Varying theta gamma: preliminary to decide these values with a more realistic num bots (10% vs 1%)
    # all_exps["vary_thetagamma"] = {}
    # for idx, theta in enumerate(configs.THETA_SHORT):
    #     for jdx,gamma in enumerate(configs.GAMMA_SHORT):
    #         cf = {'theta':theta, 'gamma':gamma}
    #         config = utils.update_dict(cf, default_net_config)
    #         config = utils.update_dict(config, default_infosys_config)
            
    #         config_name = f'{idx}{jdx}'
    #         all_exps["vary_thetagamma"][config_name] = config
            
    #         if utils.make_sure_dir_exists(saving_dir, 'vary_thetagamma'):
    #             fp = os.path.join(saving_dir, 'vary_thetagamma', f'{config_name}.json')
    #             json.dump(config,open(fp,'w'))


    # #Varying beta: (for comparing targeting strategies)
    # all_exps["vary_beta"] = {}
    # for idx,beta in enumerate(configs.BETA):
    #     for kdx,target in enumerate(configs.TARGETING):
    #         cf = {'beta': beta, 'targeting_criterion': target}
        
    #         config = utils.update_dict(cf, default_net_config)
    #         config = utils.update_dict(config, default_infosys_config)
        
    #         config_name = f'{str(target)}{idx}'
    #         all_exps["vary_beta"][config_name] = config
            
    #         if utils.make_sure_dir_exists(saving_dir, 'vary_beta'):
    #             fp = os.path.join(saving_dir, 'vary_beta', f'{config_name}.json')
    #             json.dump(config,open(fp,'w'))


    all_exps["vary_theta"] = {}
    for idx,theta in enumerate(configs.THETA_SWIPE):
        for kdx,target in enumerate(configs.TARGETING):
            cf = {'theta':theta, 'targeting_criterion': target}

            config = utils.update_dict(cf, default_net_config)
            config = utils.update_dict(config, default_infosys_config)

            config_name = f'{str(target)}{idx}'
            all_exps["vary_theta"][config_name] = config
            
            if utils.make_sure_dir_exists(saving_dir, 'vary_theta'):
                fp = os.path.join(saving_dir, 'vary_theta', f'{config_name}.json')
                json.dump(config,open(fp,'w'))


    #Varying phi: (for comparing targeting strategies)
    all_exps["vary_phi"] = {}
    for idx,phi in enumerate(configs.PHI_SWIPE):
        for kdx,target in enumerate(configs.TARGETING):
            cf = {'phi':phi, 'targeting_criterion': target}

            config = utils.update_dict(cf, default_net_config)
            config = utils.update_dict(config, default_infosys_config)

            config_name = f'{str(target)}{idx}'
            all_exps["vary_phi"][config_name] = config
            
            if utils.make_sure_dir_exists(saving_dir, 'vary_phi'):
                fp = os.path.join(saving_dir, 'vary_phi', f'{config_name}.json')
                json.dump(config,open(fp,'w'))


    #Varying gamma: (for comparing targeting strategies)
    all_exps["vary_gamma"] = {}
    for idx,gamma in enumerate(configs.GAMMA_SWIPE):
        for kdx,target in enumerate(configs.TARGETING):
            cf = {'gamma':gamma, 'targeting_criterion': target}

            config = utils.update_dict(cf, default_net_config)
            config = utils.update_dict(config, default_infosys_config)

            config_name = f'{str(target)}{idx}'
            all_exps["vary_gamma"][config_name] = config
            
            if utils.make_sure_dir_exists(saving_dir, 'vary_gamma'):
                fp = os.path.join(saving_dir, 'vary_gamma', f'{config_name}.json')
                json.dump(config,open(fp,'w'))


    fp = os.path.join(saving_dir, 'all_configs.json')
    json.dump(all_exps,open(fp,'w'))
    print(f'Finish saving config to {fp}')


if __name__=='__main__':
    #DEBUG
    # ABS_PATH = ''
    # saving_dir = os.path.join(ABS_PATH, "data_hi")

    ABS_PATH = '/N/slate/baotruon/marketplace'

    # exps results in newpipeline/results/final* (09052022)
    # saving_dir = os.path.join(ABS_PATH, "config_final")
    # make_exps(saving_dir, configs.default_net, configs.infosys_default)

    # 09102022: add vary_thetagamma to decide on realistic value of num bots (beta)
    # This and the following configs (tenpct and fivepctbot use GAMMA_SHORT, BETA_SHORT)
    # saving_dir = os.path.join(ABS_PATH, "config_09102022_onepctbot")
    # make_exps(saving_dir, configs.onepctbot_default_net, configs.infosys_notracking)

    # saving_dir = os.path.join(ABS_PATH, "config_09102022_tenpctbot") 
    # make_exps(saving_dir, configs.tenpctbot_default_net, configs.infosys_notracking)

    # saving_dir = os.path.join(ABS_PATH, "config_09152022_fivepctbot") 
    # make_exps(saving_dir, configs.fivepctbot_default_net, configs.infosys_notracking)

    # # gamma 0.05, beta 0.05, theta 5, results are in 09202022_strategies/* 
    # saving_dir = os.path.join(ABS_PATH, "config_fivefive")
    # make_exps(saving_dir, configs.fivepctbot_default_net, configs.infosys_default)

    # Note that for final experiments looking at strategies, we're using shortened values: GAMMA_SWIPE 
    # But all networks are created using longer values: BETA and GAMMA
    saving_dir = os.path.join(ABS_PATH, "config_09222022")
    make_exps(saving_dir, configs.fivepctbot_default_net, configs.infosys_default)
