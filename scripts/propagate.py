
""" Script for running simulation - Use for snakemake"""
# from InfoSystem import InfoSystem
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


def run_simulation(infosys_specs):
    # baseline:  mu=0.5, alpha=15, beta=0.01, gamma=0.001, phi=1, theta=1
    print("Create InfoSystem instance..")
    follower_sys = InfoSystem(**infosys_specs)
    print("Start simulation (mode: %s).." %infosys_specs['mode'])
    all_feeds,  meme_popularity, avg_quality = follower_sys.simulation()
    print("average quality for follower network:", avg_quality)
    return all_feeds, meme_popularity, avg_quality
    

def main(args):
    parser = argparse.ArgumentParser(
        description='run simulation on an igraph instance of InfoSystem',
    )

    parser.add_argument('-i', '--infile',
        action="store", dest="infile", type=str, required=True,
        help="path to input gml file of network")
    parser.add_argument('-o', '--outdir',
        action="store", dest="outfile", type=str, required=True,
        help="path to output directory")
    parser.add_argument('--mode',
        action="store", dest="mode", type=str, required=True,
        help="mode of implementation ['igraph', 'nx', 'infosys']")
    parser.add_argument('--trackmeme',
        action="store", dest="trackmeme", type=str, required=True,
        help="whether to track meme popularity")
    parser.add_argument('--verbose',
        action="store", dest="verbose", type=str, required=True,
        help="verbose")
    parser.add_argument('--eps',
        action="store", dest="epsilon", type=str, required=True,
        help="quality diff")
    parser.add_argument('--mu',
        action="store", dest="mu", type=str, required=True,
        help="tweet or retweet")
    parser.add_argument('--phi',
        action="store", dest="phi", type=str, required=True,
        help="fitness differential between humans and bots")
    parser.add_argument('--alpha',
        action="store", dest="alpha", type=str, required=True,
        help="feed size")
    parser.add_argument('--theta',
        action="store", dest="theta", type=str, required=True,
        help="bot flooding capability (number of retweet copies)")

    args = parser.parse_args(args)
    outdir = args.outdir
    infosys_specs = {
        "graph_gml": args.infile,
        "mode" : args.mode,
        "trackmeme": args.trackmeme,
        # "preferential_targeting": None,
        "verbose": args.verbose,
        "epsilon": args.epsilon,
        "mu": args.mu,
        "phi": args.phi,
        "alpha": args.alpha,
        "theta": args.theta
    }
    all_feeds, meme_popularity, avg_quality = run_simulation(infosys_specs)
    if len(all_feeds) > 0:
        pkl.dump(all_feeds, open(os.path.join(outdir, "meme.pkl"), 'wb'))
        pkl.dump(meme_popularity, open(os.path.join(outdir, "meme_popularity.pkl"), 'wb'))
    else:
        pass

if __name__ == "__main__": main(sys.argv[1:])

