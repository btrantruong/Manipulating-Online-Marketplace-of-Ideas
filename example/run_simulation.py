"""
    Minimal example for running simulation
"""
from infosys.ig_InfoSys import InfoSystem
import infosys.ig_utils as ig_utils
import json
import numpy as np
from collections import defaultdict
import os

DATA_PATH = "example/data"


def run_simulation(net_specs, infosys_specs, runs=10):
    G = ig_utils.init_net(**net_specs)

    network = os.path.join(DATA_PATH, "infosys_network.gml")
    G.write_gml(network)

    n_measures = defaultdict(lambda: [])

    quality = []
    print("Start simulation ..")
    for _ in range(runs):
        print("Create InfoSystem instance..")
        follower_sys = InfoSystem(network, **infosys_specs)
        verbose_results = follower_sys.simulation()

        quality += [verbose_results["quality"]]

        # Update results over multiple simulations
        for k, val in verbose_results.items():
            n_measures[k] += [val]

    print(f"*** Average quality: {np.round(np.mean(quality),3)} ***")
    print(len(quality))
    return n_measures


BETA = 0.1
GAMMA = 0.05
EPSILON = 0.0001

none_specs = {
    "targeting_criterion": None,
    "human_network": os.path.join(DATA_PATH, "follower_network.gml"),
    "n_humans": 50,
    # "beta": 0.02,
    # "gamma": 0.04,
    "beta": BETA,  # 2 bot
    "gamma": GAMMA,  # each has 5 followers
    "verbose": True,
}

infosys_specs = {
    "trackmeme": True,
    "tracktimestep": True,
    "track_forgotten": False,
    "verbose": False,
    "epsilon": EPSILON,
    "mu": 0.5,
    "phi": 10,
    "alpha": 15,
}

results = run_simulation(none_specs, infosys_specs, runs=1)
json.dump(results, open("results_phi10.json", "w"))

print("Finish saving results!")

