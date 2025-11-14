# Cumulative Voting in Participatory Budgeting: Analysis and Evaluation of Selection Methods

This repository contains the implementation and analysis scripts used in the master's thesis *"Cumulative Voting in Participatory Budgeting: Analysis and Evaluation of Selection Methods"*.  
It provides tools to reproduce the experimental results, generate plots, and evaluate fairness and satisfaction metrics for various voting rules implemented in the [pabutools](https://github.com/COMSOC-Community/pabutools/) library.
Additionally a snapshot of data from [pabulib](https://pabulib.org/) and results of analysis of that data is also stored here.

## Repository structure
- `instances_all/` - copy of all used election from pabulib
- `election_results/{rule}` - sets of chosen projects based on a chosen rule
- `plots_box` - box plots and result lists analysis runs
- `plots_violin` - violin plots of analysis runs
- `src/` - source code
    - `analisis.py` - metric functions
    - `calculate_elections_all.py` - script for calculating CSTV and greedy results of elections
    - `utils.py` - helper funtions for data loading and formatting
    - `visualization.py` - script for evaluating results and generating graphs

## Installation

This project uses Python 3.13.7.

Clone repository with

```bash
git clone https://github.com/Kapiszon2343/praca_magisterska
```

Install dependenies:
```bash
pip install -r requirements.txt
```

## Usage

This projects uses two scripts to produce results.

Running the following script will calculate results of all election rules on all instances from ./instances_all and write them to ./election_results.
Results already existing in ./election_results will be ignored, so instances can be recalculated selectively by removing results to recalculate
```bash
python ./calculate_elections_all.py
```

To analyse results second script is needed. It will read result from ./election_results and output analysis results into ./plots_box and ./plots_violin
```bash
python ./visualization.py
```

## Citation

If you use this repository or parts of it in your research, please cite:

> Kacper Harasimowicz, *Cumulative Voting in Participatory Budgeting: Analysis and Evaluation of Selection Methods*, Master's Thesis, University of Warsaw, 2025.

## License
This project is released under the MIT License. See `LICENSE.md` for details.
