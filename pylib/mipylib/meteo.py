#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2015-12-23
# Purpose: MeteoInfoLab meteo module
# Note: Jython
#-----------------------------------------------------

import minum as np

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