# TODO : havent tested this script
import infosys.utils as utils
import infosys.plot_utils as plot_utils
import archive.experiments.config_values as configs


import matplotlib.pyplot as plt
import os
import glob
import json
from collections import defaultdict
import pandas as pd
import numpy as np

print(os.getcwd())
RES_DIR = "results"
folders = ["vary_targetgamma_3runs", "vary_targetgamma_3runs"]
data = json.load(open(os.path.join(RES_DIR, folders[0], "00.json"), "r"))
# params = ['rho', 'epsilon', 'quality']
dfs = []
params = list(data.keys())
exclude = ["mode", "verbose", "human_network", "diversity", "discriminative_pow"]

# only get relevant data
target_params = list(set(params) - set(exclude))
# ['phi','graph_gml', 'beta','gamma','targeting_criterion','quality','theta']

"""
Combine results of exps in the folders into a df. 
The columns are target_params and 'quality_{suffix}', 
e.g: if folder 1 has 3 runs, the columns are 'quality00', 'quality01', 'quality02'
Then get the average quality and std of these columns for plotting  
"""
for jdx, folder in enumerate(folders):

    data = defaultdict(lambda: [])
    # iterate through all exps in this folder
    for idx, fpath in enumerate(glob.glob(os.path.join(RES_DIR, folder, "*.json"))):
        exp_res = json.load(open(fpath, "r"))
        # only check the first file:
        # if file contains multiple qualities, make 'quality' col with a suffix, e.g: quality_00
        # add a column to the df.columns
        if idx == 0:
            no_runs = len(exp_res["quality"])  # quality is a list over multiple runs
            # df_cols += [f'quality{jdx}{ith_run}' for ith_run in range(no_runs)]

        for param in target_params:
            if param == "quality":
                #                 data[param] += [exp_res[param][0]]
                for ith_run in range(no_runs):
                    data[f"quality{jdx}{ith_run}"] += [exp_res["quality"][ith_run]]

            else:
                data[param] += [exp_res[param]]

    df = pd.DataFrame(data=data, columns=data.keys())
    print(df.columns)
    dfs += [df]

## Merge results across all runs,
merge_on = list(set(target_params) - set(["quality"]))
data = dfs[0]

for idx, df in enumerate(dfs[:-1]):
    df = dfs[idx + 1]
    data = pd.merge(data, df, on=merge_on)

quality_cols = [col for col in data.columns if "quality" in col]
data["quality"] = data[quality_cols].mean(axis=1)
data["quality_std"] = data[quality_cols].std(axis=1)
data["targeting_criterion"] = data["targeting_criterion"].apply(
    lambda x: x if x is not None else "none"
)

print("")

