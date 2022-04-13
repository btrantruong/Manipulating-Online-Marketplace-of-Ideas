# ABS_PATH = ''
ABS_PATH = '/N/u/baotruon/Carbonate/marketplace'
DATA_PATH = os.path.join(ABS_PATH, "data")

print(os.getcwd())
exp_configs = json.load(open(os.path.join(DATA_PATH, 'all_configs.json'),'r'))
EXPS = list(exp_configs['vary_betagamma'].keys())


sim_num = 2
mode='igraph'
RES_DIR = os.path.join(ABS_PATH,'results', 'vary_betagamma_%sruns' %sim_num)

rule all:
    input: expand(os.path.join(RES_DIR, '{exp_no}.json'), exp_no=EXPS)

rule run_simulation:
    input: 
        network = os.path.join(DATA_PATH, mode, 'vary_betagamma', "network_{exp_no}.gml"),
        configfile = os.path.join(DATA_PATH, "vary_betagamma", "default_infosys.json")
    output: os.path.join(RES_DIR, '{exp_no}.json')
    shell: """
        python3 -m workflow.driver -i {input.network} -o {output} --config {input.configfile} --mode {mode} --times {sim_num}
    """

rule init_net:
    input: 
        follower=os.path.join(DATA_PATH, 'follower_network.gml'),
        configfile = os.path.join(DATA_PATH, 'vary_betagamma', "{exp_no}.json")
        
    output: os.path.join(DATA_PATH, mode, 'vary_betagamma', "network_{exp_no}.gml")

    shell: """
            python3 -m workflow.init_net -i {input.follower} -o {output} --config {input.configfile} --mode {mode}
        """ 