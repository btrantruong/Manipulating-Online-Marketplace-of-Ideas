
import random

class Meme:
    def __init__(self, id, is_by_bot=0, phi=1):
        self.id = id
        self.is_by_bot = is_by_bot
        self.phi = phi
        quality, fitness  = self.get_values()
        self.quality = quality
        self.fitness = fitness
    
    # return (quality, fitness, id) meme tuple depending on bot flag
    # using https://en.wikipedia.org/wiki/Inverse_transform_sampling
    # default phi = 1 is bot deception; >= 1: meme fitness higher than quality 
    # id: unique IDs
    def get_values(self):
        if self.is_by_bot==1:
            exponent = 1 + (1 / self.phi)
        else:
            exponent = 1 + self.phi
            
        u = random.random()
        fitness = 1 - (1 - u)**(1 / exponent)

        if self.is_by_bot==1:
            quality = 0
        else:
            quality = fitness
        
        return quality, fitness