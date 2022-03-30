#!/bin/bash

#!/bin/bash
#####  Constructed by HPC everywhere #####
#SBATCH --mail-user=baotruon@iu.edu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=15
#SBATCH --time=1-6:59:00
#SBATCH --mail-type=FAIL,BEGIN,END
#SBATCH --job-name=snakemake

######  Module commands #####
source /N/u/baotruon/Carbonate/miniconda3/etc/profile.d/conda.sh
conda activate graph


######  Job commands go below this line #####
cd /N/u/baotruon/Carbonate/marketplace
echo '###### vary beta gamma ######'
snakemake --snakefile workflow/vary_betagamma.smk --cores 15
echo '###### vary phi gamma ######'
snakemake --snakefile workflow/vary_phigamma.smk --cores 15
echo '###### vary target gamma ######'
snakemake --snakefile workflow/vary_targetgamma.smk --cores 15