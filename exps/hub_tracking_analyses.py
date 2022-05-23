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
    plt.scatter(p_k.keys(),p_k.values())
    
    plt.yscale('log')
    plt.xscale('log')
    plt.ylabel('p_k')
    plt.xlabel('k')
    plt.title('Degree distribution (%s degree)' %mode)
    if plot_fpath is not None:
        plt.savefig(plot_fpath, dpi=300)
    else:
        plt.show()

def meme_shares_channel_indegs(G, verbose, deg_mode='in'):
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
            else:
                info['num_humans']+=1
                info['human_largest_spreading_nodes'] += [largest_indeg]
                info['humanmeme_shares'] += [meme['human_shares']]
        else:
            if meme['is_by_bot']==1:
                info['bot_spread_only_viabot']+=1
            else:
                info['human_spread_only_viabot']+=1
        
    return info



def prob_spreading_throughhub(G, verbose):
    # Stat final state
    # Helper  ccdf_meme_spreadingnodes_final
    bot_memes = []
    human_memes = []
    deg_mode='in'

    human_agents = [int(node['id']) for node in G.vs if node['bot']==0]

    for agentid, memeids in verbose['all_feeds'][0].items():
        if any(map(str.isalpha, agentid)) is True:
            #skip bots
            continue

        verbose_memes = [meme for meme in verbose['all_memes'][0] if meme['id'] in memeids]
        for meme in verbose_memes:
            spread_through= [int(node) for node in meme['spread_via_agents']]
            human_channels = set(human_agents) & set(spread_through)

            if len(human_channels)>0:
                indegs = G.degree(list(human_channels), mode=deg_mode, loops=False)
                largest_indeg = max(indegs)

                if meme['is_by_bot']==1:
                    bot_memes += [largest_indeg]
                else:
                    human_memes += [largest_indeg]
    return bot_memes, human_memes


def ccdf_meme_spreadingnodes_final(nostrag_bot_memes, nostrag_human_memes, strag_bot_memes, strag_human_memes, plot_fpath=None, log_log=True):
    figure, (ax1, ax2) = plt.subplots(1,2, figsize=(10, 5), sharex=True)

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
    else:
        plt.show()

def plot_numshares_vs_indeg(none_largest_indegs, none_shares, hub_largest_indegs, hub_shares, plot_fpath=None):
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
    else:
        plt.show()

def ccdf_compare_hubness_between_strategies(none_bot_spread, none_human_spread, hubs_bot_spread, hubs_human_spread, plot_fpath=None, log_log=True):
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

    figure.suptitle('CCDF: Largest in-deg of spreading nodes (across whole simulation)')
    figure.tight_layout()
    if plot_fpath is not None:
        figure.savefig(plot_fpath, dpi=300)
    else:
        plt.show()


def ccdf_compare_hubness_within_strategies(none_bot_spread, none_human_spread, hubs_bot_spread, hubs_human_spread, plot_fpath=None, log_log=True):
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

    figure.suptitle('CCDF: Largest in-deg of spreading nodes (across whole simulation)')
    figure.tight_layout()
    if plot_fpath is not None:
        figure.savefig(plot_fpath, dpi=300)
    else:
        plt.show()


def separate_shares_viahubs(spreading_degs, meme_shares, hubsize=1000):
    # Helper ccdf_compare_viahubshares
    viahub = []
    not_viahub = []
    for deg,share in zip(spreading_degs, meme_shares):
        if deg>=hubsize:
            viahub+=[share]
        else:
            not_viahub +=[share]
    return viahub, not_viahub


def ccdf_compare_viahubshares_within_strategies(spreading_nodes, meme_shares, strag_spreading_nodes, strag_meme_shares, hubsize=1000, plot_fpath=None, log_log=True):
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
    else:
        plt.show()


def ccdf_compare_viahubshares_between_strategies(spreading_nodes, meme_shares, strag_spreading_nodes, strag_meme_shares, hubsize=1000, plot_fpath=None, log_log=True):
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
    else:
        plt.show()


