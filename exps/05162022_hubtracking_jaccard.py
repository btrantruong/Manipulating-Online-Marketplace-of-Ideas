import json
import infosys.utils as utils 
import igraph as ig
import os
import collections
import matplotlib.pyplot as plt
from scipy.spatial import distance

ABS_PATH = '/N/slate/baotruon/marketplace'
DATA_PATH = '/N/slate/baotruon/marketplace/data'

print(os.getcwd())
exp_configs = json.load(open(os.path.join(DATA_PATH, 'all_configs.json'),'r'))
EXPS = list(exp_configs['vary_thetaphi'].keys()) #keys are name of exp, format: '{targeting}_{thetaidx}{phiidx}' 

# map available network in `vary_targetgamma` corresponding with the exp
# networks from `vary_targetgamma` has format: '{targeting}{gamma}'
GAMMA = [0.0001, 0.0002, 0.0005, 0.001, 0.002, 0.005, 0.02, 0.05, 0.1, 0.2, 0.5]
TARGETING = [None, 'hubs', 'partisanship', 'conservative', 'liberal', 'misinformation']

EXP_NETWORK = {}

gamma = 0.1 # gamma in the range where targeting has some effect
# need to match with default_targeting
for exp in EXPS:
    if 'none' in exp:
        networkname = '%s%s' %(TARGETING.index(None), GAMMA.index(gamma))
    else: 
        networkname = '%s%s' %(TARGETING.index(exp.split('_')[0]), GAMMA.index(gamma) )
    EXP_NETWORK[exp] = networkname

sim_num = 1
mode='igraph'
RES_DIR = os.path.join(ABS_PATH,'results', 'vary_thetaphi_%sruns' %sim_num)
TRACKING_DIR = os.path.join(ABS_PATH,'long_results', 'vary_thetaphi_%sruns' %sim_num)


def jaccard_sim_meme_spreading_indegs(exp_no):
    network = os.path.join(DATA_PATH, mode, 'vary_targetgamma', "network_%s.gml" %EXP_NETWORK[exp_no])
    fpath = os.path.join(TRACKING_DIR,'%s.json.gz' %exp_no)
    G = ig.Graph.Read_GML(network)
    verbose = utils.read_json_compressed(fpath)
    print('network: ', network)

    meme_spreading_indegs = []
    for meme in verbose['all_memes'][0]:
        if meme['is_by_bot']==1:
            spread_through= [int(node) for node in meme['spread_via_agents']]
            indegs = G.degree(spread_through, mode=mode, loops=False)
            meme_spreading_indegs += [indegs]
    
    # Get pair-wise jaccard distance:
    jc = []
    for idx,meme in enumerate(meme_spreading_indegs):
        jaccards = [distance.jaccard(meme, othermeme) for othermeme in meme_spreading_indegs[idx:]]
        jc +=jaccards
    return jc


nohub = 'none_04'
hub = 'hubs_04'
nohub_jc = jaccard_sim_meme_spreading_indegs(nohub)
hub_jc = jaccard_sim_meme_spreading_indegs(hub)