from infosys.profileit import profile
import infosys.utils as utils

import networkx as nx
import random
import pandas as pd
import json
import string

# create network of humans and bots
# preferential_targeting is a flag; if False, random targeting
# default n_humans=1000 but 10k for paper
# default beta=0.1 is bots/humans ratio
# default gamma=0.1 is infiltration: probability that a human follows each bot
#
# @profile
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
    B = random_walk_network(n_bots, seed=101)
    for b in B.nodes:
        B.nodes[b]["bot"] = True

    # merge and add feed
    # Retain human and bot ids

    alphas = list(string.ascii_lowercase)
    nx.set_node_attributes(
        B, {node: str(node) + random.choice(alphas) for node in B.nodes}, name="uid"
    )
    nx.set_node_attributes(H, {node: str(node) for node in H.nodes}, name="uid")

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

    random.seed(102)
    for b in bots:
        n_followers = 0
        for _ in humans:
            if random.random() < gamma:
                n_followers += 1
        if targeting_criterion is not None:
            followers = utils.sample_with_prob_without_replacement(humans, n_followers, w)
        else:
            followers = random.sample(humans, n_followers)
        for f in followers:
            G.add_edge(f, b)

    # if verbose:
    #     average_friends = G.number_of_edges() / G.number_of_nodes()
    #     print(
    #         "--INFO SYS NET (NX): {} nodes and {} edges, with average number of friends {}".format(
    #             G.number_of_nodes(), G.number_of_edges(), average_friends
    #         )
    #     )
    return G


# create a network with random-walk growth model
# default p = 0.5 for network clustering
# default k_out = 3 is average no. friends within humans & bots
#
#TODO: comment out random seed in actual run
def random_walk_network(net_size, p=0.5, k_out=3, seed=100):
    if net_size <= k_out + 1:  # if super small just return a clique
        return nx.complete_graph(net_size, create_using=nx.DiGraph())
    G = nx.complete_graph(k_out, create_using=nx.DiGraph())

    random.seed(seed)

    for n in range(k_out, net_size):
        target = random.choice(list(G.nodes()))
        friends = [target]
        n_random_friends = 0
        for _ in range(k_out - 1):
            if random.random() < p:
                n_random_friends += 1
        friends.extend(random.sample(list(G.successors(target)), n_random_friends))
        friends.extend(random.sample(list(G.nodes()), k_out - 1 - n_random_friends))
        G.add_node(n)
        for f in friends:
            G.add_edge(n, f)
    return G


###----- I/O
# READ EMPIRICAL NETWORK FROM GML FILE
#
def read_empirical_network(file, add_feed=True):
    net = nx.read_gml(file)
    if add_feed:
        for n in net.nodes:
            net.nodes[n]["feed"] = []
    return net


def preprocess_follower(partisanship_file, follower_json, verbose=True):
    # Return follower network
    # partisanship_file: tab-separated .csv file with 3 columns: File has 3 columns: ID, partisanship, misinformation
    # follower_json: .json file of key-value pairs, each one is a dict of {uid: friend's uid list}

    stats = pd.read_csv(partisanship_file, sep="\t")
    stats = stats.astype({"uid": str}).dropna(axis=0).drop_duplicates()
    stats = stats.dropna(how="any")

    with open(follower_json) as fp:
        adjlist = json.load(fp)
    adjlist = {
        k: [str(n) for n in vlist] for k, vlist in adjlist.items()
    }  # convert uid to str

    friends = stats[stats["uid"].isin(adjlist.keys())]
    nodes = friends["uid"].values
    # Filter out nodes that have partisanship info
    user_dict = friends.to_dict(orient="records")
    user_dict = {
        user["uid"]: {
            "Partisanship": user["Partisanship"],
            "Misinformation": user["Misinformation"],
        }
        for user in user_dict
    }

    G = nx.DiGraph()
    # Directed network follower -> friend
    for s in nodes:
        G.add_node(
            s,
            partisanship=user_dict[s]["Partisanship"],
            misinfo=user_dict[s]["Misinformation"],
        )
        for f in adjlist[s]:
            G.add_edge(s, f)

    if verbose:
        average_friends = G.number_of_edges() / G.number_of_nodes()
        print(
            "{} nodes and {} edges initially, with average number of friends {}".format(
                G.number_of_nodes(), G.number_of_edges(), average_friends
            )
        )
        friends = nx.subgraph(G, nodes)
        print(
            "{} nodes and {} edges after filtering".format(
                friends.number_of_nodes(), friends.number_of_edges()
            )
        )

    return G


def sample_network(G, k_nodes=10000):
    average_friends = G.number_of_edges() / G.number_of_nodes()
    print(
        "{} nodes and {} edges initially, with average number of friends {}".format(
            G.number_of_nodes(), G.number_of_edges(), average_friends
        )
    )
    friends = nx.subgraph(G, nodes)
    print(
        "{} nodes and {} edges after filtering".format(
            friends.number_of_nodes(), friends.number_of_edges()
        )
    )
    # k-core decomposition until ~ 10k nodes in core
    core_number = nx.core_number(friends)
    nodes = friends.number_of_nodes()
    k = 0
    while nodes > k_nodes:
        k_core = nx.k_core(friends, k, core_number)
        nodes = k_core.number_of_nodes()
        k += 10
    while nodes < k_nodes:
        k_core = nx.k_core(friends, k, core_number)
        nodes = k_core.number_of_nodes()
        k -= 1
    print(
        "{}-core has {} nodes, {} edges".format(
            k, k_core.number_of_nodes(), k_core.number_of_edges()
        )
    )

    # the network is super dense, so let us delete a random sample of edges
    # we can set the initial average in/out-degree (average_friends) as a target
    friends_core = k_core.copy()
    edges_to_keep = int(friends_core.number_of_nodes() * average_friends)
    edges_to_delete = friends_core.number_of_edges() - edges_to_keep
    deleted_edges = random.sample(friends_core.edges(), edges_to_delete)
    friends_core.remove_edges_from(deleted_edges)
    print(
        "{}-core after edge-sampling has {} nodes, {} edges, and average number of friends {}".format(
            k,
            friends_core.number_of_nodes(),
            friends_core.number_of_edges(),
            friends_core.number_of_edges() / friends_core.number_of_nodes(),
        )
    )

    return G

