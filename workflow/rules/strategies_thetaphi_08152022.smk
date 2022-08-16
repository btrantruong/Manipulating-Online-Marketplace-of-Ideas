import infosys.utils as utils
import infosys.config_values as configs

### Varying thetaphi on networks of different targeting strategies

ABS_PATH = '/N/slate/baotruon/marketplace'
CONFIG_PATH = os.path.join(ABS_PATH, "data_rhoepsilon")

config_fname = os.path.join(ABS_PATH, "data_rhoepsilon", 'all_configs.json')
exp_type = 'compare_strategies'
vary_params = "vary_thetaphi"
STRATEGIES = configs.COMPARE_TARGETING
# STRATEGIES = [str(strategy) for strategy in configs.COMPARE_TARGETING]
# get network names corresponding to the strategy
STRAG2NET = {str(strag): utils.netconfig2netname(config_fname, configs.compare_strategies_net[strag]) for strag in STRATEGIES}

EXPS = json.load(open(config_fname,'r'))[vary_params].keys()
sim_num = 1
mode='igraph'

RES_DIR = os.path.join(ABS_PATH,'newpipeline', 'results', f'08152022_{exp_type}_{vary_params}_{sim_num}runs' )
TRACKING_DIR = os.path.join(ABS_PATH,'newpipeline', 'verbose', f'08152022_{exp_type}_{vary_params}_{sim_num}runs')

rule all:
    input:
        measurements = expand(os.path.join(RES_DIR, '{strategy}_{exp_no}.json'), strategy=STRATEGIES, exp_no=list(EXPS)),
        tracking = expand(os.path.join(TRACKING_DIR, '{strategy}_{exp_no}.json.gz'), strategy=STRATEGIES, exp_no=list(EXPS))


rule run_simulation:
    input: 
        network = lambda wildcards: expand(os.path.join(DATA_PATH, mode, 'vary_network', "network_%s.gml" %STRAG2NET[wildcards.strategy])),
        configfile = os.path.join(CONFIG_PATH, vary_params, "{exp_no}.json") #Note that this dir is for data/vary_THETAPHI/004.json (not compare_strategies config)
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