#!/bin/bash
#####  Constructed by HPC everywhere #####
#SBATCH --mail-user=baotruon@iu.edu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=10gb
#SBATCH --time=23:59:00
#SBATCH --mail-type=FAIL,BEGIN,END
#SBATCH --job-name=clusterqual

######  Module commands #####
source /N/u/baotruon/Carbonate/miniconda3/etc/profile.d/conda.sh
conda activate graph


######  Job commands go below this line #####
cd /N/u/baotruon/Carbonate/marketplace
echo '###### Calculate quality of cluster ######'
python3 workflow/09222022_cluster_quality.py