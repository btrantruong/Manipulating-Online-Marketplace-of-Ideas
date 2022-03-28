
""" Script for running simulation - Use for snakemake"""
# from InfoSystem import InfoSystem
from torch import mode
from ig_InfoSys import InfoSystem
from profileit import profile
import graphutils
import ig_utils
from utils import *
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
    for _ in range(20):
        print("Create InfoSystem instance..")
        follower_sys = InfoSystem(**infosys_specs)
        print("Start simulation (mode: %s).." %infosys_specs['mode'])
        qual, diver, tau_p = follower_sys.simulation()
        avg_quality +=qual
        diversity +=diver
        tau_tuple += tau_p 
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
    # parser.add_argument('-i', '--indir',
    #     action="store", dest="indir", type=str, required=True,
    #     help="input directory path")
    # parser.add_argument('-o', '--outdir',
    #     action="store", dest="outfile", type=str, required=True,
    #     help="path to output directory")
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
    # parser.add_argument('--trackmeme',
    #     action="store", dest="trackmeme", type=str, required=True,
    #     help="whether to track meme popularity")
    # parser.add_argument('--verbose',
    #     action="store", dest="verbose", type=str, required=True,
    #     help="verbose")
    # parser.add_argument('--eps',
    #     action="store", dest="epsilon", type=str, required=True,
    #     help="quality diff")
    # parser.add_argument('--mu',
    #     action="store", dest="mu", type=str, required=True,
    #     help="tweet or retweet")
    # parser.add_argument('--phi',
    #     action="store", dest="phi", type=str, required=True,
    #     help="fitness differential between humans and bots")
    # parser.add_argument('--alpha',
    #     action="store", dest="alpha", type=str, required=True,
    #     help="feed size")
    # parser.add_argument('--theta',
    #     action="store", dest="theta", type=str, required=True,
    #     help="bot flooding capability (number of retweet copies)")

    args = parser.parse_args(args)
    infile = args.infile
    outfile = args.outfile
    configfile = args.config
    
    infosys_spec = json.load(open(configfile,'r'))
    # graph_file = os.path.join(indir, infosys_spec['graph_gml'])
    infosys_spec['graph_gml'] = infile
    infosys_spec['mode'] = args.mode

    qualities, diversities, tau_tuples = multiple_simulations(**infosys_spec)
    infosys_spec.update({
        'quality': qualities,
        'diversity': diversities,
        'discriminative_pow': tau_tuples
    })
    
    if len(qualities)>0:
        json.dump(infosys_spec,open(outfile,'w'))

if __name__ == "__main__": main(sys.argv[1:])

