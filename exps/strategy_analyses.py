import json
import infosys.utils as utils 
import igraph as ig
import os
import collections
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pickle as pkl
import collections
import sys
from  scipy.stats import entropy

logger = utils.get_logger(__name__)

""" Only consider human spreading channels!"""

def get_exp_network_map(config_fname):
    exp_configs = json.load(open(config_fname,'r'))
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

    return EXP_NETWORK


def plot_degree_dist(graph, plot_fpath=None, mode='in'):
    vertices = range(len(graph.vs)) #vertices index
    degs = graph.degree(vertices, mode=mode, loops=False)
    degs = dict(collections.Counter(degs))
    k_per_deg = dict(sorted(degs.items()))
    p_k = {deg: num/len(vertices) for deg,num in k_per_deg.items()}
    
    fig,ax = plt.subplots()
    ax.scatter(p_k.keys(),p_k.values())
    
    ax.set_yscale('log')
    ax.set_xscale('log')
    ax.set_ylabel('p_k')
    ax.set_xlabel('k')
    ax.set_title('Degree distribution (%s degree)' %mode)

    if plot_fpath is not None:
        fig.savefig(plot_fpath, dpi=300)
        plt.close(fig)
    else:
        fig.show()


def plot_quality_timestep(nostrag_quality, strag_quality, plot_fpath=None):
    fig,ax = plt.subplots()

    ax.scatter(range(len(strag_quality)), strag_quality, label='targeting')
    ax.scatter(range(len(nostrag_quality)), nostrag_quality, label='no targeting')
    
    ax.set_ylabel('quality')
    ax.set_xlabel('t')
    ax.set_title('Quality across timesteps')
    ax.legend()
    
    if plot_fpath is not None:
        fig.savefig(plot_fpath, dpi=300)
        plt.close(fig)
    else:
        fig.show()


def info_memeshares_channel_indegs(G, verbose, deg_mode='in'):
    # Helper: Scatter plot of number of shares vs indeg of spreading channel (for junk memes)
    # return a dict of information to calculate: 
    # % of memes spread only by bot; num shares, indeg of nodes spreading each meme
    # (Stats across simulation)

    info = collections.defaultdict(lambda:[])
    keys= ['num_humans', 'num_bots', 'human_spread_only_viabot', 'bot_spread_only_viabot']
    for k in keys:
        info[k] = 0

    human_agents = [int(node['id']) for node in G.vs if node['bot']==0]

    for meme in verbose['all_memes'][0]: #since verbose['all_memes'] is a list over multiple simulations
        spread_through = [int(node) for node in meme['spread_via_agents']]
        human_channels = set(human_agents) & set(spread_through)

        if len(human_channels)>0:
            indegs = G.degree(list(human_channels), mode=deg_mode, loops=False)
            largest_indeg = max(indegs)
            
            if meme['is_by_bot']==1:
                info['num_bots']+=1
                info['bot_largest_spreading_nodes'] += [largest_indeg]  
                info['botmeme_shares'] += [meme['human_shares']]
                info['botmeme_fitness'] += [meme['fitness']]
            else:
                info['num_humans']+=1
                info['human_largest_spreading_nodes'] += [largest_indeg]
                info['humanmeme_shares'] += [meme['human_shares']]
                info['humanmeme_fitness'] += [meme['fitness']]
                info['humanmeme_quality'] += [meme['quality']]
        else:
            if meme['is_by_bot']==1:
                info['bot_spread_only_viabot']+=1
            else:
                info['human_spread_only_viabot']+=1
        
    return info


def final_prob_spreading_throughhub(G, verbose):
    # Stat final state
    # Helper  ccdf_final_spreadingnodes
    final_info = collections.defaultdict(lambda:[])
    deg_mode='in'

    human_agents = [int(node['id']) for node in G.vs if node['bot']==0]

    for agentid, memeids in verbose['all_feeds'][0].items():
        if any(map(str.isalpha, agentid)) is True:
            #skip bots
            continue
        
        memeinfo = (meme for meme in verbose['all_memes'][0] if meme['id'] in memeids)
        # verbose_memes = [meme for meme in verbose['all_memes'][0] if meme['id'] in memeids]
        for meme in memeinfo:
            spread_through= [int(node) for node in meme['spread_via_agents']]
            human_channels = set(human_agents) & set(spread_through)

            if len(human_channels)>0:
                indegs = G.degree(list(human_channels), mode=deg_mode, loops=False)
                largest_indeg = max(indegs)

                if meme['is_by_bot']==1:
                    final_info['botmeme_spread'] += [largest_indeg]
                    final_info['botmeme_shares'] += [meme['human_shares']]
                else:
                    final_info['humanmeme_spread'] += [largest_indeg]
                    final_info['humanmeme_shares'] += [meme['human_shares']]
    return final_info


