import json 
import os 

def plot_agent_degree_dist(graph, mode='in', plot_fpath=None):
    
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