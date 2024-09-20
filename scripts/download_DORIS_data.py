'''
This script downloads specified IDS DORIS data from https://cddis.nasa.gov/archive/doris/products/orbits/. 

Usage: download_IDS_DORIS.py [-h] [-v VERBOSE] [-c [CENTER ...]] [-s [SAT ...]] [-b BEGIN] [-e END]

Options:
  -h, --help            show this help message and exit
  -v VERBOSE, --verbose VERBOSE
                        verbose (default: False)
  -c [CENTER ...], --center [CENTER ...]
                        list of 3-letter analysis center id (type "zzz" for full list) (default: ['zzz'])
  -s [SAT ...], --sat [SAT ...]
                        list of 3-letter sattelite id (type "zzz" for full list) (default: ['zzz'])
  -b BEGIN, --begin BEGIN
                        last 2 digits of year of first position (default: 00)
  -e END, --end END     
                        last 2 digits of year of last position (default: 24) 
  -o PATH, --path PATH 
                        path to save .csv file(s)
  -fn FILENAME, --filename FILENAME
                        filename of .csv file

Strategy:
The script connects to https://cddis.nasa.gov/archive/doris/products/orbits/ using predefined authentification data.
It then loops through the specified subdirectories of analysis centers and specified subdirectories storing the satellite data.
It downloads the satellite data into an io.BytesIO stream which is read into a pd.DataFrame which is ultimately written to a .csv-file at a specified/predefined path.

Analysis centers:
grg : Center for Space Researchgrg : CNES/GRGSs
gsc : NASA/GSFCgop : Geodetic Observatory Pecny
lca : LEGOS-CLSsod : CNES/Service d'Orbitographie DORIS 
ssa : SSALTO

sp2 : Spot-2
sp3 : Spot-3
sp4 : Spot-4
sp5 : Spot-5
top : Topex/Poseidon
en1 : Envisat
ja1 : Jason-1
ja2 : Jason-2
ja3 : Jason-3
cs2 : Cryosat-2
h2a : HY-2A
h2c : HY-2C
srl : Saral
s3a : Sentinel-3a
s3b : Sentinel-3b
s6a : Sentinel-6a
h2d : HY-2D
swo : Swot
'''

# SCARPING WEB DATA IMPORTS
import requests
from bs4 import BeautifulSoup
import re
import sys
import os
from pathlib import Path
import time


# IMPORT UTILITY FUNCIONS
wd = str(Path(__file__).resolve().parents[1]) # working directory: /DORIS/

sys.path.append(wd + '/src/')# append path to ../src/ for following imports

import dl_utils  as dlu
import df_utils as dfu
import misc_utils as misc 


# CMD LINE (ARGUMENTS ARGPARSER IMPORT, PASSWORD)
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter 

from getpass import getpass


