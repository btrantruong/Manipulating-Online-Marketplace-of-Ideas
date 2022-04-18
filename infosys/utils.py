""" I/O functions and plotting """
# from base_logger import logger
import random
import numpy as np
import math
import statistics
import csv
import matplotlib.pyplot as plt
from operator import itemgetter
import sys
import fcntl
import time
import logging 
import pathlib 
import io 
import os 
import scipy.stats as stats
import glob
from matplotlib import cm 
import json 
from mpl_toolkits.axes_grid1 import make_axes_locatable
import datetime as dt 
import inspect 
import gzip 

def write_json_compressed(fout, data):
    #write compressed json for hpc - pass file handle instead of filename so we can flush
    try:
        fout.write(json.dumps(data).encode('utf-8')) 
    except Exception as e:
        print(e)


def update_dict(adict, default_dict,fill_na=True):
    #only update the dictionary if key doesn't exist
    # use to fill out the rest of the params we're not interested in
    # Fill NaN value if it exists in another dict
    for k,v in default_dict.items():
        if k not in adict.keys():
            adict.update({k:v})
        if fill_na is True and adict[k] is None:
            adict.update({k:v})
    return adict


def remove_illegal_kwargs(adict, amethod):
    #remove a keyword from a dict if it is not in the signature of a method
    new_dict = {}
    argspec = inspect.getargspec(amethod)
    legal = argspec.args
    for k,v in adict.items():
        if k in legal:
            new_dict[k] = v
    return new_dict


pprint = {'gamma':'$\gamma$','theta': '$\theta$', 'beta':'$\beta$', 'phi': '$phi$', 
        'quality': 'Relative Average Quality', 'discriminative_pow': 'Discriminative Power', 'diversity': 'Diversity'}


def plotmulti_infosys(result_dir, config_fpath=None, exp_type='vary_betagamma', anchors=[('gamma', 0.01), ('gamma', 0.02)], 
                        x='beta', y='quality', log_flag=False, relative=False):
    
    respath = glob.glob('%s/*.json' %result_dir)
    resfiles = [i.split('%s/' %result_dir)[1].replace('.json','') for i in respath]

    if config_fpath is not None:
      all_configs = json.load(open(config_fpath,'r'))
      #fill in other config
      params = {}
      for file in resfiles: 
          params[file] = all_configs[exp_type][file]
    

    for i,anchor in enumerate(anchors):
        results = {}
        for file in resfiles: 
            res = json.load(open(os.path.join(result_dir,'%s.json' %file),'r'))
            results[file] = update_dict(res, params[file])
        data = []
        for info in results.values():
            if info[anchor[0]]==anchor[1]:
                # if x in info.keys() and y in info.keys():
                if y=='discriminative_pow':
                    data += [(info[x], info[y][0])] #since discrinminative_pow is a tuple of (tau,p_val)
                else:
                    data += [(info[x], info[y])] 
#         data = [(info[x], info[y]) for info in results.values() if info[anchor[0]]==anchor[1]]
        

        avg_data = []
        y_err = []
        for xval,yval in data:
            if relative is True:
                baseline = 0.5
                avg_data += [(xval, np.mean(yval)/baseline)]
            else:
                avg_data += [(xval, np.mean(yval))]
            y_err += [np.std(yval)]

        colormap = cm.get_cmap('inferno', 10)
        colors = [colormap(i) for i in range(10)]
        plt.gca().set_prop_cycle(plt.rcParams["axes.prop_cycle"] + plt.cycler(marker=list('.s*o^v<>+x')))
        if log_flag: plt.xscale('log')
        # plt.errorbar(*zip(*sorted(avg_data)), yerr=y_err, fmt='v', color=colors(i),
        #          ecolor='lightgray', elinewidth=3, capsize=0, label=anchor[1])
        # plt.errorbar(*zip(*sorted(avg_data)), yerr=y_err, elinewidth=3, capsize=0, label=anchor[1] if anchor[1] is not None else 'None')
        plt.plot(*zip(*sorted(avg_data)),label=anchor[1] if anchor[1] is not None else 'None')
                 
    plt.xlabel(pprint[x], fontsize=16)
    plt.ylabel(pprint[y], fontsize=16)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.ylim(bottom=0)
    plt.legend()
    plt.savefig(os.path.join(result_dir, '%s%s.png' %(x,y)), dpi=300)
    # plt.show()
    plt.clf()


# def heatmap_infosys(result_dir, exp_type='vary_thetagamma', data, xticks, yticks, '$\\theta$', '$\gamma$', cmap, 'TEST', vmax=None, vmin=None)

