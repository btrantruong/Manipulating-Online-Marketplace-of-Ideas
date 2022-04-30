import infosys.utils as utils

import igraph as ig
import random 
import string 
import numpy as np 

def read_empirical_network(file):
    print('File: ', file)
    net = ig.Graph.Read_GML(file)
    
    #prevent errors with duplicate attribs
    net = _delete_unused_attributes(net, desire_attribs=['label', 'party', 'misinfo'])
    return net 

def write_gmlz(G, file):
    G.Graph.write_graphmlz(file)

#TODO: comment out random seed in actual run
def random_walk_network(net_size, p=0.5, k_out=3, seed=100):
    # create a network with random-walk growth model
    # default p = 0.5 for network clustering
    # default k_out = 3 is average no. friends within humans & bots
    #
    if net_size <= k_out + 1: # if super small just return a clique
        return ig.Graph.Full(net_size, directed=True)
    
    G = ig.Graph.Full(k_out, directed=True)

    random.seed(seed)
  
    for n in range(k_out, net_size):
        target = random.choice(G.vs)
        friends = [target]
        n_random_friends = 0
        for _ in range(k_out - 1): #bao: why kout-1 and not kout?
            if random.random() < p:
                n_random_friends += 1
        
        friends += random.sample(G.successors(target), n_random_friends) #return a list of vertex id(int)
        friends += random.sample(range(G.vcount()), k_out - 1 - n_random_friends)
        
        G.add_vertex(n) #n becomes 'name' of vertex
        
        edges = [(n,f) for f in friends]
        
        G.add_edges(edges)
    return G

# create network of humans and bots
# preferential_targeting is a flag; if False, random targeting
# default n_humans=1000 but 10k for paper
# default beta=0.1 is bots/humans ratio
# default gamma=0.1 is infiltration: probability that a human follows each bot
#
def init_net(targeting_criterion=None, verbose=False, human_network = None, n_humans=1000, beta=0.1, gamma=0.1, track_bot_followers=False):

    # humans
    if human_network is None:
        if verbose: print('Generating human network...')
        H = random_walk_network(n_humans)
    else:
        if verbose: print('Reading human network...')
        H = read_empirical_network(human_network)
        n_humans = H.vcount()

    H.vs['bot'] = [False] * H.vcount()

    # bots
    if verbose: print('Generating bot network...')
    n_bots = int(n_humans * beta) 
    B = random_walk_network(n_bots, seed=101)
    B.vs['bot'] = [True] * B.vcount()

    # merge and add feed
    # b: Retain human and bot ids - TODO: prob won't be needed later 
    alphas = list(string.ascii_lowercase)
    B.vs['uid'] = [str(node.index)+random.choice(alphas) for node in B.vs]
    if human_network is None:
        H.vs['uid'] = [str(node.index) for node in H.vs]
    else:
        H.vs['uid'] = [str(node['label']) for node in H.vs]
    
    if verbose: print('Merging human and bot networks...')
    G = H.disjoint_union(B)
    G = _delete_unused_attributes(G, desire_attribs=['uid','bot', 'party', 'misinfo'])

    assert(G.vcount() == n_humans + n_bots)
    # b:now nodes are reindex so we want to keep track of which ones are bots and which are humans
    humans = [n for n in G.vs if n['bot'] is False]
    bots = [n for n in G.vs if n['bot'] is True]
    #b:initialize feed - Omit this because saving will fail
    #   # G.nodes[n]['feed'] = []

    # humans follow bots
    if verbose: print('Humans following bots...')
    if targeting_criterion is not None:
        if targeting_criterion == 'hubs':
            w = [G.degree(h, mode='in') for h in humans]
        elif targeting_criterion == 'partisanship':
            w = [abs(float(h['party'])) for h in humans]
        elif targeting_criterion == 'misinformation':
            w = [float(h['misinfo']) for h in humans]
        elif targeting_criterion == 'conservative':
            w = [1 if float(h['party']) > 0 else 0 for h in humans]
        elif targeting_criterion == 'liberal':
            w = [1 if float(h['party']) < 0 else 0 for h in humans]
        else:
            raise ValueError('Unrecognized targeting_criterion passed to init_net')
    
        # random.seed(102)
        probs = [i/sum(w) for i in w]
    
    degs = []
    for b in bots:
        n_followers = 0
        for _ in humans:
            if random.random() < gamma:
                n_followers += 1
        if targeting_criterion is not None:
            # followers = utils.sample_with_prob_without_replacement(humans, n_followers, w)
            #Use np: (vec,size,replace=False, p=P)
            followers = np.random.choice(humans, n_followers, replace=False, p=probs)
        else:
            followers = random.sample(humans, n_followers)
        
        follower_edges = [(f,b) for f in followers]
        G.add_edges(follower_edges)

        #debug: track degree of humans that are bot followers
        if track_bot_followers is True:
            degs+=G.degree(followers, mode='in')
    
    if track_bot_followers is True:
        return G, degs
    else:
        return G

def _delete_unused_attributes(net, desire_attribs=['uid','party', 'misinfo']):
    #delete unused attribs or artifact of igraph to maintain consistency
    for attrib in net.vs.attributes():
        if attrib not in desire_attribs:
            del(net.vs[attrib])
    return net 