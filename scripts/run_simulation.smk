import os 

ABS_PATH = "/N/u/baotruon/Carbonate/marketplace/igraphvsnx"
# ABS_PATH = ''
DATA_PATH = os.path.join(ABS_PATH, "data")

beta = range(0,1,0.1)
gamma = range(0,1,0.1)

rule beta_gamma:
    input: os.path.join(path, mode, "network.gml")
    output: os.path.join(path, mode, "meme.pkl"), os.path.join(path, mode, "meme_popularity.pkl")
    shell: """
        python3 propagate.py -i {input} -o {output} \
        --mode {} --trackmeme {} --verbose {} \
        --eps {} --mu {} --phi {} --alpha {} --theta {}
    """
#TODO: difference between """ and ""? 
# {var} vs {{var}}?
 
rule make_infosys: #init_net
    #targeting_criterion=None, verbose=False, human_network = None, n_humans=1000, beta=0.1, gamma=0.1
    input: os.path.join(path, "follower_network.gml")