def get_now():
    #return timestamp
    return int(dt.datetime.now().timestamp())
    
def get_logger(name):
    # Create a custom logger
    logger = logging.getLogger(name)
    # Create handlers
    handler = logging.StreamHandler()
    # Create formatters and add it to handlers
    logger_format = logging.Formatter(
        "%(asctime)s@%(name)s:%(levelname)s: %(message)s")
    handler.setFormatter(logger_format)
    # Add handlers to the logger
    logger.addHandler(handler)
    # Set level
    level = logging.getLevelName("INFO")
    logger.setLevel(level)
    return logger

#log time profiling to file 
# def get_logger_tofile():
#     logger = logging
#     # logger = logging.getLogger(name)
#     # Create file handlers
#     make_sure_dir_exists('', 'logfiles')
#     # Create formatters and add it to handlers
#     # logging.root.handlers[0].setFormatter(CsvFormatter())
#     handler = logging.FileHandler('timing.csv')
#     handler.setFormatter(CsvFormatter())
#     logger.addHandler(handler)
#     logger.setLevel(logging.DEBUG)
#     return logger

def make_sure_dir_exists(parent_path, new_dir_name):
    try:
        new_dir = pathlib.Path(parent_path, new_dir_name)
    except FileExistsError:
        return True
    else:
        try:
            new_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            print('Cannot create dir %s in %s' %(new_dir_name, parent_path))
            return False
    return True

def make_sure_file_exists(filepath):
  file = pathlib.Path(filepath)
  if file.is_file():
    return True
  else: 
    return False

# def profile(func):
#     def wrapper(*args, **kwargs):
#         start = time.time()
#         val = func(*args, **kwargs)
#         end = time.time()
#         logger.debug('Do something')
#         # logger.debug('%s, %s' %(func.__name__, (end-start)))
#         # logging.debug('%s, %s' %(func.__name__, (end-start)))
#         # logging.info('Finish %s in %s' %(func.__name__, (end-start)))
#         return val
#     return wrapper

"""
plot average quality (relative to baseline) vs given parameters, 
     for different values of other params (one per data file)
each filename is a csv with two columns, the first is the param and the second is average quality
each label is a string, eg r'$\gamma$=0.001'
xlabel is a string, eg r'$\theta$'
"""
def plot_avg_quality(data_files, labels, xlabel, log_flag=False, baseline=0.5, path=""):
    assert(len(data_files) == len(labels))
    plt.gca().set_prop_cycle(plt.rcParams["axes.prop_cycle"] + plt.cycler(marker=list('.s*o^v<>+x')))
    if log_flag: plt.xscale('log')
    plt.xlabel(xlabel, fontsize=16)
    plt.ylabel('Relative Average Quality', fontsize=16)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.ylim(bottom=0)
    for i in range(len(data_files)):
        data = {}
        with open(path+data_files[i], newline='') as f:
            reader = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
            for row in reader:
                data[row[0]] = row[1] / baseline
        plt.plot(*zip(*sorted(data.items())), label=labels[i])
    plt.legend()


# plot some quantity in a dictionary where keys are no. followers 
#
def plot_quantity_vs_degree(title, ylabel, data_dict):
  plt.figure()
  plt.xlabel('Followers', fontsize=16)
  plt.ylabel(ylabel, fontsize=16)
  plt.title(title, fontsize=16)
  #plt.xscale('log')
  plt.plot(*zip(*sorted(data_dict.items())))


# plot heatmap
#
def draw_heatmap(ax, data, xticks, yticks, xlabel, ylabel, cmap, title, vmax=None, vmin=None):
    data = data[::-1, :]
    if vmin == None:
        vmin = data[0][0]
        for i in data:
            for j in i:
                if j<vmin:
                    vmin=j
    if vmax == None:
        vmax = data[0][0]
        for i in data:
            for j in i:
                if j>vmax:
                    vmax=j

    map = ax.imshow(data, interpolation='nearest', cmap=cmap, aspect='auto', vmin=vmin, vmax=vmax)
    # create an axes on the right side of ax. The width of cax will be 5%
    # of ax and the padding between cax and ax will be fixed at 0.05 inch.
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cb = plt.colorbar(mappable=map, cax=cax, ax=None)
    # ax.colorbar(map, cax=None, ax=ax)

    yticks = yticks[::-1]
    ax.set_yticks(range(len(yticks)))
    ax.set_yticklabels(yticks)
    ax.set_xticks(range(len(xticks)))
    ax.set_xticklabels(xticks) #, fontsize=14, rotation=40
   
    # cb = plt.colorbar(mappable=map, cax=ax, ax=None)
    # cb.ax.tick_params(labelsize=12)
    ax.set_xlabel(xlabel) #, fontsize=14
    ax.set_ylabel(ylabel)#, fontsize=14
    ax.set_title(title)
    # plt.show()
    # plt.clf()

