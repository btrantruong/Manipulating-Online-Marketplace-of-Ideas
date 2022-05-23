#!/bin/bash
#####  Constructed by HPC everywhere #####
#SBATCH --mail-user=baotruon@iu.edu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=10
#SBATCH --mem=50gb
#SBATCH --time=23:59:00
#SBATCH --mail-type=FAIL,BEGIN,END
#SBATCH --job-name=hub tracking

######  Module commands #####
source /N/u/baotruon/Carbonate/miniconda3/etc/profile.d/conda.sh
conda activate graph


######  Job commands go below this line #####
cd /N/u/baotruon/Carbonate/marketplace
echo '###### Make plots for tracking human hubs ######'
echo '###### Low infiltration ######'
python3 exps/hub_tracking_analyses.py vary_thetaphi_1runs_gamma0.005 hubs_13 none_13
echo '###### High infiltration ######'
python3 exps/hub_tracking_analyses.py vary_thetaphi_1runs hubs_13 none_13