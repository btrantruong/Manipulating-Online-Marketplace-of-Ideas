import numpy as np 
import os 
import json 
from utils import *

# ABS_PATH = "/N/u/baotruon/Carbonate/marketplace/igraphvsnx"
ABS_PATH = ''
DATA_PATH = os.path.join(ABS_PATH, "data")
mode = 'igraph'

#Beta and gamma are only used in making the info system
BETA = list(np.round(i,2) for i in np.linspace(0,1,11))
GAMMA = list(np.round(i,2) for i in np.linspace(0,1,11))
default = {'verbose':False, 'targeting_criterion':None}
for idx, b in enumerate(BETA):
    for jdx,g in enumerate(GAMMA):
        config = {'beta': b, 'gamma':g}
        config.update(default)
        if make_sure_dir_exists(DATA_PATH, 'configs'):
            fp = os.path.join(DATA_PATH, 'configs','betagamma_config_%s%s.json' %(idx,jdx))
            json.dump(config,open(fp,'w'))