def final_entropy(verbose, base=2):
    # Get entropy of the system from the distribution of probability that a feed contains a bot meme. 

    bot_probs = []
    for agentid, memeids in verbose['all_feeds'][0].items():
        if any(map(str.isalpha, agentid)) is True:
            #skip bots
            continue
        
        bot_memes = [meme for meme in verbose['all_memes'][0] if ((meme['id'] in memeids) and meme['is_by_bot']==1)]
        bot_probs += [len(bot_memes)/len(memeids) if len(memeids)>0 else 0]

    system_entropy = entropy(bot_probs, base=base)
    return system_entropy


def ccdf_quality_between_strategies(nostrag_humanquality, strag_humanquality, plot_fpath=None, log_log=False):
    # CCDF of quality of only human memes - 2 lines (none & hubs-targeting)

    figure, ax = plt.subplots()

    if log_log is True:
        ax.set_xscale('log')
        ax.set_yscale('log')
    
    sns.ecdfplot(ax=ax, data = nostrag_humanquality, complementary=True, label = 'no targeting')
    sns.ecdfplot(ax=ax, data = strag_humanquality, complementary=True, label = 'hub targeting')
    ax.set_xlabel('Quality')
    ax.legend()
    ax.set_title('CCDF: Quality of human memes between strategies')

    figure.tight_layout()
    if plot_fpath is not None:
        figure.savefig(plot_fpath, dpi=300)
        plt.close(figure)
    else:
        figure.show()


def ccdf_fitness_within_strategies_panel(nostrag_botfitness, nostrag_humanfitness, strag_botfitness, strag_humanfitness, plot_fpath=None, log_log=False):
    # CCDF of the fitness of memes - 2 lines (bot & human memes), 2 panels (none & hubs-targeting)
    
    figure, (ax1, ax2) = plt.subplots(1,2, figsize=(10, 5), sharex=True, sharey=True)
    
    if log_log is True:
        ax1.set_xscale('log')
        ax1.set_yscale('log')
    
    sns.ecdfplot(ax=ax1, data = nostrag_botfitness, complementary=True, label = 'bot memes')
    sns.ecdfplot(ax=ax1, data = nostrag_humanfitness, complementary=True, label = 'human memes')
    ax1.legend()

    sns.ecdfplot(ax=ax2, data = strag_botfitness, complementary=True, label = 'bot memes')
    sns.ecdfplot(ax=ax2, data = strag_humanfitness, complementary=True, label = 'human memes')
    ax2.legend()

    ax1.set_title('No targeting')
    ax2.set_title('Hubs targeting')
    ax1.set_xlabel('Fitness')
    ax2.set_xlabel('Fitness')

    figure.suptitle('CCDF: Fitness of memes shared during simulation')
    figure.tight_layout()
    if plot_fpath is not None:
        figure.savefig(plot_fpath, dpi=300)
        plt.close(figure)
    else:
        figure.show()


def ccdf_fitness_between_strategies_panel(nostrag_botfitness, nostrag_humanfitness, strag_botfitness, strag_humanfitness, plot_fpath=None, log_log=False):
    # CCDF of the fitness ofmemes - 2 lines (none & hubs-targeting), 2 panels (bot & human memes)

    figure, (ax1, ax2) = plt.subplots(1,2, figsize=(10, 5), sharex=True, sharey=True)
    
    if log_log is True:
        ax1.set_xscale('log')
        ax1.set_yscale('log')
    
    sns.ecdfplot(ax=ax1, data = nostrag_botfitness, complementary=True, label = 'no targeting')
    sns.ecdfplot(ax=ax1, data = strag_botfitness, complementary=True, label = 'targeting')
    ax1.legend()

    sns.ecdfplot(ax=ax2, data = nostrag_humanfitness, complementary=True, label = 'no targeting')
    sns.ecdfplot(ax=ax2, data = strag_humanfitness, complementary=True, label = 'targeting')
    ax2.legend()

    ax1.set_title('Bot memes')
    ax2.set_title('Human memes')
    ax1.set_xlabel('Fitness')
    ax2.set_xlabel('Fitness')

    figure.suptitle('CCDF: Fitness of memes shared during simulation')
    figure.tight_layout()
    if plot_fpath is not None:
        figure.savefig(plot_fpath, dpi=300)
        plt.close(figure)
    else:
        figure.show()


