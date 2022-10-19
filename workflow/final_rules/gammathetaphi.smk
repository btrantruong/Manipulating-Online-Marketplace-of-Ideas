import infosys.utils as utils

ABS_PATH = '/N/slate/baotruon/marketplace'
DATA_PATH = os.path.join(ABS_PATH, 'data')
CONFIG_PATH = os.path.join(ABS_PATH, "config_10182022")

config_fname = os.path.join(CONFIG_PATH, 'all_configs.json')
exp_type = 'vary_gammathetaphi'

EXPS = json.load(open(config_fname,'r'))[exp_type]
# get names for exp_config and network
# exclude gamma[2]=1 (default value, in which case results are same as No targeting vary_phi and vary_theta)
EXP_NOS = [
    exp_name
    for exp_name in EXPS.keys()
    if int(exp_name[0]) != 2
]

EXP2NET = {
    exp_name: utils.netconfig2netname(config_fname, net_cf)
    for exp_name, net_cf in EXPS.items()
    if exp_name in EXP_NOS
}

sim_num = 1
mode='igraph'

RES_DIR = os.path.join(ABS_PATH,'newpipeline', 'results', f'10182022_{exp_type}_{sim_num}runs')

rule all:
    input: 
        expand(os.path.join(RES_DIR, '{exp_no}.json'), exp_no=EXP_NOS),

rule run_simulation:
    input: 
        network = lambda wildcards: expand(os.path.join(DATA_PATH, mode, 'vary_network', f"network_{EXP2NET[wildcards.exp_no]}.gml")),
        configfile = os.path.join(CONFIG_PATH, exp_type, "{exp_no}.json")
    output: 
        measurements = os.path.join(RES_DIR, '{exp_no}.json')
    shell: """
        python3 -m workflow.scripts.driver -i {input.network} -o {output.measurements} --config {input.configfile} --mode {mode} --times {sim_num}
    """

rule init_net:
    input: 
        follower=os.path.join(DATA_PATH, 'follower_network.gml'),
        configfile = os.path.join(CONFIG_PATH, 'vary_network', "{net_no}.json")
        
    output: os.path.join(DATA_PATH, mode, 'vary_network', "network_{net_no}.gml")

    shell: """
            python3 -m workflow.scripts.init_net -i {input.follower} -o {output} --config {input.configfile} --mode {mode}
        """ 