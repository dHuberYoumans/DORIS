import pandas as pd
import numpy as np
import scipy.constants

# CONSTANTS 
M_earth = 5.972E24 # earth mass [kg]
G = scipy.constants.G # grav constant [m^3 s^{-2} kg^{-1}]
mu = G*M_earth # standard grav parameter for m (mass moving object) << M_earth [m^3 s^{-2}] 


# LINEAR ALGEBRA 

def norm(x:np.array) -> np.array:
    """
    (Vectorised) method to compute norm of (column -> shape = (-1,3)) vectors 
    """
    return np.sqrt(np.sum(x*x,axis=1).reshape(-1,1))

def hat(x:np.array) -> np.array:
    """
    (Vectorised) Method to normalise (column -> shape = (-1,3)) vectors  
    """
    return (x / norm(x))

# r AND v VECTORS
def rvec(df)->np.array:
    """
    Computes norm of radial position vector $r$ from DataFrame containing position (x,y,z) and velocity (vx,vy,vz)
    """
    r_vec = df[['x','y','z']].values.reshape(-1,3)

    return r_vec

def vvec(df)->np.array:
    """
    Computes norm of radial position vector $r$ from DataFrame containing position (x,y,z) and velocity (vx,vy,vz)
    """
    v_vec = df[['vx','vy','vz']].values.reshape(-1,3)

    return v_vec

def vrad(df)->np.array:
    """
    Computes radial velocity from DataFrame containing position (x,y,z) and velocity (vx,vy,vz)
    """
    v_vec = vvec(df)
    r_vec = rvec(df)

    r = norm(r_vec)

    v_rad = np.sum(v_vec*r_vec,axis=1).reshape(-1,1) / r

    return v_rad

def vperp(df)->np.array:
    """
    Computes angular velocity from DataFrame containing position (x,y,z) and velocity (vx,vy,vz)
    """
    v_vec = vvec(df)
    v = norm(v_vec)
    v_rad = vrad(df)

    v_perp = np.sqrt(v**2 - v_rad**2)

    return v_perp

# CLASSICAL ORBITAL ELEMENTS

def H(df)->np.array:
    """
    Computes mechanical energy $H$ from DataFrame containing position (x,y,z) and velocity (vx,vy,vz)
    """
    r_vec = df[['x','y','z']].values.reshape(-1,3)
    v_vec = df[['vx','vy','vz']].values.reshape(-1,3)

    # idx = r_vec.index

    r = norm(r_vec)
    v = norm(v_vec)
    
    return v**2 / 2 - G*M_earth / r

def hvec(df)->np.array:
    """
    Computes orbital momentum $h$ from DataFrame containing position (x,y,z) and velocity (vx,vy,vz)
    """
    r_vec = df[['x','y','z']].values.reshape(-1,3)
    v_vec = df[['vx','vy','vz']].values.reshape(-1,3)

    return np.cross(r_vec,v_vec)

def h(df) -> np.array:
    """
    Computes norm of orbital momentum $|h|$ from DataFrame containing position (x,y,z) and velocity (vx,vy,vz)
    """
    h_vec = hvec(df)

    return norm(h_vec)

def a(df):
    """
    Computes semi-major axis $a$ from DataFrame containing position (x,y,z) and velocity (vx,vy,vz)
    """

    return - (G*M_earth) / (2 * H(df))

def Avec(df):
    """
    Computes the (scaled) Runge-Lenz vector $A$ from DataFrame containing position (x,y,z) and velocity (vx,vy,vz)
    """
    r_vec = df[['x','y','z']].values.reshape(-1,3)
    v_vec = df[['vx','vy','vz']].values.reshape(-1,3)
    h_vec = hvec(df)

    A_vec = np.cross(v_vec,h_vec) / mu - hat(r_vec)
    return A_vec

def e(df): # df.values.shape = (-1,)
    e_sq = 1 + 2 * H(df) * h(df)**2 / (G*M_earth)**2

    return np.sqrt(e_sq)

def i(df):
    """
    Computes inclanatio $i$ from DataFrame containing position (x,y,z) and velocity (vx,vy,vz)
    """
    h_hat_z = hat(hvec(df))[:,-1]

    return np.arccos(h_hat_z).reshape(-1,1)

def RAAN_vec(df):
    """
    Computes the the Right Ascension of the Ascending Node $N$ from DataFrame containing position (x,y,z) and velocity (vx,vy,vz)
    """
    h_vec = hvec(df)

    N_vec =  np.cross([[0,0,1]]*h_vec.shape[0],h_vec)

    return N_vec

def Omega(df):
    """
    Computes the longitude of the ascending node $\Omega$ from DataFrame containing position (x,y,z) and velocity (vx,vy,vz)
    """
    N_hat = hat(RAAN_vec(df))
    N_hat_x = N_hat[:,0]
    N_hat_y = N_hat[:,1]

    Omega_ = np.zeros_like(N_hat_x) # create Omega data frame of same length as N
    Omega_[(N_hat_y < 0)] = 2*np.pi - np.arccos(N_hat_x[(N_hat_y < 0)]) # populate Omega where Ny < 0
    Omega_[(N_hat_y >= 0)] = np.arccos(N_hat_x[(N_hat_y >= 0)]) # populate Omega where Ny >= 0

    return Omega_.reshape(-1,1)

