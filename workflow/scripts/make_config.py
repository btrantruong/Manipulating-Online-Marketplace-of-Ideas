""" 
    Make exp config 
    - Exps on Human characteristics
        - baseline
        - varymu, varyalpha: No targeting strategy, default values for the rest of the parameters
        - shuffe: {community-preserved , hub-preserved}
    - Bot tactics: explore single variable & combinatory effects:
        - thetaphi
        - phigamma
        - thetagamma
    - Targeting strategies
        - Default values, only change targeting 
"""
import os

print(os.getcwd())
import infosys.utils as utils
import infosys.config_vals as configs
import os
import json


def save_config_to_subdir(config, config_name, saving_dir, exp_type):
    """
    Save each exp to a .json file 
    """
    output_dir = os.path.join(saving_dir, f"{exp_type}")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    json.dump(config, open(os.path.join(output_dir, f"{config_name}.json"), "w"))


def make_exps(saving_dir, default_net_config, default_infosys_config):
    """
    Create configs for exps
    Outputs:
        - a master file (.json) for all configs
        - an experiment config (.json) save to a separate directory `{saving_dir}/{exp_type}/{config_id}.json`
    """
    all_exps = {}

    ##### INITIALIZE NETWORK #####
    ##### Networks created are used commonly across all gamma values (we don't have to regerate network)
    # Varying beta gamma target
    all_exps["vary_network"] = {}

    for idx, beta in enumerate(configs.BETA):
        for jdx, gamma in enumerate(configs.GAMMA):
            for kdx, target in enumerate(configs.TARGETING):
                cf = {"beta": beta, "gamma": gamma, "targeting_criterion": target}
                config = utils.update_dict(cf, default_net_config)
                config = utils.update_dict(config, default_infosys_config)

                config_name = f"{idx}{jdx}{kdx}"
                all_exps["vary_network"][config_name] = config

                save_config_to_subdir(config, config_name, saving_dir, "vary_network")

    assert len(all_exps["vary_network"]) == len(configs.BETA) * len(
        configs.GAMMA
    ) * len(configs.TARGETING)

    ##### BASELINE #####
    all_exps["baseline"] = {}
    config_name = f"baseline"
    config = configs.baseline_exp
    all_exps["baseline"][config_name] = config

    save_config_to_subdir(config, config_name, saving_dir, "baseline")

    ##### HUMAN CHARACTERISTICS #####
    all_exps["vary_mu"] = {}
    for idx, mu in enumerate(configs.MU_SWIPE):
        for kdx, target in enumerate([configs.DEFAULT_STRATEGY]):
            cf = {"mu": mu, "targeting_criterion": target}

            config = utils.update_dict(cf, default_net_config)
            config = utils.update_dict(config, default_infosys_config)

            config_name = f"{str(target)}{idx}"
            all_exps["vary_mu"][config_name] = config

            save_config_to_subdir(config, config_name, saving_dir, "vary_mu")

    all_exps["vary_alpha"] = {}
    for idx, alpha in enumerate(configs.ALPHA_SWIPE):
        for kdx, target in enumerate([configs.DEFAULT_STRATEGY]):
            cf = {"alpha": alpha, "targeting_criterion": target}

            config = utils.update_dict(cf, default_net_config)
            config = utils.update_dict(config, default_infosys_config)

            config_name = f"{str(target)}{idx}"
            all_exps["vary_alpha"][config_name] = config

            save_config_to_subdir(config, config_name, saving_dir, "vary_alpha")

    ##### COMBINATORY EFFECTS #####
    all_exps["vary_thetaphi"] = {}
    for idx, theta in enumerate(configs.THETA_SWIPE):
        for jdx, phi in enumerate(configs.PHI_PROB):
            cf = {"theta": theta, "phi": phi}
            config = utils.update_dict(cf, default_net_config)
            config = utils.update_dict(config, default_infosys_config)

            config_name = f"{idx}{jdx}"
            all_exps["vary_thetaphi"][config_name] = config

            save_config_to_subdir(config, config_name, saving_dir, "vary_thetaphi")

    all_exps["vary_thetagamma"] = {}
    for idx, theta in enumerate(configs.THETA_SWIPE):
        for jdx, gamma in enumerate(configs.GAMMA_SWIPE):
            cf = {"theta": theta, "gamma": gamma}
            config = utils.update_dict(cf, default_net_config)
            config = utils.update_dict(config, default_infosys_config)

            config_name = f"{idx}{jdx}"
            all_exps["vary_thetagamma"][config_name] = config

            save_config_to_subdir(config, config_name, saving_dir, "vary_thetagamma")

    all_exps["vary_phigamma"] = {}
    for idx, phi in enumerate(configs.PHI_PROB):
        for jdx, gamma in enumerate(configs.GAMMA_SWIPE):
            cf = {"phi": phi, "gamma": gamma}
            config = utils.update_dict(cf, default_net_config)
            config = utils.update_dict(config, default_infosys_config)

            config_name = f"{idx}{jdx}"
            all_exps["vary_phigamma"][config_name] = config

            save_config_to_subdir(config, config_name, saving_dir, "vary_phigamma")

    # Vary single variable for each targeting strategy.
    # If we want to explore only 1 target, set "targeting_criterion"=None
    all_exps["vary_theta"] = {}
    for idx, theta in enumerate(configs.THETA_SWIPE):
        for kdx, target in enumerate(configs.TARGETING):
            cf = {"theta": theta, "targeting_criterion": target}

            config = utils.update_dict(cf, default_net_config)
            config = utils.update_dict(config, default_infosys_config)

            config_name = f"{str(target)}{idx}"
            all_exps["vary_theta"][config_name] = config

            save_config_to_subdir(config, config_name, saving_dir, "vary_theta")

    # Varying phi: (for comparing targeting strategies)
    all_exps["vary_phi"] = {}
    for idx, phi in enumerate(configs.PHI_PROB):
        for kdx, target in enumerate(configs.TARGETING):
            cf = {"phi": phi, "targeting_criterion": target}

            config = utils.update_dict(cf, default_net_config)
            config = utils.update_dict(config, default_infosys_config)

            config_name = f"{str(target)}{idx}"
            all_exps["vary_phi"][config_name] = config

            save_config_to_subdir(config, config_name, saving_dir, "vary_phi")

    # Varying gamma: (for comparing targeting strategies)
    all_exps["vary_gamma"] = {}
    for idx, gamma in enumerate(configs.GAMMA_SWIPE):
        for kdx, target in enumerate(configs.TARGETING):
            cf = {"gamma": gamma, "targeting_criterion": target}

            config = utils.update_dict(cf, default_net_config)
            config = utils.update_dict(config, default_infosys_config)

            config_name = f"{str(target)}{idx}"
            all_exps["vary_gamma"][config_name] = config
            save_config_to_subdir(config, config_name, saving_dir, "vary_gamma")

    fp = os.path.join(saving_dir, "all_configs.json")
    json.dump(all_exps, open(fp, "w"))
    print(f"Finish saving config to {fp}")


if __name__ == "__main__":
    # DEBUG
    # ABS_PATH = ""

    ABS_PATH = "/N/slate/baotruon/marketplace"

    saving_dir = os.path.join(ABS_PATH, "config_main")
    make_exps(saving_dir, configs.default_net, configs.infosys_default)
