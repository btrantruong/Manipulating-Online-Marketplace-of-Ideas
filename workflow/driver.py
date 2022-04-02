
""" Script for running simulation - Use for snakemake"""

from infosys.ig_InfoSys import InfoSystem
import infosys.utils as utils
import infosys.ig_utils as ig_utils
import infosys.graphutils as graphutils
from infosys.profileit import profile

import sys
import igraph
import networkx as nx 
from pathlib import Path
import pickle as pkl 
import argparse
import json
import numpy as np 


def multiple_simulations(infosys_specs, times=20):
    # baseline:  mu=0.5, alpha=15, beta=0.01, gamma=0.001, phi=1, theta=1
    avg_quality = []
    diversity = []
    tau_tuple = []
    print("Run simulation %s times.." %times)
    for _ in range(times):
        print("Create InfoSystem instance..")
        follower_sys = InfoSystem(**infosys_specs)
        print("Start simulation (mode: %s).." %infosys_specs['mode'])
        qual, diver, tau_p = follower_sys.simulation()
        avg_quality +=[qual]
        diversity +=[diver]
        tau_tuple += [tau_p] 
    print("average quality for follower network: %s pm %s" %(np.mean(np.array(avg_quality)), np.std(np.array(avg_quality))))
    return avg_quality, diversity, tau_tuple


def run_simulation(infosys_specs):
    # baseline:  mu=0.5, alpha=15, beta=0.01, gamma=0.001, phi=1, theta=1
    print("Create InfoSystem instance..")
    follower_sys = InfoSystem(**infosys_specs)
    print("Start simulation (mode: %s).." %infosys_specs['mode'])
    avg_quality, diversity, tau_tuple = follower_sys.simulation()
    print("average quality for follower network:", avg_quality)
    return avg_quality, diversity, tau_tuple


def main(args):
    parser = argparse.ArgumentParser(
        description='run simulation on an igraph instance of InfoSystem',
    )

    parser.add_argument('-i', '--infile',
        action="store", dest="infile", type=str, required=True,
        help="path to input gml file of network")
    parser.add_argument('-o', '--outfile',
        action="store", dest="outfile", type=str, required=True,
        help="path to out .gml info system network file (with bots and humans)")
    parser.add_argument('--config',
        action="store", dest="config", type=str, required=True,
        help="path to all configs file")
    parser.add_argument('--mode',
        action="store", dest="mode", type=str, required=True,
        help="mode of implementation ['igraph', 'nx', 'infosys']")
    parser.add_argument('--times',
        action="store", dest="times", type=str, required=True,
        help="Number of times to run simulation")


    args = parser.parse_args(args)
    infile = args.infile
    outfile = args.outfile
    configfile = args.config
    n_simulations = args.times
    infosys_spec = json.load(open(configfile,'r'))

    # graph_file = os.path.join(indir, infosys_spec['graph_gml'])
    infosys_spec['graph_gml'] = infile
    infosys_spec['mode'] = args.mode

    #avoid passing undefined keyword to InfoSys
    gamma=None
    if 'gamma' in infosys_spec.keys():
        gamma = infosys_spec.pop('gamma')

    qualities, diversities, tau_tuples = multiple_simulations(infosys_spec, times=int(n_simulations))
    # add back gamma for completeness
    infosys_spec.update({
        'gamma': gamma,
        'quality': qualities,
        'diversity': diversities,
        'discriminative_pow': tau_tuples
    })
    
    if len(qualities)>0:
        # json.dump(infosys_spec,open(outfile,'w'))
        fout = open(outfile,'w')
        json.dump(infosys_spec, fout)
        # force writing out the changes
        fout.flush()
        
if __name__ == "__main__": main(sys.argv[1:])

