import networkx as nx
import random
import pandas as pd 
import json 

# create a network with random-walk growth model
# default p = 0.5 for network clustering
# default k_out = 3 is average no. friends within humans & bots
#
def random_walk_network(net_size, p=0.5, k_out=3, seed=100):
    if net_size <= k_out + 1:  # if super small just return a clique
        return nx.complete_graph(net_size, create_using=nx.DiGraph())
    G = nx.complete_graph(k_out, create_using=nx.DiGraph())

    random.seed(seed)

    for n in range(k_out, net_size):
        target = random.choice(list(G.nodes()))
        friends = [target]
        n_random_friends = 0
        for _ in range(k_out - 1):
            if random.random() < p:
                n_random_friends += 1
        friends.extend(random.sample(list(G.successors(target)), n_random_friends))
        friends.extend(random.sample(list(G.nodes()), k_out - 1 - n_random_friends))
        G.add_node(n)
        for f in friends:
            G.add_edge(n, f)
    return G


###----- I/O
# READ EMPIRICAL NETWORK FROM GML FILE
#
def read_empirical_network(file, add_feed=True):
    net = nx.read_gml(file)
    if add_feed:
        for n in net.nodes:
            net.nodes[n]["feed"] = []
    return net


def preprocess_follower(partisanship_file, follower_json, verbose=True):
  # Return follower network 
  # partisanship_file: tab-separated .csv file with 3 columns: File has 3 columns: ID, partisanship, misinformation
  # follower_json: .json file of key-value pairs, each one is a dict of {uid: friend's uid list}
  
  stats = pd.read_csv(partisanship_file, sep='\t')
  stats = stats.astype({'ID': str}).dropna(axis=0).drop_duplicates()
  stats = stats.dropna(how='any')

  with open(follower_json) as fp:
      adjlist = json.load(fp)
  adjlist = {k:[str(n) for n in vlist] for k, vlist in adjlist.items()} # convert uid to str

  friends = stats[stats['ID'].isin(adjlist.keys())]
  nodes = friends['ID'].values
  # Filter out nodes that have partisanship info
  user_dict = friends.to_dict(orient='records')
  user_dict = {user['ID']: {'Partisanship': user['Partisanship'], 'Misinformation': user['Misinformation']} for user in user_dict}

  G = nx.DiGraph() 
  # Directed network follower -> friend
  for s in nodes:
      G.add_node(s, partisanship = user_dict[s]['Partisanship'], misinfo=user_dict[s]['Misinformation']) 
      for f in adjlist[s]:
          G.add_edge(s,f)
  
  if verbose:
    average_friends = G.number_of_edges() / G.number_of_nodes()
    print("{} nodes and {} edges initially, with average number of friends {}".format(G.number_of_nodes(), G.number_of_edges(), average_friends))
    friends = nx.subgraph(G, nodes)
    print("{} nodes and {} edges after filtering".format(friends.number_of_nodes(), friends.number_of_edges()))
  
  return G 


def sample_network(G, k_nodes=10000):
  average_friends = G.number_of_edges() / G.number_of_nodes()
  print("{} nodes and {} edges initially, with average number of friends {}".format(G.number_of_nodes(), G.number_of_edges(), average_friends))
  friends = nx.subgraph(G, nodes)
  print("{} nodes and {} edges after filtering".format(friends.number_of_nodes(), friends.number_of_edges()))
# k-core decomposition until ~ 10k nodes in core
  core_number = nx.core_number(friends)
  nodes = friends.number_of_nodes()
  k = 0
  while nodes > k_nodes:
      k_core = nx.k_core(friends, k, core_number)
      nodes = k_core.number_of_nodes()
      k += 10
  while nodes < k_nodes:
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

  return G