def omega(df):
    """
    Computes the argument of periapsis $\omega$ from DataFrame containing position (x,y,z) and velocity (vx,vy,vz)
    """
    r_vec = df[['x','y','z']].values.reshape(-1,3)
    v_vec = df[['vx','vy','vz']].values.reshape(-1,3)

    e_hat = hat(np.cross(v_vec,hvec(df)) / (G*M_earth) - hat(r_vec))

    if any(i(df) < 1E-9):
        e_vec = Avec(df)
        ex = e_vec[:,1]
        ey = e_vec[:,2]
        arg_eN = np.arctan(ey/ex)
    else:
        N_hat = hat(RAAN_vec(df))

        arg_eN = np.sum(e_hat*N_hat,axis=1) # arg_eN = arccos( e*N / |e| |N| ) = angle between e and N

    this_omega = np.zeros_like(arg_eN) # create omega data frame of same length as e

    this_omega[(e_hat[:,-1]<0)] = 2*np.pi - arg_eN[(e_hat[:,-1]<0)] # populate omega where ez < 0
    this_omega[(e_hat[:,-1]>=0)] = arg_eN[(e_hat[:,-1]>=0)] # populate omega where ez >= 0

    return this_omega.reshape(-1,1)

def nu(df):
    """
    Computes the true anomaly $\nu$ from DataFrame containing position (x,y,z) and velocity (vx,vy,vz)
    """
    r_vec = df[['x','y','z']].values.reshape(-1,3)

    return np.arccos(p(df) / norm(r_vec) - 1)


# MEAN ORBITAL ELEMENTS
   
def E(df):
    """
    Computes the mean eccentric anomaly $E$ from DataFrame containing position (x,y,z) and velocity (vx,vy,vz)
    """

    return np.arctan(2*np.sqrt(((1 - e(df)) / (1 + e(df))))*np.tan(0.5*nu(df)))


def M(df):
    """
    Computes the mean anomaly $M$ from DataFrame containing position (x,y,z) and velocity (vx,vy,vz)
    """
    E_ = E(df) # mean eccentric anomaly

    return E_ - e(df)*np.sin(E_)

def n(df):
    """
    Computes the mean motion $n$ from DataFrame containing position (x,y,z) and velocity (vx,vy,vz)
    """
    a_ = a(df) # semi-major axis
    e_ = e(df) # eccentricity 
    b_ = np.sqrt(a_**2 - e_**2) # semi-minor axis
    h_ = h(df) # norm of orbital momentum

    return h_ / (a_*b_)

#  MODIFIED EQUINOCTIAL ORBITAL ELEMENTS (better behaved for i = 0, e = 0)

def p(df):
    """
    Computes semi-latus rectum $p$ from DataFrame containing position (x,y,z) and velocity (vx,vy,vz)
    """
    return a(df)*(1 - e(df)**2)

def f(df):
    """
    Computes $f = e \cos(\omega + \Omega)$ from DataFrame containing position (x,y,z) and velocity (vx,vy,vz)
    """
    e_ = e(df)
    omega_ = omega(df)
    Omega_ = Omega(df)

    if any(e_ < 1E-9):
        return np.zeros_like(df).reshape(-1,1)
    else:
        if any(np.isnan(Omega_)):
            return e_*np.cos(omega_)
        else:
            return e_*np.cos(omega_ + Omega_)

def g(df):
    """
    Computes $g = e \sin(\omega + \Omega)$ from DataFrame containing position (x,y,z) and velocity (vx,vy,vz)
    """
    e_ = e(df)
    omega_ = omega(df)
    Omega_ = Omega(df)

    if any(e_ < 1E-9):
        return np.zeros_like(df).reshape(-1,1)
    else:
        if any(np.isnan(Omega_)):
            return e_*np.sin(omega_)
        else:
            return e_*np.sin(omega_ + Omega_)

def q1(df):
    """
    Computes $q_1 =  \tan(i / 2) \cos(\Omega)$ from DataFrame containing position (x,y,z) and velocity (vx,vy,vz)
    """
    i_ = i(df)

    if any(i_ < 1E-9):
        return np.zeros_like(df).reshape(-1,1)
    else:
        return np.tan( i_ / 2 ) * np.cos(Omega(df))

def q2(df):
    """
    Computes $q_1 =  \tan(i / 2) \cos(\Omega)$ from DataFrame containing position (x,y,z) and velocity (vx,vy,vz)
    """
    i_ = i(df)

    if any(i_ < 1E-9):
        return np.zeros_like(df).reshape(-1,1)
    else:
        return np.tan( i_/ 2 ) * np.sin(Omega(df))

def L(df):
    """
    Computes $L =  \Omega + \omega + nu$ from DataFrame containing position (x,y,z) and velocity (vx,vy,vz)
    """
    return Omega(df) + omega(df) + nu(df)



