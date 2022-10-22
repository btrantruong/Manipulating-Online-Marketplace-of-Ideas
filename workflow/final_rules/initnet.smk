import infosys.utils as utils

ABS_PATH = '/N/slate/baotruon/marketplace'
DATA_PATH = os.path.join(ABS_PATH, "data")
CONFIG_PATH = os.path.join(ABS_PATH, "config_09292022")

config_fname = os.path.join(CONFIG_PATH, 'all_configs.json')
exp_type = "vary_network"
# get network names corresponding to the strategy
EXPS = json.load(open(config_fname,'r'))[exp_type]

EXP_NOS = list(EXPS.keys())
mode='igraph'

rule all:
    expand(os.path.join(DATA_PATH, mode, 'vary_network', "network_{net_no}.gml"), net_no=EXP_NOS)
rule init_net:
    input: 
        follower=os.path.join(DATA_PATH, 'follower_network.gml'),
        configfile = expand(os.path.join(CONFIG_PATH, 'vary_network', "{net_no}.json"), net_no=EXP_NOS)
        
    output: os.path.join(DATA_PATH, mode, 'vary_network', "network_{net_no}.gml")

    shell: """
            python3 -m workflow.scripts.init_net -i {input.follower} -o {output} --config {input.configfile} --mode {mode}
        """ 