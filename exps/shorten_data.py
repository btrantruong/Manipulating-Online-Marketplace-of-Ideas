""" New results track memes & feeds making the files too big.
    To not run into MemoryError, we split the results into the big & small files.
    Small files contain only final measurements. Big files have memes & feeds info"""

import gzip
import glob 
import json
import os
import infosys.utils as utils 

RES_PATH = '/N/slate/baotruon/marketplace/results/vary_thetaphi_1runs/long'
fpaths = glob.glob(os.path.join(RES_PATH,'long', '*.json.gz'))

for fpath in fpaths:
    fname = fpath.split('%s/' %RES_PATH)[1].replace('.json.gz','')
    data = utils.read_json_compressed(fpath)
    data_short = {k:v for k,v in data.items() if k not in ['memes', 'feeds']}
    newpath = os.path.join(RES_PATH,'%s.json' %fname)
    fout = gzip.open(newpath, 'w')
    utils.write_json_compressed(fout, data)

print('Finish separating data!')