from infosys.User import User
from infosys.Meme import Meme
from infosys.profileit import profile
import infosys.utils as utils
import infosys.ig_utils as ig_utils
import igraph as ig

import networkx as nx
import random
import numpy as np
from collections import Counter 

"""
preferential_targeting = ['hubs', 'partisanship', 'misinformation', 'conservative', 'liberal']
or None for no targeting
"""
class InfoSystem:
    def __init__(self, graph_gml,
                mode='igraph', #mode is the implementation 
                # preferential_targeting=None,
                # count_forgotten=False,
                trackmeme=True,
                tracktimestep=None,
                verbose=False,
                epsilon=0.001,
                mu=0.5,
                phi=1,
                # gamma=0.1,
                alpha=15,
                theta=1):
        
        self.mode = mode
        self.network = None
        # self.preferential_targeting=preferential_targeting
        self.verbose = verbose
        self.trackmeme = trackmeme
        self.tracktimestep = tracktimestep
        self.quality_timestep=[]
        self.meme_popularity = None

        self.epsilon=epsilon
        self.mu=mu
        self.phi=phi
        # self.gamma=gamma 
        self.alpha=alpha
        self.theta=theta
        
        #Keep track of number of memes globally
        self.all_memes = []
        self.num_memes=0
        self.num_meme_unique=0
        self.memes_human_feed = 0
        self.quality_diff = 1
        self.quality = 1
        self.time_step=0
        
        if trackmeme is True:
            self.meme_popularity = {} #dict of {"meme_id": (human_popularity, bot_popularity)}

        if mode=='igraph': #Use igraph data struct
            try:
                self.network = ig.Graph.Read_GML(graph_gml)
                print(self.network.summary())
            except Exception as e:
                print(e)
            self.n_agents = self.network.vcount()
            self.agent_feeds = {agent['uid']:[] for agent in self.network.vs} #init an empty feed for all agents

        else: #Use our own data struct
            # dict of agent ids & list of their follower ids 
            self.follower_info = {}
            # only create a User object if that node is chosen during simulation
            # dict of agent ID - User obj for that agent
            self.tracking_agents = {}
            self._init_agents(graph_gml)
            self._init_followers()

        if verbose and mode=='igraph':
            in_deg = [self.network.degree(n, mode='in') for n in self.network.vs]#number of followers
            print('Graph Avg in deg', round(sum(in_deg)/len(in_deg),2))

    # @profile
    def _init_agents(self, graph_file):
        G = nx.read_gml(graph_file)
        
        # Try making 
        # bots = [n for n in G.nodes if G.nodes[n]['bot']==True]
        # humans = [n for n in G.nodes if G.nodes[n]['bot']==False]

        #debug
        bao_indeg = []

        for agent in G.nodes:
            id = G.nodes[agent]['uid']
            friend_ids= [G.nodes[n]['uid'] for n in G.successors(agent)]
            self.tracking_agents[id] = User(id, friend_ids, feed_size=self.alpha, is_bot=G.nodes[agent]['bot'])

            follower_ids = [G.nodes[n]['uid'] for n in G.predecessors(agent)]
            self.follower_info[id] = follower_ids
            if self.verbose:
                bao_indeg+=[len(follower_ids)]

        self.n_agents = nx.number_of_nodes(G)
        print('Initialized agents, total in original graph: {}, in Infosystem: {}'.format(self.n_agents, len(self.tracking_agents)))
        print('Number of edges: %s' %nx.number_of_edges(G))

        if self.verbose and self.mode!='igraph':
            print('Info Sys in deg: ', round(sum(bao_indeg)/len(bao_indeg),2))

    def _init_followers(self):
        for aidx, agent in self.tracking_agents.items():
            # if follower list hasn't been realized into Users(), do it
            if agent.followers is None:
                follower_list = []
                for fid in self.follower_info[aidx]:
                    follower_list += [self.tracking_agents[fid]] # add all User object based on ids from follower list
                agent.set_follower_list(follower_list)
        print('Finish populating followers')


    #TODO: Remove seed
    
    # @profile
    def simulation(self):
        while self.quality_diff > self.epsilon: 
            if self.verbose:
                # print('time_step = {}, q = {}, diff = {}'.format(self.time_step, self.quality, self.quality_diff), flush=True) 
                print('time_step = {}, q = {}, diff = {}, unique/human memes = {}/{}, all memes created={}'.format(self.time_step, self.quality, self.quality_diff, self.num_meme_unique, self.memes_human_feed, self.num_memes), flush=True) 

            self.time_step += 1
            if self.tracktimestep is True:
                self.quality_timestep+= [self.quality]

            for _ in range(self.n_agents):
                if self.mode!='igraph' and self.network is None: 
                    self.simulation_step(seed=self.num_meme_unique)
                else: #igraph mode
                    self.num_memes = sum([len(f) for f in self.agent_feeds.values() if len(f)>0])
                    self.ig_simulation_step(seed=self.num_meme_unique)
            self.update_quality()

            #TODO: track meme

        if self.mode=='igraph':
            all_feeds = self.agent_feeds
        else:
            all_feeds = self.tracking_agents

        # b: We don't need to save feed info & meme popularity in json anymore
        # feeds = {} 
        # for agent, memelist in all_feeds.items():
        #     feeds[agent] = [meme.__dict__  for meme in memelist] #convert to dict to avoid infinite recursion
        
        # return feeds, self.meme_popularity, self.quality

        self.all_memes = self._return_all_meme_info()
        tau, p_val = self.measure_kendall_tau()
        diversity = self.measure_diversity()
        return self.quality, diversity, (tau, p_val), self.quality_timestep


    # @profile
    def ig_simulation_step(self, seed=100):
        # random.seed(seed)
        agent = random.choice(self.network.vs)
        agent_id = agent['uid']
        feed = self.agent_feeds[agent_id]

        if len(feed) and random.random() > self.mu:
            # retweet a meme from feed selected on basis of its fitness
            meme = random.choices(feed, weights=[m.fitness for m in feed], k=1)[0] #random choices return a list
        else:
            # new meme
            self.num_meme_unique+=1
            meme = Meme(self.num_meme_unique, is_by_bot=agent['bot'], phi=self.phi)
            self.all_memes += [meme]

        #book keeping
        # TODO: add forgotten memes per degree
        if self.trackmeme is True:
            self._update_meme_popularity(meme, agent)

        # spread (truncate feeds at max len alpha)
        follower_idxs = self.network.predecessors(agent) #return list of int
        follower_uids = [n['uid'] for n in self.network.vs if n.index in follower_idxs]
        for follower in follower_uids:
            #print('follower feed before:', ["{0:.2f}".format(round(m[0], 2)) for m in G.nodes[f]['feed']])   
            # add meme to top of follower's feed (theta copies if poster is bot to simulate flooding)
        
            if agent['bot']==1:
                self._add_meme_to_feed(follower, meme, n_copies = self.theta)
            else:
                self._add_meme_to_feed(follower, meme)

            assert(len(self.agent_feeds[follower]) <= self.alpha)


    # @profile
    def simulation_step(self, seed=100):
        # random.seed(seed)
        id = random.choice(list(self.tracking_agents.keys())) # convert to list so that it's subscriptable
        agent = self.tracking_agents[id]
            
        # tweet or retweet
        if len(agent.feed) and random.random() > self.mu:
            # retweet a meme from feed selected on basis of its fitness
            meme = random.choices(agent.feed, weights=[m.fitness for m in agent.feed], k=1)[0] #random choices return a list
        else:
            # new meme
            self.num_meme_unique+=1
            meme = Meme(self.num_meme_unique, is_by_bot=agent.is_bot, phi=self.phi)

        #TODO: bookkeeping

        # spread (truncate feeds at max len alpha)
        
        for follower in agent.followers:
            #print('follower feed before:', ["{0:.2f}".format(round(m[0], 2)) for m in G.nodes[f]['feed']])   
            # add meme to top of follower's feed (theta copies if poster is bot to simulate flooding)
            
            if agent.is_bot==1:
                follower.add_meme_to_feed(meme, n_copies = self.theta)
                self.num_memes+=self.theta
            else:
                follower.add_meme_to_feed(meme)
                self.num_memes+=1
            assert(len(follower.feed)<=self.alpha)

    def update_quality(self):
        # use exponential moving average for convergence
        new_quality = 0.8 * self.quality + 0.2 * self.measure_average_quality()
        self.quality_diff = abs(new_quality - self.quality) / self.quality if self.quality > 0 else 0
        self.quality = new_quality

    def measure_kendall_tau(self):
        # calculate discriminative power of system
        # Call only after self._return_all_meme_info() is called 

        quality_ranked = sorted(self.all_memes, key=lambda m: m['quality']) 
        for ith, elem in enumerate(quality_ranked):
            elem.update({'qual_th':ith})
        
        share_ranked = sorted(quality_ranked, key=lambda m: m['human_shares']) 
        for ith, elem in enumerate(share_ranked):
            elem.update({'share_th':ith})

        idx_ranked = sorted(share_ranked, key=lambda m: m['id'])
        ranking1 = [meme['qual_th'] for meme in idx_ranked]
        ranking2 = [meme['share_th'] for meme in idx_ranked]
        tau, p_value = utils.kendall_tau(ranking1, ranking2)
        return tau, p_value

    def measure_average_quality(self):
        # calculate average quality of memes in system
        # count_bot=False
        # calculate meme quality for tracked Users
        total=0
        count=0
        if self.mode=='igraph':
            human_uids = [n['uid'] for n in self.network.vs if n['bot']==0]
            for u in human_uids:
                for meme in self.agent_feeds[u]:
                    total+= meme.quality
                    count+=1
        else:
            humans = [user for user in self.tracking_agents.values() if user.is_bot==0] 
            for user in humans:
                for meme in user.feed:
                    total += meme.quality
                    count +=1
        self.memes_human_feed = count
        return total / count if count >0 else 0

    #TODO: implement diversity 
    def measure_diversity(self):
        # calculate diversity of the system using entropy (in terms of unique memes)
        # Call only after self._return_all_meme_info() is called 

        humanshares = []
        for human, feed in self.agent_feeds.items():
            for meme in feed:
                humanshares += [meme.id]
        meme_counts = Counter(humanshares)
        count_byid = sorted(dict(meme_counts).items()) #return a list of [(memeid, count)], sorted by id
        humanshares = np.array([m[1] for m in count_byid])

        # humanshares = np.array([meme["human_shares"] for meme in self.all_memes])
        # humanshares = np.array([meme["human_shares"] for meme in self.all_memes])
        # botshares = np.array([meme["bot_shares"] for meme in self.all_memes])
        
        hshare_pct = np.divide(humanshares, sum(humanshares))
        diversity = utils.entropy(hshare_pct)*-1
        # Note that (np.sum(humanshares)+np.sum(botshares)) !=self.num_memes because a meme can be shared multiple times 
        return diversity

    
    def measure_average_zero_fraction(self):
        # calculate fraction of low-quality memes in system (for tracked User)
        count = 0
        zero_memes = 0 

        if self.mode=='igraph':
            human_uids = [n['uid'] for n in self.network.vs if n['bot']==0]
            for u in human_uids:
                zero_memes += sum([1 for meme in self.agent_feeds[u] if meme.quality==0])
                count += len(self.agent_feeds[u])
        else:
            human_agents = [agent for agent in self.tracking_agents.values() if agent.is_bot==0]
            for agent in human_agents:
                zero_memes += sum([1 for meme in agent.feed if meme.quality==0])
                count += len(agent.feed)
    
        return zero_memes / count

    def _add_meme_to_feed(self, agent_id, meme, n_copies=1):
        feed = self.agent_feeds[agent_id]
        feed[0:0] = [meme] * n_copies

        if len(feed) > self.alpha:
            self.agent_feeds[agent_id] = self.agent_feeds[agent_id][:self.alpha] # we can make sure dict values reassignment is correct this way
            # Remove memes from popularity info & all_meme list if extinct
            for meme in set(self.agent_feeds[agent_id][self.alpha:]):
                _ = self.meme_popularity.pop(meme.id, 'No Key found')
                self.all_memes.remove(meme)
            return True
        else:
            return True
    
    def _return_all_meme_info(self):
        #Be careful 
        memes = [meme.__dict__ for meme in self.all_memes]
        for meme_dict in memes:
            meme_dict.update(self.meme_popularity[meme_dict['id']])
        return memes

    def _update_meme_popularity(self, meme, agent):
        # meme_popularity is a value in a dict: list (is_by_bot, human popularity, bot popularity)
        # (don't use tuple! tuple doesn't support item assignment)
        if meme.id not in self.meme_popularity.keys():
            self.meme_popularity[meme.id] = {"is_by_bot": meme.is_by_bot, "human_shares":0, "bot_shares":0}
        
        if agent['bot']==0:
            self.meme_popularity[meme.id]["human_shares"] += 1
        else:
            self.meme_popularity[meme.id]["bot_shares"] += self.theta
        return 
