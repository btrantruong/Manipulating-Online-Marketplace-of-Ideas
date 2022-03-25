import os 
import numpy as np
import math
ABS_PATH = "/N/u/baotruon/Carbonate/marketplace/igraphvsnx"
# ABS_PATH = ''
DATA_PATH = os.path.join(ABS_PATH, "data")
mode = 'igraph'

#Beta and gamma are only used in making the info system
BETA = list(np.round(i,2) for i in np.linspace(0,1,11))
GAMMA = list(np.round(i,2) for i in np.linspace(0,1,11))
targeting = None

rule all:
    input: expand(os.path.join(DATA_PATH, mode, "beta{beta}gamma{gamma}_network.gml"), beta=BETA, gamma=GAMMA)

# rule run_simulation:
#     input: os.path.join(path, mode, "network.gml")
#     output: os.path.join(path, mode, "meme.pkl"), os.path.join(path, mode, "meme_popularity.pkl")
#     shell: """
#         python3 propagate.py -i {input} -o {output} \
#         --mode {} --trackmeme {} --verbose {} \
#         --eps {} --mu {} --phi {} --alpha {} --theta {}
#     """
#TODO: difference between """ and ""? 
# {var} vs {{var}}?
 
rule make_infosys: #init_net
    #targeting_criterion=None, verbose=False, human_network = None, n_humans=1000, beta=0.1, gamma=0.1
    input: os.path.join(DATA_PATH, 'configs', "betagamma_config_{exp_no}.json")
    # input: 'None'
    output: os.path.join(DATA_PATH, mode, 'intermediate', "{exp_no}_network.gml"
    shell: """
            python3 init_net.py -i {input} -o {output} \ 
            --mode {mode} --targeting {targeting} --beta {beta} --gamma {gamma}
        """ 