def ccdf_share_between_strategies(nostrag_botshares, strag_botshares, plot_fpath=None, log_log=True):
    # CCDF of shares of bot memes - 2 lines (none & hubs-targeting)

    figure, ax = plt.subplots()

    if log_log is True:
        ax.set_xscale('log')
        ax.set_yscale('log')
    
    sns.ecdfplot(ax=ax, data = nostrag_botshares, complementary=True, label = 'no targeting')
    sns.ecdfplot(ax=ax, data = strag_botshares, complementary=True, label = 'hub targeting')
    ax.set_xlabel('Number of shares')
    ax.legend()
    ax.set_title('CCDF: Number of shares (bot memes) between strategies')

    figure.tight_layout()
    if plot_fpath is not None:
        figure.savefig(plot_fpath, dpi=300)
        plt.close(figure)
    else:
        figure.show()


def ccdf_share_within_strategies_panel(nostrag_botshares, nostrag_humanshares, strag_botshares, strag_humanshares, plot_fpath=None, log_log=True):
    # CCDF of the shares of memes - 2 lines (bot & human memes), 2 panels (none & hubs-targeting)
    
    figure, (ax1, ax2) = plt.subplots(1,2, figsize=(10, 5), sharex=True, sharey=True)
    
    if log_log is True:
        ax1.set_xscale('log')
        ax1.set_yscale('log')
    
    sns.ecdfplot(ax=ax1, data = nostrag_botshares, complementary=True, label = 'bot memes')
    sns.ecdfplot(ax=ax1, data = nostrag_humanshares, complementary=True, label = 'human memes')
    ax1.legend()

    sns.ecdfplot(ax=ax2, data = strag_botshares, complementary=True, label = 'bot memes')
    sns.ecdfplot(ax=ax2, data = strag_humanshares, complementary=True, label = 'human memes')
    ax2.legend()

    ax1.set_title('No targeting')
    ax2.set_title('Hubs targeting')
    ax1.set_xlabel('number of shares')
    ax2.set_xlabel('number of shares')

    figure.suptitle('CCDF: Total number of shares during simulation')
    figure.tight_layout()
    if plot_fpath is not None:
        figure.savefig(plot_fpath, dpi=300)
        plt.close(figure)
    else:
        figure.show()

def ccdf_share_between_strategies_panel(nostrag_botshares, nostrag_humanshares, strag_botshares, strag_humanshares, plot_fpath=None, log_log=True):
    # CCDF of shares of bot memes - 2 lines (none & hubs-targeting), 2 panels (bot & human memes)

    figure, (ax1, ax2) = plt.subplots(1,2, figsize=(10, 5), sharex=True, sharey=True)
    
    if log_log is True:
        ax1.set_xscale('log')
        ax1.set_yscale('log')
    
    sns.ecdfplot(ax=ax1, data = nostrag_botshares, complementary=True, label = 'no targeting')
    sns.ecdfplot(ax=ax1, data = strag_botshares, complementary=True, label = 'targeting')
    ax1.legend()

    sns.ecdfplot(ax=ax2, data = nostrag_humanshares, complementary=True, label = 'no targeting')
    sns.ecdfplot(ax=ax2, data = strag_humanshares, complementary=True, label = 'targeting')
    ax2.legend()

    ax1.set_title('Bot memes')
    ax2.set_title('Human memes')
    ax1.set_xlabel('number of shares')
    ax2.set_xlabel('number of shares')

    figure.suptitle('CCDF: Total number of shares during simulation')
    figure.tight_layout()
    if plot_fpath is not None:
        figure.savefig(plot_fpath, dpi=300)
        plt.close(figure)
    else:
        figure.show()


def ccdf_final_spreadingnodes(nostrag_bot_memes, nostrag_human_memes, strag_bot_memes, strag_human_memes, plot_fpath=None, log_log=True):
    figure, (ax1, ax2) = plt.subplots(1,2, figsize=(10, 5), sharex=True, sharey=True)

    sns.ecdfplot(ax=ax1, data = nostrag_bot_memes, complementary=True, label = 'bot memes')
    sns.ecdfplot(ax=ax1, data = nostrag_human_memes, complementary=True, label = 'human memes')
    ax1.legend()
    if log_log is True:
        ax1.set_xscale('log')
        ax1.set_yscale('log')

    sns.ecdfplot(ax=ax2, data = strag_bot_memes, complementary=True, label = 'bot memes')
    sns.ecdfplot(ax=ax2, data = strag_human_memes, complementary=True, label = 'human memes')

    ax1.set_title('no targeting')
    ax2.set_title('hubs targeting')
    ax1.set_xlabel('Largest in-deg')
    ax2.set_xlabel('Largest in-deg')

    figure.suptitle('CCDF: Largest in-deg of human spreading nodes (final state)')
    figure.tight_layout()
    if plot_fpath is not None:
        figure.savefig(plot_fpath, dpi=300)
        plt.close(figure)
    else:
        plt.show()


