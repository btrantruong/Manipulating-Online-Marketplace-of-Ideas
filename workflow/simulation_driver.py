""" Script for running simulation - Use for debugging"""
from infosys.ig_InfoSys import InfoSystem
import infosys.utils as utils
import infosys.ig_utils as ig_utils
import infosys.graphutils as graphutils
from infosys.profileit import profile

import igraph
import networkx as nx 
from pathlib import Path
import pickle as pkl 
import json
import os
import copy
import gzip 

# ABS_PATH = "/N/u/baotruon/Carbonate/marketplace"
ABS_PATH = ''
DATA_PATH = os.path.join(ABS_PATH, "data")
# TODO: save network as .gml.gz, keep only friend relationships

# @profile
def bao_simulation(mode='igraph'):
    path = DATA_PATH

    follower_path = os.path.join(path, "follower_network.gml")
    infosys_path = os.path.join(path, mode, "network.gml")
    
    net_specs = {
        "targeting_criterion": "hubs",
        # "human_network": follower_path,
        "human_network": None, #DEBUG
        "n_humans": 100,
        "beta": 0.01,
        "gamma": 0.001,
        "verbose": True,
    }

    infosys_specs = {
        "trackmeme": True,
        "tracktimestep": True,
        "verbose": True,
        "epsilon": 0.1, #TODO: change back to 0.001
        "mu": 0.5,
        "phi": 1,
        "alpha": 15,
    }

    if utils.make_sure_file_exists(infosys_path) is False:
        if mode=='igraph':
            G = ig_utils.init_net(**net_specs)
            if utils.make_sure_dir_exists(path, mode):
                G.write_gml(infosys_path)
        else:
            G = graphutils.init_net(**net_specs)
            # nx.write_edgelist(G, "follower_net.edgelist.gz")
            if utils.make_sure_dir_exists(path, mode):
                nx.write_gml(G, infosys_path)

    print("Create InfoSystem instance..")
    follower_sys = InfoSystem(os.path.join(path,mode, "network.gml"), mode=mode, **infosys_specs)
    print("Start simulation (mode: %s).." %mode)
    verbose_results = follower_sys.simulation()
    # b: code if not saving meme and feed info
    # avg_quality, diversity, tau_tuple, quality_timestep= follower_sys.simulation()
     # print("average quality: %s - diversity: %s - tau: %s (p=%s)" %(avg_quality, diversity, tau_tuple[0], tau_tuple[1]))
   
    results = {'quality': verbose_results['quality'],
               'diversity': verbose_results['diversity'],
               'discriminative_pow': verbose_results['discriminative_pow']
    }
    print("average quality: %s - diversity: %s - tau: %s (p=%s)" %(results['quality'], results['diversity'], 
    results['discriminative_pow'][0], results['discriminative_pow'][1]))

    specs = copy.deepcopy(infosys_specs)

    #save only results
    infosys_specs.update(results)
    outfile = os.path.join(path, mode, "results.json")
    fout = open(outfile,'w')
    json.dump(infosys_specs, fout)

    #save verbose
    specs.update(verbose_results)
    verboseout = os.path.join(path, mode, "results.json.gz")
    fout = open(outfile,'w')
    fout = gzip.open(verboseout,'w')
    utils.write_json_compressed(fout, specs)
    
if __name__ == "__main__":
    bao_simulation(mode='igraph')
    # bao_simulation(mode='nx')

