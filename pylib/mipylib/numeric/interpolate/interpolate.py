# coding=utf-8
#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2017-3-9
# Purpose: MeteoInfoLab interpolate module
# Note: Jython
#-----------------------------------------------------

from org.meteoinfo.math.interpolate import InterpUtil
from org.meteoinfo.data import ArrayMath, ArrayUtil
from ucar.ma2 import Array

from mipylib.numeric.miarray import MIArray
from mipylib.numeric.dimarray import DimArray

__all__ = [
    'interp1d','interp2d'
    ]

class interp1d(object):
    '''
    Interpolate a 1-D function.
    
    :param x: (*array_like*) A 1-D array of real values.
    :param y: (*array_like*) A N-D array of real values. The length of y along the interpolation 
        axis must be equal to the length of x.
    :param kind: (*boolean*) Specifies the kind of interpolation as a string (‘linear’, 
        ‘cubic’) or as an integer specifying the order of the spline interpolator to use. 
        Default is ‘linear’.
    '''
    def __init__(self, x, y, kind='linear'):        
        if isinstance(x, list):
            x = MIArray(ArrayUtil.array(x))
        if isinstance(y, list):
            y = MIArray(ArrayUtil.array(y))
        self._func = InterpUtil.getInterpFunc(x.asarray(), y.asarray(), kind)

    def __call__(self, x):
        '''
        Evaluate the interpolate vlaues.
        
        :param x: (*array_like*) Points to evaluate the interpolant at.
        '''
        if isinstance(x, list):
            x = MIArray(ArrayUtil.array(x))
        if isinstance(x, (MIArray, DimArray)):
            x = x.asarray()
        r = InterpUtil.evaluate(self._func, x)
        if isinstance(r, float):
            return r
        else:
            return MIArray(r)
            
class interp2d(object):
    '''
    Interpolate over a 2-D grid.
    
    x, y and z are arrays of values used to approximate some function f: z = f(x, y). This class 
    returns a function whose call method uses spline interpolation to find the value of new 
    points.
    
    Note that calling interp2d with NaNs present in input values results in undefined behaviour.
    
    :param x: (*array_like*) A 1-D array of real values.
    :param y: (*array_like*) A N-D array of real values. The length of y along the interpolation 
        axis must be equal to the length of x.
    :param z: (*array_like*) The values of the function to interpolate at the data points.
    :param kind: (*boolean*) Specifies the kind of interpolation as a string (‘linear’, 
        ‘cubic’) or as an integer specifying the order of the spline interpolator to use. 
        Default is ‘linear’.
    '''
    def __init__(self, x, y, z, kind='linear'):        
        if isinstance(x, list):
            x = MIArray(ArrayUtil.array(x))
        if isinstance(y, list):
            y = MIArray(ArrayUtil.array(y))
        if isinstance(z, list):
            z = MIArray(ArrayUtil.array(z))
        self._func = InterpUtil.getInterpFunc(x.asarray(), y.asarray(), z.asarray(), kind)

    def __call__(self, x, y):
        '''
        Evaluate the interpolate vlaues.
        
        :param x: (*array_like*) X to evaluate the interpolant at.
        :param y: (*array_like*) Y to evaluate the interpolant at.
        '''
        if isinstance(x, list):
            x = MIArray(ArrayUtil.array(x))
        if isinstance(x, (MIArray, DimArray)):
            x = x.asarray()
        if isinstance(y, list):
            y = MIArray(ArrayUtil.array(y))
        if isinstance(y, (MIArray, DimArray)):
            y = y.asarray()
        r = InterpUtil.evaluate(self._func, x, y)
        if isinstance(r, float):
            return r
        else:
            return MIArray(r)