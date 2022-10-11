""" I/O functions and plotting """
# from base_logger import logger
import random
import numpy as np
import math
import statistics
import csv

from operator import itemgetter
import sys
import fcntl
import time
import logging
import pathlib
import io
import os
import json
import gzip
import glob

import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.axes_grid1 import make_axes_locatable

import datetime as dt
import inspect
import scipy.stats as stats
from scipy.stats import ks_2samp

# import infosys.config_values as configs
import infosys.final_configs as configs


### I/O
def write_json_compressed(fout, data):
    # write compressed json for hpc - pass file handle instead of filename so we can flush
    try:
        fout.write(json.dumps(data).encode("utf-8"))
    except Exception as e:
        print(e)


def read_json_compressed(fpath):
    data = None
    try:
        fin = gzip.open(fpath, "r")
        json_bytes = fin.read()
        json_str = json_bytes.decode("utf-8")
        data = json.loads(json_str)
    except Exception as e:
        print(e)
    return data


### EXP CONFIGS
def update_dict(adict, default_dict, fill_na=True):
    # only update the dictionary if key doesn't exist
    # use to fill out the rest of the params we're not interested in
    # Fill NaN value if it exists in another dict

    for k, v in default_dict.items():
        if k not in adict.keys():
            adict.update({k: v})
        if fill_na is True and adict[k] is None:
            adict.update({k: v})
    return adict


def netconfig2netname(config_fname, network_config):
    # Map specific args to pre-constructed network name
    # network_config is a dict of at least 3 keys: {'beta', 'gamma', 'strategy'}
    # structure: network_config = {'beta': 0.001, 'gamma':0.005, 'targeting_criterion': 'partisanship'}

    exp_configs = json.load(open(config_fname, "r"))
    EXPS = exp_configs[
        "vary_network"
    ]  # keys are name of network, format: '{betaidx}{gammaidx}{targetingidx}'

    legal_vals = ["beta", "gamma", "targeting_criterion"]
    network_config = {k: val for k, val in network_config.items() if k in legal_vals}

    BETA = configs.BETA
    GAMMA = configs.GAMMA
    TARGETING = configs.TARGETING

    network_fname = "%s%s%s" % (
        BETA.index(network_config["beta"]),
        GAMMA.index(network_config["gamma"]),
        TARGETING.index(network_config["targeting_criterion"]),
    )

    for arg_name in network_config.keys():
        assert EXPS[network_fname][arg_name] == network_config[arg_name]

    return network_fname


def expconfig2netname(config_fname, exp_type):
    ## Return a dict of {network name: infosys config}

    exp_configs = json.load(open(config_fname, "r"))
    # Get the network name from the exp config
    EXP2NET = {}

    if exp_type == "vary_betagamma":
        for exp, exp_config in exp_configs[exp_type].items():
            cf = {
                "beta": exp_config["beta"],
                "gamma": exp_config["gamma"],
                "targeting_criterion": configs.DEFAULT_STRATEGY,
            }
            EXP2NET[exp] = netconfig2netname(config_fname, cf)
        assert len(EXP2NET) == len(configs.BETA) * len(configs.GAMMA)

    elif exp_type == "vary_phigamma" or exp_type == "vary_thetagamma":
        for exp, exp_config in exp_configs[exp_type].items():
            cf = {
                "beta": configs.DEFAULT_BETA,
                "gamma": exp_config["gamma"],
                "targeting_criterion": configs.DEFAULT_STRATEGY,
            }
            EXP2NET[exp] = netconfig2netname(config_fname, cf)
        if exp_type == "vary_phigamma":
            assert len(EXP2NET) == len(configs.PHI_LIN) * len(configs.GAMMA)
        else:
            assert len(EXP2NET) == len(configs.THETA) * len(configs.GAMMA)

    elif exp_type == "vary_phibeta" or exp_type == "vary_thetabeta":
        for exp, exp_config in exp_configs[exp_type].items():
            cf = {
                "beta": exp_config["beta"],
                "gamma": configs.DEFAULT_GAMMA,
                "targeting_criterion": configs.DEFAULT_STRATEGY,
            }
            EXP2NET[exp] = netconfig2netname(config_fname, cf)
        if exp_type == "vary_phibeta":
            assert len(EXP2NET) == len(configs.PHI_LIN) * len(configs.BETA)
        else:
            assert len(EXP2NET) == len(configs.THETA) * len(configs.BETA)

    elif exp_type == "vary_thetaphi":
        for exp, exp_config in exp_configs[exp_type].items():
            cf = {
                "beta": configs.DEFAULT_BETA,
                "gamma": configs.DEFAULT_GAMMA,
                "targeting_criterion": configs.DEFAULT_STRATEGY,
            }
            EXP2NET[exp] = netconfig2netname(config_fname, cf)
        # assert len(EXP2NET) ==len(configs.THETA)*len(configs.PHI_LIN)

    elif exp_type == "convergence_rhoepsilon":
        for exp, exp_config in exp_configs[exp_type].items():
            cf = {
                "beta": configs.DEFAULT_BETA,
                "gamma": configs.DEFAULT_GAMMA,
                "targeting_criterion": configs.DEFAULT_STRATEGY,
            }
            EXP2NET[exp] = netconfig2netname(config_fname, cf)
        assert len(EXP2NET) == len(configs.RHO) * len(configs.EPSILON)

    for netname in EXP2NET.values():
        assert netname in exp_configs["vary_network"]

    return EXP2NET


