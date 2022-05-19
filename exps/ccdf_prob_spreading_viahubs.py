
import json
import infosys.utils as utils 
import igraph as ig
import os
import collections
import matplotlib.pyplot as plt
import numpy as np
import pickle as pkl

import seaborn as sns

ABS_PATH = '/N/slate/baotruon/marketplace'
DATA_PATH = '/N/slate/baotruon/marketplace/data'
sim_num = 1
mode='igraph'
RES_DIR = os.path.join(ABS_PATH,'results', 'vary_thetaphi_1runs_gamma0.005')
TRACKING_DIR = os.path.join(ABS_PATH,'long_results', 'vary_thetaphi_1runs_gamma0.005')
PLOT_PATH = '/N/slate/baotruon/marketplace/plots/vary_thetaphi_1runs_gamma0.005'

print(os.getcwd())
exp_configs = json.load(open(os.path.join(DATA_PATH, 'all_configs.json'),'r'))
EXPS = list(exp_configs['vary_thetaphi'].keys()) #keys are name of exp, format: '{targeting}_{thetaidx}{phiidx}' 

# map available network in `vary_targetgamma` corresponding with the exp
# networks from `vary_targetgamma` has format: '{targeting}{gamma}'
GAMMA = [0.0001, 0.0002, 0.0005, 0.001, 0.002, 0.005, 0.02, 0.05, 0.1, 0.2, 0.5]
TARGETING = [None, 'hubs', 'partisanship', 'conservative', 'liberal', 'misinformation']

EXP_NETWORK = {}

gamma = 0.005 # gamma in the range where targeting has some effect
# need to match with default_targeting
for exp in EXPS:
    if 'none' in exp:
        networkname = '%s%s' %(TARGETING.index(None), GAMMA.index(gamma))
    else: 
        networkname = '%s%s' %(TARGETING.index(exp.split('_')[0]), GAMMA.index(gamma) )
    EXP_NETWORK[exp] = networkname


def prob_spreading_throughhub(exp_no):
    mode='igraph'
    network = os.path.join(DATA_PATH, mode, 'vary_targetgamma', "network_%s.gml" %EXP_NETWORK[exp_no])
    fpath = os.path.join(TRACKING_DIR,'%s.json.gz' %exp_no)
    G = ig.Graph.Read_GML(network)
    verbose = utils.read_json_compressed(fpath)
    deg_mode='in'
    print(network)
    print(fpath)
    bot_memes = []
    human_memes = []
    # humans = [agent_id for agent_id in verbose['all_feeds'][0].keys() if any(map(str.isalpha, agent_id)) is False]
    for agentid, memeids in verbose['all_feeds'][0].items():
        if any(map(str.isalpha, agentid)) is True:
            #skip bots
            continue

        verbose_memes = [meme for meme in verbose['all_memes'][0] if meme['id'] in memeids]
        for meme in verbose_memes:
            spread_through= [int(node) for node in meme['spread_via_agents']]
            indegs = G.degree(spread_through, mode=deg_mode, loops=False)
            largest_indeg = max(indegs)
            if meme['is_by_bot']==1:
                bot_memes += [largest_indeg]
            else:
                human_memes += [largest_indeg]
    return bot_memes, human_memes

if __name__=="__main":
    nohub = 'none_02'
    hub = 'hubs_02'
    botmeme_fname = 'trackhubs_botmemes_gamma0.005.pkl'
    humanmeme_fname = 'trackhubs_humanmemes_gamma0.005.pkl'

    print('Getting data - %s ... ' %nohub)
    bot_memes, human_memes = prob_spreading_throughhub(nohub)
    print('Getting data - %s ... ' %hub)
    hubs_bot_memes, hubs_human_memes = prob_spreading_throughhub(hub)

    
    pkl.dump(bot_memes, open('%s_%s' %(nohub, botmeme_fname), 'wb'))
    pkl.dump(human_memes, open('%s_%s' %(nohub, humanmeme_fname), 'wb'))  

    pkl.dump(hubs_bot_memes, open('%s_%s' %(hub, botmeme_fname), 'wb'))
    pkl.dump(hubs_human_memes, open('%s_%s' %(hub, humanmeme_fname), 'wb'))  
    print('Plotting..')
    figure, (ax1, ax2) = plt.subplots(1,2, figsize=(10, 5), sharex=True)

    sns.ecdfplot(ax=ax1, data = bot_memes, complementary=True, label = 'bot memes')
    sns.ecdfplot(ax=ax1, data = human_memes, complementary=True, label = 'human memes')
    ax1.legend()
    ax1.set_xscale('log')

    sns.ecdfplot(ax=ax2, data = hubs_bot_memes, complementary=True, label = 'bot memes')
    sns.ecdfplot(ax=ax2, data = hubs_human_memes, complementary=True, label = 'human memes')

    ax1.set_title('no targeting')
    ax2.set_title('hubs targeting')
    ax1.set_xlabel('largest in-deg of spreading nodes')
    ax2.set_xlabel('largest in-deg of spreading nodes')

    figure.suptitle('CCDF: Largest in-deg of spreading nodes (final state)')
    plt.tight_layout()

    if utils.make_sure_dir_exists(PLOT_PATH, ''):
        plt.savefig(os.path.join(PLOT_PATH, 'ccdf_hubs_gamma0.05.png'), dpi=300)