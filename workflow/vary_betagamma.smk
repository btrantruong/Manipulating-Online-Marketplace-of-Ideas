
ABS_PATH = ''
DATA_PATH = os.path.join(ABS_PATH, "data")

print(os.getcwd())
exp_configs = json.load(open('data/all_configs.json','r'))
EXPS = list(exp_configs['vary_betagamma'].keys())


sim_num = 20
mode='igraph'

rule all:
    input: expand('results/vary_betagamma/{exp_no}.json', exp_no=EXPS)

rule run_simulation:
    input: 
        network = os.path.join(DATA_PATH, mode, 'vary_betagamma', "network_{exp_no}.gml"),
        configfile = os.path.join(DATA_PATH, "vary_betagamma", "default_infosys.json")
    output: 'results/vary_betagamma/{exp_no}.json'
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