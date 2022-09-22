import infosys.utils as utils

ABS_PATH = '/N/slate/baotruon/marketplace'
DATA_PATH = os.path.join(ABS_PATH, "data")


CONFIG_PATH = os.path.join(ABS_PATH, "config_fivefive")
config_fname = os.path.join(CONFIG_PATH, 'all_configs.json')
# Note config file is not on slate! Change this later
EXP_NOS = ['conservative', 'liberal', 'hubs', 'misinformation', 'None', 'partisanship']
EXP2NET = {}
for exp_name in EXP_NOS:
    path = os.path.join(CONFIG_PATH, 'shuffle', f'{exp_name}2.json') 
    net_cf = json.load(open(path,'r'))
    EXP2NET[exp_name] = utils.netconfig2netname(config_fname, net_cf)

SHUFFLES = ['community', 'hub']

mode='igraph'
sim_num=1
RES_DIR = os.path.join(ABS_PATH,'newpipeline', 'results', f'shuffled_strategies_{sim_num}runs')
TRACKING_DIR = os.path.join(ABS_PATH,'newpipeline', 'verbose', f'shuffled_strategies_{sim_num}runs')

rule all:
    input: 
        expand(os.path.join(RES_DIR, '{shuffle}_{exp_no}.json'), shuffle=SHUFFLES, exp_no=EXP_NOS),

rule run_simulation:
    input: 
        network = lambda wildcards: expand(os.path.join(DATA_PATH, mode, 'vary_network', f"network_{EXP2NET[wildcards.exp_no]}_shuffle_{wildcards.shuffle}.gml")),
        configfile = os.path.join(CONFIG_PATH, "{exp_no}.json")
    output: 
        measurements = os.path.join(RES_DIR, '{shuffle}_{exp_no}.json'),
        tracking = os.path.join(TRACKING_DIR, '{shuffle}_{exp_no}.json.gz')
    shell: """
        python3 -m workflow.scripts.driver -i {input.network} -o {output.measurements} -v {output.tracking} --config {input.configfile} --mode {mode} --times {sim_num}
    """

rule shuffle_net:
    input:  os.path.join(DATA_PATH, mode, 'vary_network', "network_{net_no}.gml")
    output: os.path.join(DATA_PATH, mode, 'vary_network', "network_{net_no}_shuffle_{shuffle}.gml")
    shell: """
        python3 -m workflow.scripts.shuffle_net -i {input.follower} -o {output} --mode {shuffle}
    """ 

rule init_net:
    input: 
        follower=os.path.join(DATA_PATH, 'follower_network.gml'),
        configfile = os.path.join(CONFIG_PATH, 'vary_network', "{net_no}.json")
        
    output: os.path.join(DATA_PATH, mode, 'vary_network', "network_{net_no}.gml")

    shell: """
            python3 -m workflow.scripts.init_net -i {input.follower} -o {output} --config {input.configfile} --mode {mode}
        """ 