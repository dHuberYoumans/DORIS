# SCARPING WEB DATA IMPORTS
import time
import sys


def progress_bar(count,total):
    """
    """
    bar_length = 80
    filled = int(
        round( bar_length*count / float(total) )
        )
    percentage = round( 100*count / float(total), 1 )
    bar = '#'*filled + ' '*(bar_length-filled)
    print(f'[{bar}] {percentage}% ',end='\r')
    if count == total-1:
        print(f"[{'#'*bar_length}] 100.0% ")

def progress_bar_II(total:int):
    # time.sleep(.1)
    with lock:
        shared.value += 1

    count = shared.value
    
    bar_length = 80
    filled = int(
        round( bar_length*count / float(total) ))
    percentage = round( 100*count / float(total), 1 )
    bar = '#'*filled + ' '*(bar_length-filled)

    sys.stdout.write(f'\r[{bar}] {percentage}% ({count}/{total}) ')
    sys.stdout.flush()

def globalise(t, l):
    """
    """
    global shared, lock
    shared = t
    lock = l
