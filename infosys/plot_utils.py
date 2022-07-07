import infosys.utils as utils

import igraph as ig
import random 
import string 
import numpy as np
import collections
import matplotlib.pyplot as plt
import seaborn as sns 

def plot_degree_dist(graph, mode='in', plot_fpath=None):
    # Plot degree distribution for a igraph network
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


def plot_agent_degree_dist(graph, mode='in', plot_fpath=None):
    # Plot the CCDF for the agents' degree (2 lines: bot & human agents)

    human_vertices = [v for v in graph.vs if v['bot']==0]
    human_degs = graph.degree(human_vertices, mode=mode, loops=False)
    
    bot_vertices = [v for v in graph.vs if v['bot']==1]
    bot_degs = graph.degree(bot_vertices, mode=mode, loops=False)
    
    figure, ax = plt.subplots()
    ax.set_xscale('log')
    ax.set_yscale('log')
    sns.ecdfplot(ax=ax, data = human_degs, complementary=True, label = 'human')
    sns.ecdfplot(ax=ax, data = bot_degs, complementary=True, label = 'bot')
    ax.set_xlabel("Degree")
    ax.legend()
    ax.set_title("CCDF: Degree dist. of agents")
    figure.tight_layout()
    if plot_fpath is not None:
        figure.savefig(plot_fpath, dpi=300)
        plt.close(figure)
    else:
        figure.show()