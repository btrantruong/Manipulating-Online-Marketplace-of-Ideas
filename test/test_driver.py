""" Test driver.py. Note that subprocess is called with sys.executable to make sure it uses the same python version"""
import sys
import infosys.utils as utils
import infosys.ig_utils as ig_utils
import infosys.graphutils as graphutils
import subprocess
import networkx as nx 
import json
import os


# ABS_PATH = "/N/u/baotruon/Carbonate/marketplace"
ABS_PATH = ''
DATA_PATH = os.path.join(ABS_PATH, "data")
# TODO: save network as .gml.gz, keep only friend relationships

# @profile
def bao_simulation(mode='igraph'):
    path = DATA_PATH

    follower_path = os.path.join(path, "follower_network.gml")
    infosys_path = os.path.join(path, mode, "network.gml")
    infospec_path = os.path.join(path, mode, "config.json")
    net_specs = {
        "targeting_criterion":'hubs',
        # "human_network": follower_path,
        "human_network": None, #DEBUG
        "n_humans": 100,
        "beta": 0.5,
        "gamma": 0.1,
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
    
    if utils.make_sure_file_exists(infospec_path) is False:
        json.dump(infosys_specs, open(infospec_path, 'w'))

    outfile = os.path.join(path, mode, 'results.json')
    longoutfile = os.path.join(path, mode, 'results.json.gz')
    # subprocess.run(["python3","workflow/driver.py", "-i",  "%s"%infosys_path,  "-o", "%s"%outfile,  "-v", "%s"%longoutfile, "--config", "%s"%infospec_path, "--mode", "igraph", "--times", "2"])
    subprocess.run([sys.executable,"workflow/driver.py", "-i",  "%s"%infosys_path,  "-o", "%s"%outfile,  "-v", "%s"%longoutfile, "--config", "%s"%infospec_path, "--mode", "igraph", "--times", "2"])

if __name__ == "__main__":
    bao_simulation(mode='igraph')
    # bao_simulation(mode='nx')

