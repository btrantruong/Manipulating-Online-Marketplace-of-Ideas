import infosys.utils as utils 
import infosys.plot_utils as plot_utils 
import infosys.config_values as configs

import igraph as ig
import matplotlib.pyplot as plt
import os 
import glob
import json
from collections import defaultdict
import pandas as pd
import numpy as np

## Look at verbose files where beta=0.005. (conservative3.json)

res_dir = '/N/slate/baotruon/marketplace/newpipeline/verbose'
folder = 'final_strategies_vary_beta_2runs'


def get_data(strategy):
    ## READ VERBOSE DATA
    fpath = os.path.join(res_dir, folder, f'{strategy}3.json.gz')
    data = utils.read_json_compressed(fpath)
    ## READ GRAPH (to get communities)
    graph = ig.Graph.Read_GML(data['graph_gml'])
    humans = [node for node in graph.vs if node['uid'].isdigit()]
    bots = [node for node in graph.vs if node['uid'].isdigit() is False]

    # Note that for info sys net, the bots don't have party
    communities = {} #dict of community - list of idxs
    communities['conservative']= [node['uid'] for node in humans if float(node['party']) > 0]
    communities['liberal']= [node['uid'] for node in humans if float(node['party']) < 0]
    communities['misinfo'] = [h['uid'] for h in humans if float(h['misinfo'])>0.4]
    return data['all_memes'][0], data['all_feeds'][0], communities


def get_cluster_qual(memes, feeds, uids):
    quals = []
    all_fitness = []
    for uid in uids:
        memes_in_feed = [i for memeidx in feeds[uid] for i in memes if i['id']== memeidx]
        quality = [meme['quality'] for meme in memes_in_feed]
        fitness = [meme['fitness'] for meme in memes_in_feed]
        quals += quality
        all_fitness += fitness
    avg_qual = sum(quals)/len(quals)
    avg_fitness = sum(all_fitness)/len(all_fitness)
    return avg_qual, avg_fitness


if __name__=="__main__":
    print('calculating for conservative..')
    memes, feeds, communities =  get_data('conservative')
    right_measures = get_cluster_qual(memes, feeds, communities['conservative'])
    left_measures = get_cluster_qual(memes, feeds, communities['liberal'])
    misinfo_measures = get_cluster_qual(memes, feeds, communities['misinfo'])

    print('calculating for none..')
    none_memes, none_feeds, none_communities =  get_data('None')
    right_none = get_cluster_qual(none_memes, none_feeds, none_communities['conservative'])
    left_none = get_cluster_qual(none_memes, none_feeds, none_communities['liberal'])
    misinfo_none = get_cluster_qual(none_memes, none_feeds, none_communities['misinfo'])
    print('--Difference in quality between clusters:')
    print('Targeting on conservatives:')
    print(f'conservative: {right_measures[0]} - liberal: {left_measures[0]} - misinfo: {misinfo_measures[0]}')
    print('No targeting')
    print(f'conservative: {right_none[0]} - liberal: {left_none[0]} - misinfo: {misinfo_none[0]}')
    
    print('-- Fitness')
    print('Targeting on conservatives:')
    print(f'conservative: {right_measures[1]} - liberal: {left_measures[1]} - misinfo: {misinfo_measures[1]}')
    print('No targeting')
    print(f'conservative: {right_none[1]} - liberal: {left_none[1]} - misinfo: {misinfo_none[1]}')