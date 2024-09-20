import urllib.request
from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path

wd = str(Path(__file__).resolve().parents[1]) # working directory: /DORIS/
Path(wd + '/ref/').mkdir(parents=True, exist_ok=True) # create DORIS/ref/ if not existing 
Path(wd + '/ref/tmp/').mkdir(parents=True, exist_ok=True) # create DORIS/ref/tmp/ if not existing 


sys.path.append(wd+'/src/')# append path to DORIS/src/ for following imports

import misc_utils as misc 

url = 'https://ids-doris.org/analysis-documents.html'
PATH = wd + '/ref/'

sat_id = {
    'SPOT2':'sp2',
    'SPOT3':'sp3',
    'SPOT4':'sp4',
    'SPOT5':'sp5',
    'TOPEX':'top',
    'ENVI1':'en1',
    'JASO1':'ja1',
    'JASO2':'ja2',
    'JASO3':'ja3',
    'CRYO2':'cs2',
    'HY-2A':'h2a',
    'HY-2C':'h2c',
    'SARAL':'srl',
    'SEN3A':'s3a',
    'SEN3B':'s3b',
    'SEN6A':'s6a',
    'HY-2D':'h2d',
    'SWOT1':'swo'
}

def parse_man(file_lines):
    """
    Parses the content of the maneuver .txt file and writes content into a DataFrame with columns sat_id, start, end 
    where 'sat_id' is the 3-char satellite identifier, 'start' the starting time (date) of the maneuver and 'end' the ending time (date).

    Input: Content of .txt file (from file.readlines())
    Output: pandas.DataFrame
    """
    man = pd.DataFrame()

    for line in file_lines:
        # GET SAT ID
        id = sat_id[line[:5]]

        # GET TIMESTAMP OF START
        start_year = line[6:10]
        start_day_of_year = line[11:14]
        start_hour = line[15:17]
        start_min = line[18:20]

        start = pd.to_datetime(datetime.strptime(start_year + ' ' + start_day_of_year, '%Y %j') + timedelta(hours = int(start_hour), minutes=int(start_min)))
        
        # GET TIMESTAMP OF END
        end_year = line[21:25]
        end_day_of_year = line[26:29]
        end_hour = line[30:32]
        end_min = line[33:35]
        
        end = pd.to_datetime(datetime.strptime(end_year + ' ' + end_day_of_year, '%Y %j') + timedelta(hours = int(end_hour), minutes=int(end_min)))

        # COLLECT DATAFRAME
        man = pd.concat([man,pd.DataFrame(data={'sat_id':id,'start':start,'end':end},index=['0'])],axis=0,ignore_index=True)

    return man

if __name__ == "__main__":

    # PARSE INITIAL URL
    with requests.Session() as session:
        res = session.get(url)
        soup = BeautifulSoup(res.text,'html.parser')

    # DOWNLOAD FTP FILES
    items = soup.find_all(lambda tag: 'Maneuvers' in tag.get_text(strip=True, separator=' '))[-1].find('ul').find_all('li')
    print('Downloading data...')
    for i,item in enumerate(items):
        ftp = item.find('a').get('href')
        urllib.request.urlretrieve(ftp, PATH + 'tmp/' + ftp.split('/')[-1])
        misc.progress_bar(i,len(items))
    print('')
    print('...done.')

    # PARSE THE DOWNLOADED FILES INTO A SINGLE DATAFRAME
    files = [file for file in os.listdir(PATH+'tmp/') if file.split('.')[-1]=='txt'] # avoid files like .DS_Store (Macintosh)
    maneuvers = pd.DataFrame()

    print('Parsing data...')
    for i,file in enumerate(files):
        with open(PATH+'tmp/'+file,'r') as f:
            lines = f.readlines()
        maneuvers = pd.concat([maneuvers,parse_man(lines)])
        misc.progress_bar(i,len(files))
    print('')
    print('...done.')

    # SAVE DATAFRAME 
    print(f'Saving DataFrame to {PATH+"maneuvers_schedule.csv"}...',end='')
    maneuvers.to_csv(PATH+'maneuvers_schedule.csv')
    print('done.')

    print('Cleaning up...')
    for i, file in enumerate(files):
        try:
            os.remove(PATH+'tmp/'+file)
            misc.progress_bar(i,len(files))
        except Exception as e:
            print(f'An error occured: {e}')
            
    try:
        os.rmdir(wd+'/ref/tmp/')
    except Exception as e:
        print(f'An error occured: {e}')
    print('')
    print('...done.')
