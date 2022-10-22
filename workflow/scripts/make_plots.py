import infosys.utils as utils
import infosys.plot_utils as plot_utils
import infosys.config_values as configs


import matplotlib.pyplot as plt
import os
import glob
import json
from collections import defaultdict
import pandas as pd
import numpy as np


## Pretty print greek alphabets & measurement for plots
pprint = {
    "gamma": "$\\gamma$",
    "theta": "$\\theta$",
    "beta": "$\\beta$",
    "phi": "$\phi$",
    "mu": "$\mu$",
    "quality": "Average Quality",
    "discriminative_pow": "Discriminative Power",
    "diversity": "Diversity",
}

# note that discriminative_pow and diversity can also be plotted
# here we're interested in quality
TARGET_PARAMS = [
    "theta",
    "beta",
    "gamma",
    "mu",
    "epsilon",
    "phi",
    "rho",
    "graph_gml",
    "targeting_criterion",
    "quality"
]


def read_data(res_dir, folders):
    """
    Read results of multiple runs into 1 df. 
    Result is a .json file containing target_params as specified below. 
    'quality' is stored in a list. If there are multiple runs, df contains cols: 'quality_0', 'quality_1', etc.
    
    Params: 
        - folders (list of str): result folders
        - res_dir (str): directory containing result folders 

    Outputs:
        - dfs (list of dataframes): each dataframe is the results from a call to driver.py
    """

    dfs = []

    for idx, folder in enumerate(folders):
        num_runs = 0
        data = defaultdict(lambda: [])
        for fpath in glob.glob(os.path.join(res_dir, folder, "*.json")):
            exp_res = json.load(open(fpath, "r"))

            # In case error in exp and quality is empty
            if len(exp_res["quality"]) == 0:
                continue
            for param in TARGET_PARAMS:
                # if there are multiple qualities, make 'quality' col with a suffix, e.g: quality_00
                if param == "quality":
                    for jdx, qual in enumerate(exp_res["quality"]):
                        data[f"quality_{jdx}"] += [qual]
                        if jdx + 1 > num_runs:
                            num_runs = jdx + 1
                    # make sure all quality cols have same length:
                    # e.g: if num_runs =2 and exp_res only has quality_0, append nan to quality_1
                    if len(exp_res["quality"]) < num_runs:
                        recorded_qual_idx = num_runs - len(exp_res["quality"])
                        for kdx in range(recorded_qual_idx, num_runs):
                            data[f"quality_{kdx}"] += [np.nan]
                else:
                    data[param] += [exp_res[param]]

        df = pd.DataFrame(data=data, columns=data.keys())
        # Make sure the name of no targeting strategy is corrected formatted
        df["targeting_criterion"] = df["targeting_criterion"].apply(
            lambda x: "none" if x is None else x
        )

        dfs += [df]
    return dfs


## Match each row with the baseline quality (no strategy) of the same config
def match_row(df, row):
    # getting results of none strategy with matching config to this row
    config_params = ["theta", "mu", "gamma", "epsilon", "phi", "rho", "beta"]

    query = f'targeting_criterion=="none"'
    for param in config_params:
        query += (
            f" & {param}=={row[param]}"
            if type(row[param]) != str
            else f' & {param}=="{row[param]}"'
        )

    matched = df.query(query)
    if len(matched) > 0:
        return matched
    else:
        return None


## GET QUALITY RELATIVE TO NONE QUALITY
def get_relative_qual(data):
    quality_cols = [col for col in data.columns if "quality_" in col]

    for idx, row in data.iterrows():
        # Match the result of each strategy to its no-strategy counterpart
        none = match_row(data, row)
        if none is not None:
            none = none.iloc[0]
            none_quals = none[quality_cols].values
            strag_quals = row[quality_cols].values

            # lengths can mismatch (likely because exps haven't finished), handle them
            strag_quals = [i for i in strag_quals if np.isnan(i) == False]
            none_quals = [i for i in none_quals if np.isnan(i) == False]
            length = min(len(none_quals), len(strag_quals))
            ratios = np.divide(strag_quals[:length], none_quals[:length])

            data.at[idx, "ratio_quality"] = np.mean(ratios)
            data.at[idx, "ratio_std"] = np.std(ratios)
        else:
            data.at[idx, "ratio_quality"] = np.nan
            data.at[idx, "ratio_std"] = np.nan
    return data


# Get absolute quality for plotting
def get_strategy_data(df, line_name="hubs", x_axis="beta", y_axis="quality"):
    qual_cols = [col for col in df.columns if "quality" in col]
    df["mean_quality"] = df.loc[:, qual_cols].mean(axis=1)
    df["std_quality"] = df.loc[:, qual_cols].std(axis=1)

    if line_name not in df["targeting_criterion"].unique():
        raise ValueError("targeting criterion not valid. Specify again")

    strag_data = df[df["targeting_criterion"] == line_name]

    x = strag_data[x_axis].values
    y = strag_data["mean_quality"].values
    err = strag_data["std_quality"].values
    plot_data = zip(*sorted(zip(x, y, err), key=lambda x: x[0]))

    return plot_data