def ccdf_final_spreadingnodes_between_strategies(nostrag_bot_memes, nostrag_human_memes, strag_bot_memes, strag_human_memes, plot_fpath=None, log_log=True):
    figure, (ax1, ax2) = plt.subplots(1,2, figsize=(10, 5), sharex=True, sharey=True)

    sns.ecdfplot(ax=ax1, data = nostrag_bot_memes, complementary=True, label = 'no targeting')
    sns.ecdfplot(ax=ax1, data = strag_bot_memes, complementary=True, label = 'targeting')
    ax1.legend()
    if log_log is True:
        ax1.set_xscale('log')
        ax1.set_yscale('log')

    sns.ecdfplot(ax=ax2, data = nostrag_human_memes, complementary=True, label = 'no targeting')
    sns.ecdfplot(ax=ax2, data = strag_human_memes, complementary=True, label = 'targeting')

    ax1.set_title('Bot memes')
    ax2.set_title('Human memes')
    ax1.set_xlabel('Largest in-deg')
    ax2.set_xlabel('Largest in-deg')

    figure.suptitle('CCDF: Largest in-deg of human spreading nodes (final state)')
    figure.tight_layout()
    if plot_fpath is not None:
        figure.savefig(plot_fpath, dpi=300)
        plt.close(figure)
    else:
        plt.show()


def jointplot_final_shares_spread(final_info, meme_type='bot', plot_fpath=None, xlog=False, ylog=False):
    if meme_type=='bot':
        snsplot = sns.jointplot(data=final_info, x='botmeme_spread', y='botmeme_shares', kind="hist")
    elif meme_type=='human':
        snsplot = sns.jointplot(data=final_info, x='humanmeme_spread', y='humanmeme_shares', kind="hist")

    if xlog is True:
        snsplot.ax_joint.set_xscale('log')
    if ylog is True:
        snsplot.ax_joint.set_yscale('log')

    if plot_fpath is not None:
        snsplot.figure.savefig(plot_fpath, dpi=300)
        # plt.close(snsplot.figure)

def plot_shares_vs_indeg(none_largest_indegs, none_shares, hub_largest_indegs, hub_shares, plot_fpath=None):
    # Scatter plot of number of shares vs indeg of spreading channel (for junk memes)
    fig, (ax1,ax2)= plt.subplots(1,2, sharey=True, sharex=True, figsize=(8,5))
    ax1.scatter(none_largest_indegs, none_shares)
    ax1.set_title('No targeting')
    ax1.set_xlabel('Avg in-degree of nodes spreading this meme')
    ax1.set_ylabel('shares')
    ax1.set_yscale('log')

    ax2.scatter(hub_largest_indegs, hub_shares)
    ax2.set_title('Hubs targeting')
    ax2.set_xlabel('Avg in-degree of nodes spreading this meme')
    ax2.set_ylabel('shares')

    fig.suptitle('Number of shares vs. Indeg of spreading channel (Memes by bots)')
    fig.tight_layout()
    if plot_fpath is not None:
        fig.savefig(plot_fpath, dpi=300)
        plt.close(fig)
    else:
        plt.show()

def ccdf_hubness_within_strategies(none_bot_spread, none_human_spread, hubs_bot_spread, hubs_human_spread, plot_fpath=None, log_log=True):
    # CCDF of the hubness (largest in-deg of a meme's spreading nodes) - 2 lines (bot & human memes), 2 panels (none & hubs-targeting)
    
    figure, (ax1, ax2) = plt.subplots(1,2, figsize=(10, 5), sharex=True, sharey=True)

    sns.ecdfplot(ax=ax1, data = none_bot_spread, complementary=True, label = 'bot memes')
    sns.ecdfplot(ax=ax1, data = none_human_spread, complementary=True, label = 'human memes')
    ax1.legend()

    if log_log is True:
        ax1.set_xscale('log')
        ax1.set_yscale('log')

    sns.ecdfplot(ax=ax2, data = hubs_bot_spread, complementary=True, label = 'bot memes')
    sns.ecdfplot(ax=ax2, data = hubs_human_spread, complementary=True, label = 'human memes')

    ax1.set_title('no targeting')
    ax2.set_title('hubs targeting')
    ax1.set_xlabel('largest in-deg of spreading nodes')
    ax2.set_xlabel('largest in-deg of spreading nodes')
    ax2.legend()    

    figure.suptitle('CCDF: Largest in-deg of human spreading nodes (across whole simulation)')
    figure.tight_layout()
    if plot_fpath is not None:
        figure.savefig(plot_fpath, dpi=300)
        plt.close(figure)
    else:
        plt.show()


