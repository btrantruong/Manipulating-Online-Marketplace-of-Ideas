import infosys.ig_utils as ig_utils
import infosys.graphutils as graphutils

import networkx as nx
import sys
import argparse
import json


def main(args):
    parser = argparse.ArgumentParser(
        description='initialize info system graph from human empirical network',
    )

    parser.add_argument('-i', '--infile',
        action="store", dest="infile", type=str, required=True,
        help="path to input .gml follower network file")
    parser.add_argument('-o', '--outfile',
        action="store", dest="outfile", type=str, required=True,
        help="path to out .gml info system network file (with bots and humans)")
    parser.add_argument('--config',
        action="store", dest="config", type=str, required=True,
        help="path to all configs file")
    parser.add_argument('--mode',
        action="store", dest="mode", type=str, required=True,
        help="mode of implementation")
    # parser.add_argument('--exp',
    #     action="store", dest="expno", type=str, required=True,
    #     help="experiment number in config file")
    
    # parser.add_argument('--targeting',
    #     action="store", dest="targeting", type=str, required=True,
    #     help="bot targeting strategy")
    # parser.add_argument('--beta',
    #     action="store", dest="beta", type=str, required=True,
    #     help="beta")
    # parser.add_argument('--gamma',
    #     action="store", dest="gamma", type=str, required=True,
    #     help="gamma")

    args = parser.parse_args(args)
    infile = args.infile #infile is a json containing list of {"beta": 0.0, "gamma": 0.0}
    outfile = args.outfile
    configfile = args.config
    mode = args.mode
    expno = args.expno
    # targeting = args.targeting
    # beta = args.beta
    # gamma = args.gamma

    # all_configs = json.load(open(configfile,'r'))
    # net_spec = all_configs[expno]
    net_spec = json.load(open(configfile,'r'))
    net_spec.update({'human_network':infile})

    if mode=="igraph":
        G = ig_utils.init_net(**net_spec)
        G.write_gml(outfile)
    else:
        G = graphutils.init_net(**net_spec)
        nx.write_gml(G, outfile)

if __name__ == '__main__': main(sys.argv[1:])