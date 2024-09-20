# PROCESSING DATA IMPORTS
import numpy as np
import pandas as pd
# from datetime import datetime
import re
import os

# PROGRESS BAR IMPORTS
# import time
# import sys


# UNZIPPING .Z FILES IMPORTS
import unlzw3
from pathlib import Path

# MULTIPROCESSING IMPORTS
from multiprocessing import cpu_count 
from multiprocessing.pool import Pool
from multiprocessing import Lock, Value, Manager

# MISC
from misc_utils import globalise, progress_bar, progress_bar_II

def unzip(path_zip_file:str):
    """
    Unzips .Z-file at *path_zip_file*.
    Input: path to .Z-file
    Output: (utf-8 decoded) list of strings (contents of .Z-file).
    """

    uncompressed_data = unlzw3.unlzw(Path(path_zip_file)) # use unlzw3 to unzip .Z-file

    return uncompressed_data.decode('utf-8').splitlines() # decode in utf-8 

def to_df(path_to_file:str='',from_stream:bool=False,stream=[],filename=''):
    """
    CREATES pd.DataFrame form .Z-file of stream (decoded in utf-8).
    Input: .Z-file path; optional: stream, from_stream flag, filename -> used in stream_to_csv
    Output: pd.DataFrame
    """

    # CREATE pd.DataFrame WITH COLUMNS
    #  analysis center id (ctr_id) | satellite id (sat_id) | time_stamp | x position (x) | y position (y) | z position (z) | x-momentum (px) | y-momentum (py) | z-momentum (pz)
    
    time = []
    x = []
    y = []
    z = []
    vx = []
    vy = []
    vz =[]

    
    if from_stream:
        filename = filename
        stream = stream[22:]
    else:
        filename = path_to_file.split('/')[-1] # get filename from .Z-file path
        stream = unzip(path_to_file)[22:]

    for line in stream: # omits header of .Z-file; can be addapted if more documentation is added
        # split = line.split()
        num = re.compile(r'-?\d*\.\d*') # regex pattern to filter for number: needed since VL39-64263.5220048 -3451.1598196-26497.1339810 999999.999999 may happen (can't use split)
        date = re.compile(r'\d*\d')

        # CHECK FIRST CHARACTER OF EACH LINE: 
        # * -> TIME
        # P -> POSITION
        # V -> VELOCITY 
        if bool(re.search(r'^\*',line)):
            time.append(
                pd.to_datetime(
                    ''.join(
                        list(
                            map(lambda s: s.zfill(2),re.findall(date,line)[:-1])
                            )
                        )
                    )
                )
        elif bool(re.search(r'^P.*',line)):
            split = re.findall(num,line)
            x.append(float(split[0]))
            y.append(float(split[1]))
            z.append(float(split[2]))
        elif bool(re.search(r'^V.*',line)):
            split = re.findall(num,line)
            vx.append(float(split[1]))
            vy.append(float(split[2]))
            vz.append(float(split[3]))
        else:
            pass
        # if bool(re.search(r'^\*',split[0])):
        #     time.append(
        #         pd.to_datetime(
        #             split[1] + split[2].zfill(2) + split[3].zfill(2) + split[4].zfill(2) + split[5].zfill(2)
        #             )
        #         )
        # elif bool(re.search(r'^P.*',split[0])):
        #     x.append(float(split[1]))
        #     y.append(float(split[2]))
        #     z.append(float(split[3]))
        # elif bool(re.search(r'^V.*',line[0])):
        #     vx.append(float(split[1]))
        #     vy.append(float(split[2]))
        #     vz.append(float(split[3]))
        # else:
        #     pass


    ctr_id = [filename[:3]]*len(x)
    sat_id = [filename[3:6]]*len(x)

    return pd.DataFrame({'ctr_id':ctr_id, 'sat_id':sat_id,'time_stamp':time, 'x':x, 'y':y, 'z':z, 'vx':vx, 'vy':vy, 'vz':vz})

