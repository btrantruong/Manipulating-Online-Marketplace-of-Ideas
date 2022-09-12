# Manipulating the Online Marketplace of Ideas

This repository contains code to reproduce the results in the paper [*Manipulating the Online Marketplace of Ideas*](https://arxiv.org/abs/1907.06130) by Xiaodan Lou, Alessandro Flammini, and [Filippo Menczer](https://cnets.indiana.edu/fil/).

## Environment

Our code is based on **Python3.6+**, with **jupyter notebook**.

## Notes

The results in the paper are based on averages across multiple simulation runs. To reproduce those results, we suggest running the simulations in parallel, for example on a cluster, since they will need a lot of memory and CPU time.

## Notes on revised code:
Activate virtualenv and run `pip install -e .` for the module imports to work correctly.

Run minimal example with `workflow/example/run_simulation.py`

How to multiple experiments:
- run `workflow/scripts/make_finalconfig.py` (this creates config files for different sets of param combination you want to test)
- run `workflow/final_rules/<exp_type>.smk` (exp_type: [strategies_beta, vary_thetabeta, etc.])