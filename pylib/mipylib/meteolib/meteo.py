#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2015-12-23
# Purpose: MeteoInfoLab meteo module
# Note: Jython
#-----------------------------------------------------

from org.meteoinfo.data import ArrayMath
from org.meteoinfo.data.analysis import MeteoMath
import mipylib.numeric as np
from mipylib.numeric.miarray import MIArray
from mipylib.numeric.dimarray import DimArray

P0 = 1000.          #reference pressure for potential temperature (hPa)
R = 8.3144598       #molar gas constant (J / K / mol)
Mw = 18.01528       #Molecular weight of water (g / mol)
Md = 28.9644        #Nominal molecular weight of dry air at the surface of th Earth (g / mol)
Rd = R / Md         #Gas constant for dry air at the surface of the Earth (J (K kg)^-1)
Lv = 2.501e6        #Latent heat of vaporization for liquid water at 0C (J kg^-1)
Cp_d = 1005         #Specific heat at constant pressure for dry air (J kg^-1)
epsilon = Mw / Md
kappa = 0.286
degCtoK=273.15      # Temperature offset between K and C (deg C)
g = 9.8             # Gravitational acceleration (m / s^2)

__all__ = [
    'dewpoint2rh','dry_lapse','ds2uv','equivalent_potential_temperature','h2p',
    'mixing_ratio','moist_lapse','p2h','potential_temperature','qair2rh','rh2dewpoint',
    'saturation_mixing_ratio','tc2tf','tf2tc','uv2ds','pressure_to_height_std',
    'height_to_pressure_std','eof','varimax'
    ]

def uv2ds(u, v):
    '''
    Calculate wind direction and wind speed from U/V.
    
    :param u: (*array_like*) U component of wind field.
    :param v: (*array_like*) V component of wind field.
    
    :returns: Wind direction and wind speed.
    '''
    if isinstance(u, MIArray):
        r = ArrayMath.uv2ds(u.asarray(), v.asarray())
        d = MIArray(r[0])
        s = MIArray(r[1])
        if isinstance(u, DimArray) and isinstance(v, DimArray):
            d = DimArray(d, u.dims, u.fill_value, u.proj)
            s = DimArray(s, u.dims, u.fill_value, u.proj)
        return d, s
    else:
        r = ArrayMath.uv2ds(u, v)
        return r[0], r[1]
        
def ds2uv(d, s):
    '''
    Calculate U/V from wind direction and wind speed.
    
    :param d: (*array_like*) Wind direction.
    :param s: (*array_like*) Wind speed.
    
    :returns: Wind U/V.
    '''
    if isinstance(d, MIArray):
        r = ArrayMath.ds2uv(d.asarray(), s.asarray())
        u = MIArray(r[0])
        v = MIArray(r[1])
        if isinstance(d, DimArray) and isinstance(s, DimArray):
            u = DimArray(u, d.dims, d.fill_value, d.proj)
            v = DimArray(v, d.dims, d.fill_value, d.proj)
        return u, v
    else:
        r = ArrayMath.ds2uv(d, s)
        return r[0], r[1]
        
def p2h(press):
    """
    Pressure to height
    
    :param press: (*float*) Pressure - hPa.
    
    :returns: (*float*) Height - meter.
    """
    if isinstance(press, MIArray):
        r = MIArray(ArrayMath.press2Height(press.asarray()))
        if isinstance(press, DimArray):
            r = DimArray(r, press.dims, press.fill_value, press.proj)
        return r
    else:
        return MeteoMath.press2Height(press)
        
def pressure_to_height_std(press):
    """
    Convert pressure data to heights using the U.S. standard atmosphere.
    
    :param press: (*float*) Pressure - hPa.
    
    :returns: (*float*) Height - meter.
    """
    t0 = 288.
    gamma = 6.5
    p0 = 1013.25
    h = (t0 / gamma) * (1 - (press / p0)**(Rd * gamma / g)) * 1000
    return h
        
