# ABS_PATH = ''
ABS_PATH = '/N/u/baotruon/Carbonate/marketplace'
DATA_PATH = os.path.join(ABS_PATH, "data")

print(os.getcwd())
exp_configs = json.load(open('data/all_configs.json','r'))
EXPS = list(exp_configs['vary_thetagamma'].keys())
NAMES = [tuple(expname.split('_')) for expname in EXPS] # turn "07_gamma0.05" to ('07', 'gamma0.05')
exp_nos, gs = zip(*NAMES) #example: exp_nos[i]=00, gs[i]=gamma0.01
# wildcard_constraints:
#     exp_no="\d+",
#     gamma="\d+"

sim_num = 2
mode='igraph'
RES_DIR = os.join.path(ABS_PATH,'results', 'vary_thetagamma_%sruns' %sim_num)

rule all:
    input: expand(os.path.join(RES_DIR, '{exp_no}_{gamma}.json'), zip, exp_no = exp_nos, gamma=gs)

rule run_simulation:
    input: 
        network = os.path.join(DATA_PATH, mode, 'vary_betagamma', "network_{gamma}.gml"),
        configfile = os.path.join(DATA_PATH, "vary_thetagamma", "{exp_no}_{gamma}.json")
    output: os.path.join(RES_DIR, '{exp_no}_{gamma}.json')
    shell: """
        python3 -m workflow.driver -i {input.network} -o {output} --config {input.configfile} --mode {mode} --times {sim_num}
    """

rule init_net:
    input: 
        follower=os.path.join(DATA_PATH, 'follower_network.gml'),
        configfile = os.path.join(DATA_PATH, 'vary_betagamma', "{gamma}.json")
        
    output: os.path.join(DATA_PATH, mode, 'vary_betagamma', "network_{gamma}.gml")

    shell: """
            python3 -m workflow.init_net -i {input.follower} -o {output} --config {input.configfile} --mode {mode}
        """ 