# append to file, locking file and waiting if busy in case of multi-processing
#
def save_csv(data_array, csvfile='results.csv'): 
  with open(csvfile, 'a', newline='') as file:
    while True:
      try:
        fcntl.flock(file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        writer = csv.writer(file)
        writer.writerow(data_array)
        fcntl.flock(file, fcntl.LOCK_UN)
        break
      except:
        time.sleep(0.1)


# read from file
#
def read_csv(filename):
  q_mean_random = {} 
  q_stderr_random = {} 
  q_mean_preferential = {} 
  q_stderr_preferential = {} 
  q_mean_ratio = {} 
  q_stderr_ratio = {} 
  with open(filename, newline='') as file:
    reader = csv.reader(file, quoting=csv.QUOTE_NONNUMERIC)
    for row in reader:
      q_mean_random[row[0]] = row[1]
      q_stderr_random[row[0]] = row[2]
      q_mean_preferential[row[0]] = row[3]
      q_stderr_preferential[row[0]] = row[4]
      q_mean_ratio[row[0]] = row[5]
      q_stderr_ratio[row[0]] = row[6]
  return(q_mean_random, q_stderr_random, 
         q_mean_preferential, q_stderr_preferential, 
         q_mean_ratio, q_stderr_ratio)
         

###----- Calculations
# calculate log with default base
#
def logbase(x, base=1.5):
    return np.log(x)/np.log(base)


# log-bin given histogram
#
def get_distr(count):
    distr = {}
    sum = 0
    for a in count:
        sum += count[a]
        bin = int(logbase(a))
        if bin in distr:
            distr[bin] += count[a]
        else:
            distr[bin] = count[a]
    return distr, sum


# histogram
# 
def get_count(list):
    count = {}
    for q in list:
        if q in count:
            count[q] += 1
        else:
            count[q] = 1
    return count

# log-binned distribution given log-binned histogram with default base
#
def getbins(distr, sum, base=1.5):
    mids = []
    heights = []
    bin = sorted(distr.keys())
    for i in bin:
        start = base ** i
        width = base ** (i+1) - start
        mid = start + width/2
        mids.append(mid)
        heights.append(distr[i]/(sum * width))
    return mids, heights

# calculate Gini coefficient of concentration of low-quality memes around hubs
# inspired by https://github.com/oliviaguest/gini
#
def gini(G):
  humans = []
  total = 0
  for agent in G.nodes:
    if G.nodes[agent]['bot'] == False:
      zeros = 0
      for m in G.nodes[agent]['feed']:
        if m[0] == 0: 
          zeros += 1 
      humans.append((G.in_degree(agent), zeros))
      total += zeros
  humans.sort(key=itemgetter(0))
  n = len(humans)
  coefficient = 0
  for i in range(n):
    coefficient += (2*(i+1) - n - 1) * humans[i][1]
  return coefficient / (n * total)


def kendall_tau(ranking1, ranking2):
  # ranking1: list of ranking for n elements in criteria1
  # ranking2: list of ranking for n elements in criteria2
  # such that ranking1[i] and ranking2[i] is the ranking of element i in 2 different criteria
  tau, p_value = stats.kendalltau(ranking1, ranking2)
  return tau, p_value 


def entropy(x):
  # x: list of proportion
  entropy = np.sum(x * np.log(x))
  return entropy

  
# sample a bunch of objects from a list without replacement 
# and with given weights (to be used as probabilities), which can be zero
# NB: cannot use random_choices, which samples with replacement
#     nor numpy.random.choice, which can only use non-zero probabilities
#
def sample_with_prob_without_replacement(elements, sample_size, weights): 
  
  # first remove the elements with zero prob, normalize rest
  assert(len(elements) == len(weights))
  total = 0
  non_zeros = []
  probs = []
  zeros = []
  for i in range(len(elements)):
    if weights[i] > 0:
      non_zeros.append(elements[i])
      probs.append(weights[i])
      total += weights[i]
    else: 
      zeros.append(elements[i])
  probs = [w/total for w in probs]

  # if we have enough elements with non-zero probabilities, sample from those
  if sample_size <= len(non_zeros):
    return np.random.choice(non_zeros, p=probs, size=sample_size, replace=False)
  else:
    # if we need more, take all the elements with non-zero probability
    # plus a random sample of the elements with zero probability
    return non_zeros + random.sample(zeros, sample_size - len(non_zeros))