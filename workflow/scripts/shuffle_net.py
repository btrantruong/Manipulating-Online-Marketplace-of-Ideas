import infosys.ig_utils as ig_utils
import igraph as ig
import infosys.graphutils as graphutils
import infosys.utils as utils 
import networkx as nx
import sys
import argparse
import json
import igraph


def main(args):
    parser = argparse.ArgumentParser(
        description='initialize info system graph from human empirical network',
    )

    parser.add_argument('-i', '--infile',
        action="store", dest="infile", type=str, required=True,
        help="path to input .gml info system network (with bots and humans)")
    parser.add_argument('-o', '--outfile',
        action="store", dest="outfile", type=str, required=True,
        help="path to output .gml shuffled network")
    parser.add_argument('--mode',
        action="store", dest="mode", type=str, required=True,
        help="shuffle strategy (community or hub)")


    args = parser.parse_args(args)
    infile = args.infile 
    outfile = args.outfile
    mode = args.mode

    try:
        graph = ig.Graph.Read_GML(infile)
        if mode=='community':
            shuffled = ig_utils.shuffle_preserve_community(graph)
        else:
            shuffled = ig_utils.shuffle_preserve_degree(graph)
        
        shuffled.write_gml(outfile)
    
    #Write empty file if exception so smk don't complain
    except Exception as e:
        print('Exception when creating shuffled network. Likely due to assertion error in shuffling')
        print(e)

        shuffled = igraph.Graph()
        shuffled.write_gml(outfile)

if __name__ == '__main__': main(sys.argv[1:])