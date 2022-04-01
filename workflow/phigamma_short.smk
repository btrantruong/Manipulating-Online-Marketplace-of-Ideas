## For a small numbers of exps 

# ABS_PATH = ''
ABS_PATH = '/N/u/baotruon/Carbonate/marketplace'
DATA_PATH = os.path.join(ABS_PATH, "data")

print(os.getcwd())
exp_configs = json.load(open('data/all_configs.json','r'))
anchor_gamma = 0.01 #change to 0.001
RES_DIR = os.path.join(ABS_PATH, "results", "vary_phigamma", "gamma%s" %str(anchor_gamma))
EXPS = list([name for name in exp_configs['vary_phigamma'].keys() if str(anchor_gamma) in name])
NAMES = [tuple(expname.split('_')) for expname in EXPS] # turn "07_gamma0.05" to ('07', 'gamma0.05')
exp_nos, gs = zip(*NAMES) #example: exp_nos[i]=00, gs[i]=gamma0.01
wildcard_constraints:
    exp_no="\d+",
#     gamma="\d+"

sim_num = 20
mode='igraph'

rule all:
    # input: expand("network_gamma{gamma}.gml", gamma=GAMMAS)
    input: expand(os.path.join(RES_DIR, '{exp_no}_{gamma}.json'), zip, exp_no = exp_nos, gamma=gs)
    # expand('results/vary_phigamma/{exp_no}_{gamma}.json', zip, exp_no = exp_nos, gamma=gs)

rule run_simulation:
    input: 
        network = os.path.join(DATA_PATH, mode, 'vary_betagamma', "network_{gamma}.gml"),
        configfile = os.path.join(DATA_PATH, "vary_phigamma", "{exp_no}_{gamma}.json")
    output: os.path.join(RES_DIR, '{exp_no}_{gamma}.json')
    #"results/vary_phigamma/{exp_no}_{gamma}.json"
    shell: """
        python3 -m workflow.driver -i {input.network} -o {output} --config {input.configfile} --mode {mode} --times {sim_num}
        """