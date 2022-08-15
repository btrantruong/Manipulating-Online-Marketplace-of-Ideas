""" Generate data to plot avg_qual as a function of convergence criteria to find the region where convergence is stable 
    rho: importance of past quality to the calculation of new quality 
    epsilon: convergence error
"""

import infosys.utils as utils
import infosys.config_values as configs

ABS_PATH = '/N/slate/baotruon/marketplace'
DATA_PATH = os.path.join(ABS_PATH, "data")
CONFIG_PATH = os.path.join(ABS_PATH, "data_convergence_largerho")

config_fname = os.path.join(CONFIG_PATH, 'all_configs.json')
exp_type = 'convergence_rhoepsilon'

mode='igraph'
sim_num = 1
# network_config = {'beta': configs.DEFAULT_BETA, 'gamma': configs.DEFAULT_GAMMA, 'targeting_criterion': configs.DEFAULT_STRATEGY}
# network = utils.netconfig2netname(config_fname, network_config)
# print('Network name: ' %network)

# get names for exp_config and network
EXP2NET = utils.expconfig2netname(config_fname, exp_type)
EXPS = list(EXP2NET.keys())

RES_DIR = os.path.join(ABS_PATH,'newpipeline', 'results', 'convergence_largerho')
TRACKING_DIR = os.path.join(ABS_PATH,'newpipeline', 'verbose', 'convergence_largerho')

rule all:
    input:
        measurements = expand(os.path.join(RES_DIR, '{exp_no}.json'), exp_no=EXPS),
        tracking = expand(os.path.join(TRACKING_DIR, '{exp_no}.json.gz'), exp_no=EXPS)


rule run_simulation:
    input: 
        network = lambda wildcards: expand(os.path.join(DATA_PATH, mode, 'vary_network', "network_%s.gml" %EXP2NET[wildcards.exp_no])),
        configfile = os.path.join(CONFIG_PATH, exp_type, "{exp_no}.json")
    output: 
        measurements = os.path.join(RES_DIR, '{exp_no}.json'),
        tracking = os.path.join(TRACKING_DIR, '{exp_no}.json.gz')
    shell: """
        python3 -m workflow.scripts.driver -i {input.network} -o {output.measurements} -v {output.tracking} --config {input.configfile} --mode {mode} --times {sim_num}
    """