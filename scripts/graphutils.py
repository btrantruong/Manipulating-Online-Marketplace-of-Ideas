import networkx as nx
import random
# create a network with random-walk growth model
# default p = 0.5 for network clustering
# default k_out = 3 is average no. friends within humans & bots
#
def random_walk_network(net_size, p=0.5, k_out=3):
  if net_size <= k_out + 1: # if super small just return a clique
    return nx.complete_graph(net_size, create_using=nx.DiGraph())
  G = nx.complete_graph(k_out, create_using=nx.DiGraph()) 
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
            net.nodes[n]['feed'] = []
    return net