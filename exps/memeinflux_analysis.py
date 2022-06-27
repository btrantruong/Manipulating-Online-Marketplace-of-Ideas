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
from scipy.special import entr

logger = utils.get_logger(__name__)

""" Input: verbose simulation results
    Output: plot of quality or bot meme influx vs timestep
    Run with this command: python3 exps/memeinflux_analysis.py vary_thetaphi_1runs_trackmeme_gamma0.005 hubs_22 none_22 influx_analyses 
"""

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


def quality_timestep(nostrag_quality, strag_quality, plot_fpath=None):
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


def influx_timestep(nostrag_influx, strag_influx, flow_type='bot_in', ylog=True, common_timestep=True, plot_fpath=None):
    # nostrag_influx, strag_influx: dictionary containing number of meme in or out flux (for no targeting and targeting)
    # structure: {'bot_in': [], 'bot_out': [], 'human_in': [], 'human_out': []}, each element is a timestep
    # flow_type: 'bot_in', 'bot_out', 'human_in', 'human_out'
     # common timestep: one strategy can take longer to converge than the other. Only plot the timestep they have in common on x axis.

    fig,ax = plt.subplots()

    if ylog is True:
        ax.set_yscale('log')

    strag = strag_influx[flow_type]
    nostrag = nostrag_influx[flow_type]

    if common_timestep is True:
        common = max(len(strag), len(nostrag)) 
        nostrag = nostrag[:common+1]
        strag = strag[:common+1]

    ax.plot(range(len(strag)), strag, marker='o', label='targeting')
    ax.plot(range(len(nostrag)), nostrag, marker='v', label='no targeting')
    
    ax.set_ylabel('%s' %flow_type)
    ax.set_xlabel('t')
    ax.set_title('Meme fluctuation (%s) across timesteps' %flow_type)
    ax.legend()
    
    if plot_fpath is not None:
        fig.savefig(plot_fpath, dpi=300)
        plt.close(fig)
    else:
        fig.show()


def deltaflux_timestep(nostrag_flux, strag_flux, flow_type='bot', ylog=True, common_timestep=True, plot_fpath=None):
    # nostrag_influx, strag_influx: dictionary containing number of meme in or out flux (for no targeting and targeting)
    # structure: {'bot_in': [], 'bot_out': [], 'human_in': [], 'human_out': []}, each element is a timestep
    # flow_type: 'bot' or 'human'
    # common timestep: one strategy can take longer to converge than the other. Only plot the timestep they have in common on x axis.
    # markers = list('.s*o^v<>+x')
    fig,ax = plt.subplots()

    if ylog is True:
        ax.set_yscale('log')

    inflow='%s_in' %flow_type
    outflow='%s_out' %flow_type
    nostrag_delta = np.subtract(nostrag_flux[inflow], nostrag_flux[outflow])
    strag_delta = np.subtract(strag_flux[inflow], strag_flux[outflow])

    if common_timestep is True:
        common = max(len(strag_delta), len(nostrag_delta)) 
        nostrag_delta = nostrag_delta[:common+1]
        strag_delta = strag_delta[:common+1]

    ax.plot(range(len(strag_delta)), strag_delta, marker='o',label='targeting')
    ax.plot(range(len(nostrag_delta)), nostrag_delta, marker='v',label='no targeting')

    ax.set_ylabel('memes')
    ax.set_xlabel('t')
    ax.set_title('Delta (in-out) %s memes across timesteps' %flow_type)
    ax.legend()
    
    if plot_fpath is not None:
        fig.savefig(plot_fpath, dpi=300)
        plt.close(fig)
    else:
        fig.show()


