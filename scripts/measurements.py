""" Returns relevant measurements: avg quality,
    zero fraction: fraction of low-quality memes in system
    Input: InfoSys.agent_feeds (dict of agent-feed(list of memes))
    & InfoSys.network
"""

#TODO: Rewrite these methods for ig_InfoSys
# calculate average quality of memes in system
#
def measure_average_quality(G, count_bot=False):
    total = 0
    count = 0
    for agent in G.nodes:
        if count_bot == True or G.nodes[agent]["bot"] == False:
            for m in G.nodes[agent]["feed"]:
                total += m[0]
                count += 1
    return total / count


# calculate fraction of low-quality memes in system
#
def measure_average_zero_fraction(G):
    count = 0
    zeros = 0
    for agent in G.nodes:
        if G.nodes[agent]["bot"] == False:
            for m in G.nodes[agent]["feed"]:
                count += 1
                if m[0] == 0:
                    zeros += 1
    return zeros / count

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