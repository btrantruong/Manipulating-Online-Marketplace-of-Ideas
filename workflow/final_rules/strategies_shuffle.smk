import infosys.utils as utils

ABS_PATH = '/N/slate/baotruon/marketplace'
DATA_PATH = os.path.join(ABS_PATH, "data")

# ! Note: Before running make sure config_09292022/shuffle/* exists
# `shuffle` contains .json configs copied from vary_gamma/*2.json (where gamma=0.01)
CONFIG_PATH = os.path.join(ABS_PATH, "config_09292022")
config_fname = os.path.join(CONFIG_PATH, 'all_configs.json')
EXP_NOS = ['conservative', 'liberal', 'hubs', 'None']

SHUFFLES = ['hub'] #TODO: run this for community shuffle later

mode='igraph'
sim_num=3
RES_DIR = os.path.join(ABS_PATH,'newpipeline', 'results', f'10102022_shuffled10iter_{sim_num}runs')
TRACKING_DIR = os.path.join(ABS_PATH,'newpipeline', 'verbose', f'10102022_shuffled10iter_{sim_num}runs')

rule all:
    input: 
        expand(os.path.join(RES_DIR, '{shuffle}_{exp_no}.json'), shuffle=SHUFFLES, exp_no=EXP_NOS),


rule run_simulation:
    input: 
        network = os.path.join(DATA_PATH, mode, 'shuffle_infosysnet', "network_{exp_no}2_{shuffle}.gml"),
        configfile = os.path.join(CONFIG_PATH, 'shuffle', '{exp_no}2.json')
    output: 
        measurements = os.path.join(RES_DIR, '{shuffle}_{exp_no}.json'),
        tracking = os.path.join(TRACKING_DIR, '{shuffle}_{exp_no}.json.gz')
    shell: """
        python3 -m workflow.scripts.driver -i {input.network} -o {output.measurements} -v {output.tracking} --config {input.configfile} --mode {mode} --times {sim_num}
    """


rule init_net:
    input: 
        follower = os.path.join(DATA_PATH, mode, 'shuffle_network', "network_{shuffle}_10iter.gml"),
        configfile = os.path.join(CONFIG_PATH, 'shuffle', '{exp_no}2.json')
        
    output: os.path.join(DATA_PATH, mode, 'shuffle_infosysnet', "network_{exp_no}2_{shuffle}.gml")

    shell: """
            python3 -m workflow.scripts.init_net -i {input.follower} -o {output} --config {input.configfile} --mode {mode}
        """ 


rule shuffle_net:
    input:  follower=os.path.join(DATA_PATH, 'follower_network.gml'),
    output: os.path.join(DATA_PATH, mode, 'shuffle_network', "network_{shuffle}_10iter.gml")
    shell: """
        python3 -m workflow.scripts.shuffle_net -i {input} -o {output} --mode {wildcards.shuffle} --iter 10
    """ 