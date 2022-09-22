import infosys.utils as utils

ABS_PATH = '/N/slate/baotruon/marketplace'
DATA_PATH = os.path.join(ABS_PATH, "data")


CONFIG_PATH = os.path.join(ABS_PATH, "config_fivefive")
config_fname = os.path.join(CONFIG_PATH, 'all_configs.json')
# Note config file is not on slate! Change this later
EXP_NOS = ['conservative', 'liberal', 'hubs', 'None']
# EXP2NET = {}
# for exp_name in EXP_NOS:
#     path = os.path.join(CONFIG_PATH, 'shuffle', f'{exp_name}2.json') 
#     net_cf = json.load(open(path,'r'))
#     EXP2NET[exp_name] = utils.netconfig2netname(config_fname, net_cf)

# print('test exp2net conservative:', EXP2NET['conservative'])

SHUFFLES = ['community', 'hub']

mode='igraph'
sim_num=
RES_DIR = os.path.join(ABS_PATH,'newpipeline', 'results', f'shuffled_strategies_{sim_num}runs')
TRACKING_DIR = os.path.join(ABS_PATH,'newpipeline', 'verbose', f'shuffled_strategies_{sim_num}runs')

rule all:
    input: 
        expand(os.path.join(RES_DIR, '{shuffle}_{exp_no}.json'), shuffle=SHUFFLES, exp_no=EXP_NOS),


rule run_simulation:
    input: 
        network = os.path.join(DATA_PATH, mode, 'shuffle_infosysnet', "network_{exp_no}_{shuffle}.gml"),
        configfile = os.path.join(CONFIG_PATH, 'shuffle', '{exp_no}2.json')
    output: 
        measurements = os.path.join(RES_DIR, '{shuffle}_{exp_no}.json'),
        tracking = os.path.join(TRACKING_DIR, '{shuffle}_{exp_no}.json.gz')
    shell: """
        python3 -m workflow.scripts.driver -i {input.network} -o {output.measurements} -v {output.tracking} --config {input.configfile} --mode {mode} --times {sim_num}
    """


rule init_net:
    input: 
        follower = os.path.join(DATA_PATH, mode, 'shuffle_network', "network_{shuffle}.gml"),
        configfile = os.path.join(CONFIG_PATH, 'shuffle', '{exp_no}2.json')
        
    output: os.path.join(DATA_PATH, mode, 'shuffle_infosysnet', "network_{exp_no}_{shuffle}.gml")

    shell: """
            python3 -m workflow.scripts.init_net -i {input.follower} -o {output} --config {input.configfile} --mode {mode}
        """ 


rule shuffle_net:
    input:  follower=os.path.join(DATA_PATH, 'follower_network.gml'),
    output: os.path.join(DATA_PATH, mode, 'shuffle_network', "network_{shuffle}.gml")
    shell: """
        python3 -m workflow.scripts.shuffle_net -i {input} -o {output} --mode {wildcards.shuffle}
    """ 