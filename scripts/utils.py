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
    yticks = yticks[::-1]
    ax.set_yticks(range(len(yticks)))
    ax.set_yticklabels(yticks, fontsize=14)
    ax.set_xticks(range(len(xticks)))
    ax.set_xticklabels(xticks, fontsize=14) #, rotation=40
    cb = plt.colorbar(mappable=map, cax=None, ax=None)
    cb.ax.tick_params(labelsize=12)
    plt.xlabel(xlabel, fontsize=14)
    plt.ylabel(ylabel, fontsize=14)
    plt.title(title)

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