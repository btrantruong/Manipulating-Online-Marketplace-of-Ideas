#TODO: script haven't been tested 
# ABS_PATH = ''
# ABS_PATH = '/nobackup/baotruon/marketplace'
# DATA_PATH = os.path.join(ABS_PATH, "data")

ABS_PATH = '/N/slate/baotruon/marketplace'
DATA_PATH = os.path.join(ABS_PATH, 'data')

exp_configs = json.load(open(os.path.join(DATA_PATH, 'all_configs.json'),'r'))
EXPS = list(exp_configs['vary_network'].keys())

mode='igraph'
NET_DIR = os.path.join(DATA_PATH, mode, 'vary_network')


rule all:
    input: expand(os.path.join(NET_DIR, "network_{exp_no}.gml"), exp_no=EXPS)


rule init_net:
    input: 
        follower=os.path.join(DATA_PATH, 'follower_network.gml'),
        configfile = os.path.join(DATA_PATH, 'vary_network', "{exp_no}.json")
        
    output: os.path.join(NET_DIR, "network_{exp_no}.gml")

    shell: """
            python3 -m workflow.scripts.init_net -i {input.follower} -o {output} --config {input.configfile} --mode {mode}
        """ 