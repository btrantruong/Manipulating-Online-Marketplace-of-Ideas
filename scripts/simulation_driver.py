from InfoSystem import InfoSystem
from profileit import profile
from graphutils import *
from utils import *
import string


ABS_PATH = ""
DATA_PATH = os.path.join(ABS_PATH, "data")

# create network of humans and bots
# preferential_targeting is a flag; if False, random targeting
# default n_humans=1000 but 10k for paper
# default beta=0.1 is bots/humans ratio
# default gamma=0.1 is infiltration: probability that a human follows each bot
#
@profile
def init_net(
    targeting_criterion=None,
    verbose=False,
    human_network=None,
    n_humans=1000,
    beta=0.1,
    gamma=0.1,
):

    # humans
    if human_network is None:
        if verbose:
            print("Generating human network...")
        H = random_walk_network(n_humans)
    else:
        if verbose:
            print("Reading human network...")
        H = read_empirical_network(human_network, add_feed=False)
        n_humans = H.number_of_nodes()
    for h in H.nodes:
        # h['bot'] = False #b
        H.nodes[h]["bot"] = False

    # bots
    if verbose:
        print("Generating bot network...")
    n_bots = int(n_humans * beta)
    B = random_walk_network(n_bots)
    for b in B.nodes:
        B.nodes[b]["bot"] = True

    # merge and add feed
    # Retain human and bot ids

    alphas = list(string.ascii_lowercase)
    nx.set_node_attributes(
        B, {node: str(node) + random.choice(alphas) for node in B.nodes}, name="ID"
    )
    nx.set_node_attributes(H, {node: str(node) for node in H.nodes}, name="ID")

    if verbose:
        print("Merging human and bot networks...")
    G = nx.disjoint_union(H, B)
    assert G.number_of_nodes() == n_humans + n_bots
    # b:now nodes are reindex so we want to keep track of which ones are bots and which are humans
    humans = [n for n in G.nodes if G.nodes[n]["bot"] is False]
    bots = [n for n in G.nodes if G.nodes[n]["bot"] is True]
    # b:initialize feed - Omit this because saving will fail
    #   # G.nodes[n]['feed'] = []

    # humans follow bots
    if verbose:
        print("Humans following bots...")
    if targeting_criterion is not None:
        if targeting_criterion == "hubs":
            w = [G.in_degree(h) for h in humans]
        elif targeting_criterion == "partisanship":
            w = [abs(float(G.nodes[h]["party"])) for h in humans]
        elif targeting_criterion == "misinformation":
            w = [float(G.nodes[h]["misinfo"]) for h in humans]
        elif targeting_criterion == "conservative":
            w = [1 if float(G.nodes[h]["party"]) > 0 else 0 for h in humans]
        elif targeting_criterion == "liberal":
            w = [1 if float(G.nodes[h]["party"]) < 0 else 0 for h in humans]
        else:
            raise ValueError("Unrecognized targeting_criterion passed to init_net")

    for b in bots:
        n_followers = 0
        for _ in humans:
            if random.random() < gamma:
                n_followers += 1
        if targeting_criterion is not None:
            followers = sample_with_prob_without_replacement(humans, n_followers, w)
        else:
            followers = random.sample(humans, n_followers)
        for f in followers:
            G.add_edge(f, b)

    return G


# TODO: save network as .gml.gz, keep only friend relationships


@profile
def bao_simulation():
    path = DATA_PATH

    follower_path = os.path.join(path, "follower_network.gml.gz")
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
        G = init_net(**net_specs)
        # nx.write_edgelist(G, "follower_net.edgelist.gz")
        nx.write_gml(G, os.path.join(path, "network.gml.gz"))

    print("Create InfoSystem instance..")
    follower_sys = InfoSystem(os.path.join(path, "network.gml.gz"), **infosys_specs)
    avg_quality = follower_sys.simulation()
    print("average quality for follower network:", avg_quality)


if __name__ == "__main__":
    bao_simulation()

