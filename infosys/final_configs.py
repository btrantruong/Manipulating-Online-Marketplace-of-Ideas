import os
import numpy as np 

follower_network = 'follower_network.gml'
mode = 'igraph'

BETA = sorted(list(10.0**(np.arange(-4, 0))) + list(5*(10.0**(np.arange(-4, 0)))))
GAMMA = sorted(list(10.0**(np.arange(-4, 0))) + list(5*(10.0**(np.arange(-4, 0)))))
#[0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 0.5]

GAMMA_SHORT = list(10.0**(np.arange(-4, 0)))
# 0.0001, 0.001, 0.01, 0.1 
BETA_SHORT = [0.01, 0.1]
THETA_SHORT = [1, 10, 100]

RHO = [0.125, 0.25, 0.5, 0.8]
EPSILON = [0.0001]

MU = list(np.arange(0.25,1,0.25)) + [0.9] # [0.25, 0.5, 0.75, 0.9]

TARGETING = [None, 'hubs', 'partisanship', 'conservative', 'liberal', 'misinformation']
PHI_LIN = list(range(1,11))
THETA = [1,2,4,6,8,10,12,14]

DEFAULT_BETA = 0.1
DEFAULT_GAMMA = 0.5
DEFAULT_STRATEGY = None

all_exps = {}

## NEW (FINAL) DEFAULT:

infosys_default = {
    'trackmeme': True,
    'verbose': False,
    'epsilon': 0.0001,
    'rho': 0.8,
    'mu': 0.5,
    'phi': 1,
    'alpha': 15,
    'theta': 1
}

default_net = {'beta': DEFAULT_BETA, 'gamma': DEFAULT_GAMMA, 'targeting_criterion':None,
                'verbose':False, 'human_network': follower_network}

infosys_notracking = {
    'trackmeme': False,
    'verbose': False,
    'epsilon': 0.0001,
    'rho': 0.8,
    'mu': 0.5,
    'phi': 1,
    'alpha': 15,
    'theta': 1
}

onepctbot_default_net = {'beta': 0.01, 'gamma': DEFAULT_GAMMA, 'targeting_criterion':None,
                'verbose':False, 'human_network': follower_network}

tenpctbot_default_net = {'beta': 0.1, 'gamma': DEFAULT_GAMMA, 'targeting_criterion':None,
                'verbose':False, 'human_network': follower_network}

# compare_strategies_net = {strategy: {'beta': DEFAULT_BETA, 'gamma': DEFAULT_GAMMA, 'targeting_criterion': strategy} for strategy in TARGETING}