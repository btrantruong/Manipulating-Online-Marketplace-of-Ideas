# Code to plot 1 line
from matplotlib import cm 

import matplotlib.pyplot as plt
import csv
import numpy as np 
import glob 
import json
import os
from matplotlib import cm 
import infosys.utils as utils 
from collections import defaultdict

# data = np.array([[1,2], [3,4]])
# figure = plt.figure(figsize=(13, 15), facecolor='w')
# ax = figure.add_subplot(3,2,2)
cmap = cm.get_cmap('inferno', 10)
# utils.draw_heatmap(ax, data, ['a','b'], ['a','b'], 'test', 'test', cmap, 'TEST', vmax=None, vmin=None)
ABS_PATH = ''
DATA_PATH = os.path.join(ABS_PATH, "data")

all_configs = json.load(open(os.path.join(DATA_PATH,'all_configs.json'),'r'))

RES_PATH = 'results/vary_thetagamma_2runs'

#2D array for plotting data 
result_dir = RES_PATH
exp_type = 'vary_thetagamma'
GAMMA = [0.0001, 0.0002, 0.0005, 0.001, 0.002, 0.005, 0.02, 0.05, 0.1, 0.2, 0.5]
TARGETING = [None, 'hubs', 'partisanship', 'conservative', 'liberal', 'misinformation']
PHI_LIN = list(range(1,11))
THETA = [1,2,4,6,8,10,12,14]

respath = glob.glob('%s/*.json' %result_dir)
resfiles = [i.split('%s/' %result_dir)[1].replace('.json','') for i in respath]

y = 'quality'
all_results = [json.load(open(os.path.join(result_dir,'%s.json' %file),'r')) for file in resfiles]

results = defaultdict(lambda: [])
for gamma in GAMMA:
    for theta in THETA: 
        results[gamma] += [np.mean(res[y]) for res in all_results if res['theta']==theta and res['gamma']==gamma]

figure = plt.figure(figsize=(13, 15), facecolor='w')
ax = figure.add_subplot(3,2,2)
data = np.array([gammarow for gammarow in results.values()])
utils.draw_heatmap(ax, data, THETA, GAMMA, '$\\theta$', '$\gamma$', cmap, 'TEST', vmax=None, vmin=None)
print('')