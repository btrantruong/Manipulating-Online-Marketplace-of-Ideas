from infosys.ig_InfoSys import InfoSystem
import infosys.utils as utils
import infosys.ig_utils as ig_utils
import json
import numpy as np 
import copy
from collections import defaultdict
import os
import pandas as pd 

DATA_PATH = 'workflow/example'


def make_specs(BETA,GAMMA, EPSILON, init_net_verbose=True, infosys_verbose=False):
    hub_specs = {
        "targeting_criterion": "hubs",
        "human_network": os.path.join(DATA_PATH, 'synthetic_humannet.gml'),
        "n_humans": 50,
        # "beta": 0.02, #1 bot
        # "gamma": 0.04, #each has 2 followers
        "beta": BETA, #2 bot
        "gamma": GAMMA, #each has 5 followers
        "verbose": init_net_verbose,
    }

    none_specs = {
            "targeting_criterion": None,
            "human_network": os.path.join(DATA_PATH, 'synthetic_humannet.gml'),
            "n_humans": 50,
            # "beta": 0.02,
            # "gamma": 0.04,
            "beta": BETA, #2 bot
            "gamma": GAMMA, #each has 5 followers
            "verbose": init_net_verbose,
        }

    infosys_specs = {
        "trackmeme": True,
        "tracktimestep": True,
        "track_forgotten": True,
        "verbose": infosys_verbose,
        "epsilon": EPSILON, 
        "mu": 0.5,
        "phi": 1,
        "alpha": 15,
    }

    return none_specs, hub_specs, infosys_specs

def run_simulation(net_specs, infosys_specs, runs=10):
    G = ig_utils.init_net(**net_specs)
    
    network = os.path.join(DATA_PATH, 'infosys_net.gml')
    G.write_gml(network)
    
    n_measures = defaultdict(lambda: [])
    
    quality = []
    print("Start simulation ..")
    for _ in range(runs):
        print("Create InfoSystem instance..")
        follower_sys = InfoSystem(network, **infosys_specs)
        verbose_results = follower_sys.simulation()
        
        quality +=[verbose_results['quality']]
        
        #Update results over multiple simulations
        for k,val in verbose_results.items():
            n_measures[k] += [val]
            
    print(f"*** Average quality: {np.round(np.mean(quality),3)} ***")
    print(len(quality))
    return n_measures


BETA = 0.04
GAMMA=0.1
EPSILON=0.0001
none_specs = {
            "targeting_criterion": None,
            "human_network": os.path.join(DATA_PATH, 'synthetic_humannet.gml'),
            "n_humans": 50,
            # "beta": 0.02,
            # "gamma": 0.04,
            "beta": BETA, #2 bot
            "gamma": GAMMA, #each has 5 followers
            "verbose": True,
        }

infosys_specs = {
    "trackmeme": True,
    "tracktimestep": True,
    "track_forgotten": True,
    "verbose": True,
    "epsilon": EPSILON, 
    "mu": 0.5,
    "phi": 1,
    "alpha": 15,
}

print(os.getcwd())
# none_specs, hub_specs, infosys_specs = make_specs(BETA,GAMMA, EPSILON)
hub_verbose = run_simulation(none_specs, infosys_specs, runs=1)