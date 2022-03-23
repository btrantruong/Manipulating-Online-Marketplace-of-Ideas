""" Returns relevant measurements: avg quality,
    zero fraction: fraction of low-quality memes in system
    Input: InfoSys.agent_feeds (dict of agent-feed(list of memes))
    & InfoSys.network
"""

#TODO: Rewrite these methods for ig_InfoSys
# calculate average quality of memes in system
# count_bot=False
def measure_average_quality(self):
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

# calculate fraction of low-quality memes in system (for tracked User)
#
def measure_average_zero_fraction(self):
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
    
# relationship between indegree (#followers) and low-quality in humans
#
def quality_vs_degree(G):
    avg_quality = {}
    n_zeros = {}
    for agent in G.nodes:
        if G.nodes[agent]["bot"] == False:
            count = 0
            total = 0
            zeros = 0
            for m in G.nodes[agent]["feed"]:
                count += 1
                total += m[0]
                if m[0] == 0:
                    zeros += 1
            k = G.in_degree(agent)
            if count > 0:
                if k not in avg_quality:
                    avg_quality[k] = []
                    n_zeros[k] = []
                avg_quality[k].append(total / count)
                n_zeros[k].append(zeros)
    for k in avg_quality:
        avg_quality[k] = statistics.mean(avg_quality[k])
    for k in n_zeros:
        n_zeros[k] = statistics.mean(n_zeros[k])
    return (avg_quality, n_zeros)