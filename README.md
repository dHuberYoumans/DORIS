# DORIS

**Work in progress**

This project is about finding orbit correcting manoeuvres in satellites of the DORIS cluster.
At its heart, these manoeuvres can be seen as outliers or anomalies of the periodic patterns underlying the observational data and as such, once stripped of all physical meaning, one can simplify the problem to an anomaly detection algorithm of tabulated time series data.


The data is freely available from the CDDIS DORIS data center.

Python scripts are provided to download data for various satellites, time frames, and analysis centers, as well as to download the schedule of maneuvers. The actual detection algorithm is being developed in a Jupyter notebook. This notebook guides the reader through the author's thought process and decision-making. As this is a work in progress, ideas, comments, and suggestions are welcome and appreciated.

##### Table of Contents
- [Getting Around](#getting-around)
    * [literature](#literature)
    * [notebooks](#notebooks)
    * [refs](#ref)
    * [requirements.yml](#requirementsyml)
    * [sat](#sat)
    * [scripts](#scripts)
    * [src](#src)


- [Getting Started](#getting-started)
    * [Installing the Virtual Environment](#installing-the-virtual-environment)
    * [Downloading Sample Data](#downloading-sample-data)

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

This folder contains the Python scripts `download_maneuver_schedule.py` and `download_DORIS_data.py` to download the scheduled manoeuvres and the satellite data respectively. 

### src

The source folder contains various custom modules which define convenience functions of different purpose. 

* `ana_utils.py`: utility methods for analysis purposes
* `df_utils.py`:  utility methods for data frames
* `dl_utils.py`:  utility methods for downloads
* `kepler_utils.py`: utility methods to compute orbital elements
* `misc_utils.py`:  miscellaneous utility methods (like a progress bar)
* `preprocessing_utils.py`: utility methods for preprocessing
    

## Getting Started

### Installing the Virtual Environment

The first thing to do is to install the virtual environment (venv) using the `requirements.yml` file to ensure that all necessary packages are installed.

To set up the virtual environment using Anaconda, run  

```
conda env create --file=requirements.yml
```

which sets up the venv `DORIS`. To activate the venv, run 

```
conda activate DORIS
```

### Downloading Sample Data

Next, we need to download some sample data.
One needs to register a free account at [https://urs.earthdata.nasa.gov](https://urs.earthdata.nasa.gov).

Once registered, we can use the `download_DORIS_data.py` located in `scripts` to download some sample data.
The script contains a help function which explains the usage.
Run

```
python3 scripts/download_DORIS_data.py --help
```
to access the help function
```
usage: download_DORIS_data.py [-h] [-v VERBOSE] [-c [CENTER ...]]
                              [-s [SAT ...]] [-b BEGIN] [-e END] [-o PATH]
                              [-fn FILENAME]

options:
  -h, --help            show this help message and exit
  -v VERBOSE, --verbose VERBOSE
                        verbose (default: False)
  -c [CENTER ...], --center [CENTER ...]
                        list of 3-letter analysis center id (type "zzz" for
                        full list) (default: ['zzz'])
  -s [SAT ...], --sat [SAT ...]
                        list of 3-letter sattelite id (type "zzz" for full
                        list) (default: ['zzz'])
  -b BEGIN, --begin BEGIN
                        last 2 digits of year of first position (default: 0)
  -e END, --end END     last 2 digits of year of last position (inlusive in
                        search) (default: 0)
  -o PATH, --path PATH  (create) directory to save .csv-file (default:
                        /Users/donny/Documents/DORIS/sat/)
  -fn FILENAME, --filename FILENAME
                        filename.csv (including extension) (default: sat.csv)
```