if __name__ == "__main__":
    # PARSE CMD LINE ARGUMENTSS
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', '--verbose', default=False, help='verbose')
    parser.add_argument('-c', '--center', default=['zzz'], nargs='*', type=str, help='list of 3-letter analysis center id (type "zzz" for full list)')
    parser.add_argument('-s', '--sat', default=['zzz'], nargs='*', type=str, help='list of 3-letter sattelite id (type "zzz" for full list)')
    parser.add_argument('-b', '--begin', default=0 ,type=int, help='last 2 digits of year of first position')
    parser.add_argument('-e', '--end', default=0, type=int, help='last 2 digits of year of last position (inlusive in search)')
    parser.add_argument('-o', '--path', default=wd+'/sat/', type=str, help='(create) directory to save .csv-file')
    parser.add_argument('-fn', '--filename', default='sat.csv', type=str, help='filename.csv (including extension)')
    args = vars(parser.parse_args())

    verbose = args['verbose']

    if args['center'] == ['zzz']:
        ctr_id = ['grg','gsc','lca','ssa']
    else:
        ctr_id = args['center']
    
    if args['sat'] == ['zzz']:
        sat_id = ['sp2','sp3','sp4','sp5','top','en1','ja1','ja2','ja3','cs2','h2a','h2c','h2d','srl','s3a','s3b','s6a','swo']
    else:
        sat_id = args['sat']


    begin = args['begin']
    end = args['end']

    # REGEX PATTERN TO FILTER TIME FRAME
    # pattern for bYY... where begin <= YY <= end
    b = re.compile(r'.*b([0-9][0-9]).*'.format(t=begin))
    e = re.compile(r'.*e([0-9][0-9]).*'.format(t=begin))

    # SETUP
    Path(wd + '/tmp/').mkdir(parents=True, exist_ok=True) # create DORIS/tmp folder if not existing
    Path(args['path']).mkdir(parents=True, exist_ok=True) # creates folder (including parents) of indicated paths if not existing

    PATH_TMP = wd + '/tmp/'
    PATH = args['path']+args['filename']

    MAX_RETRIES = 10

    SCHEME ='https://'
    BASE = 'cddis.nasa.gov/archive/doris/products/orbits'

    TARGET_URL = SCHEME + BASE

    # LOGIN CREDENTIALS
    USERNAME = input('Username: ') 
    PASSWORD = getpass('Password: ')

    files = [] # name of downloaded files

    # START A SESSION (FOR PERSISTANT COOKIES)
    with requests.Session() as session:

        # SAVE AUTHENTICATION DATA IN SESSION ATTRIBUTE FOR REUSAGE
        session.auth=(USERNAME, PASSWORD)

        # TRY TO ACCESS TARGET URL
        response = session.get(TARGET_URL)

        # GET REDIRECTION URL
        soup = BeautifulSoup(response.text,'html.parser')

        LOGIN_URL = response.url 
        
        r0 = session.get(LOGIN_URL) # format: rX; r = response, X = level

        if r0.ok:
            print('\nLogin successful.\n')
            
            # LEVEL 1: CONTAINS SUB-DIRECTORIES OF ANALYSIS-CENTERS - LOOP OVER  CENTERS
            t_init = time.time() # starting time

            print(f'Retrieving links...\n',flush=True)
            LINKS = []

            for cID in ctr_id:
                URL1 = r0.url+cID

                for i in range(MAX_RETRIES): # try to get URL1
                    
                    try: 
                        r1 = session.get(URL1)
            
                        # print(f'{cID} -> ',end='',flush=True)
                        if r1.ok:

                            for satID in sat_id:
                                URL2 = r1.url + satID
                                
                                for j in range(MAX_RETRIES): # try to get URL2

                                    try: 
                                        r2 = session.get(URL2)
                
                                        # LEVEL 2: CONTAINS SUB-DIRECTORIEES OF SATELLITES - LOOP OVER SATS 
                                        print(f'{cID} -> {satID} -> ',end='',flush=True)
                                        if r2.ok:

                                            # FILTER LINKS FOR THOSE STARTING WITH cccsss... (3-letter center id)(3-letter sat id) AND SPECIFIED TIME FRAME
                                            p = re.compile(r'^{s}.*'.format(s = cID+satID))

                                            # CHECK IF YEAR WAS SPECIFIED
                                            if begin == 0 and end == 0:
                                                LINKS += [s for s in dlu.retrieve_zip_urls(r2) if p.match(s.split('/')[-1])]

                                            elif begin !=0 and end==0:
                                                LINKS += [b.match(p).group(0) for p in dlu.retrieve_zip_urls(r2) if b.match(p.split('/')[-1]) and (begin <= int(b.match(p.split('/')[-1]).group(1)))] 
                                                # LINKS += [s for s in retrieve_zip_urls(r2) if p.match(s.split('/')[-1]) and b.match(s.split('/')[-1])]

                                            elif begin == 0 and end != 0:
                                                LINKS += [b.match(p).group(0) for p in dlu.retrieve_zip_urls(r2) if b.match(p.split('/')[-1]) and (int(b.match(p.split('/')[-1]).group(1)) <= end)] 
                                                # LINKS += [s for s in retrieve_zip_urls(r2) if p.match(s.split('/')[-1]) and e.match(s.split('/')[-1])]

                                            else:
                                                LINKS += [b.match(p).group(0) for p in dlu.retrieve_zip_urls(r2) if b.match(p.split('/')[-1]) and (begin <= int(b.match(p.split('/')[-1]).group(1)) <= end)] 

                                                # LINKS += [s for s in retrieve_zip_urls(r2) if p.match(s.split('/')[-1]) and ((b.match(s.split('/')[-1]) or e.match(s.split('/')[-1])))]
                                                
                                            print('done.',flush=True)

                                            # SET LINKS WHICH ARE ALREADY DOWNLOADED CTR FOR LATER USE: IF CONNECTION TIMES OUT, RESTART WITH LINKS WHICH ARE NOT YET DOWNLOADED.
                                            # currupt_links = []

                                            if len(LINKS) == 0:
                                                print(f'{cID} has no data for {satID} for specified time frame.\n')
                                                
                                            r2.close() # close response
                                            break # break out of MAX_RETRIES loop

                                        else:
                                            print(f'failed: {r2.status_code}')
                                            r2.close()
                                            break # break out of MAX_RETRIES loop

                                    except requests.exceptions.ConnectionError:
                                        print(f'Connection lost. Reconnecting.')
                                        time.sleep(1)

                                    if j == MAX_RETRIES-1:
                                        print('Maximal number of retries exceeded. ')
                                        exit()
                        else:
                            print(f'failed: {r1.status_code}')
                            
                        r1.close() # close response
                        break # break out of MAX_RETRIES loop
                        
                    except requests.exceptions.ConnectionError:
                        print(f'Connection lost. Reconnecting.')
                        time.sleep(1)

                    if i == MAX_RETRIES-1:
                        print('Maximal number of retries exceeded. ')
                        exit()

            print('\n... complete.\n')

            #  COLLECT FILENAMES
            files = list(map(lambda s: PATH_TMP + s.split('/')[-1],LINKS)) # add filenames

            # PARALLEL DONWLOAD
            
            print(f'Starting download ({len(LINKS)} files).\n')

            t0 = time.time()
            
            dlu.download_Z_II(session,LINKS,PATH_TMP,verbose)

            print('\n\nDonwload complete.')

            # PRINT TOTAL DOWNLOAD TIME
            print(f'Total downlad time: {time.time()-t_init}s\n')

            # CREATE DATA FRAMES
            print('Creating DataFrames ...\n')

            # Z_to_csv_II(files, PATH)
            df = dfu.write_to_df_II() 

            print('\n... done.\n')

            print(f'Saving to {PATH} ... ', end = '')

            df.to_csv(PATH)

            print('done.\n')

            print('Cleaning up ...')
            for i, file in enumerate(files):
                try:
                    os.remove(file)
                    misc.progress_bar(i,len(files))
                except Exception as e:
                    print(f'An error occured: {e}')
            print('\n... done. All set.')

            try:
                os.rmdir(wd+'/tmp/')
            except Exception as e:
                print(f'An error occured: {e}')
                             
        else:
            print('Login failed.\n')
            if r0.status_code == 404:
                print(f'URL could not be found: {r0.status_code}')
                r0.close()
                exit()
            
            if r0.status_code == 401:
                print('Invalid credentials.\n')
                r0.close()
                os.execv(sys.executable, ['python3'] + sys.argv)

        
