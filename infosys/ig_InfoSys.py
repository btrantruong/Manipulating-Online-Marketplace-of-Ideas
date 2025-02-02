""" 
Code to (re)produce results in the paper 
"Manipulating the Online Marketplace of Ideas" (Lou et al.)
https://arxiv.org/abs/1907.06130

Main class to run the simulation. Representing an Information System

Inputs: 
    - graph_gml (str): path to igraph .graphml file
    - track_forgotten (bool): if True, keep track of forgotten memes (track meme influx and outflux)
    - tracktimestep (bool): if True, track overall quality at each timestep 
    - verbose (bool): if True, print messages 
    - epsilon (float): threshold of quality difference between 2 consecutive timesteps to decide convergence. Default: 0.0001
    - rho (float): weight of the immediate past timestep's in calculating new quality. Default: 0.8
    - mu (float): probability that an agent create new memes. Default: 0.5
    - phi (int): phi*0.1 is the probability that a bot meme's fitness equals 1. Default: 0
    - alpha (int): agent's feedsize. Default: 15
    - theta (int): number of copies bots make when creating memes. Default: 1
Important note: 
    - graph_gml: link direction is following (follower -> friend), opposite of info spread!
    - Epsilon value was tested and fixed to the default values above.
        to ensure convergence on the empirical network or network with >=10000 nodes:
            - epsilon <= 0.0001
            - rho >= 0.5
Outputs:
    - measurements (dict): results and information tracked during the simulation. The fields are:
        - quality (float): average quality of all memes from a humans' feeds.
        - diversity (float): entropy calculated from all meme's quality
        - discriminative_pow (list): results of the Kendall's correlation coefficient test: [tau, p-value]
        - quality_timestep (list of dict): quality of the system over time 
        - all_memes (list of dict): each dictionary contains the meme's information. Dict keys are:
            - id (int): unique identifier for this meme
            - agent_id (str): uid of agent originating this meme
            - is_by_bot (int): 0 if meme is by human, 1 if by bot
            - phi (int): same as phi specified in InfoSys
            - quality (float): quality
            - fitness (float): engagement 
            - human_shares (int): number of shares by humans
            - bot_shares (int): number of shares by bots
            - spread_via_agents (list): list of uids of agents who reshared this meme
            - seen_by_agents (list): list of uids of agents who are exposed to this meme (disregard bot spam)
            - infeed_of_agents (list): list of uids of agents who are exposed to this meme (including bot spam)
            - qual_th (int): quality ranking
            - share_th (int): popularity ranking
        - all_feeds (dict): dictionary mapping agent's feed to the memes it contains at convergence
            Structure: {agent_id (str): meme ids(list)} 
            - agent_id (str): uid -- unique identifier of an agent (different from vertex id)
        - meme_influx: 
        - meme_netchange: 
        - reshares (list of dict): each dict is a reshare edge. The keys are:
            - meme_id (int): unique identifier of a meme
            - timestep (int): timestamp of the reshare
            - agent1 (str): uid of the agent spreading the meme
            - agent2 (str): uid of the agent resharing the meme
"""

from infosys.Meme import Meme
import infosys.utils as utils
import igraph as ig
import csv
import random
import numpy as np
from collections import Counter, defaultdict

