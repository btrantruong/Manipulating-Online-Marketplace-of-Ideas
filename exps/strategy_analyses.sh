#!/bin/bash
#####  Constructed by HPC everywhere #####
#SBATCH --mail-user=baotruon@iu.edu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=10
#SBATCH --mem=100gb
#SBATCH --time=23:59:00
#SBATCH --mail-type=FAIL,BEGIN,END
#SBATCH --job-name=plots

######  Module commands #####
source /N/u/baotruon/Carbonate/miniconda3/etc/profile.d/conda.sh
conda activate graph


######  Job commands go below this line #####
cd /N/u/baotruon/Carbonate/marketplace
echo '###### Make plots for tracking human hubs ######'
echo '###### Very low infiltration ######'
python3 exps/strategy_analyses.py vary_thetaphi_1runs_gamma0.0005 hubs_22 none_22 strategy_analyses

echo '###### Low infiltration ######'
python3 exps/strategy_analyses.py vary_thetaphi_1runs_gamma0.005 hubs_22 none_22 strategy_analyses
echo '###### High infiltration ######'
python3 exps/strategy_analyses.py vary_thetaphi_1runs hubs_22 none_22 strategy_analyses