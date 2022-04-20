""" New results track memes & feeds making the files too big.
    To not run into MemoryError, we split the results into the big & small files.
    Small files contain only final measurements. Big files have memes & feeds info"""

import gzip
import glob 
import json
import os
import infosys.utils as utils 

RES_PATH = '/N/slate/baotruon/marketplace/results/vary_thetaphi_1runs'
fpaths = glob.glob(os.path.join(RES_PATH,'long', '*.json.gz'))

print('Separating %s files..' %len(fpaths))
exists = 0
for fpath in fpaths:
    fname = fpath.split('%s/long/' %RES_PATH)[1].replace('.json.gz','')
    newpath = os.path.join(RES_PATH,'%s.json' %fname)
    if utils.make_sure_file_exists(newpath):
        exists+=1
        continue
    else:
        data = utils.read_json_compressed(fpath)
        data_short = {k:v for k,v in data.items() if k not in ['memes', 'feeds']}
        fout = gzip.open(newpath, 'w')
        utils.write_json_compressed(fout, data)
print('%s files exists' %exists)
print('Finish separating data!')