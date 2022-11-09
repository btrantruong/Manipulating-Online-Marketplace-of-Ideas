"""
Use prior to 09292022
"""
import os
import numpy as np

# ABS_PATH = ''
ABS_PATH = "/N/slate/baotruon/marketplace"
DATA_PATH = os.path.join(ABS_PATH, "data")
follower_network = "follower_network.gml"
mode = "igraph"

BETA = sorted(list(10.0 ** (np.arange(-4, 0))) + list(5 * (10.0 ** (np.arange(-4, 0)))))
GAMMA = sorted(
    list(10.0 ** (np.arange(-4, 0))) + list(5 * (10.0 ** (np.arange(-4, 0))))
)
# [0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 0.5]

# Convergence criteria
""" Values used for first exploration of rho epsilon
/N/slate/baotruon/marketplace/newpipeline/results/convergence_criteria
oneminusrho = sorted(list(10.0**(np.arange(-5, 0))))
# [1e-05, 0.0001, 0.001, 0.01, 0.1]
RHO = [1-val for val in oneminusrho]
EPSILON = sorted(list(10.0**(np.arange(-5, 0))))
"""

""" Values used for 2nd exploration of rho epsilon
/N/slate/baotruon/marketplace/newpipeline/results/convergence_largerho
RHO = [0.125, 0.25, 0.5, 0.8]
EPSILON = sorted(list(10.0**(np.arange(-5, -2))))
# [1e-05, 0.0001, 0.001]
"""

RHO = [0.125, 0.25, 0.5, 0.8]
EPSILON = [0.0001]

TARGETING = [None, "hubs", "partisanship", "conservative", "liberal", "misinformation"]
COMPARE_TARGETING = [None, "hubs"]
PHI_LIN = list(range(1, 11))
THETA = [1, 2, 4, 6, 8, 10, 12, 14]

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
## OLD DEFAULT SETTINGS (before determining rho epsilon)
# Default:alpha (15), beta (0.01), gamma (0.001), phi (1), theta (1)
# default_infosys = {
#     'trackmeme': True,
#     'verbose': False,
#     'epsilon': 0.001,
#     'mu': 0.5,
#     'phi': 1,
#     'alpha': 15,
#     'theta': 1
# }

# 08152022: rho 0.5, epsilon 0.0001
infosys_rhoepsilon = {
    "trackmeme": True,
    "verbose": False,
    "epsilon": 0.0001,
    "rho": 0.8,
    "mu": 0.5,
    "phi": 1,
    "alpha": 15,
    "theta": 1,
}

infosys_hiepsilon = {
    "trackmeme": True,
    "verbose": False,
    "epsilon": 0.0001,
    "mu": 0.5,
    "phi": 1,
    "alpha": 15,
    "theta": 1,
}

infosys_lowepsilon = {
    "trackmeme": True,
    "verbose": False,
    "epsilon": 0.01,
    "mu": 0.5,
    "phi": 1,
    "alpha": 15,
    "theta": 1,
}

# default_net = {'verbose':False, 'human_network': follower_network, 'beta':DEFAULT_BETA, 'gamma': DEFAULT_GAMMA, 'targeting_criterion':DEFAULT_STRATEGY}
default_net = {
    "verbose": False,
    "human_network": follower_network,
    "targeting_criterion": None,
}
compare_strategies_net = {
    strategy: {
        "beta": DEFAULT_BETA,
        "gamma": DEFAULT_GAMMA,
        "targeting_criterion": strategy,
    }
    for strategy in COMPARE_TARGETING
}
compare_strategies_hiinfiltration = {
    strategy: {"beta": 0.1, "gamma": 0.01, "targeting_criterion": strategy}
    for strategy in COMPARE_TARGETING
}
# gamma is 0.01 for the range in which targeting has some effect
# default_targeting = {'verbose':False, 'targeting_criterion':None, 'human_network': follower_network, 'beta': 0.01, 'gamma': 0.1}