def ccdf_hubness_between_strategies(none_bot_spread, none_human_spread, hubs_bot_spread, hubs_human_spread, plot_fpath=None, log_log=True):
    # CCDF of the hubness (largest in-deg of a meme's spreading nodes) - 2 lines (none & hubs-targeting), 2 panels (bot & human memes)
    figure, (ax1, ax2) = plt.subplots(1,2, figsize=(10, 5), sharex=True, sharey=True)

    sns.ecdfplot(ax=ax1, data = none_bot_spread, complementary=True, label = 'no targeting')
    sns.ecdfplot(ax=ax1, data = hubs_bot_spread, complementary=True, label = 'hubs-targeting')
    ax1.legend()

    if log_log is True:
        ax1.set_xscale('log')
        ax1.set_yscale('log')

    sns.ecdfplot(ax=ax2, data = none_human_spread, complementary=True, label = 'no targeting')
    sns.ecdfplot(ax=ax2, data = hubs_human_spread, complementary=True, label = 'hubs-targeting')
    ax2.legend()

    ax1.set_title('Bot memes')
    ax2.set_title('Human memes')
    ax1.set_xlabel('largest in-deg of spreading nodes')
    ax2.set_xlabel('largest in-deg of spreading nodes')

    figure.suptitle('CCDF: Largest in-deg of human spreading nodes (across whole simulation)')
    figure.tight_layout()
    if plot_fpath is not None:
        figure.savefig(plot_fpath, dpi=300)
        plt.close(figure)
    else:
        plt.show()


def separate_shares_viahubs(spreading_degs, meme_shares, hubsize=1000):
    # Helper ccdf_viahubshares, ccdf_viahubfitness
    viahub = []
    not_viahub = []
    for deg,share in zip(spreading_degs, meme_shares):
        if deg>=hubsize:
            viahub+=[share]
        else:
            not_viahub +=[share]
    return viahub, not_viahub


def ccdf_viahubshares_within_strategies(spreading_nodes, meme_shares, strag_spreading_nodes, strag_meme_shares, hubsize=1000, plot_fpath=None, log_log=True):
    # CCDF of the shares (of bot memes) - 2 lines (via hubs vs not via hub), 2 panels (no target vs target)
    viahub, not_viahub = separate_shares_viahubs(spreading_nodes, meme_shares, hubsize=hubsize)
    strag_viahub, strag_not_viahub = separate_shares_viahubs(strag_spreading_nodes, strag_meme_shares, hubsize=hubsize)
    
    figure, (ax1, ax2) = plt.subplots(1,2, figsize=(10, 5), sharex=True, sharey=True)

    sns.ecdfplot(ax=ax1, data = viahub, complementary=True, label = 'via hubs')
    sns.ecdfplot(ax=ax1, data = not_viahub, complementary=True, label = 'not via hub')
    ax1.legend()
    if log_log is True:
        ax1.set_xscale('log')
        ax1.set_yscale('log')
    sns.ecdfplot(ax=ax2, data = strag_viahub, complementary=True, label = 'via hubs')
    sns.ecdfplot(ax=ax2, data = strag_not_viahub, complementary=True, label = 'not via hub')

    ax1.set_title('No targeting')
    ax2.set_title('Targeting')
    ax1.set_xlabel('Shares')
    ax2.set_xlabel('Shares')

    figure.suptitle('CCDF: Number of shares of bot memes')
    figure.tight_layout()
    if plot_fpath is not None:
        figure.savefig(plot_fpath, dpi=300)
        plt.close(figure)
    else:
        plt.show()


def ccdf_viahubshares_between_strategies(spreading_nodes, meme_shares, strag_spreading_nodes, strag_meme_shares, hubsize=1000, plot_fpath=None, log_log=True):
    # CCDF of the shares (of bot memes) - 2 lines (no target vs target), 2 panels (via hubs vs not via hub)
    viahub, not_viahub = separate_shares_viahubs(spreading_nodes, meme_shares, hubsize=hubsize)
    strag_viahub, strag_not_viahub = separate_shares_viahubs(strag_spreading_nodes, strag_meme_shares, hubsize=hubsize)
    
    figure, (ax1, ax2) = plt.subplots(1,2, figsize=(10, 5), sharex=True, sharey=True)

    sns.ecdfplot(ax=ax1, data = viahub, complementary=True, label = 'no targeting')
    sns.ecdfplot(ax=ax1, data = strag_viahub, complementary=True, label = 'targeting')

    ax1.legend()
    if log_log is True:
        ax1.set_xscale('log')
        ax1.set_yscale('log')
    sns.ecdfplot(ax=ax2, data = not_viahub, complementary=True, label = 'no targeting')
    sns.ecdfplot(ax=ax2, data = strag_not_viahub, complementary=True, label = 'targeting')

    ax1.set_title('Via hubs')
    ax2.set_title('Not via hub')
    ax1.set_xlabel('Shares')
    ax2.set_xlabel('Shares')

    figure.suptitle('CCDF: Number of shares of bot memes')
    figure.tight_layout()
    if plot_fpath is not None:
        figure.savefig(plot_fpath, dpi=300)
        plt.close(figure)
    else:
        plt.show()


