from infosys.ig_InfoSys import InfoSystem
import infosys.utils as utils
import infosys.ig_utils as ig_utils
import json
import numpy as np 
import copy
from collections import defaultdict
import os
import pandas as pd 

DATA_PATH = 'exps'


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
        "epsilon": EPSILON, #TODO: change back to 0.001
        "mu": 0.5,
        "phi": 1,
        "alpha": 15,
    }

    return none_specs, hub_specs, infosys_specs

def run_simulation(net_specs, infosys_specs, strategy_name='hub', runs=10):
    G = ig_utils.init_net(**net_specs)
    
    network = os.path.join(DATA_PATH, '%s_network_lowinfiltration.gml' %strategy_name)
    G.write_gml(network)
    
    print("Create InfoSystem instance..")
    follower_sys = InfoSystem(network, **infosys_specs)
    
    n_measures = defaultdict(lambda: [])
    
    quality = []
    print("Start simulation ..")
    for i in range(runs):
        # print('--%s' %i)
        verbose_results = follower_sys.simulation()
        
        quality +=[verbose_results['quality']]
        
        #Update results over multiple simulations
        for k,val in verbose_results.items():
            n_measures[k] += [val]
            
    print(" \n *** Average quality (%s): %s " %(strategy_name, np.round(np.mean(quality),3)))
    print(len(quality))
    return n_measures

# is_verbose= False
# BETA = 0.04
# GAMMA=0.1
# EPSILON=0.0001
# hub_verbose = run_simulation(hub_specs, infosys_specs, strategy_name='hub', runs=10)

BETAs=[0.02, 0.04, 0.1]
GAMMAs = [0.02, 0.04, 0.1]
EPSILONs = [0.01, 0.001, 0.0001]

df = pd.DataFrame(columns=['strategy','beta', 'gamma', 'epsilon', 'avg_qual'])
for BETA in BETAs:
    for GAMMA in GAMMAs:
        for EPSILON in EPSILONs:
            try: 
                none_specs, hub_specs, infosys_specs = make_specs(BETA,GAMMA, EPSILON)

                print('*** Beta: %s - gamma: %s - epsilon: %s ***' %(BETA, GAMMA, EPSILON))
                none_verbose = run_simulation(none_specs, infosys_specs, strategy_name='none', runs=30)
                none_avg = np.round(np.mean(none_verbose['quality']),3)
                df.loc[len(df), :] = ['none', BETA, GAMMA, EPSILON, none_avg]

                hub_verbose = run_simulation(hub_specs, infosys_specs, strategy_name='hub', runs=30)
                hub_avg = np.round(np.mean(hub_verbose['quality']),3)
                df.loc[len(df), :] = ['hub', BETA, GAMMA, EPSILON, hub_avg]
                
            except Exception as e:
                print(e)

df.to_csv(os.path.join(DATA_PATH, 'syntheticnet_sim_results_30runs.csv'), sep='\t') 
print('Finish saving')          
