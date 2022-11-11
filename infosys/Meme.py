"""
Class representing a meme.
"""

import random


class Meme:
    def __init__(self, id, is_by_bot=0, phi=1):
        """
        Initialize a meme
        """
        self.id = id
        self.is_by_bot = is_by_bot
        self.phi = phi * 0.1
        quality, fitness = self.get_values()
        self.quality = quality
        self.fitness = fitness

    def get_values(self):
        """
        Assign quality and fitness values to a meme depending on bot flag & phi. 
        human_fitness is drawn from a distribution
            using https://en.wikipedia.org/wiki/Inverse_transform_sampling
        """
        u = random.random()
        exponent = 2  # b: previously human exponent = 1+phi
        human_fitness = 1 - (1 - u) ** (1 / exponent)

        if self.is_by_bot == 1:
            fitness = 1 if u < self.phi else human_fitness
        else:
            fitness = human_fitness

        if self.is_by_bot == 1:
            quality = 0
        else:
            quality = fitness

        return quality, fitness
