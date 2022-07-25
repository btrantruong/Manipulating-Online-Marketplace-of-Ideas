import os
import numpy as np 

# ABS_PATH = ''
ABS_PATH = '/N/slate/baotruon/marketplace'
DATA_PATH = os.path.join(ABS_PATH, "data")
follower_network = 'follower_network.gml'
mode = 'igraph'

BETA = sorted(list(10.0**(np.arange(-4, 0))) + list(5*(10.0**(np.arange(-4, 0)))))
GAMMA = sorted(list(10.0**(np.arange(-4, 0))) + list(5*(10.0**(np.arange(-4, 0)))))
#[0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 0.5]

TARGETING = [None, 'hubs', 'partisanship', 'conservative', 'liberal', 'misinformation']
COMPARE_TARGETING = [None, 'hubs']
PHI_LIN = list(range(1,11))
THETA = [1,2,4,6,8,10,12,14]

DEFAULT_BETA = 0.05
DEFAULT_GAMMA = 0.005
DEFAULT_STRATEGY = None
# DEBUG
# BETA = [0.1, 0.02]
# GAMMA = [0.1, 0.02]
# PHI_LIN = list(range(1,3))
# TARGETING = [None, 'hubs']
# THETA = [2,8]
#!TODO: Change back epsilon in default params! 

# PHI_LOG = [2,4,8,16,32]

all_exps = {}
## DEFAULT 
#Default:alpha (15), beta (0.01), gamma (0.001), phi (1), theta (1)
default_infosys = {
    'trackmeme': True,
    'verbose': False,
    'epsilon': 0.001,
    'mu': 0.5,
    'phi': 1,
    'alpha': 15,
    'theta': 1
}

# default_net = {'verbose':False, 'human_network': follower_network, 'beta':DEFAULT_BETA, 'gamma': DEFAULT_GAMMA, 'targeting_criterion':DEFAULT_STRATEGY}
default_net = {'verbose':False, 'human_network': follower_network, 'targeting_criterion':None, 'human_network': None}
compare_strategies_net = {strategy: {'beta': DEFAULT_BETA, 'gamma': DEFAULT_GAMMA, 'targeting_criterion': strategy} for strategy in COMPARE_TARGETING}
#gamma is 0.01 for the range in which targeting has some effect
# default_targeting = {'verbose':False, 'targeting_criterion':None, 'human_network': follower_network, 'beta': 0.01, 'gamma': 0.1}