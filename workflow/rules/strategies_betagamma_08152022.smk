import infosys.utils as utils
import infosys.config_values as configs

### Varying network configs (only perform on hubs and none strategy)

ABS_PATH = '/N/slate/baotruon/marketplace'
DATA_PATH = os.path.join(ABS_PATH, "data")
CONFIG_PATH = os.path.join(ABS_PATH, "data_rhoepsilon")

config_fname = os.path.join(ABS_PATH, "data_rhoepsilon", 'all_configs.json')
exp_type = 'compare_strategies'
vary_params = "vary_network"
STRATEGIES = configs.COMPARE_TARGETING
# exp_no is the same as network name (unique network config)
all_networks = json.load(open(config_fname,'r'))[vary_params]

COMPARE_EXPS = {exp: params for exp, params in all_networks.items() if params['targeting_criterion'] in STRATEGIES}
EXPS = list(COMPARE_EXPS.keys())
sim_num = 1
mode='igraph'

RES_DIR = os.path.join(ABS_PATH,'newpipeline', 'results', f'08152022_{exp_type}_betagamma_{sim_num}runs' )
TRACKING_DIR = os.path.join(ABS_PATH,'newpipeline', 'verbose', f'08152022_{exp_type}_betagamma_{sim_num}runs')

rule all:
    input:
        measurements = expand(os.path.join(RES_DIR, '{exp_no}.json'), exp_no=EXPS),
        tracking = expand(os.path.join(TRACKING_DIR, '{exp_no}.json.gz'), exp_no=EXPS)


rule run_simulation:
    input: 
        network = os.path.join(DATA_PATH, mode, 'vary_network', "network_{exp_no}.gml"),
        configfile = os.path.join(CONFIG_PATH, vary_params, "{exp_no}.json")
    output: 
        measurements = os.path.join(RES_DIR, '{exp_no}.json'),
        tracking = os.path.join(TRACKING_DIR, '{exp_no}.json.gz')
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