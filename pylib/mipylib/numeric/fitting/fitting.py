# coding=utf-8
#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2017-3-9
# Purpose: MeteoInfoLab fitting module
# Note: Jython
#-----------------------------------------------------

from org.meteoinfo.math.fitting import FittingUtil

from mipylib.numeric.miarray import MIArray

__all__ = [
    'power_fit', 'exp_fit','poly_fit','predict'
    ]

def power_fit(x, y, func=False):
    '''
    Power law fitting.
    
    :param x: (*array_like*) x data array.
    :param y: (*array_like*) y data array.
    :param func: (*boolean*) Return fit function (for predict function) or not. Default is ``False``.
    
    :returns: Fitting parameters and function (optional).
    '''
    if isinstance(x, list):
        x = minum.array(x)
    if isinstance(y, list):
        y = minum.array(y)
    r = FittingUtil.powerFit(x.asarray(), y.asarray())
    if func:
        return r[0], r[1], r[2], r[3]
    else:
        return r[0], r[1], r[2]
        
def exp_fit(x, y, func=False):
    '''
    Exponent fitting.
    
    :param x: (*array_like*) x data array.
    :param y: (*array_like*) y data array.
    :param func: (*boolean*) Return fit function (for predict function) or not. Default is ``False``.
    
    :returns: Fitting parameters and function (optional).
    '''
    if isinstance(x, list):
        x = minum.array(x)
    if isinstance(y, list):
        y = minum.array(y)
    r = FittingUtil.expFit(x.asarray(), y.asarray())
    if func:
        return r[0], r[1], r[2], r[3]
    else:
        return r[0], r[1], r[2]
        
def poly_fit(x, y, degree, func=False):
    '''
    Polynomail fitting.
    
    :param x: (*array_like*) x data array.
    :param y: (*array_like*) y data array.
    :param func: (*boolean*) Return fit function (for predict function) or not. Default is ``False``.
    
    :returns: Fitting parameters and function (optional).
    '''
    if isinstance(x, list):
        x = minum.array(x)
    if isinstance(y, list):
        y = minum.array(y)
    r = FittingUtil.polyFit(x.asarray(), y.asarray(), degree)
    if func:
        return r[0], r[1], r[2]
    else:
        return r[0], r[1]
    
def predict(func, x):
    '''
    Predict y value using fitting function and x value.
    
    :param func: (*Fitting function object*) Fitting function.
    :param x: (*float*) x value.
    
    :returns: (*float*) y value.
    '''
    return func.predict(x)