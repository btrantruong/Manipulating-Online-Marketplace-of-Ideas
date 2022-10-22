#!/bin/bash
#####  Constructed by HPC everywhere #####
#SBATCH --mail-user=baotruon@iu.edu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=3
#SBATCH --time=3-23:59:00
#SBATCH --mail-type=FAIL,BEGIN,END
#SBATCH --job-name=baseline

######  Module commands #####
source /N/u/baotruon/Carbonate/miniconda3/etc/profile.d/conda.sh
conda activate graph


######  Job commands go below this line #####
cd /N/u/baotruon/Carbonate/marketplace
echo '###### baseline ######'
python3 workflow/scripts/driver.py -i /N/slate/baotruon/marketplace/data/igraph/vary_network/follower_network.gml -o /N/slate/baotruon/marketplace/newpipeline/results/10202022_baseline/baseline.json -v /N/slate/baotruon/marketplace/newpipeline/verbose/10202022_baseline/baseline.json.gz --config /N/slate/baotruon/marketplace/config_10222022_baseline/baseline/baseline.json --mode igraph --times 2