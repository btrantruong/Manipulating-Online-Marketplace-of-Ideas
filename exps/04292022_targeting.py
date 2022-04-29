""" Plot Degree of bot followers 
"""
import numpy as np 
import matplotlib.pyplot as plt
import infosys.ig_utils as ig_utils
from collections import Counter
import os
import infosys.utils as utils 

#debug
# ABS_PATH=''
# BETAS = [0.1, 0.5]
# GAMMAS = [ 0.1,0.5]

ABS_PATH = '/N/u/baotruon/Carbonate/marketplace'
DATA_PATH = '/N/slate/baotruon/marketplace/data'
TARGETING = [None, 'hubs']
COLORS = ['blue', 'orange']

BETAS = [0.001, 0.01, 0.1, 0.5]
GAMMAS = [0.001, 0.01, 0.1, 0.5]
human_net = os.path.join(DATA_PATH, 'follower_network.gml')
plot_path = os.path.join(ABS_PATH, 'exps')

def get_prob_dist(degs):
    counts = Counter(degs)
    P_k = []
    k_count = dict(sorted(counts.items()))
    for k,count in k_count.items():
        P_k += [(k, count/len(degs))]
    return zip(*P_k)


for kdx,beta in enumerate(BETAS):
    plt_no = 0
    # fig, axs = plt.subplots(2,2,  sharex=True, sharey=True)
    fig, axs = plt.subplots(2,4, figsize=(16,8), sharex=True, sharey=True)
    for idx,(color,targeting) in enumerate(zip(COLORS, TARGETING)):
        for jdx,gamma in enumerate(GAMMAS):
            net_specs = {
                    "targeting_criterion":targeting,
                    "human_network": human_net, 
                    # "n_humans": 100,
                    "beta": beta,
                    "gamma": gamma,
                    "track_bot_followers": True
                }
            
            G, degs = ig_utils.init_net(**net_specs)
            k, Pk =  get_prob_dist(degs)
            ax = axs[idx,jdx]
            ax.scatter(k, Pk, color=color, alpha=0.8)
            ax.set_xscale('log')
            ax.set_yscale('log')
            ax.set_title('%s targeting gamma %s' %(targeting, gamma))
            if jdx==0:
                ax.set_xlabel('k')
                ax.set_ylabel('Pk')
            if plt_no%4==0:
                print('--plot no: ', plt_no)
            plt_no+=1
    # plt.tight_layout()        
    fig.suptitle('Degree of human bot followers', fontsize=12)
    if utils.make_sure_dir_exists(plot_path, '04292022_check_targeting'):
        plt.savefig(os.path.join(plot_path, '04292022_check_targeting', 'beta%s.png'%beta), dpi=300)
    # plt.show()
