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

Once registered, we can use the `download_DORIS_data.py` located in `scripts` to download some sample data from [https://cddis.nasa.gov/archive/doris/products/orbits/](https://cddis.nasa.gov/archive/doris/products/orbits/).

The CDDIS archive is built up as follows: there are 4 folders which store the satellite's data (position and velocity) recorded by a _analysis center_. The analysis centers are abriviated by three letters, for example _grc_. 
<p align="center">
  <img src="https://github.com/dHuberYoumans/DORIS/blob/main/img/centers.png"/>
</p>

Within each such folder there are subfolders containing the data of specific satelleites. These folders are named by the satellite IDs given by three letters, for example _s6a_ (for _sentinel-6a_). 

<p align="center">
  <img src="https://github.com/dHuberYoumans/DORIS/blob/main/img/sats.png"/>
</p>

These folders then finally contain the satellite data chopped up into several compressed (.Z) files.
The compressed files contain a text document in the SP3c format lisiting position and velocity vectors of the satellite. More about the SP3c format and the naming convention of the files can be found in the provided literature (see [Data-Structure-Format.pdf](https://github.com/dHuberYoumans/DORIS/blob/main/literature/Data-Structure-Formats.pdf) and [SP3c_format.pdf](https://github.com/dHuberYoumans/DORIS/blob/main/literature/SP3c_format.pdf)).

<p align="center">
  <img src="https://github.com/dHuberYoumans/DORIS/blob/main/img/data.png"/>
</p>

**Remark** There are two additional text document in each folder storing the actual satellite data. These contain a list of hash file pairs which can be used to ensure that the correct files were downloaded.

The script `download_DORIS_data.py` downlaods the data for a specified time frame of a specified satellite and stores the data in a .csv file in a specified destination. It contains a help function which explains the usage; run
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

For example, running 
```
python3 ./scripts/download_DORIS_data.py -c gsc -s s6a -b 20 -e 22 -o "~/Desktop/tmp/" -fn "s6a_20_22.csv"
```
from the base folder of the project, we call the script `download_DORIS_data.py` with the options 
* `-c` specifying which analysis center we want retrieve informations from
* `-s` specifying which satellite data we are interessted in
* `-b 20 -e 22` specifying that we want to retrieve all data starting from 2020 until 2022
* `-o` specifying the path where to save the download
* `-fn` specifying the filename of the output

The script will therefore download and save the data of the satellite _s6a_ in the time frame _2020_ to _2022_ as observed by the analysis center _gsc_:

<p align="center">
  <img src="https://github.com/dHuberYoumans/DORIS/blob/main/img/download_DORIS.gif" alt="animated" />
</p>

