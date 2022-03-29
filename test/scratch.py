# from base_logger import logger
import utils 
import random
from profileit import profile
import igraph
from pathlib import Path
from Meme import Meme

a = Meme(1)
attribs = a.__dict__
for attr in attribs:
    b = {attr: a.attr}
# def _convert_meme_to_json_object(self, meme):
        
@profile
def test_random():
    # logger.debug('Doing something')
    a = range(0,1000)
    b = random.choices(a, k=50)

test_random()

path = 'data/syntheticz.gml'
my_file = Path(path)
if my_file.is_file():
    net = igraph.Graph.Read_GML(path)
else:
    raise Exception('File not available')

print(net.summary())