def remove_illegal_kwargs(adict, amethod):
    # remove a keyword from a dict if it is not in the signature of a method
    new_dict = {}
    argspec = inspect.getargspec(amethod)
    legal = argspec.args
    for k, v in adict.items():
        if k in legal:
            new_dict[k] = v
    return new_dict


def get_now():
    # return timestamp
    return int(dt.datetime.now().timestamp())


def get_logger(name):
    # Create a custom logger
    logger = logging.getLogger(name)
    # Create handlers
    handler = logging.StreamHandler()
    # Create formatters and add it to handlers
    logger_format = logging.Formatter("%(asctime)s@%(name)s:%(levelname)s: %(message)s")
    handler.setFormatter(logger_format)
    # Add handlers to the logger
    logger.addHandler(handler)
    # Set level
    level = logging.getLevelName("INFO")
    logger.setLevel(level)
    return logger


def get_file_logger(log_dir=".log", also_print=False):
    """Create logger."""

    # Create log_dir if it doesn't exist already
    try:
        os.makedirs(f"{log_dir}")
    except:
        pass

    # Create logger and set level
    logger = logging.getLogger(__name__)
    logger.setLevel(level=logging.INFO)

    # Configure file handler
    formatter = logging.Formatter(
        fmt="%(asctime)s-%(name)s-%(levelname)s-%(message)s",
        datefmt="%Y-%m-%d_%H:%M:%S",
    )
    log_fpath = os.path.join(log_dir, f"{__name__}_{get_now()}")
    fh = logging.FileHandler(log_fpath)
    fh.setFormatter(formatter)
    fh.setLevel(level=logging.INFO)
    # Add handlers to logger
    logger.addHandler(fh)

    # If true, also print the output to the console in addition to sending it to the log file
    if also_print:
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(formatter)
        ch.setLevel(level=logging.INFO)
        logger.addHandler(ch)

    return logger


# log time profiling to file
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
            print("Cannot create dir %s in %s" % (new_dir_name, parent_path))
            return False
    return True


def make_sure_file_exists(filepath):
    file = pathlib.Path(filepath)
    if file.is_file():
        return True
    else:
        return False


