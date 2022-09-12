import infosys.utils as utils

# ABS_PATH = ''
# DATA_PATH = os.path.join(ABS_PATH, "data")
# CONFIG_PATH = os.path.join(ABS_PATH, "config_final")

ABS_PATH = '/N/slate/baotruon/marketplace'
DATA_PATH = os.path.join(ABS_PATH, 'data')
CONFIG_PATH = os.path.join(ABS_PATH, "config_final")

config_fname = os.path.join(CONFIG_PATH, 'all_configs.json')
exp_type = 'vary_thetabeta'
# get names for exp_config and network
# TODO: delete expconfig2netname, change this to netconfig2netname
EXP2NET = utils.expconfig2netname(config_fname, exp_type)
EXPS = list(EXP2NET.keys())

sim_num = 1
mode='igraph'

RES_DIR = os.path.join(ABS_PATH,'newpipeline', 'results', f'final_{exp_type}_{sim_num}runs')
TRACKING_DIR = os.path.join(ABS_PATH,'newpipeline', 'verbose', f'final_{exp_type}_{sim_num}runs')

rule all:
    input: 
        results = expand(os.path.join(RES_DIR, '{exp_no}.json'), exp_no=EXPS),
        tracking = expand(os.path.join(TRACKING_DIR, '{exp_no}.json.gz'), exp_no=EXPS)

rule run_simulation:
    input: 
        network = lambda wildcards: expand(os.path.join(DATA_PATH, mode, 'vary_network', "network_%s.gml" %EXP2NET[wildcards.exp_no])),
        configfile = os.path.join(CONFIG_PATH, exp_type, "{exp_no}.json") #data/vary_thetabeta/004.json
    output: 
        measurements = os.path.join(RES_DIR, '{exp_no}.json'),
        tracking = os.path.join(TRACKING_DIR, '{exp_no}.json.gz')
    shell: """
        python3 -m workflow.scripts.driver -i {input.network} -o {output.measurements} -v {output.tracking} --config {input.configfile} --mode {mode} --times {sim_num}
    """

rule init_net:
    input: 
        follower=os.path.join(DATA_PATH, 'follower_network.gml'),
        configfile = os.path.join(CONFIG_PATH, 'vary_network', "{net_no}.json")
        
    output: os.path.join(DATA_PATH, mode, 'vary_network', "network_{net_no}.gml")

    shell: """
            python3 -m workflow.scripts.init_net -i {input.follower} -o {output} --config {input.configfile} --mode {mode}
        """ 