import infosys.utils as utils

ABS_PATH = '/N/slate/baotruon/marketplace'
DATA_PATH = os.path.join(ABS_PATH, "data")
CONFIG_PATH = os.path.join(ABS_PATH, "config_09222022")

config_fname = os.path.join(CONFIG_PATH, 'all_configs.json')
# get network names corresponding to the config
config = json.load(os.path.join(CONFIG_PATH, 'default_network.json'), 'r')
net_no = utils.netconfig2netname(config_fname, config) #540
exp_type = vary_mu
MUS = [0.25, 0.5, 0.75]
EXP_NOS = list(range(len(MUS)))

sim_num = 2
mode='igraph'

RES_DIR = os.path.join(ABS_PATH,'newpipeline', 'results', f'09222022_{exp_type}_{sim_num}runs')
TRACKING_DIR = os.path.join(ABS_PATH,'newpipeline', 'verbose', f'09222022_{exp_type}_{sim_num}runs')

rule all:
    input: 
        expand(os.path.join(RES_DIR, '{exp_no}.json'), exp_no=EXP_NOS),

rule run_simulation:
    input: 
        network = os.path.join(DATA_PATH, mode, 'vary_network', f"network_{net_no}.gml"),
        configfile = os.path.join(CONFIG_PATH, exp_type, "{exp_no}.json")
    output: 
        measurements = os.path.join(RES_DIR, '{exp_no}.json'),
        tracking = os.path.join(TRACKING_DIR, '{exp_no}.json.gz')
    shell: """
        python3 -m workflow.scripts.driver -i {input.network} -o {output.measurements} -v {output.tracking} --config {input.configfile} --mode {mode} --times {sim_num}
    """

rule init_net:
    input: 
        follower=os.path.join(DATA_PATH, 'follower_network.gml'),
        configfile = os.path.join(CONFIG_PATH, 'vary_network', f"{net_no}.json")
        
    output: os.path.join(DATA_PATH, mode, 'vary_network', f"network_{net_no}.gml")

    shell: """
            python3 -m workflow.scripts.init_net -i {input.follower} -o {output} --config {input.configfile} --mode {mode}
        """ 