def h2p(height):
    """
    Height to pressure
    
    :param height: (*float*) Height - meter.
    
    :returns: (*float*) Pressure - hPa.
    """
    if isinstance(height, MIArray):
        r = MIArray(ArrayMath.height2Press(height.asarray()))
        if isinstance(height, DimArray):
            r = DimArray(r, height.dims, height.fill_value, height.proj)
        return r
    else:
        return MeteoMath.height2Press(height)
        
def height_to_pressure_std(height):
    """
    Convert height data to pressures using the U.S. standard atmosphere.
    
    :param height: (*float*) Height - meter.
    
    :returns: (*float*) Height - meter.
    """
    t0 = 288.
    gamma = 6.5
    p0 = 1013.25
    height = height * 0.001
    p = p0 * (1 - (gamma / t0) * height) ** (g / (Rd * gamma))
    return p
        
def tf2tc(tf):
    """
    Fahrenheit temperature to Celsius temperature
        
    tf: DimArray or MIArray or number 
        Fahrenheit temperature - degree f   
        
    return: DimArray or MIArray or number
        Celsius temperature - degree c
    """    
    if isinstance(tf, MIArray):
        r = MIArray(ArrayMath.tf2tc(tf.asarray()))
        if isinstance(tf, DimArray):
            r = DimArray(r, tf.dims, tf.fill_value, tf.proj)
        return r
    else:
        return MeteoMath.tf2tc(tf)
        
def tc2tf(tc):
    """
    Celsius temperature to Fahrenheit temperature
        
    tc: DimArray or MIArray or number 
        Celsius temperature - degree c    
        
    return: DimArray or MIArray or number
        Fahrenheit temperature - degree f
    """    
    if isinstance(tc, MIArray):
        r = MIArray(ArrayMath.tc2tf(tc.asarray()))
        if isinstance(tc, DimArray):
            r = DimArray(r, tc.dims, tc.fill_value, tc.proj)
        return r
    else:
        return MeteoMath.tc2tf(tc)

def qair2rh(qair, temp, press=1013.25):
    """
    Specific humidity to relative humidity
        
    qair: DimArray or MIArray or number 
        Specific humidity - dimensionless (e.g. kg/kg) ratio of water mass / total air mass
    temp: DimArray or MIArray or number
        Temperature - degree c
    press: DimArray or MIArray or number
        Pressure - hPa (mb)
    
    return: DimArray or MIArray or number
        Relative humidity - %
    """    
    if isinstance(press, MIArray) or isinstance(press, DimArray):
        p = press.asarray()
    else:
        p = press
    if isinstance(qair, MIArray):
        r = MIArray(ArrayMath.qair2rh(qair.asarray(), temp.asarray(), p))
        if isinstance(qair, DimArray):
            r = DimArray(r, qair.dims, qair.fill_value, qair.proj)
        return r
    else:
        return MeteoMath.qair2rh(qair, temp, press)
        
def dewpoint2rh(dewpoint, temp):    
    """
    Dew point to relative humidity
        
    dewpoint: DimArray or MIArray or number 
        Dew point - degree c
    temp: DimArray or MIArray or number
        Temperature - degree c
        
    return: DimArray or MIArray or number
        Relative humidity - %
    """    
    if isinstance(dewpoint, MIArray):
        r = MIArray(MeteoMath.dewpoint2rh(dewpoint.asarray(), temp.asarray()))
        if isinstance(dewpoint, DimArray):
            r = DimArray(r, dewpoint.dims, dewpoint.fill_value, dewpoint.proj)
        return r
    else:
        return MeteoMath.dewpoint2rh(temp, dewpoint)     
        
def rh2dewpoint(rh, temp):    
    """
    Calculate dewpoint from relative humidity and temperature
        
    rh: DimArray or MIArray or number 
        Relative humidity - %
    temp: DimArray or MIArray or number
        Temperature - degree c
        
    return: DimArray or MIArray or number
        Relative humidity - %
    """    
    if isinstance(rh, MIArray):
        r = MIArray(MeteoMath.rh2dewpoint(rh.asarray(), temp.asarray()))
        if isinstance(rh, DimArray):
            r = DimArray(r, rh.dims, rh.fill_value, rh.proj)
        return r
    else:
        return MeteoMath.rh2dewpoint(rh, temp)     

