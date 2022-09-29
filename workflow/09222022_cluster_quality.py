import infosys.utils as utils 
import igraph as ig
import os 
import pandas as pd

## Previously: Look at verbose files where beta=0.005, gamma=0.5. (final_strategies_vary_beta_2runs/conservative3.json)
# /N/u/baotruon/Carbonate/marketplace/exp_clustering_quality.out 

res_dir = '/N/slate/baotruon/marketplace/newpipeline/verbose'
folder = '09222022_strategies_vary_gamma_2runs'

def get_data(strategy):
    ## READ VERBOSE DATA
    fpath = os.path.join(res_dir, folder, f'{strategy}3.json.gz')
    data = utils.read_json_compressed(fpath)
    ## READ GRAPH (to get communities)
    graph = ig.Graph.Read_GML(data['graph_gml'])
    humans = [node for node in graph.vs if node['uid'].isdigit()]
    bots = [node for node in graph.vs if node['uid'].isdigit() is False]

    # Note that for info sys net, the bots don't have party
    communities = {} #dict of community - list of idxs
    communities['conservative']= [node['uid'] for node in humans if float(node['party']) > 0]
    communities['liberal']= [node['uid'] for node in humans if float(node['party']) < 0]
    communities['misinfo'] = [h['uid'] for h in humans if float(h['misinfo'])>0.4]
    return data['all_memes'][0], data['all_feeds'][0], communities


def get_cluster_qual(memes, feeds, uids):
    quals = []
    all_fitness = []
    for uid in uids:
        memes_in_feed = [i for memeidx in feeds[uid] for i in memes if i['id']== memeidx]
        quality = [meme['quality'] for meme in memes_in_feed]
        fitness = [meme['fitness'] for meme in memes_in_feed]
        quals += quality
        all_fitness += fitness
    avg_qual = sum(quals)/len(quals)
    avg_fitness = sum(all_fitness)/len(all_fitness)
    return avg_qual, avg_fitness

def compare_cluster_quality(strategies):
    """
    get clustering quality for each group of agents 
    eg: strategy1: conservative, strategy2: None
    Return 2 dfs (quality/fitness) where:
    each row: results for a strategy 
    each col: quality/fitness for a cluster (conservative, liberal, misinfo)

    """
    CLUSTERS = ['conservative', 'liberal', 'misinfo']
    quals = []
    fitness =[]
    for strategy in strategies:
        print(f'-- calculating for {strategy}..')
        memes, feeds, communities =  get_data(strategy)
        qual_dict = {'strategy':strategy} # dict: e.g: {'liberal': qual, 'misinfo': qual}
        fitness_dict = {'strategy':strategy}
        
        for cluster in CLUSTERS:
            vals = get_cluster_qual(memes, feeds, communities[cluster])
            qual_dict[cluster] = vals[0]
            fitness_dict[cluster] = vals[1]
            print(f'quality {cluster}: {qual_dict[cluster]}')
            print(f'fitness {cluster}: {fitness_dict[cluster]}')
        
        quals +=[qual_dict]
        fitness +=[fitness_dict]

    quality_df = pd.DataFrame.from_records(quals)
    fitness_df = pd.DataFrame.from_records(fitness)
    return quality_df, fitness_df

if __name__=="__main__":
    strategies= ['conservative', 'liberal', 'None']
    quality_df, fitness_df = compare_cluster_quality(strategies)
    # note that file obj is opened with mode 'wb', not 'w'
    out1 = utils.safe_open(os.path.join('exps', '09292022_clustering','quality.csv'), mode='wb')
    quality_df.to_csv(out1, index=False)
    out2 = utils.safe_open(os.path.join('exps', '09292022_clustering','fitness.csv'), mode='wb')
    fitness_df.to_csv(out2, index=False)