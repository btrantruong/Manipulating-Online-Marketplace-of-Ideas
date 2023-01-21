import os
import numpy as np

follower_network = "follower_network.gml"
mode = "igraph"

### DONT CHANGE THESE VALUES ###

DEFAULT_PHI = 0
DEFAULT_THETA = 1
DEFAULT_BETA = 0.05
DEFAULT_GAMMA = 0.01
MINIMAL_GAMMA = 0.0001
DEFAULT_STRATEGY = None
DEFAULT_RHO = 0.8
DEFAULT_EPSILON = 0.0001
DEFAULT_MU = 0.5
DEFAULT_ALPHA = 15

GAMMA_SWIPE = sorted(list(10.0 ** (np.arange(-4, 0))))
THETA_SWIPE = [1, 2, 4, 8, 16, 32, 64]  # default 1 can be copied from vary_gamma
PHI_PROB = list(range(0, 11))  # default 0 can be copied from vary_gamma
MU_SWIPE = [0.1, 0.25, 0.5, 0.75, 0.9]  # because 0.5 is the default
ALPHA_SWIPE = [1, 2, 4, 8, 16, 32, 64, 128]

##### NETWORK INITIALIZATION #####
# Don't change! Keep these arrays to match config with the networks we've created.
TARGETING = [None, "hubs", "partisanship", "conservative", "liberal", "misinformation"]
BETA = sorted(list(10.0 ** (np.arange(-4, 0))) + list(5 * (10.0 ** (np.arange(-4, 0)))))
GAMMA = sorted(
    list(10.0 ** (np.arange(-4, 0))) + list(5 * (10.0 ** (np.arange(-4, 0))))
)
# [0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 0.5]

##### EXPLORING CONVERGENCE #####
RHO = [0.125, 0.25, 0.5, 0.8]
EPSILON = [0.0001]


infosys_default = {
    "trackmeme": True,
    "verbose": False,
    "epsilon": DEFAULT_EPSILON,
    "rho": DEFAULT_RHO,
    "mu": DEFAULT_MU,
    "phi": DEFAULT_PHI,
    "alpha": DEFAULT_ALPHA,
    "theta": DEFAULT_THETA,
}

default_net = {
    "beta": DEFAULT_BETA,
    "gamma": DEFAULT_GAMMA,
    "targeting_criterion": None,
    "verbose": False,
    "human_network": follower_network,
}


infosys_notracking = {
    "trackmeme": True,
    "track_forgotten": False,
    "verbose": False,
    "epsilon": 0.0001,
    "rho": 0.8,
    "mu": 0.5,
    "phi": 1,
    "alpha": 15,
    "theta": DEFAULT_THETA,
}

baseline_exp = {
    "beta": 0,
    "targeting_criterion": DEFAULT_STRATEGY,
    "gamma": 0,
    "verbose": False,
    "human_network": "follower_network.gml",
    "trackmeme": True,
    "epsilon": DEFAULT_EPSILON,
    "rho": DEFAULT_RHO,
    "mu": DEFAULT_MU,
    "phi": DEFAULT_PHI,
    "alpha": DEFAULT_ALPHA,
    "theta": DEFAULT_THETA,
}

extreme_exp = {
    "beta": DEFAULT_BETA,
    "targeting_criterion": DEFAULT_STRATEGY,
    "gamma": GAMMA_SWIPE[-1],
    "verbose": False,
    "human_network": "follower_network.gml",
    "trackmeme": True,
    "epsilon": DEFAULT_EPSILON,
    "rho": DEFAULT_RHO,
    "mu": DEFAULT_MU,
    "alpha": DEFAULT_ALPHA,
    "phi": PHI_PROB[-1],
    "theta": THETA_SWIPE[-1],
}

### PREVIOUS EXPLORATION WITH VARYING BETA ###

# fivepctbot_minimal_infiltration_default_net = {
#     "beta": 0.05,
#     "gamma": MINIMAL_GAMMA,
#     "targeting_criterion": None,
#     "verbose": False,
#     "human_network": follower_network,
# }

# fivepctbot_default_net = {
#     "beta": 0.05,
#     "gamma": DEFAULT_GAMMA,
#     "targeting_criterion": None,
#     "verbose": False,
#     "human_network": follower_network,
# }

# onepctbot_default_net = {
#     "beta": 0.01,
#     "gamma": DEFAULT_GAMMA,
#     "targeting_criterion": None,
#     "verbose": False,
#     "human_network": follower_network,
# }

# tenpctbot_default_net = {
#     "beta": 0.1,
#     "gamma": DEFAULT_GAMMA,
#     "targeting_criterion": None,
#     "verbose": False,
#     "human_network": follower_network,
# }
