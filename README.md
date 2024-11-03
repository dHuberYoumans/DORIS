# DORIS

**Work in progress**

This project is about finding orbit correcting manoeuvres in satellites of the DORIS cluster.
At its heart, these manoeuvres can be seen as outliers or anomalies of the periodic patterns underlying the observational data and as such, once stripped of all physical meaning, one can simplify the problem to an anomaly detection algorithm of tabulated time series data.


The data is freely available from the CDDIS DORIS data center.

Python scripts are provided to download data for various satellites, time frames, and analysis centers, as well as to download the schedule of maneuvers. The actual detection algorithm is being developed in a Jupyter notebook. This notebook guides the reader through the author's thought process and decision-making. As this is a work in progress, ideas, comments, and suggestions are welcome and appreciated.

##### Table of Contents
- [Getting Around](#getting-around)
- [Getting Started](#getting-started)

## Getting Around

This repository is organised as showing by the following tree structure

```
── README.md
├── literature
│   ├── Data-Structure-Formats.pdf
│   ├── M002-Cartesian_State_Vectors_to_Keplerian_Orbit_Elements.pdf
│   ├── SP3_format.pdf
│   ├── SP3c_format.pdf
│   └── perturbation_celestial_mechanics.pdf
├── notebooks
│   └── finding_DORIS.ipynb
├── ref
│   └── manoeuvres_schedule.csv
├── requirements.yml
├── sat
│   └── s6assa2024
│       ├── s6assa_20_24.csv
│       └── s6assa_20_24.csv.zip
├── scripts
│   ├── download_DORIS_data.py
│   └── download_maneuver_schedule.py
└── src
    ├── ana_utils.py
    ├── df_utils.py
    ├── dl_utils.py
    ├── kepler_utils.py
    ├── misc_utils.py
    └── preprocessing_utils.py
```

### literature 

The folder `literature` contains several references used in this project.
For example, it contains information about the IDS data structure format [Data-Structure-Format](https://github.com/dHuberYoumans/DORIS/blob/main/literature/Data-Structure-Formats.pdf), which is used when downloading the observational data files.
It also contains a [paper](https://github.com/dHuberYoumans/DORIS/blob/main/literature/perturbation_celestial_mechanics.pdf) by J. A. Burns explaining the elementary derivation of perturbative celestial motions. 
The results of these paper are used for physics inspired feature engineering later on.

### notebooks

This folder contains a notebook Jupyter notebook explaining step by step the thought process behind the development of the algorithm. Simple functions, models and tests are implemented and compared and their various advantages and disadvantages are discussed on the go.

### ref

This folder contains a reference file (.csv) of the actual scheduled manoeuvres.
It is the output of the following script `download_maneuver_schedule.py` which scrapes [https://ids-doris.org/analysis-documents.html](https://ids-doris.org/analysis-documents.html) for the information about the scheduled manoeuvres.
The reference file is later used in the evaluation the models.

### requirements.yml

This .yml file contains all informations about the requirements of a virtual environment to run the project in.

### sat

This folder contains the example data which is analysed in the notebook.
It is the output of the script `download_DORIS_data.py` script, which allows to download the data of a specified satellite in a specified time frame from [https://cddis.nasa.gov/archive/doris/products/orbits](https://cddis.nasa.gov/archive/doris/products/orbits) (a free user account is needed)

### scripts

### src

## Getting Started

We first need to retrieve the satellite data from 
