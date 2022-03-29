import random

choices= range(100)
def make_rand_num():
    return random.choices(choices,k=5)

random.seed(100)
seq = make_rand_num()
print(seq)
print('Shuffle \n')
random.seed(100)
random.shuffle(seq)
print(seq)
random.seed(100)
seq2 = make_rand_num()
print(seq2)
print('Shuffle \n')
random.seed(100)
random.shuffle(seq2)
print(seq2)