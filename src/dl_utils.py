# SCARPING WEB DATA IMPORTS
from bs4 import BeautifulSoup
import io
import time
from time import sleep



# PARALLELISM
from multiprocessing import cpu_count 
from multiprocessing.pool import Pool
from multiprocessing import Lock, Value

# MISC
from misc_utils import progress_bar_II, globalise

def get_url(session,url):
    try:
        return session.get(url)
    
    except Exception as e:
        print(f'An error occured: {e}')
        print('retrying...')
        time.sleep(1)
        get_url(session,url)

def retrieve_dir(response):
    """
    Retrieves url of sub directories (like grg/, gsc/, ...) from initial url.
    Input: requests response object
    Output: list of urls.
    """
    
    url_old = response.url

    url_text = response.text

    dirs = []

    soup = BeautifulSoup(url_text,'html.parser') # for parsing url_text for url of sub directories
    
    if soup.find_all('div',class_='archiveDir'):
        for dir in soup.find_all('div',class_='archiveDir'):
            dirs.append(url_old + dir.a['href']) # appends relative url to directory
        
    else:
        print('In retrieve_dir: Could not find div-Tag with attribute "archiveDir".')

    return dirs


def retrieve_zip_urls(response):
    """
    Retrieves urls of the actual .Z-files.
    Input: requests response object
    Output: list of urls (locations) of .Z-files 
    """
    
    url_old = response.url
    url_text = response.text
    links=[]
    soup = BeautifulSoup(url_text,'html.parser') # for parsing url_text for hyperref urls (location of .Z-files)
    if soup.find_all('a',class_="archiveItemText"):
        for href in soup.find_all('a',class_="archiveItemText"):
            links.append((url_old + href['href']).strip()) 
    else:
        print('In retrieve_zip_urls: Could not find a-Tag with class "archiveItemText".')
    return links
        
def downlaod_to_csv(session,url_zip_file:str,save_path:str):
    """
    Downloads .Z-file directly to .csv-file.
    Input: current session for authentication; url to .Z-file; path to save/write .Z-file to .csv-file.
    """

    filename = url_zip_file.split('/')[-1] # get filename from .Z-file url 
   
    response = session.get(url_zip_file)
          
    if response.ok:
        print(f'Downloading and processing {url_zip_file} ... ',end='')
        
        stream = io.BytesIO(response.content).getvalue() # read contents of .Z-file as bytes-stream
        uncompressed_data = unlzw3.unlzw(stream).decode('utf-8').splitlines() # unpack using unlzw3 into list of strings (decode using utf-8)
      
        stream_to_csv(uncompressed_data,save_path,filename) # write to .csv
        
        print('done.')
       
    else:
        print(f'Could not download {url_zip_file}')

def stream_to_csv(stream,save_path:str,filename:str):
    """
    Writes contents of stream to .csv-file.
    Input: stream (io.BytesIO object); path to save .csv-file; filename;
    """
    df = to_df(stream=stream,from_stream=True,filename=filename)
    df.to_csv(save_path+filename+'.csv')


def downlaod_to_csv_parallel(session,url_zip_file:str,save_path:str,verbose:bool):
    """
    Used in *donwload_to_csv_II* - downloads .Z-file to .csv-file.
    Input: current session for authentication; path to .Z-file; path to save/write .csv-file to
    """

    filename = url_zip_file.split('/')[-1][:-2]
   
    response = session.get(url_zip_file)
          
    if response.ok:
        t0 = time.time() 
 
        stream = io.BytesIO(response.content).getvalue()
        uncompressed_data = unlzw3.unlzw(stream).decode('utf-8').splitlines()
      
        stream_to_csv(uncompressed_data,save_path,filename)
        response.close() # close response explicitly
        
        if verbose:
            print(f'Download {url_zip_file} done: {time.time()-t0:.3f}s')
        sleep(0.2) # sleep for 200ms to avoid that server blocks us
        response.close()
    else:
        print(f'Could not download {url_zip_file}')
        response.close()

    return url_zip_file # return the .Z-file url when file was downloaded correctly - this ensures that one can restart the download at last successfully downloaded file