# TODO: clean up the bool variable
# TODO: change default track_forgotten to False
# TODO: change phi to be in range [0,1]
class InfoSystem:
    def __init__(
        self,
        graph_gml,
        track_forgotten=False,
        tracktimestep=True,
        verbose=False,
        epsilon=0.0001,  # Don't change this value
        rho=0.8,  # Don't change this value, check note above
        mu=0.5,
        phi=0,
        alpha=15,
        theta=1,
    ):

        self.graph_gml = graph_gml
        self.network = None  # TODO: can remove this
        self.verbose = verbose
        self.track_forgotten = track_forgotten
        self.tracktimestep = tracktimestep
        self.quality_timestep = []
        if self.track_forgotten is True:
            # aggregate in and outflux caused by all agents
            print("Tracking forgotten memes")

            self.meme_all_changes = defaultdict(lambda: [])
            # track the influx and outflux of memes globally. #TODO: Might not need this later
            # All changes happening in simulation: max num_memes= alpha * num_agents * num_followers (avg)
            # structure: {"bot_in":[], "bot_out": [], "human_in":[], "human_out":[]} - items in list correspond to each timestep

        self.epsilon = epsilon
        self.rho = rho
        self.mu = mu
        self.phi = phi
        self.alpha = alpha
        self.theta = theta

        # Keep track of number of memes globally
        # list of dicts, contains of {"meme_id": meme.__dict__ and popularity information updated from self.meme_popularity}
        self.meme_dict = []
        self.all_memes = []  # list of Meme objects

        self.num_memes = 0  # for verbose debug
        self.num_meme_unique = 0  # for verbose debug
        self.memes_human_feed = 0  # for verbose debug
        self.quality_diff = 1
        self.quality = 1
        self.time_step = 0

        self.meme_popularity = {}
        # dict of popularity (all memes), structure: {"meme_id": {"is_by_bot": meme.is_by_bot, "human_shares":0, "bot_shares":0, "spread_via_agents":[]}}
        # self.reshares = [] # deprecated
        try:
            self.network = ig.Graph.Read_GML(self.graph_gml)
            print(self.network.summary())

            self.n_agents = self.network.vcount()
            self.agent_feeds = {
                agent["uid"]: [] for agent in self.network.vs
            }  # init an empty feed for all agents
            if self.track_forgotten is True:
                self.meme_net_change_timestep = {
                    "bot_in": [],
                    "bot_out": [],
                    "human_in": [],
                    "human_out": [],
                }
                # track the influx and outflux of memes globally.
                # All changes happening in simulation: max num_memes= alpha * num_agents
                # structure: {"bot_in":[], "bot_out": [], "human_in":[], "human_out":[]} - items in list correspond to each timestep

            if verbose:
                in_deg = [
                    self.network.degree(n, mode="in") for n in self.network.vs
                ]  # number of followers
                print("Graph Avg in deg", round(sum(in_deg) / len(in_deg), 2))

        except Exception as e:
            print(e)
            print(f"Graph file: {graph_gml}")

    # @profile
    def simulation(self, reshare_fpath, exposure_fpath, activation_fpath):
        """
        - reshare_fpath: path to .csv file containing reshare cascade info
        - exposure_fpath: path to .csv file containing exposure cascade info
        - activation_fpath: path to .csv file containing agent activation info
        """

        self.reshare_fpath = reshare_fpath
        reshare_fields = ["meme_id", "timestep", "agent1", "agent2"]
        with open(self.reshare_fpath, "w", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(reshare_fields)

        self.exposure_fpath = exposure_fpath
        exposure_fields = ["agent_id", "meme_id", "reshared_by_agent", "timestep"]
        with open(self.exposure_fpath, "w", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(exposure_fields)

        self.activation_fpath = activation_fpath
        activation_fields = ["agent_id", "timestep_activated", "meme_id"]
        with open(self.activation_fpath, "w", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(activation_fields)

        while self.quality_diff > self.epsilon:
            if self.verbose:
                # print('time_step = {}, q = {}, diff = {}'.format(self.time_step, self.quality, self.quality_diff), flush=True)
                print(
                    f"time_step = {self.time_step}, q = {self.quality}, diff = {self.quality_diff}, unique/human memes = {self.num_meme_unique}/{self.memes_human_feed}, all memes created={self.num_memes}",
                    flush=True,
                )

            self.time_step += 1
            if self.tracktimestep is True:
                self.quality_timestep += [self.quality]
            if self.track_forgotten is True:
                self.meme_all_changes_timestep = defaultdict(lambda: 0)
                # structure: {"bot_in":0, "bot_out": 0, "human_in":0, "human_out":0}

                self.meme_replacement = {
                    agent["uid"]: {
                        "bot_in": 0,
                        "bot_out": 0,
                        "human_in": 0,
                        "human_out": 0,
                    }
                    for agent in self.network.vs
                    if agent["bot"] == 0
                }

            for _ in range(self.n_agents):
                # simulation
                self.num_memes = sum(
                    [len(f) for f in self.agent_feeds.values() if len(f) > 0]
                )
                influx_by_agent_all = (
                    self.ig_simulation_step()
                )  # meme in outflux per agent {"bot_in":0, "bot_out": 0, "human_in":0, "human_out":0}
                # ^ self.meme_replacement is modified at this step

                if self.track_forgotten is True:
                    # add meme flow done by this agent (on all their followers) to the total changes by all agents in this cycle
                    for key in influx_by_agent_all.keys():
                        self.meme_all_changes_timestep[key] += influx_by_agent_all[key]

            # book keeping system's net meme flow
            if self.track_forgotten is True:
                for key in dict(self.meme_all_changes_timestep).keys():
                    # add total meme changes by all agents to the timeline
                    self.meme_all_changes[key] += [self.meme_all_changes_timestep[key]]

                for flow_type in self.meme_net_change_timestep.keys():
                    # update meme net change at the end of cycle to the timeline
                    total_flow = sum(
                        [
                            self.meme_replacement[agent][flow_type]
                            for agent in self.meme_replacement.keys()
                        ]
                    )
                    self.meme_net_change_timestep[flow_type] += [total_flow]

            self.update_quality()

        all_feeds = (
            self.agent_feeds
        )  # dict of {agent['uid']:[Meme()] } each value is a list of Meme obj in the agent's feed

        # b: Save feed info of agent & meme popularity
        feeds = {}
        for agent, memelist in all_feeds.items():
            # convert self.agent_feed into dict of agent_uid - [meme_id]
            feeds[agent] = [meme.id for meme in memelist]

        # return feeds, self.meme_popularity, self.quality
        self.meme_dict = (
            self._return_all_meme_info()
        )  # need to call this before calculating tau and diversity!!

        measurements = {
            "quality": self.quality,
            "diversity": self.measure_diversity(),
            "discriminative_pow": self.measure_kendall_tau(),
            "quality_timestep": self.quality_timestep,
            "all_memes": self.meme_dict,
            "all_feeds": feeds,
        }
        if self.track_forgotten is True:
            measurements["meme_influx"] = self.meme_all_changes
            measurements["meme_netchange"] = self.meme_net_change_timestep
        return measurements

    # @profile
    def ig_simulation_step(self):
        # returns dict: influx_by_agent_all: the number of memes changed in this cycle by all human agents

        agent = random.choice(self.network.vs)
        agent_id = agent["uid"]
        feed = self.agent_feeds[agent_id]

        self._update_activation_data(
            agent_id, self.time_step, [meme.id for meme in feed]
        )
        if len(feed) > 0 and random.random() > self.mu:
            # retweet a meme from feed selected on basis of its fitness
            # unpack because random choices return a list
            (meme,) = random.choices(feed, weights=[m.fitness for m in feed], k=1)
        else:
            # new meme
            self.num_meme_unique += 1
            meme = Meme(self.num_meme_unique, is_by_bot=agent["bot"], phi=self.phi)

            self.all_memes += [meme]

        # book keeping
        # TODO: add forgotten memes per degree
        self._update_meme_popularity(meme, agent)
        self._update_exposure(feed, agent)

        influx_by_agent_all = {
            "bot_in": 0,
            "bot_out": 0,
            "human_in": 0,
            "human_out": 0,
        }  # update meme_all_changes_timestep

        # spread (truncate feeds at max len alpha)
        follower_idxs = self.network.predecessors(agent)  # return list of int
        follower_uids = [n["uid"] for n in self.network.vs if n.index in follower_idxs]

        humfollower_uids = [
            n["uid"]
            for n in self.network.vs
            if (n.index in follower_idxs) and (n["bot"] == 0)
        ]

        for follower in follower_uids:
            # print('follower feed before:', ["{0:.2f}".format(round(m[0], 2)) for m in G.nodes[f]['feed']])
            # add meme to top of follower's feed (theta copies if poster is bot to simulate flooding)
            if agent["bot"] == 1:
                follower_influx = self._add_meme_to_feed(
                    target_id=follower,
                    meme=meme,
                    source_id=agent_id,
                    n_copies=self.theta,
                )
            else:
                follower_influx = self._add_meme_to_feed(
                    target_id=follower, meme=meme, source_id=agent_id
                )

            assert len(self.agent_feeds[follower]) <= self.alpha

            self._update_reshares(meme, agent_id, follower)

            # only track in-outflux for human agents
            if (self.track_forgotten is True) and (follower in humfollower_uids):
                for flowtype in follower_influx.keys():
                    influx_by_agent_all[flowtype] += follower_influx[flowtype]

                for flowtype in follower_influx.keys():
                    self.meme_replacement[follower][flowtype] = follower_influx[
                        flowtype
                    ]

        return influx_by_agent_all

    def update_quality(self):
        # use exponential moving average for convergence
        # new_quality = 0.8 * self.quality + 0.2 * self.measure_average_quality()
        new_quality = (
            self.rho * self.quality + (1 - self.rho) * self.measure_average_quality()
        )  # b: forget the past slowly
        self.quality_diff = (
            abs(new_quality - self.quality) / self.quality if self.quality > 0 else 0
        )
        self.quality = new_quality

    def measure_kendall_tau(self):
        # calculate discriminative power of system
        # Call only after self._return_all_meme_info() is called

        quality_ranked = sorted(self.meme_dict, key=lambda m: m["quality"])
        for ith, elem in enumerate(quality_ranked):
            elem.update({"qual_th": ith})

        share_ranked = sorted(quality_ranked, key=lambda m: m["human_shares"])
        for ith, elem in enumerate(share_ranked):
            elem.update({"share_th": ith})

        idx_ranked = sorted(share_ranked, key=lambda m: m["id"])
        ranking1 = [meme["qual_th"] for meme in idx_ranked]
        ranking2 = [meme["share_th"] for meme in idx_ranked]
        tau, p_value = utils.kendall_tau(ranking1, ranking2)
        return tau, p_value

    def measure_average_quality(self):
        # calculate average quality of memes in system
        # count_bot=False
        # calculate meme quality for tracked Users
        total = 0
        count = 0

        human_uids = [n["uid"] for n in self.network.vs if n["bot"] == 0]
        for u in human_uids:
            for meme in self.agent_feeds[u]:
                total += meme.quality
                count += 1

        self.memes_human_feed = count
        return total / count if count > 0 else 0

    def measure_diversity(self):
        # calculate diversity of the system using entropy (in terms of unique memes)
        # Call only after self._return_all_meme_info() is called

        humanshares = []
        for human, feed in self.agent_feeds.items():
            for meme in feed:
                humanshares += [meme.id]
        meme_counts = Counter(humanshares)
        # return a list of [(memeid, count)], sorted by id
        count_byid = sorted(dict(meme_counts).items())
        humanshares = np.array([m[1] for m in count_byid])

        hshare_pct = np.divide(humanshares, sum(humanshares))
        diversity = utils.entropy(hshare_pct) * -1
        # Note that (np.sum(humanshares)+np.sum(botshares)) !=self.num_memes because a meme can be shared multiple times
        return diversity

    def measure_average_zero_fraction(self):
        # calculate fraction of low-quality memes in system (for tracked User)
        count = 0
        zero_memes = 0

        human_uids = [n["uid"] for n in self.network.vs if n["bot"] == 0]
        for u in human_uids:
            zero_memes += sum([1 for meme in self.agent_feeds[u] if meme.quality == 0])
            count += len(self.agent_feeds[u])

        return zero_memes / count

    def _add_meme_to_feed(self, target_id, meme, source_id, n_copies=1):
        """
        Add meme to agent's feed, update all news feed information.
        Input: 
        - target_id (str): uid of agent resharing the meme -- whose feed we're adding the meme to 
        - meme (Meme object): meme being reshared
        - source_id (str): uid of agent spreading the meme
        """

        # Insert meme to feed. Forget if feed size exceeds alpha (Last in last out)
        # Return information about meme flow in/out of the feed
        feed = self.agent_feeds[target_id]
        feed[0:0] = [meme] * n_copies

        self._update_feed_data(target=target_id, meme_id=meme.id, source=source_id)
        # if self.track_forgotten is True:
        meme_influx = {"bot_in": 0, "bot_out": 0, "human_in": 0, "human_out": 0}

        if meme.is_by_bot == 1:
            meme_influx["bot_in"] = n_copies
        else:
            meme_influx["human_in"] = n_copies

        if len(feed) > self.alpha:
            if self.track_forgotten is True:
                forgotten = self.agent_feeds[target_id][
                    self.alpha :
                ]  # keep track of forgotten memes
                n_bot_out = len([meme for meme in forgotten if meme.is_by_bot == 1])
                n_human_out = len(forgotten) - n_bot_out

                meme_influx["bot_out"] = n_bot_out
                meme_influx["human_out"] = n_human_out

            self.agent_feeds[target_id] = self.agent_feeds[target_id][
                : self.alpha
            ]  # we can make sure dict values reassignment is correct this way
            # Remove memes from popularity info & all_meme list if extinct
            for meme in set(self.agent_feeds[target_id][self.alpha :]):
                _ = self.meme_popularity.pop(meme.id, "No Key found")
                self.all_memes.remove(meme)
            return dict(meme_influx)
        else:
            return dict(meme_influx)

    def _return_all_meme_info(self):
        for meme in self.all_memes:
            assert isinstance(meme, Meme)
        # Be careful: convert to dict to avoid infinite recursion
        memes = [meme.__dict__ for meme in self.all_memes]
        for meme_dict in memes:
            meme_dict.update(self.meme_popularity[meme_dict["id"]])
        return memes

    def _update_reshares(self, meme, source, target):
        """
        Update the reshare cascade information to a file. 
        Input: 
        - meme (Meme object): meme being reshared
        - source (str): uid of agent spreading the meme
        - target (str): uid of agent resharing the meme
        """
        # ncopies of the meme on agent2's feed can be referred from source uid & theta (if bot, theta)
        # reshare = {
        #     "meme_id": meme.id,
        #     "timestep": self.time_step,
        #     "agent1": source,
        #     "agent2": target,
        # }
        # self.reshares += [reshare]
        with open(self.reshare_fpath, "a", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow([meme.id, self.time_step, source, target])

        return

    def _update_activation_data(self, agent_id, timestep, meme_ids):
        """
        Update activation data
        fields: "agent_id", "timestep_activated", "meme_ids"]
        Input: 
        - agent_id (str): uid of agent being activated
        - timestep (int): timestep in which the agent is activate
        - meme_ids (list): list of meme ids in the agent's feed at activation
        """

        with open(self.activation_fpath, "a", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=",")
            for id in meme_ids:
                writer.writerow([agent_id, timestep, id])

        return

    def _update_feed_data(self, target, meme_id, source):
        """
        Concat news feed information to feed information at all time
        fields: "agent_id", "meme_id", "reshared_by_agent", "timestep"]
        Input: 
        - target: agent_id (str): uid of agent being activated
        - meme_id (int): id of meme in this agent's feed 
        - source: reshared_by_agent (str): uid of agent who shared the meme
        """

        with open(self.exposure_fpath, "a", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow([target, meme_id, source, self.time_step])

        return

    def _update_exposure(self, feed, agent):
        """
        Update human's exposure to meme whenever an agent is activated (equivalent to logging in)
        Input: 
        - feed (list of Meme objects): agent's news feed
        - agent (Graph vertex): agent resharing the meme
        """
        seen = []
        for meme in feed:
            if meme.id not in seen:
                self.meme_popularity[meme.id]["seen_by_agents"] += [agent["uid"]]
            self.meme_popularity[meme.id]["infeed_of_agents"] += [agent["uid"]]
            seen += [meme.id]
        return

    def _update_meme_popularity(self, meme, agent):
        """
        Update information of a meme whenever it is reshared. 
        Input: 
        - meme (Meme object): meme being reshared
        - agent (Graph vertex): agent resharing the meme
        """
        # (don't use tuple! tuple doesn't support item assignment)
        if meme.id not in self.meme_popularity.keys():
            self.meme_popularity[meme.id] = {
                "agent_id": agent["uid"],
                "is_by_bot": meme.is_by_bot,
                "human_shares": 0,
                "bot_shares": 0,
                "spread_via_agents": [],
                "seen_by_agents": [],  # disregard bot spam
                "infeed_of_agents": [],  # regard bot spam
            }

        self.meme_popularity[meme.id]["spread_via_agents"] += [agent["uid"]]

        if agent["bot"] == 0:
            self.meme_popularity[meme.id]["human_shares"] += 1
        else:
            self.meme_popularity[meme.id]["bot_shares"] += self.theta
        return

    def __repr__(self):
        """
        Define the representation of the object.
        """
        return "".join(
            [
                f"<{self.__class__.__name__}() object> constructed from {self.graph_gml}\n",
                f"epsilon: {self.epsilon} -- rho: {self.rho}\n",
                f"mu (posting rate): {self.mu} -- alpha (feedsize): {self.alpha}\n",
                f"phi (deception): {self.phi} -- theta (flooding): {self.theta}\n",
            ]
        )
