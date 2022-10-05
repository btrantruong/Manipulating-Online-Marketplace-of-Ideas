#!/bin/bash
#####  Constructed by HPC everywhere #####
#SBATCH --mail-user=baotruon@iu.edu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=50gb
#SBATCH --time=3-23:59:00
#SBATCH --mail-type=FAIL,BEGIN,END
#SBATCH --job-name=shufflenet

######  Module commands #####
source /N/u/baotruon/Carbonate/miniconda3/etc/profile.d/conda.sh
conda activate graph


######  Job commands go below this line #####
cd /N/u/baotruon/Carbonate/marketplace
echo '###### shuffle network ######'
python3 workflow/scripts/shuffle_net.py -i /N/slate/baotruon/marketplace/data/follower_network.gml -o /N/slate/baotruon/marketplace/data/igraph/shuffle/network_community.gml --mode community --iter 3

python3 workflow/scripts/shuffle_net.py -i /N/slate/baotruon/marketplace/data/follower_network.gml -o /N/slate/baotruon/marketplace/data/igraph/shuffle/network_hub.gml --mode hub --iter 3