def download_to_csv_II(*args):
    """
    Download .Z-files to .csv-file in parallel. Uses *donwload_to_csv_parallel*.
    Input: *args = (current session for authentification, .Z-file url, path to save .csv-file)
    """
    cpus = cpu_count()  # get number of cpus to use in parallel download

    # UNPACK ARGUMENTS 
    session = args[0] 
    url_zip_file = args[1]
    save_path = args[2]
    verbose = args[3]

    # PARALLEL DOWNLOAD: USE starmap TO HANDLE MULTIPLE INPUTS
    with Pool(cpus) as pool:
        pool.starmap(downlaod_to_csv_parallel,zip([session]*len(url_zip_file),url_zip_file,[save_path]*len(url_zip_file),[verbose]*len(url_zip_file))) # need to create list of tuples (session, .Z-file url, save_path) where only the 2nd argument varies
            
def downlaod_Z(session,url_zip_file:str,save_path:str,verbose,progress_bar_len:int=None,chunk_size=1024):
    """
    Downloads .Z-file and wirtes contents to *save_path*.
    Input: current session for authentication; urlz of .Z-file; path to save (write) .Z-file (contents); chunk size (Default = 128)
    """

    filename = url_zip_file.split('/')[-1] # get file name from .Z-file path
   
    response = session.get(url_zip_file,stream=True) 
          
    if response.ok:
        t0 = time.time() 

        try:
            with open(save_path+filename, 'wb') as file: # create new file if not already existing
                for chunk in response.iter_content(chunk_size=chunk_size):
                    file.write(chunk)

            if verbose:
                print(f'Download {url_zip_file} done: {time.time()-t0:.3f}s')
            else:
                progress_bar_II(progress_bar_len)

            response.close()
            sleep(0.1)
            
        except Exception: # catch timeout exceptions or any other currupt downloads
            # print(f'\nConnection lost. Continue download.\n')
            response.close()
            return url_zip_file # return the .Z-file url when file could not be downloaded correctly
    
    else:
        print(f'Could not download {url_zip_file}')
        response.close()
        
    
def download_Z_II(*args):
    """
    Download .Z-files in parallel. Uses *donwload_Z_parallel*.
    Input: *args = (current session for authentification, .Z-file url, path to save .Z-file)
    """
    cpus = cpu_count()  # get number of cpus to use in parallel download

    # UNPACK ARGUMENTS 
    session = args[0] 
    url_zip_file = args[1]
    save_path = args[2]
    verbose = args[3]
    currupt_urls = []

    # PARALLEL DOWNLOAD: USE starmap TO HANDLE MULTIPLE INPUTS
    shared = Value('i', 0)
    lock = Lock()
    progress_bar_len = len(url_zip_file)

    with Pool(processes=cpus,initializer=globalise, initargs=[shared, lock]) as pool:

        jobs = pool.starmap_async(downlaod_Z,[(session,url,save_path,verbose,progress_bar_len) for url in url_zip_file])
    
        pool.close()
        pool.join()

        # jobs = pool.starmap(downlaod_Z,[(session,url,save_path,verbose) for url in url_zip_file]) # create list of tuples (session, .Z-file url, save_path, verbose) where only the 2nd argument varies
        currupt_urls = [currupt_url for currupt_url in jobs.get() if currupt_url]

    # RESTART DOWNLOAD IF THERE ARE CURRUPT DOWNLOADS 
    if len(currupt_urls) !=0:
        print(f'\n{len(currupt_urls)} currupt download(s) encountered:\n')
        # for currupt_url in currupt_urls:
        #     print(currupt_url.split('/')[-1])
        print('Attempting to download missing files...')
        sleep(1)
        download_Z_II(session,currupt_urls,save_path,verbose)
    else:
        pass


