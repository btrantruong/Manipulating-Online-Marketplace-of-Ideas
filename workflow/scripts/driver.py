
""" Script for running simulation - Use for snakemake"""

from infosys.ig_InfoSys import InfoSystem
import infosys.utils as utils

import gzip
import sys
import argparse
import json
import numpy as np 
import copy
from collections import defaultdict

def multiple_simulations(infosys_specs, times=20):
    # baseline:  mu=0.5, alpha=15, beta=0.01, gamma=0.001, phi=1, theta=1
    n_measures = defaultdict(lambda: [])

    print("Run simulation %s times.." %times)
    for _ in range(times):
        print("Create InfoSystem instance..")
        follower_sys = InfoSystem(**infosys_specs)
        print("Start simulation ..")
        measurements = follower_sys.simulation()

        #Update results over multiple simulations
        for k,val in measurements.items():
            n_measures[k] += [val]
            
    print("average quality for follower network: %s pm %s" %(np.mean(np.array(n_measures['quality'])), np.std(np.array(n_measures['quality']))))
    
    results = {'quality': n_measures['quality'],
               'diversity': n_measures['diversity'],
               'discriminative_pow': n_measures['discriminative_pow']
    }
    #return a short & long (more details) version of measurements
    return results, dict(n_measures)


def run_simulation(infosys_specs):
    # baseline:  mu=0.5, alpha=15, beta=0.01, gamma=0.001, phi=1, theta=1
    print("Create InfoSystem instance..")
    follower_sys = InfoSystem(**infosys_specs)
    print("Start simulation (mode: %s).." %infosys_specs['mode'])
    measurements = follower_sys.simulation()
    print("average quality for follower network:", measurements['quality'])
    return measurements


def main(args):
    #TODO: remove mode
    parser = argparse.ArgumentParser(
        description='run simulation on an igraph instance of InfoSystem',
    )

    parser.add_argument('-i', '--infile',
        action="store", dest="infile", type=str, required=True,
        help="path to input gml file of network")
    parser.add_argument('-o', '--outfile',
        action="store", dest="outfile", type=str, required=True,
        help="path to .json file containing infosys measurements")
    parser.add_argument('-v', '--verboseoutfile',
        action="store", dest="verboseoutfile", type=str, required=False,
        help="path to .json.gz file containing verbose infosys measurements (track all memes & feeds)")
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
    verboseout = args.verboseoutfile
    configfile = args.config
    n_simulations = args.times
    infosys_spec = json.load(open(configfile,'r'))

    # graph_file = os.path.join(indir, infosys_spec['graph_gml'])
    infosys_spec['graph_gml'] = infile
    infosys_spec['mode'] = args.mode

    #avoid passing undefined keyword to InfoSys
    legal_specs = utils.remove_illegal_kwargs(infosys_spec, InfoSystem.__init__)

    nruns_measurements, verbose_tracking = multiple_simulations(legal_specs, times=int(n_simulations))
    # add infosys configuration
    infosys_spec.update(nruns_measurements)
    
    if len(nruns_measurements['quality'])>0:
        fout = open(outfile,'w')
        json.dump(infosys_spec, fout)
        fout.flush()

        if verboseout is not None:
            specs = copy.deepcopy(infosys_spec)
            specs.update(verbose_tracking)
            fout = gzip.open(verboseout,'w')
            utils.write_json_compressed(fout, specs)
            # force writing out the changes
            fout.flush()
        
        
if __name__ == "__main__": main(sys.argv[1:])

