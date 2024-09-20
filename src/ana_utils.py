import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from datetime import timedelta

def f(x,offset,freq,ampl,phase):
    """ function f(x) = ampl*sin(freq*x + phase) + offset for fitting data using scipy.optimize.curve_fit 
    
        input: x (array-like) - independent variable, usually simply range(len(observations))

        parameters: 
        * ampl - amplitude
        * freq - frequency
        * phase - phase of sine curve
        * offset - intercept

        output:  ampl*sin(freq*x + phase) + offset
    """
    return  ampl*np.sin(freq * x + phase) + offset

def harmonics(x,*params):
    """ function f(x) =  $offset + \sum_k s_k sin(freq * n*x) + c_k cos(freq*n)$ for fitting data using scipy.optimize.curve_fit 
    
        input: x (array-like) - independent variable, usually simply range(len(observations))

        parameters: 
        * offset -- intercept
        * freq -- frequency
        * [s_1,c_1,s_2,c_2,...] with s_k = coefficient of sin, c_k coefficient of cos

        output:  offset + \sum_k s_k sin(freq * n*x) + c_k cos(freq*n)
    """

    offset = params[0]
    freq = params[1]
    scoeffs = params[2::2] # coeff sin
    ccoeffs = params[3::2] # coeff cos

    res = offset
    for n in range(len(scoeffs)):
        res += scoeffs[n] * np.sin((n+1)*freq*x) + ccoeffs[n] * np.cos((n+1)*freq*x)

    return  res

# SCIPY CURVE_FIT

def detect_outliers(Idot : pd.Series, 
                    window_size : int = 120, 
                    step_size : int = 90, 
                    n_sigma : int = 3,
                    method : str = 'harmonic',
                    period : float = 60,
                    n_harmonics : int = 5
                    # p0 = [1,2*np.pi/60,0,0]
                    )->pd.DataFrame:
    """
    input: 
    * Idot : pandas.Series -- normalised panda series containing values of the time derivative of the classical non-perturbative invariant
    * window_size : int -- size of rolling window in minutes (optional, default = 120 minutes)
    * step_size : int -- size of stride in minutes (optional, default = 90 minutes)
    * n_sigma : int -- n-sigma level of confidence 
    * method : str -- which method (function) is used to plot (optional, default = 'harmonics')
    * period : float -- period of the time series data
    * n_harmonics : int -- number of harmonics (optional, default = 5)

    output: pandas.DataFrame of dates (start and end date) of outliers (maneuvers)
    """

    window_size_ = timedelta(minutes=window_size)
    step_size_ = timedelta(minutes=step_size)
              
    start_of_maneuver = []
    end_of_maneuver = []

    steps = len(Idot)//(step_size_.seconds//60) 
    start_date =  Idot.index.min()
    
    if method == 'sin':
        p0 = np.array([Idot.loc[start_date,2*np.pi/period,1,0]])
    elif method == 'harmonic':
        p0 = np.array([Idot.loc[start_date],2*np.pi/period]+list(np.zeros(2*n_harmonics)))

    p0_tmp = p0.copy()

    for n in range(steps):
        start = start_date + n*step_size_
        end = start_date + n*step_size_ + window_size_ 

        if end > Idot.index.max():
            end = Idot.index.max()

        y = Idot.loc[start:end]
        x = np.arange(len(y))

        try:
            if method == 'harmonic':
                fit = curve_fit(harmonics, xdata=x, ydata=y.values,p0=p0_tmp)
                baseline = pd.Series(harmonics(x,*fit[0]),name='baseline',index=y.index)
                p0_tmp = fit[0]
                p0_tmp[-1] = harmonics(step_size,*fit[0]) # set guees_intercept to value f(new start = step size)
            
            elif method == 'sin':
                fit = curve_fit(f, xdata=x, ydata=y.values,p0=p0_tmp)
                baseline = pd.Series(f(x,*fit[0]),name='baseline',index=y.index)
                p0_tmp = fit[0]
                p0_tmp[-1] = f(step_size,*fit[0]) # set guees_intercept to value f(new start = step size)


        except Exception as e:
            print(f'Error in window {start} - {end}. Using previous fit data. -- {e}')
            if method == 'harmonic':
                baseline = pd.Series(harmonics(x,*fit[0]),name='baseline',index=y.index)
            elif method == 'sin':
                baseline = pd.Series(f(x,*fit[0]),name='baseline',index=y.index)

        residuals = y - baseline

        z_score = ( residuals - residuals.mean() ) / residuals.std()
        outliers = z_score[np.abs(z_score) > n_sigma]

        if len(outliers) > 0:
            start_of_maneuver.append(outliers.index[0])
            end_of_maneuver.append(outliers.index[-1])

    return pd.DataFrame(data={'Idot':Idot.name,'start':start_of_maneuver,'end':end_of_maneuver})