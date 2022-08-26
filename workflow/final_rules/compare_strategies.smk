import infosys.utils as utils
import infosys.final_configs as configs

#TODO: work on this!
### Varying thetaphi on networks of different targeting strategy
# ABS_PATH = ''
# DATA_PATH = os.path.join(ABS_PATH, "data_")
# TRACKING_DIR = os.path.join(ABS_PATH, "verbose")

ABS_PATH = '/N/slate/baotruon/marketplace'
DATA_PATH = os.path.join(ABS_PATH, "data")
CONFIG_PATH = os.path.join(ABS_PATH, "config_final")

config_fname = os.path.join(CONFIG_PATH, 'all_configs.json')
exp_type = 'compare_strategies'
vary_params = "vary_thetaphi"
STRATEGIES = configs.COMPARE_TARGETING
# STRATEGIES = [str(strategy) for strategy in configs.COMPARE_TARGETING]
# get network names corresponding to the strategy
STRAG2NET = {str(strag): utils.netconfig2netname(config_fname, configs.compare_strategies_net[strag]) for strag in STRATEGIES}

EXPS = json.load(open(config_fname,'r'))[vary_params].keys()
sim_num = 2
mode='igraph'

RES_DIR = os.path.join(ABS_PATH,'newpipeline', 'results', '%s_%sruns' %(exp_type, sim_num))
TRACKING_DIR = os.path.join(ABS_PATH,'newpipeline', 'verbose', '%s_%sruns' %(exp_type, sim_num))

rule all:
    input:
        measurements = expand(os.path.join(RES_DIR, '{strategy}_{exp_no}.json'), strategy=STRATEGIES, exp_no=list(EXPS)),
        tracking = expand(os.path.join(TRACKING_DIR, '{strategy}_{exp_no}.json.gz'), strategy=STRATEGIES, exp_no=list(EXPS))


rule run_simulation:
    input: 
        network = lambda wildcards: expand(os.path.join(DATA_PATH, mode, 'vary_network', "network_%s.gml" %STRAG2NET[wildcards.strategy])),
        configfile = os.path.join(DATA_PATH, vary_params, "{exp_no}.json") #Note that this dir is for data/vary_THETAPHI/004.json (not compare_strategies config)
    output: 
        measurements = os.path.join(RES_DIR, '{strategy}_{exp_no}.json'),
        tracking = os.path.join(TRACKING_DIR, '{strategy}_{exp_no}.json.gz')
    shell: """
        python3 -m workflow.scripts.driver -i {input.network} -o {output.measurements} -v {output.tracking} --config {input.configfile} --mode {mode} --times {sim_num}
    """

rule init_net:
    input: 
        follower=os.path.join(DATA_PATH, 'follower_network.gml'),
        configfile = os.path.join(DATA_PATH, 'vary_network', "{net_no}.json")
        
    output: os.path.join(DATA_PATH, mode, 'vary_network', "network_{net_no}.gml")

    shell: """
            python3 -m workflow.scripts.init_net -i {input.follower} -o {output} --config {input.configfile} --mode {mode}
        """ 