def save_stats(nostrag_info, strag_info, fpath):
    with open(fpath, 'w') as outfile:
        for name,info in {'NO STRATEGY': nostrag_info, 'HUB STRATEGY': strag_info}.items():
            info['bot_spread_only_viabot_pct'] = np.round(info['bot_spread_only_viabot']/info['num_bots'], 2)
            info['human_spread_only_viabot_pct'] = np.round(info['human_spread_only_viabot']/info['num_humans'], 2)
            outfile.write('%s \n' %name)
            for k,v in info.items():
                outfile.write('%s %s' %(k,v))
    logger.info('Finished saving stats!')


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

    RES_DIR = os.path.join(ABS_PATH,'results', exp)
    TRACKING_DIR = os.path.join(ABS_PATH,'long_results',exp)
    NETWORK_PATH = os.path.join(DATA_PATH, 'igraph/vary_targetgamma')
    PLOT_DIR = os.path.join(ABS_PATH,'analysis_plots',exp)
    utils.make_sure_dir_exists(PLOT_DIR, '')


    hub_network = os.path.join(NETWORK_PATH, "network_%s.gml" %exp2network[hub_expname])
    hub_verbose = utils.read_json_compressed(os.path.join(TRACKING_DIR,'%s.json.gz' %hub_expname))
    hub_graph = ig.Graph.Read_GML(hub_network)
    
    none_network = os.path.join(NETWORK_PATH, "network_%s.gml" %exp2network[none_expname])
    none_verbose = utils.read_json_compressed(os.path.join(TRACKING_DIR,'%s.json.gz' %none_expname))
    none_graph = ig.Graph.Read_GML(none_network)

    hubstrag_info = meme_shares_channel_indegs(hub_graph, hub_verbose, deg_mode='in')
    nostrag_info =  meme_shares_channel_indegs(none_graph, none_verbose, deg_mode='in')
    try:
        save_stats(nostrag_info, hubstrag_info, os.path.join(PLOT_DIR, 'stats_%s%s.txt' %(none_expname, hub_expname)))

        plot_degree_dist(none_graph, plot_fpath=os.path.join(PLOT_DIR, 'degree_dist_%s.png' %none_expname), mode='in')
        plot_degree_dist(hub_graph, plot_fpath=os.path.join(PLOT_DIR, 'degree_dist_%s.png' %hub_expname), mode='in')

        none_bot_spread= nostrag_info['bot_largest_spreading_nodes']
        none_human_spread= nostrag_info['human_largest_spreading_nodes']
        hubs_bot_spread= hubstrag_info['bot_largest_spreading_nodes']
        hubs_human_spread= hubstrag_info['human_largest_spreading_nodes']

        plot_numshares_vs_indeg(none_bot_spread, nostrag_info['botmeme_shares'],
                                hubs_bot_spread, hubstrag_info['botmeme_shares'], 
                                plot_fpath=os.path.join(PLOT_DIR, 'numshares_indeg_%s%s.png' %(none_expname, hub_expname)))

        ccdf_compare_hubness_between_strategies(none_bot_spread, none_human_spread, hubs_bot_spread, hubs_human_spread, 
                                                plot_fpath=os.path.join(PLOT_DIR, 'hubness_between_strategies_%s%s.png' %(none_expname, hub_expname)), 
                                                log_log=True)
        
        ccdf_compare_hubness_between_strategies(none_bot_spread, none_human_spread, hubs_bot_spread, hubs_human_spread, 
                                                plot_fpath=os.path.join(PLOT_DIR, 'hubness_between_strategies_%s%s_norm.png' %(none_expname, hub_expname)), 
                                                log_log=False)
        
        ccdf_compare_hubness_within_strategies(none_bot_spread, none_human_spread, hubs_bot_spread, hubs_human_spread, 
                                            plot_fpath=os.path.join(PLOT_DIR, 'hubness_within_strategies_%s%s.png' %(none_expname, hub_expname)), 
                                            log_log=True)

        ccdf_compare_viahubshares_within_strategies(none_bot_spread, nostrag_info['botmeme_shares'], hubs_bot_spread, hubstrag_info['botmeme_shares'], hubsize=1000, 
                                        plot_fpath=os.path.join(PLOT_DIR, 'viahub_within_strategies_%s%s.png' %(none_expname, hub_expname)), 
                                        log_log=True)
        
        ccdf_compare_viahubshares_between_strategies(none_bot_spread, nostrag_info['botmeme_shares'], hubs_bot_spread, hubstrag_info['botmeme_shares'], hubsize=1000, 
                                        plot_fpath=os.path.join(PLOT_DIR, 'viahub_between_strategies_%s%s.png' %(none_expname, hub_expname)), 
                                        log_log=True)

        nostrag_bot_memes, nostrag_human_memes = prob_spreading_throughhub(none_graph, none_verbose)
        strag_bot_memes, strag_human_memes = prob_spreading_throughhub(hub_graph, hub_verbose)

        ccdf_meme_spreadingnodes_final(nostrag_bot_memes, nostrag_human_memes, strag_bot_memes, strag_human_memes, 
                                        plot_fpath=os.path.join(PLOT_DIR, 'spreading_final_%s%s_log.png' %(none_expname, hub_expname)), 
                                        log_log=True)
    except Exception as e:
        logger.info('Error: ', e)