def create_df(path_to_file:str=''):
    """
    CREATES pd.DataFrame form .Z-file of stream (decoded in utf-8).
    Input: .Z-file path; optional: stream, from_stream flag, filename -> used in stream_to_csv
    Output: pd.DataFrame
    """

    # CREATE pd.DataFrame WITH COLUMNS
    #  analysis center id (ctr_id) | satellite id (sat_id) | time_stamp | x position (x) | y position (y) | z position (z) | x-momentum (px) | y-momentum (py) | z-momentum (pz)
    
    time = []
    x = []
    y = []
    z = []
    vx = []
    vy = []
    vz =[]

    filename = path_to_file.split('/')[-1] # get filename from .Z-file path
    stream = unzip(path_to_file)[22:]

    # REGEX 
    num = re.compile(r'-?\d*\.\d*') # regex pattern to filter for number: needed since VL39-64263.5220048 -3451.1598196-26497.1339810 999999.999999 may happen (can't use split)
    date = re.compile(r'\d*\d')

    # LIST OF DATES
    dates = [''.join(list(map(lambda s: s.zfill(2),re.findall(date,line)[:-1]))) for line in stream[:-1:3]]  # last entry = 'EOF'

    time = list(map( lambda t: pd.to_datetime(t),  dates ) )

    positions=[re.findall(num,line)[:-1] for line in stream[1::3]]
    x = np.array(positions)[:,0].astype(float)
    y = np.array(positions)[:,1].astype(float)
    z = np.array(positions)[:,2].astype(float)

    velocities =[re.findall(num,line)[:-1] for line in stream[2::3]]
    vx = np.array(velocities)[:,0].astype(float)
    vy = np.array(velocities)[:,1].astype(float)
    vz = np.array(velocities)[:,2].astype(float)

    ctr_id = [filename[:3]]*len(x)
    sat_id = [filename[3:6]]*len(x)

    # time = list(map(
    #     lambda t: pd.to_datetime(' '.join( list(map(lambda s: s.zfill(2), t.split()[1:-1])) ),format='%Y %m %d %H %M'), stream[:-1:3] # last entry = 'EOF'
    #     ))
    # positions = list(map(lambda pos : pos.split()[1:-1], stream[1::3]))
    # x = np.array(positions)[:,0].astype(float)
    # y = np.array(positions)[:,1].astype(float)
    # z = np.array(positions)[:,2].astype(float)

    # velocities = list(map(lambda pos : pos.split()[1:-1], stream[2::3]))
    # vx = np.array(velocities)[:,0].astype(float)
    # vy = np.array(velocities)[:,1].astype(float)
    # vz = np.array(velocities)[:,2].astype(float)

    # ctr_id = [filename[:3]]*len(x)
    # sat_id = [filename[3:6]]*len(x)

    return pd.DataFrame({'ctr_id':ctr_id, 'sat_id':sat_id,'time_stamp':time, 'x':x, 'y':y, 'z':z, 'vx':vx, 'vy':vy, 'vz':vz})

def Z_to_csv(path_to_file:str,save_path:str,progress_bar_len=None):

    """
    Writes .Z-file to .csv-file.
    Input: .Z-file path; path to save .csv-file.
    """
    
    filename = path_to_file.split('/')[-1] # get filename

    try:
        df = create_df(path_to_file)
    except Exception as e:
        print(f'error in {path_to_file}: {e}')
        exit()

    df.to_csv(save_path+filename+'.csv')

    if progress_bar_len:
        progress_bar_II(progress_bar_len)

def Z_to_csv_II(*args):
    """
    """
    cpus = cpu_count()  # get number of cpus to use in parallel download

    # UNPACK ARGUMENTS 
    paths_to_files = args[0]
    save_path = args[1]

    shared = Value('i', 0)
    lock = Lock()
    nb_files = len(paths_to_files)


    with Pool(processes=cpus,initializer=globalise, initargs=[shared, lock]) as pool:

        pool.starmap_async(Z_to_csv,[(path,save_path,nb_files) for path in paths_to_files])
    
        pool.close()
        pool.join()

def write_to_dfs():
    """
    Creates single big DataFrame (from .Z-file in ./tmp/ directory) and wirtes it to .csv-file.
    Input: Path to save .csv-file (save_path) including the output filename with .csv-extension. 
    """

    try:
        # GET WORKING DIRECTORY AND LIST 
        working_dir = os.getcwd() + '/tmp/'
        Z_file_names = os.listdir(working_dir)
        Z_files = sorted([working_dir+file for file in Z_file_names if file.endswith('.Z')]) # sort to detect overlap in observation date  
        total = len(Z_files) # total number of files

        dfs = [] # list of DataFrames 
        
        for i,file in enumerate(Z_files):
            dfs.append(create_df(file))
            progress_bar(i,total)

        return pd.concat(dfs)
        
    except Exception as e:
        print(f'An error occured: {e}')
        exit()

def write_to_dfs_II_worker(Z_file,shared_list,progress_bar_len=None):
    """
    Worker function for write_to_dfs_II() method
    Creates single big DataFrame (from .Z-file in ./tmp/ directory) and wirtes it to .csv-file.
    Input: Z_file, shared list among processes ( multiprocessing.Manager().list() ) 
    Optional: number of processes for progress bar (progress_bar_len)
    Output: DataFrame from .Z-file
    """

    try:
        shared_list.append(create_df(Z_file))

        if progress_bar_len:
            progress_bar_II(progress_bar_len)
        
    except Exception as e:
        print(f'An error occured: {e}')
        exit()

def write_to_df_II():
    """
    Multiprocess version of write_to_dfs() method.

    Creates single big DataFrame (from .Z-file in ./tmp/ directory) and wirtes it to .csv-file.
    Input: Path to save .csv-file (save_path) including the output filename with .csv-extension.
    Output: (unordered) DataFrame
    """

    # GET WORKING DIRECTORY AND LIST 
    working_dir = os.getcwd() + '/tmp/'
    Z_file_names = os.listdir(working_dir)
    Z_files = sorted([working_dir+file for file in Z_file_names if file.endswith('.Z')]) # sort to detect overlap in observation date 

    nb_files = len(Z_files)

    cpus  = cpu_count()

    manager = Manager()
    dfs = manager.list()

    shared = Value('i', 0)
    lock = Lock()


    with Pool(processes=cpus,initializer=globalise, initargs=[shared, lock]) as pool:

        pool.starmap_async(write_to_dfs_II_worker,[(file,dfs,nb_files) for file in Z_files])
    
        pool.close()
        pool.join()

        return pd.concat(dfs)