# Get quality ratio (relative to No strategy) for plotting
def get_strategy_ratio(df, line_name="hub", x_axis="beta", y_axis="quality"):
    strag_data = df[df["targeting_criterion"] == line_name]
    x = strag_data[x_axis].values
    y = strag_data["ratio_quality"].values
    err = strag_data["ratio_std"].values
    plot_data = zip(*sorted(zip(x, y, err), key=lambda x: x[0]))
    return plot_data


def draw_lines(ax, data, line_name="hub", marker="."):

    # Input: data=(x,y, err)
    # line_name=['hub', 'none']

    x, y, y_err = data
    ax.plot(x, y, label=line_name, marker=marker)
    ax.fill_between(
        x,
        np.subtract(np.array(y), np.array(y_err)),
        np.add(np.array(y), np.array(y_err)),
        alpha=0.3,
    )

    return


def plot_single_strategy(
    data,
    strategy="none",
    x_axis="beta",
    y_axis="quality",
    marker=".",
    logx=False,
    logy=False,
    fpath=None,
):
    """
    Inputs: 
        - data: df of raw results
    Outputs:
        - save file to fpath or show figure 
    """

    fig, ax = plt.subplots(figsize=(6, 4))

    plot_data = get_strategy_data(
        data, line_name=strategy, x_axis=x_axis, y_axis=y_axis
    )
    draw_lines(ax, plot_data, line_name=strategy, marker=marker)

    if logx:
        plt.xscale("log")
    if logy:
        plt.yscale("log")

    plt.xlabel(pprint[x_axis])
    plt.ylabel(pprint[y_axis])

    plt.tight_layout()
    if fpath is not None:
        plt.savefig(f"{fpath}.pdf")
        plt.savefig(f"{fpath}.png")
    else:
        plt.show()


def plot_multiple_strategies(
    data, x_axis="beta", y_axis="quality", logx=False, logy=False, fpath=None
):
    """
    Plot (and save if fpath not None) the ratio of 
    Inputs: 
        - data: df of raw results
    Outputs:
        - save file to fpath or show figure 
    """

    data = get_relative_qual(data)

    # get available strategies
    available_strategies = list(
        set(data["targeting_criterion"].unique()) - set(["none"])
    )

    plt.gca().set_prop_cycle(
        plt.rcParams["axes.prop_cycle"] + plt.cycler(marker=list(".s*o^v<>+x"))
    )
    markers = list(".s*o^v<>+x")
    fig, ax = plt.subplots(figsize=(6, 4))
    for idx, strategy in enumerate(available_strategies):
        try:
            plot_data = get_strategy_ratio(
                data, line_name=strategy, x_axis=x_axis, y_axis=y_axis
            )
            draw_lines(ax, plot_data, line_name=strategy, marker=markers[idx])
        except:
            continue

    plt.legend(
        bbox_to_anchor=(0, 0.95, 1, 0.2),
        loc="lower left",
        mode="expand",
        ncol=3,
        fancybox=True,
        shadow=True,
    )

    if logx:
        plt.xscale("log")
    if logy:
        plt.yscale("log")
    plt.xlabel(pprint[x_axis])
    plt.ylabel(f"{pprint[y_axis]} Ratio")

    plt.tight_layout()
    if fpath is not None:
        plt.savefig(f"{fpath}.pdf")
        plt.savefig(f"{fpath}.png")
    else:
        plt.show()

def single_variable_plots(res_dir, folders, figure_dir="", variable='gamma', save_fig=False):
    """
    Make 2 plots (in both .png and .pdf)
        - plot of none strategy
        - plot comparing strategies by ratio
    """

    dfs = read_data(res_dir, folders)
    data = dfs[0]
    for df in dfs[1:]:
        data = pd.merge(data, df, on=list(set(TARGET_PARAMS) - set(["quality"])), how="outer")
        print(data.shape)


    if save_fig is True:
        if not os.path.exists(figure_dir):
            os.makedirs(figure_dir)
        single_strategy_path = os.path.join(figure_dir, f"varying_{variable}")
        multi_strategy_path = os.path.join(figure_dir, f"strategies_{variable}")
    else:
        single_strategy_path=None
        multi_strategy_path=None
        
    plot_single_strategy(
    data,
    strategy="none",
    x_axis=variable,
    y_axis="quality",
    marker=".",
    logx=False,
    logy=False,
    fpath=single_strategy_path,
)
    
    plot_multiple_strategies(
    data, x_axis=variable, y_axis="quality", logx=False, logy=False, fpath=multi_strategy_path
)

if __name__ == "__main__":
    ## PLOTTING GAMMA
    res_dir = "/N/slate/baotruon/marketplace/newpipeline/results"
    folders = [
        "09292022_strategies_vary_gamma_2runs",
        "10102022_strategies_vary_gamma_3runs",
    ]

    

