""" Script for running simulation - Use for debugging"""
from infosys.ig_InfoSys import InfoSystem
import infosys.utils as utils
import infosys.ig_utils as ig_utils
import infosys.graphutils as graphutils

import igraph
import networkx as nx 
from pathlib import Path
import pickle as pkl 
import json
import os

ABS_PATH = "/N/u/baotruon/Carbonate/marketplace"
# ABS_PATH = ''
# DATA_PATH = os.path.join(ABS_PATH, "data")
DATA_PATH = '/N/slate/baotruon/marketplace/data'

follower_path = os.path.join(DATA_PATH, "follower_network.gml")

hub = os.path.join(DATA_PATH, 'vary_thetagamma/13_gamma0.001.json')
nohub= os.path.join(DATA_PATH, 'vary_betagamma/gamma0.001.json')

default_infosys = {
    "trackmeme": True,
    "tracktimestep": True,
    "verbose": False,
    "epsilon": 0.001,
    "mu": 0.5,
    "phi": 1,
    "alpha": 15,
    "theta": 1
}
def bao_simulation(net_fpath, infosys_specs, mode='igraph'):
    if utils.make_sure_file_exists(net_fpath) is True:
        specs = {'graph_gml': net_fpath, 'mode':mode}.update(infosys_specs)

    ts = utils.get_now()
    timestep_fname = os.path.join(ABS_PATH, 'timestep_%s.pkl' %ts)

    print("Create InfoSystem instance..")
    print("Time step saved at %s" %ts)
    follower_sys = InfoSystem(**specs)
    print("Start simulation (mode: %s).." %mode)
    avg_quality, diversity, tau_tuple, quality_timestep= follower_sys.simulation()
    
    pkl.dump(quality_timestep, open(timestep_fname, 'wb'))

    print("average quality: %s - diversity: %s - tau: %s (p=%s)" %(avg_quality, diversity, tau_tuple[0], tau_tuple[1]))
    
if __name__ == "__main__":
    print('--- NO HUB')
    bao_simulation(nohub, default_infosys, mode='igraph')

    print('--- HUB')
    bao_simulation(hub, default_infosys, mode='igraph')

