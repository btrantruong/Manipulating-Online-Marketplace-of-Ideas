import ig_utils
import graphutils
import networkx as nx
import sys
import argparse

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
    parser.add_argument('--mode',
        action="store", dest="outfile", type=str, required=True,
        help="mode of implementation")
    parser.add_argument('--targeting',
        action="store", dest="targeting", type=str, required=True,
        help="bot targeting strategy")
    parser.add_argument('--beta',
        action="store", dest="beta", type=str, required=True,
        help="beta")
    parser.add_argument('--gamma',
        action="store", dest="gamma", type=str, required=True,
        help="gamma")

    args = parser.parse_args(args)
    infile = args.infile #infile is a json {"beta": 0.0, "gamma": 0.0}
    outfile = args.outfile
    mode = args.mode
    targeting = args.targeting
    beta = args.beta
    gamma = args.gamma

    if mode=="igraph":
        G = ig_utils.init_net(targeting_criterion=targeting, verbose=False, human_network=infile, beta=beta, gamma=gamma)
        G.write_gml(outfile)
    else:
        G = graphutils.init_net(targeting_criterion=targeting, verbose=False, human_network=infile, beta=beta, gamma=gamma)
        nx.write_gml(G, outfile)

if __name__ == '__main__': main(sys.argv[1:])