def potential_temperature(pressure, temperature):
    """
    Calculate the potential temperature.
    Uses the Poisson equation to calculation the potential temperature
    given `pressure` and `temperature`.
    Parameters
    ----------
    pressure : array_like
        The total atmospheric pressure
    temperature : array_like
        The temperature
    Returns
    -------
    array_like
        The potential temperature corresponding to the the temperature and
        pressure.
    See Also
    --------
    dry_lapse
    Notes
    -----
    Formula:
    .. math:: \Theta = T (P_0 / P)^\kappa
    Examples
    --------
    >>> from metpy.units import units
    >>> metpy.calc.potential_temperature(800. * units.mbar, 273. * units.kelvin)
    290.9814150577374
    """

    return temperature * (P0 / pressure)**kappa

def dry_lapse(pressure, temperature):
    """
    Calculate the temperature at a level assuming only dry processes
    operating from the starting point.
    This function lifts a parcel starting at `temperature`, conserving
    potential temperature. The starting pressure should be the first item in
    the `pressure` array.
    Parameters
    ----------
    pressure : array_like
        The atmospheric pressure level(s) of interest
    temperature : array_like
        The starting temperature
    Returns
    -------
    array_like
       The resulting parcel temperature at levels given by `pressure`
    See Also
    --------
    moist_lapse : Calculate parcel temperature assuming liquid saturation
                  processes
    parcel_profile : Calculate complete parcel profile
    potential_temperature
    """

    return temperature * (pressure / pressure[0])**kappa
    
def moist_lapse(pressure, temperature):
    """
    Calculate the temperature at a level assuming liquid saturation processes
    operating from the starting point.
    This function lifts a parcel starting at `temperature`. The starting
    pressure should be the first item in the `pressure` array. Essentially,
    this function is calculating moist pseudo-adiabats.
    Parameters
    ----------
    pressure : array_like
        The atmospheric pressure level(s) of interest
    temperature : array_like
        The starting temperature
    Returns
    -------
    array_like
       The temperature corresponding to the the starting temperature and
       pressure levels.
    See Also
    --------
    dry_lapse : Calculate parcel temperature assuming dry adiabatic processes
    parcel_profile : Calculate complete parcel profile
    Notes
    -----
    This function is implemented by integrating the following differential
    equation:
    .. math:: \frac{dT}{dP} = \frac{1}{P} \frac{R_d T + L_v r_s}
                                {C_{pd} + \frac{L_v^2 r_s \epsilon}{R_d T^2}}
    This equation comes from [1]_.
    References
    ----------
    .. [1] Bakhshaii, A. and R. Stull, 2013: Saturated Pseudoadiabats--A
           Noniterative Approximation. J. Appl. Meteor. Clim., 52, 5-15.
    """

    def dt(t, p):
        rs = saturation_mixing_ratio(p, t)
        frac = ((Rd * t + Lv * rs) /
                (Cp_d + (Lv * Lv * rs * epsilon / (Rd * t * t)))).to('kelvin')
        return frac / p
    return dt
                                    
def mixing_ratio(part_press, tot_press):
    """
    Calculates the mixing ratio of gas given its partial pressure
    and the total pressure of the air.
    There are no required units for the input arrays, other than that
    they have the same units.
    Parameters
    ----------
    part_press : array_like
        Partial pressure of the constituent gas
    tot_press : array_like
        Total air pressure
    Returns
    -------
    array_like
        The (mass) mixing ratio, dimensionless (e.g. Kg/Kg or g/g)
    See Also
    --------
    vapor_pressure
    """

    return epsilon * part_press / (tot_press - part_press)

def saturation_mixing_ratio(tot_press, temperature):
    """
    Calculates the saturation mixing ratio given total pressure
    and the temperature.
    The implementation uses the formula outlined in [4]
    Parameters
    ----------
    tot_press: array_like
        Total atmospheric pressure
    temperature: array_like
        The temperature
    Returns
    -------
    array_like
        The saturation mixing ratio, dimensionless
    References
    ----------
    .. [4] Hobbs, Peter V. and Wallace, John M., 1977: Atmospheric Science, an Introductory
            Survey. 73.
    """

    return mixing_ratio(saturation_vapor_pressure(temperature), tot_press)

