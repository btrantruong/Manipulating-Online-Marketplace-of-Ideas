
from exps.strategy_analyses import PLOT_DIR
import strategy_analyses 
import infosys.utils as utils 
import infosys.plot_utils as plot_utils 
import infosys.config_values as configs
import os 
import igraph as ig
import matplotlib.pyplot as plt
import seaborn as sns 
import sys 
#TODO: clean up this script!
logger = utils.get_logger(__name__)

def bot_followers(graph):
    # Get the indegree of all humans that follow bots
    bots = [node for node in graph.vs if node['bot']==1]
    humfollower_degs = []
    for bot in bots:
        follower_idxs = [node for node in graph.predecessors(bot)]
        hum_followers = [node for node in graph.vs if int(node['id']) in follower_idxs and node['bot']==0]
        humfollower_deg = graph.degree(hum_followers, mode='in')
        humfollower_degs += humfollower_deg
    return humfollower_degs


def deg_dist_human_following_bots(none_graph, hub_graph, plot_fpath=None):
    none_follower_degs = bot_followers(none_graph)
    hub_follower_degs = bot_followers(hub_graph)

    figure, ax = plt.subplots()
    ax.set_xscale('log')
    ax.set_yscale('log')
    sns.ecdfplot(ax=ax, data = none_follower_degs, complementary=True, label = 'no targeting')
    sns.ecdfplot(ax=ax, data = hub_follower_degs, complementary=True, label = 'targeting')
    ax.set_xlabel("Degree")
    ax.legend()
    ax.set_title("CCDF: Degree dist. of humans following bots")
    figure.tight_layout()
    if plot_fpath is not None:
        figure.savefig(plot_fpath, dpi=300)
        plt.close(figure)
    else:
        figure.show()


def numbot_humanfollowers(graph):
    # Return the number of bots and humans that humans follow, ratio of bot/human
    
    humans = [node for node in graph.vs if node['bot']==0]
    
    num_humfollowings = []
    num_botfollowings = []
    ratios =[]
    for human in humans:
        following_idxs = [node for node in graph.successors(human)]
        
        hum_followings = [node for node in graph.vs if (node.index in following_idxs and node['bot']==0)]
        bot_followings = [node for node in graph.vs if (node.index in following_idxs and node['bot']==1)]
        num_humfollowings += [len(hum_followings)]
        num_botfollowings += [len(bot_followings)]
        ratios +=[len(bot_followings)/len(following_idxs) if len(following_idxs)>0 else 0]
    return num_humfollowings, num_botfollowings, ratios


def plot_num_bots_humans_humanfollowers(none_graph, hub_graph, plot_fpath=None):
    hums, bots, ratios = numbot_humanfollowers(none_graph)
    hhums, hbots, hratios = numbot_humanfollowers(hub_graph)
    
    figure, ax = plt.subplots()
    ax.set_xscale('log')
    ax.set_yscale('log')

    sns.ecdfplot(ax=ax, data = hums, complementary=True, label = 'humans')
    sns.ecdfplot(ax=ax, data = bots, complementary=True, label = 'bots')
    ax.set_xlabel("Number")
    ax.legend()
    ax.set_title("CCDF: Number of followings by humans (No targeting)")
    if plot_fpath is not None:
        figure.savefig(os.path.join(plot_fpath,'none_num_followed_by_humans.png'), dpi=300)
        plt.close(figure)
    else:
        figure.show()
    plt.clf()


    sns.ecdfplot(ax=ax, data = hhums, complementary=True, label = 'humans')
    sns.ecdfplot(ax=ax, data = hbots, complementary=True, label = 'bots')
    ax.set_xlabel("Number")
    ax.legend()
    ax.set_title("CCDF: Number of followings by humans (Hubs-targeting)")
    if plot_fpath is not None:
        figure.savefig(os.path.join(plot_fpath,'hubs_num_followed_by_humans.png'), dpi=300)
        plt.close(figure)
    else:
        figure.show()
    plt.clf()


    sns.ecdfplot(ax=ax, data = bots, complementary=True, label = 'no targeting')
    sns.ecdfplot(ax=ax, data = hbots, complementary=True, label = 'hubs-targeting')
    ax.set_xlabel("Number")
    ax.legend()
    ax.set_title("CCDF: Number of bots followed by humans")
    if plot_fpath is not None:
        figure.savefig(os.path.join(plot_fpath,'bots_followed_by_humans.png'), dpi=300)
        plt.close(figure)
    else:
        figure.show()
    plt.clf()


    sns.ecdfplot(ax=ax, data = hums, complementary=True, label = 'no targeting')
    sns.ecdfplot(ax=ax, data = hhums, complementary=True, label = 'hubs-targeting')
    ax.set_xlabel("Number")
    ax.legend()
    ax.set_title("CCDF: Number of humans followed by humans")
    if plot_fpath is not None:
        figure.savefig(os.path.join(plot_fpath,'humans_followed_by_humans.png'), dpi=300)
        plt.close(figure)
    else:
        figure.show()
    plt.clf()

    sns.ecdfplot(ax=ax, data = ratios, complementary=True, label = 'no targeting')
    sns.ecdfplot(ax=ax, data = hratios, complementary=True, label = 'hubs-targeting')
    ax.set_xlabel("bot %")
    ax.legend()
    ax.set_title("CCDF: Proportion of bots in all accounts followed by humans")
    if plot_fpath is not None:
        figure.savefig(os.path.join(plot_fpath,'prop_followed_by_humans.png'), dpi=300)
        plt.close(figure)
    else:
        figure.show()
    plt.clf()

if __name__=="__main__":
    logger.info('WORKING DIR: %s' %(os.getcwd()))
    ABS_PATH = '/N/slate/baotruon/marketplace'
    DATA_PATH = '/N/slate/baotruon/marketplace/data'
    
    config_fname= os.path.join(DATA_PATH, 'all_configs.json')
    exp_type = 'compare_strategies'
    vary_params = "vary_thetaphi"
    mode='igraph'
    sim_num=2


    beta=0.1
    gamma=0.01
    NETWORK_PATH = os.path.join(DATA_PATH, mode, 'vary_network', "network_%s.gml")
    TRACKING_DIR = os.path.join(ABS_PATH,'newpipeline', 'verbose', '%s_%sruns' %(exp_type, sim_num))
    hubconfig = {'beta': beta, 'gamma':gamma, 'targeting_criterion': 'hubs'}
    noneconfig = {'beta':beta, 'gamma':gamma, 'targeting_criterion': None}
    hubnet = utils.netconfig2netname(config_fname, hubconfig)
    nonenet = utils.netconfig2netname(config_fname, noneconfig)

    print('Nonenet: %s, hubnet: %s' %(nonenet, hubnet))
    hub_graph = ig.Graph.Read_GML(os.path.join(DATA_PATH, mode, 'vary_network', "network_%s.gml" %hubnet))
    none_graph = ig.Graph.Read_GML(os.path.join(DATA_PATH, mode, 'vary_network', "network_%s.gml" %nonenet))

    PLOT_DIR = utils.make_sure_dir_exists('', 'beta%s_gammma%s' %(beta, gamma))
    deg_dist_human_following_bots(none_graph, hub_graph, plot_fpath=os.path.join(PLOT_DIR, 'deg_dist.png'))

    plot_num_bots_humans_humanfollowers(none_graph, hub_graph, plot_fpath=PLOT_DIR)
    print('FINISH PLOTTING')
    # nonenet=sys.argv[1]
    # hubnet=sys.argv[2]

    # plot_folder=sys.argv[3]
