import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

import numpy as np

import os
import sys
from pathlib import Path

# GET CURRENT WORKING DIRECTORY
cwd = Path(os.getcwd())

# APPEND /src/ TO PATH TO IMPORT kutils
sys.path.append(str(cwd.parent)+'/src/')

import kepler_utils as kutls

class ConvertUnits(BaseEstimator, TransformerMixin):

    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, sat):
        """
        Convert units - position: km -> m, velocity: dm/s -> m/s
        """
        sat_ = sat.copy()

        # CONVERT POS TO [km]->[m] (MULTIPLY BY 1000) AND VELOCITY TO [dm/s]->[m/s] (DIVIDE BY 10)
        sat_[['x','y','z']] = sat_[['x','y','z']] * 1_000
        sat_[['vx','vy','vz']] = sat_[['vx','vy','vz']] / 10

        return sat_

class DropDuplIdx(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self
    
    def transform(self, sat):
        """
        Drop duplicated indices
        """
        sat_ = sat.copy()

        sat_ = (sat_
             .reset_index()
             .drop_duplicates(subset='time_stamp',keep='last')
             .set_index('time_stamp'))
        
        return sat_
    
class LoadSingleSat(BaseEstimator, TransformerMixin):
    def __init__(self,path=None):
        self.path = path

    def fit(self, X, y=None):
        return self
    
    def transform(self,X=None):
        """
        Load and return the DORIS .csv-file in single DataFrame (with DateTime index) with sorted index
        """

        dtypes_ = {'time_stamp':'str','x':'float','y':'float','z':'float','vx':'float','vy':'float','vz':'float'}
        sat_ = pd.read_csv(self.path,index_col=[0],dtype=dtypes_,parse_dates=['time_stamp'])
    
        return sat_.sort_index() 
    
class LoadSats(BaseEstimator, TransformerMixin):
    def __init__(self,path=None):
        self.path = path

    def fit(self, X, y=None):
        return self
    
    def transform(self,X=None):
        """
        Load and return the DORIS .csv-file in single DataFrame (with DateTime index) with sorted index
        """

        dtypes_ = {'ctr_id':'str','sat_id':'str','time_stamp':'str','x':'float','y':'float','z':'float','vx':'float','vy':'float','vz':'float'}
        sat_ = pd.read_csv(self.path,usecols=range(1,10),index_col=[2],dtype=dtypes_,parse_dates=['time_stamp'])
    
        return sat_.sort_index() 
        
class OrbitalElements(BaseEstimator, TransformerMixin):
    def __init__(self,type:str='kepler',custom_elements=None):
        self.elements_type = type
        self.custom_elements = custom_elements

    def fit(self, X, y=None):
        return self

    def transform(self,sat):
        sat_ = sat.copy()
        data_ = {}

        if self.elements_type == 'kepler':
            elements_ = ['a','e','i','nu','omega','Omega']

        elif self.elements_type == 'equinoctial':
            elements_ = ['p','f','g','q1','q2','L']

        elif self.elements_type == 'all':
            elements_ = ['a','e','i','nu','omega','Omega','p','f','g','q1','q2','L','E','M','n']

        elif self.elements_type == 'custom':
            elements_ = self.custom_elements


        for elem in elements_:
            data_[elem] = eval(f'kutls.{elem}(sat).reshape(-1,)')

        orbital_elements_ = pd.DataFrame(data=data_).set_index(sat_.index)

        sat_ = pd.concat([sat_,orbital_elements_],axis=1)

        return sat_


def grad(ts:pd.Series,dt)->pd.Series:
    tsname_ = ts.name
    tsdot_ = pd.Series(np.gradient(ts,dt),ts.index,name='{c}dot'.format(c=tsname_))

    return tsdot_
    