def equivalent_potential_temperature(pressure, temperature):
    """
    Calculates equivalent potential temperature given an air parcel's
    pressure and temperature.
    The implementation uses the formula outlined in [5]
    Parameters
    ----------
    pressure: array_like
        Total atmospheric pressure
    temperature: array_like
        The temperature
    Returns
    -------
    array_like
        The corresponding equivalent potential temperature of the parcel
    Notes
    -----
    .. math:: \Theta_e = \Theta e^\frac{L_v r_s}{C_{pd} T}
    References
    ----------
    .. [5] Hobbs, Peter V. and Wallace, John M., 1977: Atmospheric Science, an Introductory
            Survey. 78-79.
    """

    pottemp = potential_temperature(pressure, temperature)
    smixr = saturation_mixing_ratio(pressure, temperature)
    return pottemp * np.exp(Lv * smixr / (Cp_d * temperature))
    
def eof(x, svd=False, transform=False):
    '''
    Empirical Orthogonal Function (EOF) analysis to finds both time series and spatial patterns.
    
    :param x: (*array_like*) Input 2-D array with space-time field.
    :param svd: (*boolean*) Using SVD or eigen method.
    :param transform: (*boolean*) Do space-time transform or not. This transform will speed up
        the computation if the space location number is much more than time stamps. Only valid
        when ``svd=False``.
        
    :returns: (EOF, E, PC) EOF: eigen vector 2-D array; E: eigen values 1-D array;
        PC: Principle component 2-D array.
    '''
    has_nan = False
    if x.contains_nan():       #Has NaN value
        valid_idx = np.where(x[:,0]!=np.nan)[0]
        xx = x[valid_idx,:]
        has_nan = True
    else:
        xx = x
        
    m, n = xx.shape    
    if svd:
        U, S, V = np.linalg.svd(xx)
        EOF = U
        C = np.zeros((m, n))
        for i in range(len(S)):
            C[i,i] = S[i]
        PC = np.dot(C, V)
        E = S**2 / n
    else:
        if transform:        
            C = np.dot(xx.T, xx)
            E1, EOF1 = np.linalg.eig(C)
            EOF1 = EOF1[:,::-1]
            E = E1[::-1]
            EOFa = np.dot(xx, EOF1)
            EOF = np.zeros((m,n))
            for i in range(n):
                EOF[:,i] = EOFa[:,i]/np.sqrt(abs(E[i]))
            PC = np.dot(EOF.T, xx)
        else:
            C = np.dot(xx, xx.T) / n
            E, EOF = np.linalg.eig(C)
            PC = np.dot(EOF.T, xx)
            EOF = EOF[:,::-1]
            PC = PC[::-1,:]
            E = E[::-1]
    
    if has_nan:
        _EOF = np.ones(x.shape) * np.nan
        _PC = np.ones(x.shape) * np.nan
        _EOF[valid_idx,:] = -EOF
        _PC[valid_idx,:] = -PC
        return _EOF, E, _PC
    else:
        return EOF, E, PC
    
def varimax(x, normalize=False, tol=1e-10, it_max=1000):
    '''
    Rotate EOFs according to varimax algorithm
    
    :param x: (*array_like*) Input 2-D array.
    :param normalize: (*boolean*) Determines whether or not to normalize the rows or columns
        of the loadings before performing the rotation.
    :param tol: (*float*) Tolerance.
    :param it_max: (*int*) Specifies the maximum number of iterations to do.
    
    :returns: Rotated EOFs and rotate matrix.
    '''
    p, nc = x.shape
    TT = np.eye(nc)
    d = 0
    for i in range(it_max):
        z = np.dot(x, TT)
        B = np.dot(x.T, (z**3 - np.dot(z, np.diag(np.squeeze(np.dot(np.ones((1,p)), (z**2))))) / p))
        U, S, Vh = np.linalg.svd(B)
        TT = np.dot(U, Vh)        
        d2 = d;
        d = np.sum(S)
        # End if exceeded tolerance.
        if d < d2 * (1 + tol):
            break
            
    # Final matrix.
    r = np.dot(x, TT)
    return r, TT