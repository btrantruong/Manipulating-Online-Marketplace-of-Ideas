# import queue 

class User:
    def __init__(self, id, friends, followers=None, feed_size= 15, is_bot=False):
        #friends: list of users this one follows 
        self.id = id
        self.friends = friends # list of ids, since we only need to count 
        self.followers = followers # list of User(), since we need to spread
        self.is_bot = is_bot
        self.feedsize = feed_size #alpha
        self.feed = []
        # self.feed = queue.Queue() #FIFO
        # self.follows = []
        self.count_forgotten_memes = True
    
    def maintain_feed_size(self):
        if len(self.feed) > self.feedsize:
            self.feed = self.feed[:self.feedsize]
        #TODO: meme bookeeping
            #track forgotten meme
            # if self.count_forgotten_memes and self.is_bot == False:
            #     # count only forgotten memes with zero quality
            #     forgotten_zeros = 0
            #     for m in G.nodes[f]['feed'][alpha:]:
            #     if m[0] == 0:
            #         forgotten_zeros += 1
            #     forgotten_memes_per_degree(forgotten_zeros, G.in_degree(f))
            # del G.nodes[f]['feed'][alpha:]
        #print('follower feed after :', ["{0:.2f}".format(round(m[0], 2)) for m in G.nodes[f]['feed']]) 
        #print('Bot' if G.nodes[agent]['bot'] else 'Human', 'posted', meme, 'to', G.in_degree(agent), 'followers', flush=True) 
    
    def add_meme_to_feed(self, meme, n_copies=1):
        # newest: index 0; oldest: -1
        self.feed[0:0] = [meme] * n_copies #prepend n copies to feed
        self.maintain_feed_size()

    def add_follower(self, agent):
        self.followers += [agent] 
    
    def add_friend(self, agent):
        self.friends += [agent] 
    