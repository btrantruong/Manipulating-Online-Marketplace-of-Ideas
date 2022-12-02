import infosys.utils as utils
# NOTE: expconfig2netname is deprecated
# ABS_PATH = ''
# DATA_PATH = os.path.join(ABS_PATH, "data_")

ABS_PATH = '/N/slate/baotruon/marketplace'
DATA_PATH = os.path.join(ABS_PATH, 'data')

print(os.getcwd())
config_fname = os.path.join(DATA_PATH, 'all_configs.json')
exp_type = 'vary_betagamma'
# get names for exp_config and network
EXP2NET = utils.expconfig2netname(config_fname, exp_type)
EXPS = list(EXP2NET.keys())

sim_num = 1
mode='igraph'

RES_DIR = os.path.join(ABS_PATH,'newpipeline', 'results', '%s_%sruns' %(exp_type, sim_num))
TRACKING_DIR = os.path.join(ABS_PATH,'newpipeline', 'verbose', '%s_%sruns' %(exp_type, sim_num))

rule all:
    input: expand(os.path.join(RES_DIR, '{exp_no}.json'), exp_no=EXPS)


rule run_simulation:
    input: 
        network = lambda wildcards: expand(os.path.join(DATA_PATH, mode, 'vary_network', "network_%s.gml" %EXP2NET[wildcards.exp_no])),
        configfile = os.path.join(DATA_PATH, "vary_betagamma", "{exp_no}.json")
    output: os.path.join(RES_DIR, '{exp_no}.json')
    shell: """
        python3 -m workflow.scripts.driver -i {input.network} -o {output} --config {input.configfile} --mode {mode} --times {sim_num}
    """

rule init_net:
    input: 
        follower=os.path.join(DATA_PATH, 'follower_network.gml'),
        configfile = os.path.join(DATA_PATH, 'vary_network', "{net_no}.json")
        
    output: os.path.join(DATA_PATH, mode, 'vary_network', "network_{net_no}.gml")

    shell: """
            python3 -m workflow.scripts.init_net -i {input.follower} -o {output} --config {input.configfile} --mode {mode}
        """ 