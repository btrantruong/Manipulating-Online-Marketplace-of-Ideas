import networkx as nx
import csv
import json
import pandas as pd
import random
import importlib
# import model as bot_model
import bot_model
import os

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

ABS_PATH = ''
DATA_PATH = os.path.join(ABS_PATH, 'data')
path = DATA_PATH

follower_path = os.path.join(path, 'follower_network.gml.gz')

# baseline:  mu=0.5, alpha=15, beta=0.01, gamma=0.001, phi=1, theta=1

# follower_net = bot_model.init_net(False, verbose=True, human_network = follower_path, beta=0.01, gamma=0.001)
follower_net = bot_model.init_net(False, verbose=True, beta=0.01, gamma=0.001)
avg_quality = bot_model.simulation(False, network=follower_net, verbose=True, mu=0.5, phi=1, alpha=15)
print('average quality for follower network:', avg_quality)