import networkx as nx
from User import User 

G = nx.read_gml('data/follower_network.gml.gz')
# G = nx.read_gml('network.gml.gz')
nodes = [n for n in G.nodes()]
for agent in nodes:
    name = G[agent]['ID']
