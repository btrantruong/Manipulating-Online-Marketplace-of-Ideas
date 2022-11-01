import infosys.utils as utils

ABS_PATH = '/N/slate/baotruon/marketplace'
DATA_PATH = os.path.join(ABS_PATH, 'data')
CONFIG_PATH = os.path.join(ABS_PATH, "config_10302022")

config_fname = os.path.join(CONFIG_PATH, 'all_configs.json')
exp_type = 'vary_phigamma'
# get names for exp_config and network
EXPS = json.load(open(config_fname,'r'))[exp_type]

# exclude phi[0] exps (same as results in No targeting vary_gamma)
# exclude gamma[2]=0.01 (default value, in which case results are same as No targeting vary_phi)
EXP_NOS = [
    exp_name
    for exp_name in EXPS.keys()
    if int(exp_name[0]) != 0 and int(exp_name[1]) != 2
]

EXP2NET = {
    exp_name: utils.netconfig2netname(config_fname, net_cf)
    for exp_name, net_cf in EXPS.items()
    if exp_name in EXP_NOS
}

sim_num = 2
mode='igraph'

RES_DIR = os.path.join(ABS_PATH,'results', 'short', f'10302022_{exp_type}_{sim_num}runs')
TRACKING_DIR = os.path.join(ABS_PATH,'results', 'verbose', f'10302022_{exp_type}_{sim_num}runs')


rule all:
    input: 
        results = expand(os.path.join(RES_DIR, '{exp_no}.json'), exp_no=EXP_NOS)

rule run_simulation:
    input: 
        network = ancient(lambda wildcards: expand(os.path.join(DATA_PATH, mode, 'vary_network', "network_%s.gml" %EXP2NET[wildcards.exp_no]))),
        configfile = ancient(os.path.join(CONFIG_PATH, exp_type, "{exp_no}.json")) #data/vary_thetabeta/004.json
    output: 
        measurements = os.path.join(RES_DIR, '{exp_no}.json'),
        tracking = os.path.join(TRACKING_DIR, '{exp_no}.json.gz')
    shell: """
        python3 -m workflow.scripts.driver -i {input.network} -o {output.measurements} -v {output.tracking} --config {input.configfile} --mode {mode} --times {sim_num}
    """

rule init_net:
    input: 
        follower= ancient(os.path.join(DATA_PATH, 'follower_network.gml')),
        configfile = ancient(os.path.join(CONFIG_PATH, 'vary_network', "{net_no}.json"))
        
    output: os.path.join(DATA_PATH, mode, 'vary_network', "network_{net_no}.gml")
    shell: """
            python3 -m workflow.scripts.init_net -i {input.follower} -o {output} --config {input.configfile} --mode {mode}
        """ 