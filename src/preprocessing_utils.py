import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

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
        
   