def ccdf_viahubfitness_within_strategies(meme_tuples, hubsize=1000, plot_fpath=None, log_log=False):
    # meme_tuples: dict of line name - tuples of (spreading_nodes, meme_fitness)
    # CCDF of the fitness (of bot memes) - 4 lines (via hubs vs not via hub - for bots and human memes), 2 panels (no target vs target)

    bot_viahub, bot_not_viahub = separate_shares_viahubs(*meme_tuples['bot_notargeting'], hubsize=hubsize) #Reuse the same function as shares
    botstrag_viahub, botstrag_not_viahub = separate_shares_viahubs(*meme_tuples['bot_targeting'], hubsize=hubsize)
    
    human_viahub, human_not_viahub = separate_shares_viahubs(*meme_tuples['human_notargeting'], hubsize=hubsize) #Reuse the same function as shares
    humanstrag_viahub, humanstrag_not_viahub = separate_shares_viahubs(*meme_tuples['human_targeting'], hubsize=hubsize)

    figure, (ax1, ax2) = plt.subplots(1,2, figsize=(10, 5), sharex=True, sharey=True)

    sns.ecdfplot(ax=ax1, data = bot_viahub, complementary=True, label = 'Bot via hubs')
    sns.ecdfplot(ax=ax1, data = bot_not_viahub, complementary=True, label = 'Bot not via hub')
    sns.ecdfplot(ax=ax1, data = human_viahub, complementary=True, label = 'Human via hubs')
    sns.ecdfplot(ax=ax1, data = human_not_viahub, complementary=True, label = 'Human not via hub')

    ax1.legend()

    if log_log is True:
        ax1.set_xscale('log')
        ax1.set_yscale('log')
    
    sns.ecdfplot(ax=ax2, data = botstrag_viahub, complementary=True, label = 'Bot via hubs')
    sns.ecdfplot(ax=ax2, data = botstrag_not_viahub, complementary=True, label = 'Bot not via hub')
    sns.ecdfplot(ax=ax2, data = humanstrag_viahub, complementary=True, label = 'Human via hubs')
    sns.ecdfplot(ax=ax2, data = humanstrag_not_viahub, complementary=True, label = 'Human not via hub')

    ax1.set_title('No targeting')
    ax2.set_title('Targeting')
    ax1.set_xlabel('fitness')
    ax2.set_xlabel('fitness')

    figure.suptitle('CCDF: Fitness of memes')
    figure.tight_layout()
    if plot_fpath is not None:
        figure.savefig(plot_fpath, dpi=300)
        plt.close(figure)
    else:
        plt.show()


def save_stats(nostrag_info, strag_info, fpath):
    with open(fpath, 'w') as outfile:
        for name,info in {'NO STRATEGY': nostrag_info, 'HUB STRATEGY': strag_info}.items():
            info['bot_spread_only_viabot_pct'] = np.round(info['bot_spread_only_viabot']/info['num_bots'], 2)
            info['human_spread_only_viabot_pct'] = np.round(info['human_spread_only_viabot']/info['num_humans'], 2)
            outfile.write('%s \n' %name)
            for k,v in info.items():
                if isinstance(v,list) is True:
                    continue
                else:
                    outfile.write('%s %s \n' %(k,v))
    logger.info('Finished saving stats!')


def save_entropy(nostrag_entropy, strag_entropy, fpath):
    with open(fpath, 'a+') as outfile:
        outfile.write('ENTROPY: \n')
        outfile.write('No targeting: %s \n' %np.round(nostrag_entropy,4))
        outfile.write('With targeting: %s \n' %np.round(strag_entropy,4))
    logger.info('Finished saving entropy to existing file!')