def final_entropy(verbose_tracking, base=2, verbose=True):
    # Get entropy of the system from the distribution of probability that a feed contains a bot meme. 

    bot_frac = []
    zero_len_feed=0
    botmeme_ids = [meme['id'] for meme in verbose_tracking['all_memes'][0] if meme['is_by_bot']==1]

    for agentid, memeids in verbose_tracking['all_feeds'][0].items():
        if any(map(str.isalpha, agentid)) is True:
            #skip bots
            continue
        
        if len(memeids)<=0:
            zero_len_feed +=1

        else:
            bot_num= len([memeid for memeid in memeids if memeid in botmeme_ids])
            assert(bot_num<=len(memeids))

            bot_frac += [bot_num/len(memeids)]

    system_entropy= entropy(bot_frac, base=base) # stats.entropy(): probs are normalized
    #system_entr = entr(bot_frac).sum() #use special.entr for no normalization

    if verbose is True:
        logger.info('Zero-length feed: %s/%s' %(zero_len_feed, len(verbose_tracking['all_feeds'][0])))
        logger.info('Entropy: %s' %system_entropy)

    return system_entropy


def ccdf_botmemefrac_between_strategies(nostrag_junkfrac, strag_junkfrac, plot_fpath=None, log_log=False):
    # CCDF of fraction of bot memes in human agent's feeds at final state- 2 lines (none & hubs-targeting)

    figure, ax = plt.subplots()

    if log_log is True:
        ax.set_xscale('log')
        ax.set_yscale('log')
    
    sns.ecdfplot(ax=ax, data = nostrag_junkfrac, complementary=True, label = 'no targeting')
    sns.ecdfplot(ax=ax, data = strag_junkfrac, complementary=True, label = 'hub targeting')
    ax.set_xlabel("Fraction of bot memes in agent's feed")
    ax.legend()
    ax.set_title("CCDF: Fraction of bot memes in agent's feed")

    figure.tight_layout()
    if plot_fpath is not None:
        figure.savefig(plot_fpath, dpi=300)
        plt.close(figure)
    else:
        figure.show()


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


def save_entropy(nostrag_entropy, strag_entropy, fpath):
    with open(fpath, 'w') as outfile:
        outfile.write('**ENTROPY: \n')
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
    PLOT_DIR = os.path.join(ABS_PATH,plot_folder,exp)
    utils.make_sure_dir_exists(PLOT_DIR, '')

    hub_verbose = utils.read_json_compressed(os.path.join(TRACKING_DIR,'%s.json.gz' %hub_expname))
    none_verbose = utils.read_json_compressed(os.path.join(TRACKING_DIR,'%s.json.gz' %none_expname))

    try:
        nostrag_entropy = final_entropy(none_verbose)
        strag_entropy = final_entropy(hub_verbose)
        save_entropy(nostrag_entropy, strag_entropy, os.path.join(PLOT_DIR, 'entropy_%s%s.txt' %(none_expname, hub_expname)))

        quality_timestep(none_verbose['quality_timestep'][0], hub_verbose['quality_timestep'][0], 
                        plot_fpath=os.path.join(PLOT_DIR, 'quality_timestep%s%s.png' %(none_expname, hub_expname)))
        
        for flowtype in ['bot_in', 'bot_out', 'human_in', 'human_out']:
            influx_timestep(none_verbose['meme_influx'][0], hub_verbose['meme_influx'][0], flow_type=flowtype, common_timestep=False,
                            plot_fpath=os.path.join(PLOT_DIR, 'influx_%s_%s%s.png' %(flowtype,none_expname, hub_expname)))

            influx_timestep(none_verbose['meme_influx'][0], hub_verbose['meme_influx'][0], flow_type=flowtype, common_timestep=True,
                            plot_fpath=os.path.join(PLOT_DIR, 'influx_common_%s_%s%s.png' %(flowtype,none_expname, hub_expname)))
        
        for flowtype in ['bot','human']:
            deltaflux_timestep(none_verbose['meme_influx'][0], hub_verbose['meme_influx'][0], flow_type=flowtype, common_timestep=False,
                                            plot_fpath=os.path.join(PLOT_DIR, 'delta_%s_%s%s.png' %(flowtype, none_expname, hub_expname)))

            deltaflux_timestep(none_verbose['meme_influx'][0], hub_verbose['meme_influx'][0], flow_type=flowtype, common_timestep=True,
                                            plot_fpath=os.path.join(PLOT_DIR, 'delta_common_%s_%s%s.png' %(flowtype, none_expname, hub_expname)))

    except Exception as e:
        logger.info('Error: ', e)