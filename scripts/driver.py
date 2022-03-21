# from InfoSystem import InfoSystem
from ig_InfoSys import InfoSystem
import graphutils
import ig_utils
from utils import *
import igraph
import networkx as nx 

ABS_PATH = "/N/u/baotruon/Carbonate/marketplace/igraph_vs_nx"
DATA_PATH = os.path.join(ABS_PATH, "data")

def run_simulation(mode='igraph'):
    path = DATA_PATH

    follower_path = os.path.join(path, "follower_network.gml")
    network_avail = False
    net_specs = {
        "targeting_criterion": "hubs",
        "human_network": follower_path,
        "n_humans": 1000,
        "beta": 0.01,
        "gamma": 0.001,
        "verbose": True,
    }

    infosys_specs = {
        "preferential_targeting": None,
        "verbose": True,
        "mu": 0.5,
        "phi": 1,
        "alpha": 15,
    }

    if network_avail is False:
        if mode=='igraph':
            G = ig_utils.init_net(**net_specs)
            if make_sure_dir_exists(path, mode):
                G.write_gml(os.path.join(path, mode, "network.gml"))
        else:
            G = graphutils.init_net(**net_specs)
            # nx.write_edgelist(G, "follower_net.edgelist.gz")
            if make_sure_dir_exists(path, mode):
                nx.write_gml(G, os.path.join(path,mode, "network.gml"))

    print("Create InfoSystem instance..")
    follower_sys = InfoSystem(os.path.join(path,mode, "network.gml"), mode=mode, **infosys_specs)
    avg_quality = follower_sys.simulation()
    print("average quality for follower network:", avg_quality)


if __name__ == "__main__":
    run_simulation(mode='igraph')
    run_simulation(mode='nx')

