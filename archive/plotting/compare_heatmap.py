from matplotlib import cm

import matplotlib.pyplot as plt
import numpy as np
import glob
import json
import os
import sys
from matplotlib import cm
import infosys.utils as utils
from collections import defaultdict
from archive.experiments.config_values import ABS_PATH, THETA, GAMMA, PHI_LIN, BETA
import plotting.plots as infosysplot

# ABS_PATH = '/N/slate/baotruon/marketplace'
ABS_PATH = ""
DATA_PATH = os.path.join(ABS_PATH, "data")
RES_PATH = os.path.join(ABS_PATH, "newpipeline")
folders = ["compare_strategies_2runs"]
exp = "vary_thetaphi"


def plot_compare(
    exp_name, folders, strategies=["None", "hubs"], measure="quality", plot_fpath=None
):
    # plot heatmap for 2 strategies side by side
    params = {
        "axes.labelsize": 10,
        "axes.titlesize": 10,
        "legend.fontsize": 10,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
    }

    plt.rcParams.update(params)
    figure, axs = plt.subplots(1, 2, figsize=(10, 5), facecolor="w")

    for ax, strategy in zip(axs, strategies):
        infosysplot.plot_heatmap(
            ax,
            exp_name,
            RES_PATH,
            folders,
            exp_prefix=strategy,
            title="%s strategy" % strategy,
            cell_type=measure,
            cbar_max=0.5,
            cbar_min=0,
        )
    # infosysplot.plot_heatmap(ax2, exp_name, RES_PATH, folders, title='Hubs strategy', cell_type=measure)
    figure.tight_layout()

    if plot_fpath is not None:
        plt.savefig(os.path.join(plot_fpath), dpi=200)
    else:
        figure.show()
    return


plot_compare(exp, folders, measure="quality", plot_fpath=None)
plt.show()
