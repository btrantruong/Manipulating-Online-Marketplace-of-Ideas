""" Values are used for experiments prior to Oct 28, 2022
    Corresponding configs (specified in the code comments) are created in experiement_config_archive.py
"""

import os
import numpy as np

follower_network = "follower_network.gml"
mode = "igraph"


# # default values for the results in results/final*
# DEFAULT_BETA = 0.1
# DEFAULT_GAMMA = 0.5


# DEFAULT_THETA = 5 #default for results/09222022*
DEFAULT_THETA = 1
DEFAULT_BETA = 0.05
DEFAULT_GAMMA = 0.01
MINIMAL_GAMMA = 0.0001
# DEFAULT_GAMMA = 0.05 #values for results in results/config_fivefive
DEFAULT_STRATEGY = None

# vals for exp 09292022. vary 1 variable while keeping the rest fixed
# BETA_SWIPE = [DEFAULT_BETA]
# GAMMA_SWIPE = sorted(list(10.0**(np.arange(-4, 0))))
# THETA_SWIPE = [2, 4, 8 ,16, 32] # default 1 can be copied from vary_gamma
# PHI_SWIPE = list(range(2,11)) # default 1 can be copied from vary_gamma
# MU_SWIPE = [0.25, 0.75, 0.9] #because 0.5 is the default


# vals for exp 10102022. vary 2 variables
BETA_SWIPE = [DEFAULT_BETA]
GAMMA_SWIPE = sorted(list(10.0 ** (np.arange(-4, 0))))
THETA_SWIPE = [1, 2, 4, 8, 16, 32]  # default 1 can be copied from vary_gamma
PHI_SWIPE = list(range(1, 11))  # default 1 can be copied from vary_gamma
MU_SWIPE = [0.25, 0.75, 0.9]  # because 0.5 is the default


# # Vals for all full exps before 09222022
# Keep these arrays to match config with the networks we've created.
BETA = sorted(list(10.0 ** (np.arange(-4, 0))) + list(5 * (10.0 ** (np.arange(-4, 0)))))
GAMMA = sorted(
    list(10.0 ** (np.arange(-4, 0))) + list(5 * (10.0 ** (np.arange(-4, 0))))
)
# [0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 0.5]


# # vals for exp 09222022
# BETA_SWIPE = [DEFAULT_BETA]
# GAMMA_SWIPE = sorted(list(10.0**(np.arange(-4, 0))))
# THETA_SWIPE = [2, 4, 8 ,16, 32]
# PHI_SWIPE = list(range(1,11))

## First iteration of checking beta gamma theta (onepct, tenpct, fivepct.smk)
# BETA_SHORT = [0.01, 0.1]
# THETA_SHORT = [1, 10, 100]

## Second iteration of checking beta gamma theta (results in results/fivefive*)
# GAMMA_SHORT = [0.05]
# BETA_SHORT = [0.01, 0.1]
# THETA_SHORT = [1, 2, 5, 8 ,10]

RHO = [0.125, 0.25, 0.5, 0.8]
EPSILON = [0.0001]


TARGETING = [None, "hubs", "partisanship", "conservative", "liberal", "misinformation"]
# values for the results in results/final*
# PHI_LIN = list(range(1,11))
PHI_LIN = [1, 2, 4, 8, 10]
THETA = [1, 2, 4, 6, 8, 10, 12, 14]


all_exps = {}

## NEW (FINAL) DEFAULT:

infosys_default = {
    "trackmeme": True,
    "verbose": False,
    "epsilon": 0.0001,
    "rho": 0.8,
    "mu": 0.5,
    "phi": 1,
    "alpha": 15,
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

fivepctbot_minimal_infiltration_default_net = {
    "beta": 0.05,
    "gamma": MINIMAL_GAMMA,
    "targeting_criterion": None,
    "verbose": False,
    "human_network": follower_network,
}

fivepctbot_default_net = {
    "beta": 0.05,
    "gamma": DEFAULT_GAMMA,
    "targeting_criterion": None,
    "verbose": False,
    "human_network": follower_network,
}

onepctbot_default_net = {
    "beta": 0.01,
    "gamma": DEFAULT_GAMMA,
    "targeting_criterion": None,
    "verbose": False,
    "human_network": follower_network,
}

tenpctbot_default_net = {
    "beta": 0.1,
    "gamma": DEFAULT_GAMMA,
    "targeting_criterion": None,
    "verbose": False,
    "human_network": follower_network,
}

# compare_strategies_net = {strategy: {'beta': DEFAULT_BETA, 'gamma': DEFAULT_GAMMA, 'targeting_criterion': strategy} for strategy in TARGETING}