if __name__=="__main__":
    logger.info('WORKING DIR: %s' %(os.getcwd()))
    ABS_PATH = '/N/slate/baotruon/marketplace'
    DATA_PATH = '/N/slate/baotruon/marketplace/data'
    
    config_fname= os.path.join(DATA_PATH, 'all_configs.json')
    exp2network = get_exp_network_map(config_fname)
    
    # CHANGE THESE VARS FOR OTHER INFILTRATION VALUES
    # exp = 'vary_thetaphi_1runs_gamma0.005'
    # hub_expname='hubs_04'
    # none_expname='none_04'

    exp=sys.argv[1]
    hub_expname = sys.argv[2]
    none_expname = sys.argv[3]
    plot_folder=sys.argv[4]

    RES_DIR = os.path.join(ABS_PATH,'results', exp)
    TRACKING_DIR = os.path.join(ABS_PATH,'long_results',exp)
    NETWORK_PATH = os.path.join(DATA_PATH, 'igraph/vary_targetgamma')
    PLOT_DIR = os.path.join(ABS_PATH,plot_folder,exp)
    utils.make_sure_dir_exists(PLOT_DIR, '')


    hub_network = os.path.join(NETWORK_PATH, "network_%s.gml" %exp2network[hub_expname])
    hub_verbose = utils.read_json_compressed(os.path.join(TRACKING_DIR,'%s.json.gz' %hub_expname))
    hub_graph = ig.Graph.Read_GML(hub_network)
    
    none_network = os.path.join(NETWORK_PATH, "network_%s.gml" %exp2network[none_expname])
    none_verbose = utils.read_json_compressed(os.path.join(TRACKING_DIR,'%s.json.gz' %none_expname))
    none_graph = ig.Graph.Read_GML(none_network)

    hubstrag_info = info_memeshares_channel_indegs(hub_graph, hub_verbose, deg_mode='in')
    nostrag_info =  info_memeshares_channel_indegs(none_graph, none_verbose, deg_mode='in')
    try:
        # save_stats(nostrag_info, hubstrag_info, os.path.join(PLOT_DIR, 'stats_%s%s.txt' %(none_expname, hub_expname)))

        # plot_degree_dist(none_graph, plot_fpath=os.path.join(PLOT_DIR, 'degree_dist_%s.png' %none_expname), mode='in')
        # plot_degree_dist(hub_graph, plot_fpath=os.path.join(PLOT_DIR, 'degree_dist_%s.png' %hub_expname), mode='in')

        # plot_quality_timestep(none_verbose['quality_timestep'][0], hub_verbose['quality_timestep'][0], 
        #                         plot_fpath=os.path.join(PLOT_DIR, 'quality_timestep%s%s.png' %(none_expname, hub_expname)))

        # none_bot_spread= nostrag_info['bot_largest_spreading_nodes']
        # none_human_spread= nostrag_info['human_largest_spreading_nodes']
        # hubs_bot_spread= hubstrag_info['bot_largest_spreading_nodes']
        # hubs_human_spread= hubstrag_info['human_largest_spreading_nodes']

        
        # plot_shares_vs_indeg(none_bot_spread, nostrag_info['botmeme_shares'],
        #                         hubs_bot_spread, hubstrag_info['botmeme_shares'], 
        #                         plot_fpath=os.path.join(PLOT_DIR, 'shares_indeg_%s%s.png' %(none_expname, hub_expname)))
        
        # ccdf_quality_between_strategies(nostrag_info['humanmeme_quality'], hubstrag_info['humanmeme_quality'], 
        #                                 plot_fpath=os.path.join(PLOT_DIR, 'quality_between_strategies_%s%s.png' %(none_expname, hub_expname)))

        # ccdf_fitness_within_strategies_panel(nostrag_info['botmeme_fitness'], nostrag_info['humanmeme_fitness'], 
        #                                     hubstrag_info['botmeme_fitness'], hubstrag_info['humanmeme_fitness'],  
        #                                     plot_fpath=os.path.join(PLOT_DIR, 'fitness_within_strategies_%s%s.png' %(none_expname, hub_expname)))

        # ccdf_fitness_between_strategies_panel(nostrag_info['botmeme_fitness'], nostrag_info['humanmeme_fitness'], 
        #                                     hubstrag_info['botmeme_fitness'], hubstrag_info['humanmeme_fitness'],  
        #                                     plot_fpath=os.path.join(PLOT_DIR, 'fitness_between_strategies_%s%s.png' %(none_expname, hub_expname)))

        # fitness_dict={
        #     'bot_notargeting': (none_bot_spread, nostrag_info['botmeme_fitness']),
        #     'bot_targeting': (hubs_bot_spread, hubstrag_info['botmeme_fitness']),
        #     'human_notargeting': (none_human_spread, nostrag_info['humanmeme_fitness']),
        #     'human_targeting': (hubs_human_spread, hubstrag_info['humanmeme_fitness'])
        # }

        # ccdf_viahubfitness_within_strategies(fitness_dict, hubsize=1000,
        #                                      plot_fpath=os.path.join(PLOT_DIR, 'viahubfitness_%s%s.png' %(none_expname, hub_expname)))


        # ccdf_share_between_strategies(nostrag_info['botmeme_shares'], hubstrag_info['botmeme_shares'], 
        #                             plot_fpath=os.path.join(PLOT_DIR, 'shares_between_strategies_%s%s_single.png' %(none_expname, hub_expname)), 
        #                             log_log=True)

        # ccdf_share_between_strategies_panel(nostrag_info['botmeme_shares'], nostrag_info['humanmeme_shares'],  hubstrag_info['botmeme_shares'], hubstrag_info['humanmeme_shares'], 
        #                                     plot_fpath=os.path.join(PLOT_DIR, 'shares_between_strategies_%s%s.png' %(none_expname, hub_expname)), 
        #                                     log_log=True)

        # ccdf_share_within_strategies_panel(nostrag_info['botmeme_shares'], nostrag_info['humanmeme_shares'],  hubstrag_info['botmeme_shares'], hubstrag_info['humanmeme_shares'], 
        #                                     plot_fpath=os.path.join(PLOT_DIR, 'shares_within_strategies_%s%s.png' %(none_expname, hub_expname)), 
        #                                     log_log=True)

        # ccdf_hubness_within_strategies(none_bot_spread, none_human_spread, hubs_bot_spread, hubs_human_spread, 
        #                                         plot_fpath=os.path.join(PLOT_DIR, 'hubness_within_strategies_%s%s.png' %(none_expname, hub_expname)), 
        #                                         log_log=True)
        
        # ccdf_hubness_within_strategies(none_bot_spread, none_human_spread, hubs_bot_spread, hubs_human_spread, 
        #                                         plot_fpath=os.path.join(PLOT_DIR, 'hubness_within_strategies_%s%s_norm.png' %(none_expname, hub_expname)), 
        #                                         log_log=False)
        
        # ccdf_hubness_between_strategies(none_bot_spread, none_human_spread, hubs_bot_spread, hubs_human_spread, 
        #                                     plot_fpath=os.path.join(PLOT_DIR, 'hubness_between_strategies_%s%s.png' %(none_expname, hub_expname)), 
        #                                     log_log=True)

        # ccdf_viahubshares_within_strategies(none_bot_spread, nostrag_info['botmeme_shares'], hubs_bot_spread, hubstrag_info['botmeme_shares'], hubsize=1000, 
        #                                 plot_fpath=os.path.join(PLOT_DIR, 'shareviahub_within_strategies_%s%s.png' %(none_expname, hub_expname)), 
        #                                 log_log=True)
        
        # ccdf_viahubshares_between_strategies(none_bot_spread, nostrag_info['botmeme_shares'], hubs_bot_spread, hubstrag_info['botmeme_shares'], hubsize=1000, 
        #                                 plot_fpath=os.path.join(PLOT_DIR, 'shareviahub_between_strategies_%s%s.png' %(none_expname, hub_expname)), 
        #                                 log_log=True)

        # nostrag_final_info = final_prob_spreading_throughhub(none_graph, none_verbose)
        # strag_final_info = final_prob_spreading_throughhub(hub_graph, hub_verbose)

        # ccdf_final_spreadingnodes(nostrag_final_info['botmeme_spread'], nostrag_final_info['humanmeme_spread'], 
        #                             strag_final_info['botmeme_spread'], strag_final_info['humanmeme_spread'], 
        #                             plot_fpath=os.path.join(PLOT_DIR, 'finalspreading_%s%s.png' %(none_expname, hub_expname)), 
        #                             log_log=True)

        # ccdf_final_spreadingnodes_between_strategies(nostrag_final_info['botmeme_spread'], nostrag_final_info['humanmeme_spread'], 
        #                             strag_final_info['botmeme_spread'], strag_final_info['humanmeme_spread'], 
        #                             plot_fpath=os.path.join(PLOT_DIR, 'finalspreading_between_strategies%s%s.png' %(none_expname, hub_expname)), 
        #                             log_log=True)

        # jointplot_final_shares_spread(nostrag_final_info, meme_type='bot', plot_fpath=os.path.join(PLOT_DIR, 'joint_final_bot%s.png' %none_expname), xlog=True, ylog=True)
        # jointplot_final_shares_spread(nostrag_final_info, meme_type='human', plot_fpath=os.path.join(PLOT_DIR, 'joint_final_human%s.png' %none_expname), xlog=True)
        # jointplot_final_shares_spread(strag_final_info, meme_type='bot', plot_fpath=os.path.join(PLOT_DIR, 'joint_final_bot%s.png' %hub_expname), xlog=True, ylog=True)
        # jointplot_final_shares_spread(strag_final_info, meme_type='human', plot_fpath=os.path.join(PLOT_DIR, 'joint_final_human%s.png' %hub_expname), xlog=True)
    
        nostrag_entropy = final_entropy(none_verbose)
        strag_entropy = final_entropy(hub_verbose)
        save_entropy(nostrag_entropy, strag_entropy, os.path.join(PLOT_DIR, 'stats_%s%s.txt' %(none_expname, hub_expname)))

    
    except Exception as e:
        logger.info('Error: ', e)