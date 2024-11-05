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
    * [Downloading Scheduled Manoeuvres](#downloading-scheduled-manoeuvres)
 
- [Developing the Algorithm](#developing-the-algorithm)

- [Theory](#theory)
     * [Orbital Elements](#orbital-elements)
     * [Harmoinc Regression](#harmonic-regression)
     * [Common Outlier Detection Algorithms](#common-outlier-detection-algorithms)


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
  <img src="https://github.com/dHuberYoumans/DORIS/blob/main/img/download_DORIS.gif" alt="animated" width=500px height=auto />
</p>

### Downloading Scheduled Manoeuvres

In order to evaluate any model we build, we need to a way to verify when a manoeuvre was actually performed. 
These orbital satellite manoeuvres are prescheduled and a list of their dates can be downloaded.

The script `download_maneuver_schedule.py` scrapes [https://ids-doris.org/analysis-documents.html](https://ids-doris.org/analysis-documents.html) for FTP files containing the timestamps of the manoeuvres, satellite by satellite, and combines them into a .csv file 

<p align="center">
  <img src="https://github.com/dHuberYoumans/DORIS/blob/main/img/download_mans.gif" alt="animated" width=500px height=auto />
</p>

**Remark** 
The script creates a temporary folder `tmp/` inside `ref/` which it uses to first download and store all FTP files. It then parses the downloaded files and combines into a .csv file which is saved in `ref/`. Afterwards, it deletes `tmp/` including all stored FTP files. Information on the structure of the FTP files can be found in the documentation [man.readme](https://github.com/dHuberYoumans/DORIS/blob/main/literature/man.readme)

The .csv file contains contains three columns

* sat_id: satellite ID
* start: timestamp when the manoeuvre started
* end: timestamp when the manoeuvre ended

Reading the .csv into a pandas data frame, the head of this data frame is shown below

```
sat_id	start	end
0	srl	2013-02-27 13:14:00	2013-02-27 13:19:00
1	srl	2013-02-27 14:58:00	2013-02-27 15:04:00
2	srl	2013-03-01 15:51:00	2013-03-01 15:53:00
3	srl	2013-03-02 06:03:00	2013-03-02 06:05:00
4	srl	2013-03-03 02:10:00	2013-03-03 02:12:00
```

## Developing the Algorithm

Detialed information and the thought process beghind the development of the outlier detection algorithm is explained step by step in the [notebook](https://github.com/dHuberYoumans/DORIS/blob/main/notebooks/finding_DORIS.ipynb).
We stress that this project is **work in progress** and we will add new ideas as we go along.

However, we would like to point out some key ideas of how we approach this problem.

### Methodology 
After the download the data, we have read it into a pandas data frame. 

As we are dealing with real-world data, it is messy and some preprocessing is required. For the sake of readibility and to mitigate error sources, using `sklearn.pipeline.Pipline`, we build a pipeline with custom transformers which 

1. loads the data
2. drops duplicated timestamp indices
3. converts units into SI units
4. computes orbital elements

as shown in the code snippet below.

```
# LOADING AND PREPROCESSING SATELLITE DATA

sat_path = str(cwd.parent)+'/sat/s6assa2024/s6assa_20_24.csv'

if not os.path.isfile(sat_path):
    raise Exception('Indicated path does not point to a valid file')

# DEFINE CUSTOM TRANSFORMERS
load_sat = preputls.LoadSingleSat(path=sat_path)
drop_dupl_idx = preputls.DropDuplIdx()
convert_units = preputls.ConvertUnits()
compute_orbital_elements = preputls.OrbitalElements(type='all')

# BUILD PIPELINE FOR PREPROCESSING
prep_pipeline = Pipeline(
    steps=[
    ('load_sat', load_sat),                                 # load satellite data
    ('drop_duplicated_idx', drop_dupl_idx),                 # drop duplicated indices
    ('convert_units',convert_units),                        # convert units 
    ('compute_orbital_elements',compute_orbital_elements)   # compute orbital elements
])

print('Loading data ... ',end='')

# GET DATA FROM PIPELINE
s6ssa = prep_pipeline.fit_transform(None)

print('done.\n')

# CHECK FOR NAN
print('Checking for null-values:')
print(s6ssa.isna().sum().value_counts())

print('\n loading of satellite data complete.')
```

Computing orbital elements may be seen already a feature engineering. Indeed, orbital elements are conserved quantities which in the absence of all forces acting on the satellite would be constants of motions, i.e. constant throughout time. In this case, they would uniqule define the orbit of the satellite around earth. However, since the satellite is subject to various pertrubative forces, these features are not constant but show a oscillatory behaviour (see [Theory](#theory) for more on this). Nevertheless, the idea is to analyse the sinusoidal pattern of these orbital elements. 
An example of such a feature, namely of the so-called _semi-parameter_ $p$, and its oscillatory nature is shown below:

<p align="center">
  <img src="https://github.com/dHuberYoumans/DORIS/blob/main/img/p.png" hieght=400px width=auto />
</p>

The red dot indicates the time a manoeuvre took place. 
By closer inspection one sees that the manoeuvre causes a ripple in the periodic pattern of the feature. 
The detection algorithm now aims to identify these ripples.

To enhance the effect of the pattern breaking, we work with the first and second derivative of the feature.

<p align="center">
  <img src="https://github.com/dHuberYoumans/DORIS/blob/main/img/pdot.png" hieght=400px width=auto />
</p>

As we are working with a time series, it is crucial to test for stationarity. 

```
# STATIONARITY: ADF (AUGMENTED DICKEY-FULLER) TEST 
adf_test = pm.arima.ADFTest(alpha=0.05)


# SINCE THE TIME SERIES HAS A LOT OF DATA POINTS, TEST FOR STATIONARITY IN SPECIFIED INTERVALS [start:end]
start = 100_000
end = 200_000

print('Test of stationarity of dot_p$:')
p_val, should_diff = adf_test.should_diff(dot_p[start:end])
print(f'p value = {p_val}')
print(f'stationary: {~should_diff}\n')

print('Test of stationarity of ddot_p$:')
p_val, should_diff = adf_test.should_diff(ddot_p[start:end])
print(f'p value = {p_val}')
print(f'stationary: {~should_diff}')

--------------------------------------------------------------------
Test of stationarity of dot_p$:
p value = 0.01
stationary: True

Test of stationarity of ddot_p$:
p value = 0.01
stationary: True
```
It is tempting to use standard time series analysis methods such as (S)ARIMA. However, since the data is too large (sevral million entries) we have to follow a rolling window approach and the (S)ARIMA model overfits the data

<p align="center">
  <img src="https://github.com/dHuberYoumans/DORIS/blob/main/img/ARIMA.png" hieght=400px width=auto />
</p>

We therefore define a custom Harmonic Regression model `HarmonicRegression()`. The class contains a method `fit()` which takes the follwing input 
* a feature (pandas Series)
* a date of manoeuvre (string)
* a time step (int, measured in hours) to define the window of observation 
* a cut-off (float, default 1e-6) which determines when the method stops to improve the fit
* and a verbose flag (bool) which, when set to `True` prints information about the numebr of harmonics which is fitted and the mean squared error compared to the actual observed data

The method fits a harmonic regression model to the feature. In order to improve the fit, the method loops over the number of harmonics which are to be considered computing at each step the mean square error (MSE) to the actual observed data. Once the MSE falls below the cut-off parameter `eps`, the model stops and sets the attributes 
* `n_harmonics` (number of harmonics used in the fit)
* `y` (actual observed data),
* `baseline` (fitted curve)
* `residuals` (diffrence `y - baseline`)
accordingly.

The `residuals` can then be analysed for outliers, for example using a simple _Z-score_, _robust Z-score_ (_MAD-score_) or more complicated outlier detection algorithms.  

<p align="center">
  <img src="https://github.com/dHuberYoumans/DORIS/blob/main/img/baseline_and_residuals.png" hieght=400px width=auto />
</p>

For more details and ideas we refer the interested reader to the  [notebook](https://github.com/dHuberYoumans/DORIS/blob/main/notebooks/finding_DORIS.ipynb).

## Theory

### Orbital Elements

### Harmoinc Regression

### Common Outlier Detection Algorithms


