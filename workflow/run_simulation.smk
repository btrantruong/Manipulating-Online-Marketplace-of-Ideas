import os 
import numpy as np
import math
import json 
# ABS_PATH = "/N/u/baotruon/Carbonate/marketplace/igraphvsnx"
ABS_PATH = ''
DATA_PATH = os.path.join(ABS_PATH, "data")
mode = 'igraph'
wildcard_constraints:
    exp_no="\d+"

exp_configs = json.load(open('data/all_configs/bgconfig.json','r'))
EXPS = list(exp_configs.keys())


rule all:
    # input: os.path.join(DATA_PATH, mode, 'intermediate', "{exp_no}_network.gml")
    input:  expand(os.path.join(DATA_PATH, mode, 'intermediate', "{exp_no}_network.gml"), exp_no = EXPS)

# rule run_simulation:
#     input: os.path.join(path, mode, "network.gml")
#     output: os.path.join(path, mode, "meme.pkl"), os.path.join(path, mode, "meme_popularity.pkl")
#     shell: """
#         python3 driver.py -i {input} -o {output} \
#         --mode {} --trackmeme {} --verbose {} \
#         --eps {} --mu {} --phi {} --alpha {} --theta {}
#     """
#TODO: difference between """ and ""? 
# {var} vs {{var}}?
 
rule init_net:
    input: 
        follower=os.path.join(DATA_PATH, 'follower_network.gml'),
        configfile = os.path.join(DATA_PATH, 'configs', "bgconfig_{exp_no}.json")
    output: os.path.join(DATA_PATH, mode, 'intermediate', "{exp_no}_network.gml")
    shell: """
            python3 init_net.py -i {input.follower} -o {output} --config {input.configfile} --mode {mode} --exp {wildcards.exp_no}
        """ 

# rule make_infosys: #init_net
#     #targeting_criterion=None, verbose=False, human_network = None, n_humans=1000, beta=0.1, gamma=0.1
#     input: 
#         follower=os.path.join(DATA_PATH, 'follower_network.gml'),
#         exp_no = EXPS
#     # input: 'None'
#     output: expand(os.path.join(DATA_PATH, mode, 'intermediate', "{exp_no}_network.gml"), exp_no = EXPS)
#     shell: """
#             python3 init_net.py -i {input.follower} -o {output} --config {input.configfile} --mode {mode} --exp {exp_no}
#         """ 
# rule make_infosys: #init_net
#     #targeting_criterion=None, verbose=False, human_network = None, n_humans=1000, beta=0.1, gamma=0.1
#     input: os.path.join(DATA_PATH, 'configs', "bgconfig_{exp_no}.json")
#     # input: 'None'
#     output: os.path.join(DATA_PATH, mode, 'intermediate', "{exp_no}_network.gml")
#     shell: """
#             python3 init_net.py -i {input} -o {output} --mode {mode}
#         """ 