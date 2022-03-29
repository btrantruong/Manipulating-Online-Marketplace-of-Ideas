
# GAMMAS = [0.0001, 0.0002, 0.0005, 0.001, 0.002, 0.005, 0.02, 0.05, 0.1, 0.2, 0.5]
GAMMAS = [0.1, 0.02, 0.5]
ABS_PATH = ''
DATA_PATH = os.path.join(ABS_PATH, "data")

print(os.getcwd())
exp_configs = json.load(open('data/all_configs.json','r'))
EXPS = list(exp_configs['vary_phigamma'].keys())
NAMES = [tuple(expname.split('_')) for expname in EXPS] # turn "07_gamma0.05" to ('07', 'gamma0.05')
exp_nos, gs = zip(*NAMES)
# wildcard_constraints:
#     exp_no="\d+",
#     gamma="\d+"

sim_num = 20
mode='igraph'

rule all:
    # input: expand("network_gamma{gamma}.gml", gamma=GAMMAS)
    input: expand('results/vary_phigamma/{exp_no}_gamma{gamma}.json', zip, exp_no = exp_nos, gamma=GAMMAS)

rule run_simulation:
    input: 
        network = os.path.join(DATA_PATH, mode, 'intermediate', "network_gamma{gamma}.gml"),
        configfile = os.path.join(DATA_PATH, "vary_phigamma", "{exp_no}_gamma{gamma}.json")
    output: 'results/vary_phigamma/{exp_no}_gamma{gamma}.json'
    shell: """
        python3 -m scripts.driver.py -i {input.network} -o {output} --config {input.configfile} --mode {mode} --times {sim_num}
    """

rule init_net:
    input: 
        follower=os.path.join(DATA_PATH, 'follower_network.gml'),
        configfile = os.path.join(DATA_PATH, 'vary_betagamma', "gamma{gamma}.json")
        
    output: os.path.join(DATA_PATH, mode, 'intermediate', "network_gamma{gamma}.gml")

    shell: """
            python3 -m scripts.init_net.py -i {input.follower} -o {output} --config {input.configfile} --mode {mode}
        """ 