def safe_open(path, mode="w"):
    """ Open "path" for writing or reading, creating any parent directories as needed.
        mode =[w, wb, r, rb]
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return open(path, mode)


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
    assert len(data_files) == len(labels)
    plt.gca().set_prop_cycle(
        plt.rcParams["axes.prop_cycle"] + plt.cycler(marker=list(".s*o^v<>+x"))
    )
    if log_flag:
        plt.xscale("log")
    plt.xlabel(xlabel, fontsize=16)
    plt.ylabel("Relative Average Quality", fontsize=16)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.ylim(bottom=0)
    for i in range(len(data_files)):
        data = {}
        with open(path + data_files[i], newline="") as f:
            reader = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
            for row in reader:
                data[row[0]] = row[1] / baseline
        plt.plot(*zip(*sorted(data.items())), label=labels[i])
    plt.legend()


# plot some quantity in a dictionary where keys are no. followers
#
def plot_quantity_vs_degree(title, ylabel, data_dict):
    plt.figure()
    plt.xlabel("Followers", fontsize=16)
    plt.ylabel(ylabel, fontsize=16)
    plt.title(title, fontsize=16)
    # plt.xscale('log')
    plt.plot(*zip(*sorted(data_dict.items())))


# plot heatmap
#
def draw_heatmap(
    ax, data, xticks, yticks, xlabel, ylabel, cmap, title, vmax=None, vmin=None
):
    data = data[::-1, :]
    if vmin == None:
        vmin = data[0][0]
        for i in data:
            for j in i:
                if j < vmin:
                    vmin = j
    if vmax == None:
        vmax = data[0][0]
        for i in data:
            for j in i:
                if j > vmax:
                    vmax = j

    map = ax.imshow(
        data, interpolation="nearest", cmap=cmap, aspect="auto", vmin=vmin, vmax=vmax
    )
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
    ax.set_xticklabels(xticks)  # , fontsize=14, rotation=40

    # cb = plt.colorbar(mappable=map, cax=ax, ax=None)
    # cb.ax.tick_params(labelsize=12)
    ax.set_xlabel(xlabel)  # , fontsize=14
    ax.set_ylabel(ylabel)  # , fontsize=14
    ax.set_title(title)
    # plt.show()
    # plt.clf()


# append to file, locking file and waiting if busy in case of multi-processing
#
def save_csv(data_array, csvfile="results.csv"):
    with open(csvfile, "a", newline="") as file:
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
    with open(filename, newline="") as file:
        reader = csv.reader(file, quoting=csv.QUOTE_NONNUMERIC)
        for row in reader:
            q_mean_random[row[0]] = row[1]
            q_stderr_random[row[0]] = row[2]
            q_mean_preferential[row[0]] = row[3]
            q_stderr_preferential[row[0]] = row[4]
            q_mean_ratio[row[0]] = row[5]
            q_stderr_ratio[row[0]] = row[6]
    return (
        q_mean_random,
        q_stderr_random,
        q_mean_preferential,
        q_stderr_preferential,
        q_mean_ratio,
        q_stderr_ratio,
    )


###----- Calculations
# calculate log with default base
#
def logbase(x, base=1.5):
    return np.log(x) / np.log(base)


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
        width = base ** (i + 1) - start
        mid = start + width / 2
        mids.append(mid)
        heights.append(distr[i] / (sum * width))
    return mids, heights


# calculate Gini coefficient of concentration of low-quality memes around hubs
# inspired by https://github.com/oliviaguest/gini
#
def gini(G):
    humans = []
    total = 0
    for agent in G.nodes:
        if G.nodes[agent]["bot"] == False:
            zeros = 0
            for m in G.nodes[agent]["feed"]:
                if m[0] == 0:
                    zeros += 1
            humans.append((G.in_degree(agent), zeros))
            total += zeros
    humans.sort(key=itemgetter(0))
    n = len(humans)
    coefficient = 0
    for i in range(n):
        coefficient += (2 * (i + 1) - n - 1) * humans[i][1]
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
    assert len(elements) == len(weights)
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
    probs = [w / total for w in probs]

    # if we have enough elements with non-zero probabilities, sample from those
    if sample_size <= len(non_zeros):
        return np.random.choice(non_zeros, p=probs, size=sample_size, replace=False)
    else:
        # if we need more, take all the elements with non-zero probability
        # plus a random sample of the elements with zero probability
        return non_zeros + random.sample(zeros, sample_size - len(non_zeros))


def ks_test(dist1, dist2, alpha=0.01, verbose=False):
    # Use Kolmogorov-Smirnov tset, return True if 2 distributions are drawn from the same distribution.
    # for coefficient - alpha map, see https://sparky.rice.edu//astr360/kstest.pdf

    c_alphas = [1.22, 1.36, 1.48, 1.63, 1.73, 1.95]
    alphas = [0.1, 0.05, 0.025, 0.01, 0.005, 0.001]

    c_alpha = c_alphas[alphas.index(alpha)]

    ks_res = ks_2samp(dist1, dist2)

    # get critical value according to sample size

    critical_val = (
        np.sqrt((len(dist1) + len(dist2)) / (len(dist1) * len(dist2))) * c_alpha
    )
    similar = ks_res.statistic < critical_val  # whether 2 distributions are similar

    if verbose is True:
        print(ks_res)
        print("Statistic is smaller than critical value") if similar is True else print(
            "Statistic is larger than critical value"
        )

        print(
            "The 2 distributions are similar: %s (At alpha %s, D=%s)"
            % (similar, alpha, np.round(critical_val, 3))
        )

    return similar
