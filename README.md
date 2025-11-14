# Cumulative Voting in Participatory Budgeting: Analysis and Evaluation of Selection Methods

This repository contains the implementation and analysis scripts used in the master's thesis *"Cumulative Voting in Participatory Budgeting: Analysis and Evaluation of Selection Methods"*.  
It provides tools to reproduce the experimental results, generate plots, and evaluate fairness and satisfaction metrics for various voting rules implemented in the [pabutools](https://github.com/COMSOC-Community/pabutools/) library.
Additionally a snapshot of data from [pabulib](https://pabulib.org/) and results of analysis of that data is also stored here.

## Repository structure
- `./instances_all` - Copy of all elections used from Pabulib
- `./election_results/{rule}` - Sets of chosen projects based on a chosen rule
- `./plots_box` - Box plots and result lists analysis runs
- `./plots_violin` - Violin plots of analysis runs
- `./src` - Source code
    - `analisis.py` - Metric functions
    - `calculate_elections_all.py` - Script for calculating CSTV and greedy results of elections
    - `utils.py` - Helper functions for data loading and formatting
    - `visualization.py` - Script for evaluating results and generating graphs

## Installation

This project uses Python 3.13.7.

Clone repository with

```bash
git clone https://github.com/Kapiszon2343/praca_magisterska
```

Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

This repository provides two main scripts: one for calculating election results and one for analyzing them and generating plots.

### 1. Calculate election results

This script calculates results of all voting rules on all instances in `./instances_all` and writes them to `./election_results`.  

Existing results are **not overwritten**; to recalculate specific instances, delete the corresponding files in `./election_results` first or set `force_recalculate = True` in `calculate_elections_all.py`.

Run the script:

```bash
python ./calculate_elections_all.py
```

Optional: to calculate a subset of instances, you can modify the instances_all list inside the script or pass a filtered list as input.

### 2. Analyze results and generate plots

This script reads results from `./election_results` and produces visualizations and summary outputs:

- Box plots: `./plots_box`
- Violin plots: `./plots_violin`

Run the script:

```bash
python ./visualization.py
```

Optional: you can modify the script to select specific rules or subsets of results for plotting.

## Citation

If you use this repository or parts of it in your research, please cite:

> Kacper Harasimowicz, *Cumulative Voting in Participatory Budgeting: Analysis and Evaluation of Selection Methods*, Master's Thesis, University of Warsaw, 2025. 

## License
This project is released under the MIT License. See `LICENSE.md` for details.
