import networkx as nx
import csv
import json
import pandas as pd
import random
import importlib
import model as bot_model
import matplotlib.pyplot as plt
import igraph as ig

import os
ABS_PATH = '/N/u/baotruon/Carbonate/marketplace'
DATA_PATH = os.path.join(ABS_PATH, 'follower_network')

path = DATA_PATH
files={
    # File has 3 columns: ID \t partisanship \t misinformation \n
    'user_info': 'measures.tab', 
    'adjlist': 'anonymized-friends.json'
}

# Make directed network follower -> friend
# Get a subgraph of partisan users 
def make_network_bao(path, files):
    stats = pd.read_csv(os.path.join(path, files['user_info']), sep='\t')
    stats = stats.astype({'ID': str}).dropna(axis=0).drop_duplicates()

    with open(os.path.join(path, files['adjlist'])) as fp:
        adjlist = json.load(fp)
    # Convert all node names from int to str. Keys are already str
    adjlist = {k:[str(n) for n in vlist] for k, vlist in adjlist.items()}

    friends = stats[stats['ID'].isin(adjlist.keys())]
    nodes = friends['ID'].values
    print('Nodes that have partisanship info: ', len(nodes))
    user_dict = friends.to_dict(orient='records')
    user_dict = {user['ID']: {'Partisanship': user['Partisanship'], 'Misinformation': user['Misinformation']} for user in user_dict}
    
    G = nx.DiGraph() 
    # Directed network follower -> friend
    for s in nodes:
        G.add_node(s, partisanship = user_dict[s]['Partisanship'], misinfo=user_dict[s]['Misinformation']) 
        for f in adjlist[s]:
            G.add_edge(s,f)
    
    return filter_graph(G, nodes)

def filter_graph(G, nodes_to_filter):
    average_friends = G.number_of_edges() / G.number_of_nodes()
    print("{} nodes and {} edges initially, with average number of friends {}".format(G.number_of_nodes(), G.number_of_edges(), average_friends))
    friends = nx.subgraph(G, nodes_to_filter)
    print("{} nodes and {} edges after filtering".format(friends.number_of_nodes(), friends.number_of_edges()))

    # k-core decomposition until ~ 10k nodes in core
    core_number = nx.core_number(friends)
    nodes = friends.number_of_nodes()
    k = 0
    while nodes > 10000:
        k_core = nx.k_core(friends, k, core_number)
        nodes = k_core.number_of_nodes()
        k += 10
    while nodes < 10000:
        k_core = nx.k_core(friends, k, core_number)
        nodes = k_core.number_of_nodes()
        k -= 1
    print("{}-core has {} nodes, {} edges".format(k, k_core.number_of_nodes(), k_core.number_of_edges()))
    
    # the network is super dense, so let us delete a random sample of edges
    # we can set the initial average in/out-degree (average_friends) as a target 
    friends_core = k_core.copy()
    edges_to_keep = int(friends_core.number_of_nodes() * average_friends)
    edges_to_delete = friends_core.number_of_edges() - edges_to_keep
    deleted_edges = random.sample(friends_core.edges(), edges_to_delete)
    friends_core.remove_edges_from(deleted_edges)
    print("{}-core after edge-sampling has {} nodes, {} edges, and average number of friends {}".format(k, friends_core.number_of_nodes(), friends_core.number_of_edges(), friends_core.number_of_edges() / friends_core.number_of_nodes()))
    return friends_core

def make_network_fil():
    print('FIL results:')
    # File has 3 columns: ID \t partisanship \t misinformation \n
    partisanship = {}
    misinformation = {}
    with open(path + "/measures.tab") as fd:
        rd = csv.reader(fd, delimiter="\t")
        next(rd) # skip header row
        for row in rd:
            partisanship[int(row[0])] = row[1]
            misinformation[int(row[0])] = row[2]

    with open(path + '/anonymized-friends.json') as fp:
        adjlist = json.load(fp)

    G = nx.DiGraph() 
    # Directed network follower -> friend
    for s in adjlist:
        n = int(s)
        if n in partisanship and n in misinformation:
            G.add_node(n, party=partisanship[n], misinfo=misinformation[n]) 
            for f in adjlist[s]:
                G.add_edge(n,f)
    filter_graph(G, partisanship.keys())

friends_core  = make_network_bao(path, files)
nx.write_gml(friends_core, os.path.join(path, 'follower_network.gml.gz'))
