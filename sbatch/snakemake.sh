#!/bin/bash

#!/bin/bash
#####  Constructed by HPC everywhere #####
#SBATCH --mail-user=baotruon@iu.edu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=20
#SBATCH --time=1-6:59:00
#SBATCH --mail-type=FAIL,BEGIN,END
#SBATCH --job-name=marketplacesnakemake

######  Module commands #####
source /N/u/baotruon/Carbonate/miniconda3/etc/profile.d/conda.sh
conda activate graph


######  Job commands go below this line #####
cd /N/u/baotruon/Carbonate/marketplace
echo '###### compare strategies vary thetaphi ######'
snakemake --nolock --snakefile workflow/rules/compare_strategies.smk --cores 20
echo '###### vary theta phi ######'
snakemake --nolock --snakefile workflow/rules/vary_thetaphi.smk --cores 20
echo '###### vary theta gamma ######'
snakemake --nolock --snakefile workflow/rules/vary_thetagamma.smk --cores 20
echo '###### vary phi gamma ######'
snakemake --nolock --snakefile workflow/rules/vary_phigamma.smk --cores 20
echo '###### vary beta gamma ######'
snakemake --nolock --snakefile workflow/rules/vary_betagamma.smk --cores 20
