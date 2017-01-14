#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2015-12-23
# Purpose: MeteoInfoLab meteo module
# Note: Jython
#-----------------------------------------------------

from org.meteoinfo.data import ArrayMath
from org.meteoinfo.data.analysis import MeteoMath
import mipylib.numeric.minum as np
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
degCtoK=273.15        # Temperature offset between K and C (deg C)

__all__ = [
    'dewpoint2rh','dry_lapse','ds2uv','dt','equivalent_potential_temperature','h2p',
    'mixing_ratio','moist_lapse','p2h','potential_temperature','qair2rh',
    'saturation_mixing_ratio','tc2tf','tf2tc','uv2ds'
    ]

def uv2ds(u, v):
    '''
    Calculate wind direction and wind speed from U/V.
    
    :param u: (*array_like*) U component of wind field.
    :param v: (*array_like*) V component of wind field.
    
    :returns: Wind direction and wind speed.
    '''
    if isinstance(u, (MIArray, DimArray)):
        r = ArrayMath.uv2ds(u.asarray(), v.asarray())
        return MIArray(r[0]), MIArray(r[1])
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
    if isinstance(d, (MIArray, DimArray)):
        r = ArrayMath.ds2uv(d.asarray(), s.asarray())
        return MIArray(r[0]), MIArray(r[1])
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
        return MIArray(ArrayMath.press2Height(press.asarray()))
    elif isinstance(press, DimArray):
        return DimArray(MIArray(ArrayMath.press2Height(press.asarray())), press.dims, press.fill_value, press.proj)
    else:
        return MeteoMath.press2Height(press)
        
def h2p(height):
    """
    Height to pressure
    
    :param height: (*float*) Height - meter.
    
    :returns: (*float*) Pressure - hPa.
    """
    if isinstance(height, MIArray):
        return MIArray(ArrayMath.height2Press(height.asarray()))
    elif isinstance(height, DimArray):
        return DimArray(MIArray(ArrayMath.height2Press(height.asarray())), height.dims, height.fill_value, height.proj)
    else:
        return MeteoMath.height2Press(height)
        
def tf2tc(tf):
    """
    Fahrenheit temperature to Celsius temperature
        
    tf: DimArray or MIArray or number 
        Fahrenheit temperature - degree f   
        
    return: DimArray or MIArray or number
        Celsius temperature - degree c
    """    
    if isinstance(tf, MIArray):
        return MIArray(ArrayMath.tf2tc(tf.asarray()))
    elif isinstance(tf, DimArray):
        return DimArray(MIArray(ArrayMath.tf2tc(tf.asarray())), tf.dims, tf.fill_value, tf.proj)
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
        return MIArray(ArrayMath.tc2tf(tc.asarray()))
    elif isinstance(tc, DimArray):
        return DimArray(MIArray(ArrayMath.tc2tf(tc.asarray())), tc.dims, tc.fill_value, tc.proj)
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
        return MIArray(ArrayMath.qair2rh(qair.asarray(), temp.asarray(), p))
    elif isinstance(qair, DimArray):
        return DimArray(MIArray(ArrayMath.qair2rh(qair.asarray(), temp.asarray(), p)), qair.dims, qair.fill_value, qair.proj)
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
        return MIArray(ArrayMath.dewpoint2rh(dewpoint.asarray(), temp.asarray()))
    elif isinstance(dewpoint, DimArray):
        return DimArray(MIArray(ArrayMath.dewpoint2rh(dewpoint.asarray(), temp.asarray())), dewpoint.dims, dewpoint.fill_value, dewpoint.proj)
    else:
        return MeteoMath.dewpoint2rh(temp, dewpoint)     

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