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


def influx_timestep_between_strategies(nostrag_influx, strag_influx, flow_type='bot_in', ylog=True, common_timestep=True, plot_fpath=None):
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
        common = min(len(strag), len(nostrag)) 
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


def memeflow_timestep(flow_verbose, meme_type='bot', ylog=True, plot_fpath=None):
    # Plot 2 flows of meme (in & out) across timesteps
    # flow_verbose: dictionary containing number of memes flowing in or out
    # structure: {'bot_in': [], 'bot_out': [], 'human_in': [], 'human_out': []}, each element is a timestep
    # meme_type: ['bot', 'human'] 
    # common timestep: one strategy can take longer to converge than the other. Only plot the timestep they have in common on x axis.

    fig,ax = plt.subplots()

    if ylog is True:
        ax.set_yscale('log') 

    inflow='%s_in' %meme_type
    outflow='%s_out' %meme_type

    ax.plot(range(len(flow_verbose[inflow])), flow_verbose[inflow], marker='o',label='inflow')
    ax.plot(range(len(flow_verbose[outflow])), flow_verbose[outflow], marker='v',label='outflow')

    ax.set_ylabel('num memes')
    ax.set_xlabel('t')
    ax.set_title('Meme fluctuation (%s) across timesteps' %meme_type)
    ax.legend()
    
    if plot_fpath is not None:
        fig.savefig(plot_fpath, dpi=300)
        plt.close(fig)
    else:
        fig.show()

def draw_delta_memeflow_timestep(ax, flow_verbose, meme_type='bot', label=None):
    # Plot delta flow of memes (in - out) across timesteps
    # flow_verbose: dictionary containing number of memes flowing in or out
    # structure: {'bot_in': [], 'bot_out': [], 'human_in': [], 'human_out': []}, each element is a timestep
    # meme_type: ['bot', 'human'] 

    # DONT USE SYMLOG - it makes the difference seems more extreme than actual
    # if ylog is True:
    #     ax.set_yscale('symlog') 
    delta = np.subtract(flow_verbose['%s_in' %meme_type], flow_verbose['%s_out' %meme_type])
    ax.scatter(range(len(delta)), delta, label=label)

    ax.set_ylabel('num memes')
    ax.set_xlabel('t')
    ax.legend()


def delta_flow_timestep(flow_verbose, meme_type='bot', plot_fpath=None):
    # Single Plot of delta flow of memes (in - out) across timesteps 
    fig,ax = plt.subplots()
    
    draw_delta_memeflow_timestep(ax, flow_verbose, meme_type=meme_type, label=meme_type)
    ax.set_title('Delta meme (%s in-out) across timesteps' %meme_type)
    
    if plot_fpath is not None:
        fig.savefig(plot_fpath, dpi=300)
        plt.close(fig)
    else:
        fig.show() 

def delta_flow_panel(verbose1, verbose2,  meme_type1='bot', meme_type2='bot', label1='no strategy', label2='hub strategy',  plot_fpath=None):
    # Single Plot of delta flow of memes (in - out) across timesteps 
    # verbose1, verbose2: dict of num_memes flowing in or out, for 2 strategies 
    fig,axs = plt.subplots(1,2, sharey=True)
    draw_delta_memeflow_timestep(axs[0], verbose1, meme_type=meme_type1, label=label1)
    draw_delta_memeflow_timestep(axs[1], verbose2, meme_type=meme_type2, label=label2)
    fig.suptitle('Delta meme (%s in-out) across timesteps' %'bot')

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


def save_entropy(nostrag_entropy, strag_entropy, fpath):
    with open(fpath, 'w') as outfile:
        outfile.write('**ENTROPY: \n')
        outfile.write('No targeting: %s \n' %np.round(nostrag_entropy,4))
        outfile.write('With targeting: %s \n' %np.round(strag_entropy,4))
    logger.info('Finished saving entropy to file!')


if __name__=="__main__":
    logger.info('WORKING DIR: %s' %(os.getcwd()))
    ABS_PATH = '/N/slate/baotruon/marketplace'
    DATA_PATH = '/N/slate/baotruon/marketplace/data'
    
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
        
        meme_type='bot'
        memeflow_timestep(none_verbose['meme_netchange'][0], meme_type=meme_type, plot_fpath=os.path.join(PLOT_DIR, 'influx_%s_%s.png' %(meme_type, none_expname)))
        memeflow_timestep(hub_verbose['meme_netchange'][0], meme_type=meme_type, plot_fpath=os.path.join(PLOT_DIR, 'influx_%s_%s.png' %(meme_type, hub_expname)))

        # delta_flow_timestep(none_verbose['meme_netchange'][0], meme_type='bot', plot_fpath=os.path.join(PLOT_DIR, 'delta_%s_%s.png' %(meme_type, hub_expname)))

        delta_flow_panel(none_verbose['meme_netchange'][0], hub_verbose['meme_netchange'][0],  meme_type1='bot', meme_type2='bot', label1='no strategy', label2='hub strategy', 
                         plot_fpath=os.path.join(PLOT_DIR, 'delta_%s_%s%s.png' %(meme_type, none_expname,hub_expname)))
    except Exception as e:
        logger.info('Error: ', e)