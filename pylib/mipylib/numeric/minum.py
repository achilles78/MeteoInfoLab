#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2014-12-27
# Purpose: MeteoInfo numerical module
# Note: Jython
#-----------------------------------------------------
import os
import sys
import math
import cmath
import datetime
from org.meteoinfo.data import GridData, GridArray, StationData, DataMath, TableData, TimeTableData, ArrayMath, ArrayUtil, TableUtil, DataTypes
from org.meteoinfo.data.meteodata import MeteoDataInfo, Dimension, DimensionType
from org.meteoinfo.data.meteodata.netcdf import NetCDFDataInfo
from org.meteoinfo.data.meteodata.arl import ARLDataInfo
from org.meteoinfo.data.meteodata.bufr import BufrDataInfo
from org.meteoinfo.data.mapdata import MapDataManage
from org.meteoinfo.data.mapdata.geotiff import GeoTiff
from org.meteoinfo.data.analysis import MeteoMath
from org.meteoinfo.geoprocess import GeoComputation
from org.meteoinfo.projection import KnownCoordinateSystems, ProjectionInfo, Reproject
from org.meteoinfo.global import PointD
from org.meteoinfo.shape import ShapeUtil
from org.meteoinfo.legend import BreakTypes
from ucar.nc2 import NetcdfFileWriter
from ucar.ma2 import Array, DataType

import dimarray
import miarray
import mipylib.miutil
from dimarray import PyGridData, DimArray, PyStationData
from miarray import MIArray
import mitable
from mitable import PyTableData
import series
from series import Series

from java.awt import Color
from java.lang import Math, Double
from java.util import Calendar, ArrayList, Date

# Global variables
pi = Math.PI
e = Math.E
inf = Double.POSITIVE_INFINITY
nan = Double.NaN

__all__ = [
    'pi','e','inf','nan','absolute','arange','arange1',    
    'array','asarray','asgridarray','asgriddata','asin','asmiarray','asstationdata',
    'atan','atan2','ave_month','histogram','broadcast_to','cdiff','concatenate',
    'corrcoef','cos','degrees','diag','dim_array','datatable','series','dot','exp','eye','fmax','fmin',
    'griddata','hcurl','hdivg','identity','interp2d',
    'interpn','isgriddata','isstationdata','linregress','linspace','log','log10',
    'logspace','magnitude','maximum','mean','median','meshgrid','minimum','monthname',
    'numasciicol','numasciirow','nonzero','ones','ones_like','pol2cart','polyval','power',
    'project','projectxy','projinfo','radians','readtable','reshape',
    'rolling_mean','rot90','sin','sort','squeeze','argsort','sqrt','std','sum','tan',
    'transpose','trapz','vdot',
    'where','zeros','zeros_like'
    ]

def isgriddata(gdata):
    return isinstance(gdata, PyGridData)
    
def isstationdata(sdata):
    return isinstance(sdata, PyStationData)

def numasciirow(filename):
    '''
    Returns the number of rows in an ASCII file.
    
    :param filename: (*string*) The ASCII file name.
    
    :returns: The number of rows in the file.
    '''
    nrow = ArrayUtil.numASCIIRow(filename)
    return nrow
    
def numasciicol(filename, delimiter=None, headerlines=0):
    '''
    Returns the number of columns in an ASCII file.
    
    :param filename: (*string*) The ASCII file name.
    :param delimiter: (*string*) Field delimiter character. Default is ``None``, means space or tab 
        delimiter.
    :param headerlines: (*int*) Lines to skip at beginning of the file. Default is ``0``.
    
    :returns: The number of columns in the file.
    '''
    ncol = ArrayUtil.numASCIICol(filename, delimiter, headerlines)
    return ncol
        
def asciiread(filename, **kwargs):
    '''
    Read data from an ASCII file.
    
    :param filename: (*string*) The ASCII file name.
    :param delimiter: (*string*) Field delimiter character. Default is ``None``, means space or tab 
        delimiter.
    :param headerlines: (*int*) Lines to skip at beginning of the file. Default is ``0``.
    :param shape: (*string*) Data array dimension shape. Default is ``None``, the file content will
        be readed as one dimension array.
    :param readfirstcol: (*boolean*) Read first column data or not. Default is ``True``.
    
    :returns: (*MIArray*) The data array.
    '''
    delimiter = kwargs.pop('delimiter', None)
    datatype = kwargs.pop('datatype', None)
    headerlines = kwargs.pop('headerlines', 0)
    shape = kwargs.pop('shape', None)
    rfirstcol = kwargs.pop('readfirstcol', True)
    a = ArrayUtil.readASCIIFile(filename, delimiter, headerlines, datatype, shape, rfirstcol)
    return MIArray(a)
        
def readtable(filename, **kwargs):
    '''
    Create table by reading column oriented data from a file.
    
    :param filename: (*string*) File name for reading.
    :param delimiter: (*string*) Variable delimiter character. Default is ``None``, means space or tab 
        delimiter.
    :param format: (*string*) Colomn format of the file. Default is ``None``, means all columns were
        read as string variable. ``%s``: string; ``%i``: integer; ``%f``: float; ``%{yyyyMMdd...}D``: 
        date time.
    :param headerlines: (*int*) Lines to skip at beginning of the file. Default is ``0``. The line
        after the skip lines will be read as variable names of the table. the ``headerlines`` should set
        as ``-1`` if there is no field name line at beginning of the file.
    :param encoding: (*string*) Character encoding scheme associated with the file. Default is ``UTF8``.
    :param varnames: (*string*) Specified variable names for the readed table. Default is ``None``, means
        the variable names should be read from the file.
    :param readvarnames: (*boolean*) Read variable names or not. Default is ``True``.
    :param readrownames: (*boolean*) Read row names or not. Default is ``False``.
        
    :returns: (*PyTableData*) The table.
    '''
    delimiter = kwargs.pop('delimiter', None)
    format = kwargs.pop('format', None)
    headerlines = kwargs.pop('headerlines', 0)
    encoding = kwargs.pop('encoding', 'UTF8')
    readvarnames = kwargs.pop('readvarnames', True)
    readrownames = kwargs.pop('readrownames', False)
    tdata = TableUtil.readASCIIFile(filename, delimiter, headerlines, format, encoding)
    r = PyTableData(tdata)
    varnames = kwargs.pop('colnames', None)
    varnames = kwargs.pop('varnames', varnames)
    if not varnames is None:
        r.setcolnames(varnames)
    return r
    
def geotiffread(filename):
    '''
    Return data array from a GeoTiff data file.
    
    :param filename: (*string*) The GeoTiff file name.
    
    :returns: (*MIArray*) Readed data array.
    '''
    geotiff = GeoTiff(filename)
    geotiff.read()
    r = geotiff.readArray()
    return MIArray(r)

def array(object):
    """
    Create an array.
    
    :param object: (*array_like*) A Jython list or digital object.
                        
    :returns: (*MIArray*) An array object satisfying the specified requirements.
                    
    Examples
    
    ::
    
        >>> array([1,2,3])
        array([1, 2, 3])
        >>> array(25.6)
        array([25.6])
        
    More than one dimensions:
    
    ::
    
        >>> array([[1,2], [3,4]])
        array([[1.0, 2.0]
              [3.0, 4.0]])
    """
    if isinstance(object, DimArray):
        return object.array
    elif isinstance(object, MIArray):
        return object
    return MIArray(ArrayUtil.array(object))
    
def dim_array(a, dims):
    '''
    Create a dimension array (DimArray).
    
    :param a: (*array_like*) Array (MIArray) or data list.
    :param dims: (*list*) List of dimensions.
    
    :returns: (*DimArray*) Dimension array.
    '''
    return DimArray(a, dims)
    
def datatable(data=None):
    '''
    Create a PyTableData object.
    
    :param data: (*TableData*) Table data.
    
    :returns: (*PyTableData*) PyTableData object.
    '''
    return PyTableData(data)
    
def series(data, index=None):
    '''
    One-dimensional array with axis labels (including time series).
        
    :param data: (*array_like*) One-dimensional array data.
    :param index: (*list*) Data index list. Values must be unique and hashable, same length as data.
    '''
    return Series(data, index)
    
def arange(*args):
    """
    Return evenly spaced values within a given interval
    
    Values are generated within the half-open interval ``[start, stop]`` (in other words,
    the interval including *start* but excluding *stop*).
    
    When using a non-integer step, such as 0.1, the results will often not be consistent.
    It is better to use ``linespace`` for these cases.
    
    :param start: (*number, optional*) Start of interval. The interval includes this value.
        The default start value is 0.
    :param stop: (*number*) End of interval. The interval does not include this value,
        except in some cases where *step* is not an integer and floating point round-off
        affects the length of *out*.
    :param step: (*number, optional*) Spacing between values. For any output *out*, this
        is the distance between two adjacent values, ``out[i+1] - out[i]``. The default
        step size is 1. If *step* is specified. *start* must also be given.
    :param dtype: (*dtype*) The type of output array. If dtype is not given, infer the data
        type from the other input arguments.
        
    :returns: (*MIArray*) Array of evenly spaced values.
    
    Examples::
    
        >>> arange(3)
        array([0, 1, 2])
        >>> arange(3,7,2)
        array([3, 5])
    """
    if len(args) == 1:
        start = 0
        stop = args[0]
        step = 1
    elif len(args) == 2:
        start = args[0]
        stop = args[1]
        step = 1
    else:
        start = args[0]
        stop = args[1]
        step = args[2]
    return MIArray(ArrayUtil.arrayRange(start, stop, step))
    
def arange1(start, num=50, step=1):
    """
    Return evenly spaced values within a given interval.
    
    :param start: (*number*) Start of interval. The interval includes this value.
    :param num: (*int*) Number of samples to generate. Default is 50. Must 
        be non-negative.
    :param step: (*number*) Spacing between values. For any output *out*, this
        is the distance between two adjacent values, ``out[i+1] - out[i]``. The default
        step size is 1.
        
    :returns: (*MIArray*) Array of evenly spaced values.
    
    Examples::
    
        >>> arange1(2, 5)
        array([2, 3, 4, 5, 6])
        >>> arange1(2, 5, 0.1)
        array([2.0, 2.1, 2.2, 2.3, 2.4])
    """
    return MIArray(ArrayUtil.arrayRange1(start, num, step))
    
def linspace(start, stop, num=50, endpoint=True, retstep=False, dtype=None):
    """
    Return evenly spaced numbers over a specified interval.

    Returns *num* evenly spaced samples, calculated over the interval [*start, stop*].

    The endpoint of the interval can optionally be excluded.
    
    :param start: (*number*) Start of interval. The interval includes this value.
    :param stop: (*number*) The end value of the sequence, unless endpoint is set to 
        False. In that case, the sequence consists of all but the last of ``num + 1`` 
        evenly spaced samples, so that stop is excluded. Note that the step size changes 
        when endpoint is False.
    :param num: (*int, optional*) Number of samples to generate. Default is 50. Must 
        be non-negative.
    :param endpoint: (*boolean, optional*) If true, stop is the last sample. Otherwise, it is not included. 
        Default is True.
    :param dtype: (*dtype*) The type of output array. If dtype is not given, infer the data
        type from the other input arguments.
        
    :returns: (*MIArray*) Array of evenly spaced values.
    
    Examples::
    
        >>> linspace(2.0, 3.0, num=5)
        array([2.0, 2.25, 2.5, 2.75, 3.0])
        >>> linspace(2.0, 3.0, num=5, endpoint=False)
        array([2.0, 2.25, 2.5, 2.75])
    """
    return MIArray(ArrayUtil.lineSpace(start, stop, num, endpoint))
    
def logspace(start, stop, num=50, endpoint=True, base=10.0, dtype=None):
    """
    Return numbers spaced evenly on a log scale.

    In linear space, the sequence starts at base ** start (*base to the power of start*) and ends with
    base ** stop.
    
    :param start: (*float*) Base ** start is the starting value of the sequence.
    :param stop: (*float*) Base ** stop is the final value of the sequence, unless *endpoint* is False.
        In that case, num + 1 values are spaced over the interval in log-space, of which all but the last
        (a sequence of length num) are returned.
    :param num: (*int, optional*) Number of samples to generate. Default is 50. Must 
        be non-negative.
    :param endpoint: (*boolean, optional*) If true, stop is the last sample. Otherwise, it is not included. 
        Default is True.
    :param base: (*float, optional*) The base of the log space. The step size between the elements in
        ln(samples) / ln(base) (or log_base(samples)) is uniform. Default is 10.0. 
    :param dtype: (*dtype*) The type of output array. If dtype is not given, infer the data
        type from the other input arguments.
        
    :returns: (*MIArray*) Array of evenly spaced values.
    
    Examples::
    
        >>> logspace(2.0, 3.0, num=4)
        array([100.0, 215.4434295785405, 464.1589682991224, 1000.0])
        >>> logspace(2.0, 3.0, num=4, base=2.0)
        array([4.0, 5.0396839219614975, 6.349604557649573, 8.0])
    """
    r = MIArray(ArrayUtil.lineSpace(start, stop, num, endpoint))
    r = pow(base, r)
    return r
    
def zeros(shape, dtype='float'):
    """
    Create a new aray of given shape and type, filled with zeros.

    :param shape: (*int or sequence of ints*) Shape of the new array, e.g., ``(2, 3)`` or ``2``.
    :param dtype: (*data-type, optional*) The desired data-type for the array, including 'int', 
        'float' and 'double'.
        
    :returns: (*MIArray*) Array of zeros with the given shape and dtype.
                    
    Examples::
    
        >>> zeros(5)
        array([0.0, 0.0, 0.0, 0.0, 0.0])
        >>> zeros(5, dtype='int')
        array([0, 0, 0, 0, 0])
        >>> zeros((2, 1))
        array([[0.0]
              [0.0]])
    """
    shapelist = []
    if isinstance(shape, int):
        shapelist.append(shape)
    else:
        shapelist = shape
    return MIArray(ArrayUtil.zeros(shapelist, dtype))
    
def zeros_like(a, dtype=None):
    '''
    Return an array of zeros with the same shape and type as a given array.
    
    :param a: (*array*) The shape and data-type of a define these same attributes of the returned array.
    :param dtype: (*string*) Overrides the data type of the result. Default is ``None``, keep the data
        type of array ``a``.
        
    :returns: Array of zeros with the same shape and type as a.
    '''
    shape = a.shape
    if dtype is None:
        dtype = ArrayUtil.dataTypeString(a.dtype)
    return MIArray(ArrayUtil.zeros(shape, dtype))
    
def ones_like(a, dtype=None):
    '''
    Return an array of ones with the same shape and type as a given array.
    
    :param a: (*array*) The shape and data-type of a define these same attributes of the returned array.
    :param dtype: (*string*) Overrides the data type of the result. Default is ``None``, keep the data
        type of array ``a``.
        
    :returns: Array of ones with the same shape and type as a.
    '''
    shape = a.shape
    if dtype is None:
        dtype = ArrayUtil.dataTypeString(a.dtype)
    return MIArray(ArrayUtil.ones(shape, dtype))
    
def ones(shape, dtype='float'):
    """
    Create a new aray of given shape and type, filled with ones.

    :param shape: (*int or sequence of ints*) Shape of the new array, e.g., ``(2, 3)`` or ``2``.
    :param dtype: (*data-type, optional*) The desired data-type for the array, including 'int', 
        'float' and 'double'.
        
    :returns: (*MIArray*) Array of ones with the given shape and dtype.
                    
    Examples::
    
        >>> ones(5)
        array([1.0, 1.0, 1.0, 1.0, 1.0])
        >>> ones(5, dtype='int')
        array([1, 1, 1, 1, 1])
        >>> ones((2, 1))
        array([[1.0]
              [1.0]])
    """
    shapelist = []
    if isinstance(shape, int):
        shapelist.append(shape)
    else:
        shapelist = shape
    return MIArray(ArrayUtil.ones(shapelist, dtype))
    
def identity(n, dtype='float'):
    '''
    Return the identity array - a square array with ones on the main diagonal.
    
    :param n: (*int*) Number of rows (and columns) in ``n x n`` output.
    :param dtype: (*string*) The desired data-type for the array, including 'int', 
        'float' and 'double'. Default is ``float``.
        
    :returns: (*MIArray*) ``n x n`` array with its main diagonal set to one, and all other elements 0.
    '''
    return MIArray(ArrayUtil.identity(n, dtype))
    
def eye(n, m=None, k=0, dtype='float'):
    '''
    Return a 2-D array with ones on the diagonal and zeros elsewhere.
    
    :param n: (*int*) Number of rows in the output.
    :param m: (*int*) Number of columns in the output. If ``None``, defaults to ``n``.
    :param k: (*int*) Index of the diagonal: 0 (the default) refers to the main diagonal, a positive value 
        refers to an upper diagonal, and a negative value to a lower diagonal.
    :param dtype: (*string*) The desired data-type for the array, including 'int', 
        'float' and 'double'. Default is ``float``.
        
    :returns: (*MIArray*) ``n x n`` array with its main diagonal set to one, and all other elements 0.
    '''
    if m is None:
        m = n
    return MIArray(ArrayUtil.eye(n, m, k, dtype))
    
def diag(v, k=0):
    '''
    Extract a diagonal or construct a diagonal array.
    
    See the more detailed documentation for ``numpy.diagonal`` if you use this
    function to extract a diagonal and wish to write to the resulting array;
    whether it returns a copy or a view depends on what version of numpy you
    are using.
    
    Parameters
    ----------
    v : array_like
        If `v` is a 2-D array, return a copy of its `k`-th diagonal.
        If `v` is a 1-D array, return a 2-D array with `v` on the `k`-th
        diagonal.
    k : int, optional
        Diagonal in question. The default is 0. Use `k>0` for diagonals
        above the main diagonal, and `k<0` for diagonals below the main
        diagonal.
        
    Returns
    -------
    out : ndarray
        The extracted diagonal or constructed diagonal array.
    '''
    if isinstance(v, (list, tuple)):
        v = array(v)
    return MIArray(ArrayUtil.diag(v.asarray(), k))
    
def rand(*args):
    """
    Random values in a given shape.
    
    Create an array of the given shape and propagate it with random samples from a uniform 
        distribution over [0, 1).
    
    :param d0, d1, ..., dn: (*int*) optional. The dimensions of the returned array, should all
        be positive. If no argument is given a single Python float is returned.
        
    :returns: Random values array.
    """
    if len(args) == 0:
        return ArrayUtil.rand()
    elif len(args) == 1:
        return MIArray(ArrayUtil.rand(args[0]))
    else:
        return MIArray(ArrayUtil.rand(args))
        
def absolute(x):
    '''
    Calculate the absolute value element-wise.
    
    :param x: (*array_like*) Input array.
    
    :returns: An array containing the absolute value of each element in x. 
        For complex input, a + ib, the absolute value is \sqrt{ a^2 + b^2 }.
    '''
    if isinstance(x, list):
        x = array(x)
    if isinstance(x, (DimArray, MIArray)):
        return x.abs()
    else:
        return math.abs(x)
    
def sqrt(x):
    """
    Return the positive square-root of an array, element-wise.
    
    :param x: (*array_like*) The values whose square-roots are required.
    
    :returns y: (*array_like*) An array of the same shape as *x*, containing the positive
        square-root of each element in *x*.
        
    Examples::
    
        >>> sqrt([1,4,9])
        array([1.0, 2.0, 3.0])
    """
    if isinstance(x, list):
        return array(x).sqrt()
    elif isinstance(x, (DimArray, MIArray)):
        return x.sqrt()
    else:
        return math.sqrt(x)
        
def power(x1, x2):
    """
    First array elements raised to powers from second array, element-wise.
    
    :param x1: (*array_like*) The bases.
    :param x2: (*array_like*) The exponents.
    
    :returns: (*array_like*) The bases in *x1* raised to the exponents in *x2*.
    """
    if isinstance(x1, list):
        x1 = array(x1)
    if isinstance(x2, list):
        x2 = array(x2)
    if isinstance(x1, (DimArray, MIArray)):
        if isinstance(x2, (DimArray, MIArray)):
            return MIArray(ArrayMath.pow(x1.asarray(), x2.asarray()))
        else:
            return MIArray(ArrayMath.pow(x1.asarray(), x2))
    else:
        if isinstance(x2, (DimArray, MIArray)):
            return MIArray(ArrayMath.pow(x1, x2.asarray()))
        else:
            if isinstance(x1, complex):
                return pow(x1, x2)
            else:
                return math.pow(x1, x2)
    
def degrees(x):
    '''
    Convert radians to degrees.
    
    :param x: (*array_like*) Array in radians.
    
    :returns: (*array_like*) Array in degrees.
    '''
    if isinstance(x, (list, tuple)):
        x = array(x)
    if isinstance(x, (DimArray, MIArray)):
        return MIArray(ArrayMath.toDegrees(x.asarray()))
    else:
        return math.degrees(x)
        
def radians(x):
    '''
    Convert degrees to radians.
    
    :param x: (*array_like*) Array in degrees.
    
    :returns: (*array_like*) Array in radians.
    '''
    if isinstance(x, (list, tuple)):
        x = array(x)
    if isinstance(x, (DimArray, MIArray)):
        return MIArray(ArrayMath.toRadians(x.asarray()))
    else:
        return math.radians(x)

def sin(x):
    """
    Trigonometric sine, element-wise.
    
    :param x: (*array_like*) Angle, in radians.
    
    :returns: (*array_like*) The sine of each element of x.
    
    Examples::
    
        >>> sin(pi/2.)
        1.0
        >>> sin(array([0., 30., 45., 60., 90.]) * pi / 180)
        array([0.0, 0.49999999999999994, 0.7071067811865475, 0.8660254037844386, 1.0])
    """
    if isinstance(x, list):
        return array(x).sin()
    elif isinstance(x, (DimArray, MIArray)):
        return x.sin()
    else:
        if isinstance(x, complex):
            return cmath.sin(x)
        else:
            return math.sin(x)
    
def cos(x):
    """
    Trigonometric cosine, element-wise.
    
    :param x: (*array_like*) Angle, in radians.
    
    :returns: (*array_like*) The cosine of each element of x.
    
    Examples::
    
        >>> cos(array([0, pi/2, pi]))
        array([1.0, 6.123233995736766E-17, -1.0])
    """
    if isinstance(x, list):
        return array(x).cos()
    elif isinstance(x, (DimArray, MIArray)):
        return x.cos()
    else:
        if isinstance(x, complex):
            return cmath.cos(x)
        else:
            return math.cos(x)
        
def tan(x):
    """
    Trigonometric tangent, element-wise.
    
    :param x: (*array_like*) Angle, in radians.
    
    :returns: (*array_like*) The tangent of each element of x.
    
    Examples::
    
        >>> tan(array([-pi,pi/2,pi]))
        array([1.2246467991473532E-16, 1.633123935319537E16, -1.2246467991473532E-16])
    """
    if isinstance(x, list):
        return array(x).tan()
    elif isinstance(x, (DimArray, MIArray)):
        return x.tan()
    else:
        if isinstance(x, complex):
            return cmath.tan(x)
        else:
            return math.tan(x)
        
def asin(x):
    """
    Trigonometric inverse sine, element-wise.
    
    :param x: (*array_like*) *x*-coordinate on the unit circle.
    
    :returns: (*array_like*) The inverse sine of each element of *x*, in radians and in the
        closed interval ``[-pi/2, pi/2]``.
    
    Examples::
    
        >>> asin(array([1,-1,0]))
        array([1.5707964, -1.5707964, 0.0])
    """
    if isinstance(x, list):
        return array(x).asin()
    elif isinstance(x, (DimArray, MIArray)):
        return x.asin()
    else:
        if isinstance(x, complex):
            return cmath.asin(x)
        else:
            return math.asin(x)
        
def acos(x):
    """
    Trigonometric inverse cosine, element-wise.
    
    :param x: (*array_like*) *x*-coordinate on the unit circle. For real arguments, the domain
        is ``[-1, 1]``.
    
    :returns: (*array_like*) The inverse cosine of each element of *x*, in radians and in the
        closed interval ``[0, pi]``.
    
    Examples::
    
        >>> acos([1, -1])
        array([0.0, 3.1415927])
    """
    if isinstance(x, list):
        return array(x).acos()
    elif isinstance(x, (DimArray, MIArray)):
        return x.acos()
    else:
        if isinstance(x, complex):
            return cmath.acos(x)
        else:
            return math.acos(x)
        
def atan(x):
    """
    Trigonometric inverse tangent, element-wise.
    
    The inverse of tan, so that if ``y = tan(x)`` then ``x = atan(y)``.
    
    :param x: (*array_like*) Input values, ``atan`` is applied to each element of *x*.
    
    :returns: (*array_like*) Out has the same shape as *x*. Its real part is in
        ``[-pi/2, pi/2]`` .
    
    Examples::
    
        >>> atan([0, 1])
        array([0.0, 0.7853982])
    """
    if isinstance(x, list):
        return array(x).atan()
    elif isinstance(x, (DimArray, MIArray)):
        return x.atan()
    else:
        if isinstance(x, complex):
            return cmath.atan(x)
        else:
            return math.atan(x)
        
def atan2(x1, x2):
    """
    Element-wise arc tangent of ``x1/x2`` choosing the quadrant correctly.

    :param x1: (*array_like*) *y*-coordinates.
    :param x2: (*array_like*) *x*-coordinates. *x2* must be broadcastable to match the 
        shape of *x1* or vice versa.
        
    :returns: (*array_like*) Array of angles in radians, in the range ``[-pi, pi]`` .
    
    Examples::
    
        >>> x = array([-1, +1, +1, -1])
        >>> y = array([-1, -1, +1, +1])
        >>> atan2(y, x) * 180 / pi
        array([-135.00000398439022, -45.000001328130075, 45.000001328130075, 135.00000398439022])
    """    
    if isinstance(x1, DimArray) or isinstance(x1, MIArray):
        return MIArray(ArrayMath.atan2(x1.asarray(), x2.asarray()))
    else:
        return math.atan2(x1, x2)
        
def exp(x):
    """
    Calculate the exponential of all elements in the input array.
    
    :param x: (*array_like*) Input values.
    
    :returns: (*array_like*) Output array, element-wise exponential of *x* .
    
    Examples::
    
        >>> x = linspace(-2*pi, 2*pi, 10)
        >>> exp(x)
        array([0.0018674424051939472, 0.007544609964764651, 0.030480793298392952, 
            0.12314470389303135, 0.4975139510383202, 2.0099938864286777, 
            8.120527869949177, 32.80754507307142, 132.54495655444984, 535.4917491531113])
    """
    if isinstance(x, list):
        return array(x).exp()
    elif isinstance(x, (DimArray, MIArray)):
        return x.exp()
    else:
        if isinstance(x, complex):
            return cmath.exp(x)
        else:
            return math.exp(x)
        
def log(x):
    """
    Natural logarithm, element-wise.
    
    The natural logarithm log is the inverse of the exponential function, so that 
    *log(exp(x))* = *x* . The natural logarithm is logarithm in base e.
    
    :param x: (*array_like*) Input values.
    
    :returns: (*array_like*) The natural logarithm of *x* , element-wise.
    
    Examples::
    
        >>> log([1, e, e**2, 0])
        array([0.0, 1.0, 2.0, -Infinity])
    """
    if isinstance(x, list):
        return array(x).log()
    elif isinstance(x, (DimArray, MIArray)):
        return x.log()
    else:
        if isinstance(x, complex):
            return cmath.exp(x)
        else:
            return math.log(x)
        
def log10(x):
    """
    Return the base 10 logarithm of the input array, element-wise.
    
    :param x: (*array_like*) Input values.
    
    :returns: (*array_like*) The logarithm to the base 10 of *x* , element-wise.
    
    Examples::
    
        >>> log10([1e-15, -3.])
        array([-15.,  NaN])
    """
    if isinstance(x, list):
        return array(x).log10()
    elif isinstance(x, (DimArray, MIArray)):
        return x.log10()
    else:
        if isinstance(x, complex):
            return cmath.log10(x)
        else:
            return math.log10(x)

def sum(x, axis=None):
    """
    Sum of array elements over a given axis.
    
    :param x: (*array_like or list*) Input values.
    
    returns: (*array_like*) Sum result
    """
    if isinstance(x, list):
        if isinstance(x[0], (MIArray, DimArray)):
            a = []
            for xx in x:
                a.append(xx.asarray())
            r = ArrayMath.sum(a)
            if isinstance(x[0], MIArray):            
                return MIArray(r)
            else:
                return DimArray(MIArray(r), x[0].dims, x[0].fill_value, x[0].proj)
        else:
            x = array(x)
    if axis is None:
        r = ArrayMath.sum(x.asarray())
        return r
    else:
        r = ArrayMath.sum(x.asarray(), axis)
        if isinstance(x, MIArray):
            return MIArray(r)
        else:
            dims = []
            for i in range(0, x.ndim):
                if i != axis:
                    dims.append(x.dims[i])
            return DimArray(MIArray(r), dims, x.fill_value, x.proj)
            
def mean(x, axis=None):
    """
    Compute tha arithmetic mean along the specified axis.
    
    :param x: (*array_like or list*) Input values.
    :param axis: (*int*) Axis along which the standard deviation is computed. 
        The default is to compute the standard deviation of the flattened array.
    
    returns: (*array_like*) Mean result
    """
    if isinstance(x, list):
        if isinstance(x[0], (MIArray, DimArray)):
            a = []
            for xx in x:
                a.append(xx.asarray())
            r = ArrayMath.mean(a)
            if isinstance(x[0], MIArray):            
                return MIArray(r)
            else:
                return DimArray(MIArray(r), x[0].dims, x[0].fill_value, x[0].proj)
        elif isinstance(x[0], PyStationData):
            a = []
            for xx in x:
                a.append(xx.data)
            r = DataMath.mean(a)
            return PyStationData(r)
        else:
            x = array(x)
    if axis is None:
        r = ArrayMath.mean(x.asarray())
        return r
    else:
        r = ArrayMath.mean(x.asarray(), axis)
        if isinstance(x, MIArray):
            return MIArray(r)
        else:
            dims = []
            for i in range(0, x.ndim):
                if i != axis:
                    dims.append(x.dims[i])
            return DimArray(MIArray(r), dims, x.fill_value, x.proj)
            
def std(x, axis=None):
    '''
    Compute the standard deviation along the specified axis.
    
    :param x: (*array_like or list*) Input values.
    :param axis: (*int*) Axis along which the standard deviation is computed. 
        The default is to compute the standard deviation of the flattened array.
    
    returns: (*array_like*) Standart deviation result.
    '''
    if axis is None:
        r = sqrt(mean((x - mean(x))**2))
        return r
    else:
        r = ArrayMath.std(x.asarray(), axis)
        if isinstance(x, MIArray):
            return MIArray(r)
        else:
            dims = []
            for i in range(0, x.ndim):
                if i != axis:
                    dims.append(x.dims[i])
            return DimArray(MIArray(r), dims, x.fill_value, x.proj)
                
def median(x, axis=None):
    """
    Compute tha median along the specified axis.
    
    :param x: (*array_like or list*) Input values.
    
    returns: (*array_like*) Median result
    """
    if isinstance(x, list):
        if isinstance(x[0], (MIArray, DimArray)):
            a = []
            for xx in x:
                a.append(xx.asarray())
            r = ArrayMath.median(a)
            if isinstance(x[0], MIArray):            
                return MIArray(r)
            else:
                return DimArray(MIArray(r), x[0].dims, x[0].fill_value, x[0].proj)
        elif isinstance(x[0], PyStationData):
            a = []
            for xx in x:
                a.append(xx.data)
            r = DataMath.median(a)
            return PyStationData(r)
        else:
            x = array(x)
            r = ArrayMath.median(x.asarray())
            return r
    else:
        if axis is None:
            r = ArrayMath.median(x.asarray())
            return r
        else:
            r = ArrayMath.median(x.asarray(), axis)
            if isinstance(x, MIArray):
                return MIArray(r)
            else:
                dims = []
                for i in range(0, x.ndim):
                    if i != axis:
                        dims.append(x.dims[i])
                return DimArray(MIArray(r), dims, x.fill_value, x.proj)
                
def maximum(x1, x2):
    """
    Element-wise maximum of array elements.
    
    Compare two arrays and returns a new array containing the element-wise maxima. If one of the elements 
    being compared is a NaN, then that element is returned. If both elements are NaNs then the first is 
    returned. The latter distinction is important for complex NaNs, which are defined as at least one of 
    the real or imaginary parts being a NaN. The net effect is that NaNs are propagated.
    
    :param x1,x2: (*array_like*) The arrays holding the elements to be compared. They must have the same 
        shape.
    
    :returns: The maximum of x1 and x2, element-wise. Returns scalar if both x1 and x2 are scalars.
    """
    if isinstance(x1, list):
        x1 = array(x1)
    if isinstance(x2, list):
        x2 = array(x2)
    if isinstance(x1, MIArray):
        return MIArray(ArrayMath.maximum(x1.asarray(), x2.asarray()))
    elif isinstance(x1, DimArray):
        r = MIArray(ArrayMath.maximum(x1.asarray(), x2.asarray()))
        return DimArray(r, x1.dims, x1.fill_value, x1.proj)
    else:
        return max(x1, x2)
        
def fmax(x1, x2):
    """
    Element-wise maximum of array elements.
    
    Compare two arrays and returns a new array containing the element-wise maxima. If one of the 
    elements being compared is a NaN, then the non-nan element is returned. If both elements are 
    NaNs then the first is returned. The latter distinction is important for complex NaNs, which 
    are defined as at least one of the real or imaginary parts being a NaN. The net effect is that 
    NaNs are ignored when possible.
    
    :param x1,x2: (*array_like*) The arrays holding the elements to be compared. They must have the same 
        shape.
    
    :returns: The maximum of x1 and x2, element-wise. Returns scalar if both x1 and x2 are scalars.
    """
    if isinstance(x1, list):
        x1 = array(x1)
    if isinstance(x2, list):
        x2 = array(x2)
    if isinstance(x1, MIArray):
        return MIArray(ArrayMath.fmax(x1.asarray(), x2.asarray()))
    elif isinstance(x1, DimArray):
        r = MIArray(ArrayMath.fmax(x1.asarray(), x2.asarray()))
        return DimArray(r, x1.dims, x1.fill_value, x1.proj)
    else:
        return max(x1, x2)
        
def minimum(x1, x2):
    """
    Element-wise minimum of array elements.
    
    Compare two arrays and returns a new array containing the element-wise minima. If one of the elements 
    being compared is a NaN, then that element is returned. If both elements are NaNs then the first is 
    returned. The latter distinction is important for complex NaNs, which are defined as at least one of 
    the real or imaginary parts being a NaN. The net effect is that NaNs are propagated.
    
    :param x1,x2: (*array_like*) The arrays holding the elements to be compared. They must have the same 
        shape.
    
    :returns: The minimum of x1 and x2, element-wise. Returns scalar if both x1 and x2 are scalars.
    """
    if isinstance(x1, list):
        x1 = array(x1)
    if isinstance(x2, list):
        x2 = array(x2)
    if isinstance(x1, MIArray):
        return MIArray(ArrayMath.minimum(x1.asarray(), x2.asarray()))
    elif isinstance(x1, DimArray):
        r = MIArray(ArrayMath.minimum(x1.asarray(), x2.asarray()))
        return DimArray(r, x1.dims, x1.fill_value, x1.proj)
    else:
        return min(x1, x2)
        
def fmin(x1, x2):
    """
    Element-wise minimum of array elements.
    
    Compare two arrays and returns a new array containing the element-wise minima. If one of the 
    elements being compared is a NaN, then the non-nan element is returned. If both elements are 
    NaNs then the first is returned. The latter distinction is important for complex NaNs, which 
    are defined as at least one of the real or imaginary parts being a NaN. The net effect is that 
    NaNs are ignored when possible.
    
    :param x1,x2: (*array_like*) The arrays holding the elements to be compared. They must have the same 
        shape.
    
    :returns: The minimum of x1 and x2, element-wise. Returns scalar if both x1 and x2 are scalars.
    """
    if isinstance(x1, list):
        x1 = array(x1)
    if isinstance(x2, list):
        x2 = array(x2)
    if isinstance(x1, MIArray):
        return MIArray(ArrayMath.fmin(x1.asarray(), x2.asarray()))
    elif isinstance(x1, DimArray):
        r = MIArray(ArrayMath.fmin(x1.asarray(), x2.asarray()))
        return DimArray(r, x1.dims, x1.fill_value, x1.proj)
    else:
        return min(x1, x2)

def ave_month(data, colnames, t):
    """
    Average data month by month.
    
    :param data: (*list of Array*) Data array list.
    :param colnames: (*list of string*) Column name list.
    :param t: (*list of datetime*) Datetime list.
    
    :returns: (*PyTableData*) Averaged table data.
    """
    jt = miutil.jdate(t)
    if isinstance(data, MIArray):
        a = [data.asarray()]
    else:
        a = []
        for d in data:
            a.append(d.asarray())
    r = TableUtil.ave_Month(a, colnames, jt)
    return PyTableData(TableData(r))
    
def histogram(a, bins=10):
    '''
    Compute the histogram of a set of data.
    
    :param a: (*array_like*) Input data. The histogram is computed over the flattened array.
    :param bins: (*int or list*) If bins is an int, it defines the number of equal-width bins in the given 
        range (10, by default). If bins is a sequence, it defines the bin edges, including the rightmost edge, allowing for non-uniform bin widths.
    
    :returns: The values of the histogram (hist) and the bin edges (length(hist)+1).
    '''
    if isinstance(a, list):
        a = array(a)
    if isinstance(bins, list):
        bins = array(bins)
    r = ArrayUtil.histogram(a.asarray(), bins.asarray())
    return MIArray(r[0]), MIArray(r[1])
                
def sort(a, axis=-1):
    """
    Returns the indices that would sort an array.
    
    :param a: (*array_like*) Array to be sorted.
    :param axis: (*int or None*) Optional. Axis along which to sort. If None, the array is
        flattened after sorting. The default is ``-1`` , which sorts along the last axis.
        
    :returns: (*MIArray*) Sorted array.
    """
    if isinstance(a, list):
        a = array(a)
    r = ArrayUtil.sort(a.asarray(), axis)
    return MIArray(r)
    
def argsort(a, axis=-1):
    """
    Return a sorted copy of an array.
    
    :param a: (*array_like*) Array to be sorted.
    :param axis: (*int or None*) Optional. Axis along which to sort. If None, the array is
        flattened after sorting. The default is ``-1`` , which sorts along the last axis.
        
    :returns: (*MIArray*) Array of indices that sort a along the specified axis. If a is 
        one-dimensional, a[index_array] yields a sorted a.
    """
    if isinstance(a, list):
        a = array(a)
    r = ArrayUtil.argSort(a.asarray(), axis)
    return MIArray(r)
    
def nonzero(a):
    '''
    Return the indices of the elements that are non-zero.
    
    Returns a tuple of arrays, one for each dimension of a, containing the indices of the 
    non-zero elements in that dimension.
        
    :param a: (*array_like*) Input array.
    
    :returns: (*tuple*) Indices of elements that are non-zero.
    '''
    if isinstance(a, list):
        a = array(a)
    ra = ArrayMath.nonzero(a.asarray())
    if ra is None:
        return None
        
    r = []
    for aa in ra:
        r.append(MIArray(aa))
    return tuple(r)
    
def where(condition):
    '''
    Return elements, either from x or y, depending on condition.

    If only condition is given, return condition.nonzero().
    
    :param condition: (*array_like*) Input array.
    
    :returns: (*tuple*) Indices of elements that are non-zero.
    '''
    return nonzero(condition)
    
def concatenate(arrays, axis=0):
    '''
    Join a sequence of arrays along an existing axis.
    
    :param arrays: (list of arrays) The arrays must have the same shape, except in the dimension 
        corresponding to axis (the first, by default).
    :param axis: (*int*) The axis along which the arrays will be joined. Default is 0.
    
    :returns: (*array_like*) The concatenated array.
    '''
    ars = []
    for a in arrays:
        ars.append(a.asarray())
    r = ArrayUtil.concatenate(ars, axis)
    return MIArray(r)
                
def dot(a, b):
    """
    Matrix multiplication.
    
    :param a: (*2D Array*) Matrix a.
    :param b: (*2D Array*) Matrix b.
    
    :returns: Result Matrix.
    """
    if isinstance(a, (int, long, float, complex)) and isinstance(b, (int, long, float, complex)):
        return a * b
        
    if isinstance(a, list):
        a = array(a)
    if isinstance(b, list):
        b = array(b)
    r = ArrayMath.dot(a.asarray(), b.asarray())
    return MIArray(r)
    
def vdot(a, b):
    '''
    Return the dot product of two vectors.
    
    Note that ``vdot`` handles multidimensional arrays differently than dot: it does not 
    perform a matrix product, but flattens input arguments to 1-D vectors first. 
    Consequently, it should only be used for vectors.
    
    :param a: (*array_like*) First argument to the dot product.
    :param b: (*array_like*) Second argument to the dot product.
    
    :returns: (*float*) Dot product of ``a`` and ``b``.    
    '''
    if isinstance(a, list):
        a = array(a)
    if isinstance(b, list):
        b = array(b)
    if a.ndim > 1:
        a = a.flatten()
    if b.ndim > 1:
        b = b.flatten()
    return ArrayMath.vdot(a.asarray(), b.asarray())
        
def reshape(a, *args):
    """
    Gives a new shape to an array without changing its data.
    
    :param a: (*array_like*) Array to be reshaped.
    :param shape: (*int or tuple of ints*) The new shape should be compatible with the original 
        shape. If an integer, then the result will be a 1-D array of that length. One shape 
        dimension can be -1. In this case, the value is inferred from the length of the array and 
        remaining dimensions.
        
    :returns: Reshaped array.
    """
    return a.reshape(*args)
    
def squeeze(a):
    '''
    Remove single-dimensional entries from the shape of an array.
    
    :param a: (*array_like*) Input data array.
    
    :returns: (*array_like*) The input array, but with all or a subset of the dimensions of length 1 
        removed.
    '''
    da = a.asarray()
    da = da.reduce()
    if isinstance(a, MIArray):
        return MIArray(da)
    else:
        dims = []
        for dim in a.dims:
            if dim.getLength() > 1:
                dims.append(dim)
        return DimArray(MIArray(da), dims, a.fill_value, a.proj)
        
def meshgrid(x, y):
    '''
    Returns 2-D grid coordinates based on the coordinates contained in vectors x and y. is a matrix 
    where each row is a copy of x, and Y is a matrix where each column is a copy of y. The grid 
    represented by the coordinates X and Y has length(y) rows and length(x) columns.

    :param x: (*array_like*) 1-D array representing the x coordinate of a grid. 
    :param y: (*array_like*) 1-D array representing the y coordinate of a grid.
    
    :returns X, Y: 2-D array. 2-D arrays.
    '''
    if isinstance(x, list):
        x = array(x)
    if isinstance(y, list):
        y = array(y)
        
    if x.ndim != 1 or y.ndim != 1:
        print 'The paramters must be vector arrays!'
        return None
        
    xa = x.asarray()
    ya = y.asarray()
    ra = ArrayUtil.meshgrid(xa, ya)
    return MIArray(ra[0]), MIArray(ra[1])
    
def broadcast_to(a, shape):
    """
    Broadcast an array to a new shape.
    
    :param a: (*array_like*) The array to broadcast.
    :param shape: (*tuple*) The shape of the desired array.
    
    :returns: (*MIArray*) A readonly view on the original array with the given shape.
    """
    if isinstance(a, list):
        a = array(a)
    r = ArrayUtil.broadcast(a.asarray(), shape)
    if r is None:
        raise ValueError('Can not broadcast to the shape!')
    return MIArray(r)
    
def corrcoef(x, y):
    """
    Return Pearson product-moment correlation coefficients.
    
    :param x: (*array_like*) A 1-D or 2-D array containing multiple variables and observations. 
        Each row of x represents a variable, and each column a single observation of all those 
        variables.
    :param y: (*array_like*) An additional set of variables and observations. y has the same 
        shape as x.
        
    :returns: The correlation coefficient matrix of the variables.
    """
    if isinstance(x, list):
        x = array(x)
    if isinstance(y, list):
        y = array(y)
    a = ArrayMath.getR(x.asarray(), y.asarray())
    b = ArrayMath.getR(y.asarray(), x.asarray())
    r = array([[1, a], [b, 1]])
    return r
        
def linregress(x, y):
    '''
    Calculate a linear least-squares regression for two sets of measurements.
    
    :param x, y: (*array_like*) Two sets of measurements. Both arrays should have the same length.
    
    :returns slope, intercept, rvalue, pvalue, dnum: Result slope, intercept, relative coefficient,
        two-sided p-value for a hypothesis test whose null hypothesis is that the slope is zero, validate
        data number (remove NaN values).
    '''
    if isinstance(x, list):
        x = array(x)
    if isinstance(y, list):
        y = array(y)
    r = ArrayMath.lineRegress(x.asarray(), y.asarray())
    return r[0], r[1], r[2], r[3], r[4]
    
def polyval(p, x):
    """
    Evaluate a polynomial at specific values.
    
    If p is of length N, this function returns the value:
    
    p[0]*x**(N-1) + p[1]*x**(N-2) + ... + p[N-2]*x + p[N-1]
    
    If x is a sequence, then p(x) is returned for each element of x. If x is another polynomial then the 
    composite polynomial p(x(t)) is returned.
    
    :param p: (*array_like*) 1D array of polynomial coefficients (including coefficients equal to zero) 
        from highest degree to the constant term.
    :param x: (*array_like*) A number, an array of numbers, or an instance of poly1d, at which to evaluate 
        p.
        
    :returns: Polynomial value
    """
    return MIArray(ArrayMath.polyVal(p, x.asarray()))
    
def transpose(a, dim1=0, dim2=1):
    '''
    Transpose 2-D array.
    
    :param a: (*array*) 2-D array to be transposed.
    
    :returns: Transposed array.
    '''
    r = ArrayMath.transpose(a.asarray(), dim1, dim2)
    if isinstance(a, MIArray):
        return MIArray(r)
    else:
        dims = []
        for i in range(0, len(a.dims)):
            if i == dim1:
                dims.append(a.dims[dim2])
            elif i == dim2:
                dims.append(a.dims[dim1])
            else:
                dims.append(a.dims[i])
        return DimArray(MIArray(r), dims, a.fill_value, a.proj) 
        
def rot90(a, k=1):
    """
    Rotate an array by 90 degrees in the counter-clockwise direction. The first two dimensions
    are rotated if the array has more than 2 dimensions.
    
    :param a: (*array_like*) Array for rotate.
    :param k: (*int*) Number of times the array is rotated by 90 degrees
    
    :returns: (*array_like*) Rotated array.
    """
    r = ArrayMath.rot90(a.asarray(), k)
    if isinstance(a, MIArray):
        return MIArray(r)
    else:
        dims = []
        if Math.abs(k) == 1 or Math.abs(k) == 3:
            dims.append(a.dims[1])
            dims.append(a.dims[0])
            for i in range(2, len(a.dims)):            
                dims.append(a.dims[i])
        else:
            for i in range(0, len(a.dims)):
                dims.append(a.dims[i])
        return DimArray(MIArray(r), dims, a.fill_value, a.proj) 
        
def trapz(y, x=None, dx=1.0, axis=-1):
    """
    Integrate along the given axis using the composite trapezoidal rule.
    
    :param y: (*array_like*) Input array to integrate.
    :param x: (*array_like*) Optional, If x is None, then spacing between all y elements is dx.
    :param dx: (*scalar*) Optional, If x is None, spacing given by dx is assumed. Default is 1.
    :param axis: (*int*) Optional, Specify the axis.
    
    :returns: Definite integral as approximated by trapezoidal rule.
    """
    if isinstance(y, list):
        y = array(y)
    
    if y.ndim == 1:
        if x is None:
            r = ArrayMath.trapz(y.asarray(), dx)
        else:
            if isinstance(x, list):
                x = array(x)
            r = ArrayMath.trapz(y.asarray(), x.asarray())
        return r
    else:
        if axis == -1:
            shape = y.shape
            for i in range(y.ndim):
                if shape[i] > 1:
                    axis = i
                    break
        if x is None:
            r = ArrayMath.trapz(y.asarray(), dx, axis)
        else:
            if isinstance(x, list):
                x = array(x)
            r = ArrayMath.trapz(y.asarray(), x.asarray(), axis)
        if isinstance(y, MIArray):
            return MIArray(r)
        else:
            dims = []
            for i in range(0, y.ndim):
                if i != axis:
                    dims.append(y.dims[i])
            return DimArray(MIArray(r), dims, y.fill_value, y.proj)
            
def rolling_mean(x, window, center=False):
    '''
    Moving average function
    
    :param x: (*array_like*) Input data array. Must be vector (one dimension).
    :param window: (*int*) Size of the moving window.
    :param center: (*boolean*) Set the labels at the center of the window. Default is ``False``.
    
    :returns: (*array_like*) Moving averaged array.
    '''
    if isinstance(x, list):
        x = array(x)
    r = ArrayMath.rolling_mean(x.asarray(), window, center)
    return MIArray(r)  

# Performs a centered difference operation on a array in a specific direction    
def cdiff(a, dimidx):
    '''
    Performs a centered difference operation on a array in a specific direction
    
    :param a: (*array*) The input array.
    :param dimidx: (*int*) Demension index of the specific direction.
    
    :returns: Result array.
    '''
    if isinstance(a, DimArray):
        r = ArrayMath.cdiff(a.asarray(), dimidx)
        return DimArray(MIArray(r), a.dims, a.fill_value, a.proj)
    else:
        return MIArray(ArrayMath.cdiff(a.asarray(), dimidx))

# Calculates the vertical component of the curl (ie, vorticity)    
def hcurl(u, v):
    '''
    Calculates the vertical component of the curl (ie, vorticity). The data should be lon/lat projection.
    
    :param u: (*array*) U component array.
    :param v: (*array*) V component array.
    
    :returns: Array of the vertical component of the curl.
    '''
    if isinstance(u, DimArray) and isinstance(v, DimArray):
        ydim = u.ydim()
        xdim = u.xdim()
        r = ArrayMath.hcurl(u.asarray(), v.asarray(), xdim.getDimValue(), ydim.getDimValue())
        return DimArray(MIArray(r), u.dims, u.fill_value, u.proj)

#  Calculates the horizontal divergence using finite differencing        
def hdivg(u, v):
    '''
    Calculates the horizontal divergence using finite differencing. The data should be lon/lat projection.
    
    :param u: (*array*) U component array.
    :param v: (*array*) V component array.
    
    :returns: Array of the horizontal divergence.
    '''
    if isinstance(u, DimArray) and isinstance(v, DimArray):
        ydim = u.ydim()
        xdim = u.xdim()
        r = ArrayMath.hdivg(u.asarray(), v.asarray(), xdim.getDimValue(), ydim.getDimValue())
        return DimArray(MIArray(r), u.dims, u.fill_value, u.proj)
              
def magnitude(u, v):
    '''
    Performs the calculation: sqrt(u*u+v*v).
    
    :param u: (*array*) U component array.
    :param v: (*array*) V component array.
    
    :returns: Result array.
    '''
    if isinstance(u, DimArray) and isinstance(v, DimArray):
        r = ArrayMath.magnitude(u.asarray(), v.asarray())
        return DimArray(MIArray(r), u.dims, u.fill_value, u.proj)
    elif isinstance(u, MIArray) and isinstance(v, MIArray):
        r = ArrayMath.magnitude(u.asarray(), v.asarray())
        return MIArray(r)
    else:
        r = sqrt(u * u + v * v)
        return r

def asarray(data):
    '''
    Get array from array_like data (ie., MIArray, DimArray and list).
    
    :param data: (*array_like*) The input data.
    
    :returns: Array data.
    '''
    if isinstance(data, Array):
        return data
    elif isinstance(data, (DimArray, MIArray)):
        return data.asarray()
    elif isinstance(data, (list, tuple)):
        if isinstance(data[0], datetime.datetime):
            dd = []
            for d in data:
                v = miutil.date2num(d)
                dd.append(v)
            return array(dd).array
        else:
            return array(data).array
    else:
        return array([data]).array()

def asmiarray(data):
    '''
    Convert the array_like data to MIArray data.
    
    :param data: (*array_like*) The input data.
    
    :returns: MIArray data.
    '''
    if isinstance(data, Array):
        return MIArray(data)
    elif isinstance(data, DimArray):
        return data.array
    elif isinstance(data, MIArray):
        return data
    else:
        return array(data)       
        
def asgriddata(data, x=None, y=None, fill_value=-9999.0):
    if x is None:    
        if isinstance(data, PyGridData):
            return data
        elif isinstance(data, DimArray):
            return data.asgriddata()
        elif isinstance(data, MIArray):
            if x is None:
                x = arange(0, data.shape[1])
            if y is None:
                y = arange(0, data.shape[0])
            gdata = GridData(data.array, x.array, y.array, fill_value)
            return PyGridData(gdata)
        else:
            return None
    else:
        gdata = GridData(data.asarray(), x.asarray(), y.asarray(), fill_value)
        return PyGridData(gdata)
        
def asgridarray(data, x=None, y=None, fill_value=-9999.0):
    if x is None:    
        if isinstance(data, PyGridData):
            return data.data.toGridArray()
        elif isinstance(data, DimArray):
            return data.asgridarray()
        elif isinstance(data, MIArray):
            if x is None:
                x = arange(0, data.shape[1])
            if y is None:
                y = arange(0, data.shape[0])
            gdata = GridArray(data.array, x.array, y.array, fill_value)
            return gdata
        else:
            return None
    else:
        gdata = GridArray(data.asarray(), x.asarray(), y.asarray(), fill_value)
        return gdata
        
def asstationdata(data, x, y, fill_value=-9999.0):
    stdata = StationData(data.asarray(), x.asarray(), y.asarray(), fill_value)
    return PyStationData(stdata)
    
def polygon(x, y = None):
    '''
    Create polygon from coordinate data.
    
    :param x: (*array_like*) X coordinate array. If y is ``None``, x should be 2-D array contains x and y.
    :param y: (*array_like*) Y coordinate array.
    
    :returns: (*PolygonShape*) Created polygon.
    '''
    if y is None:
        polygon = ShapeUtil.createPolygonShape(x)
    else:
        if isinstance(x, MIArray):
            x = x.aslist()
        if isinstance(y, MIArray):
            y = y.aslist()
        polygon = ShapeUtil.createPolygonShape(x, y)
    return polygon
    
def inpolygon(x, y, polygon):
    '''
    Judge if a point is inside a polygon or not.
    
    :param x: (*float*) X coordinate of the point.
    :param y: (*float*) Y coordinate of the point.
    :param polygon: (*PolygonShape*) The polygon.
    
    :returns: (*boolean*) Inside or not.
    '''
    return GeoComputation.pointInPolygon(polygon, x, y)
    
def distance(x, y, islonlat=False):
    """
    Get distance of a line.
    
    :param x: (*array_like*) X coordinates.
    :param y: (*array_like*) Y coordinates.
    :param islonlat: (*boolean*) x/y is longitude/latitude or not.
    
    :returns: Distance, meters for lon/lat.
    """
    if isinstance(x, (MIArray, DimArray)):
        x = x.aslist()
    if isinstance(y, (MIArray, DimArray)):
        y = y.aslist()
    r = GeoComputation.getDistance(x, y, islonlat)
    return r
    
def polyarea(*args, **kwargs):
    '''
    Calculate area of polygon.
    
    Parameter is a polygon object or x, y coordinate arrays.
    
    :return: The area of the polygon.
    '''
    islonlat = kwargs.pop('islonlat', False)
    if len(args) == 1:
        if islonlat:
            r = args[0].getSphericalArea()
        else:
            r = args[0].getArea()
    else:
        x = args[0]
        y = args[1]
        if isinstance(x, MIArray):
            x = x.aslist()
        if isinstance(y, MIArray):
            y = y.aslist()
        r = GeoComputation.getArea(x, y, islonlat)
    return r
    
def maskout(data, mask, x=None, y=None):
    """
    Maskout data by polygons - NaN values of elements outside polygons.
    
    :param mask: (*list*) Polygon list as maskout borders.
    :param data: (*array_like*) Array data for maskout.
    :param x: (*array_like*) X coordinate array.
    :param y: (*array_like*) Y coordinate array.

    :returns: (*array_like*) Maskouted data array.
    """
    if mask is None:
        return data
    elif isinstance(mask, (MIArray, DimArray)):
        r = ArrayMath.maskout(data.asarray(), mask.asarray())
        return MIArray(r)
    if x is None or y is None:
        if isinstance(data, DimArray):
            return data.maskout(mask)
        else:
            return None
    else:
        if not isinstance(mask, (list, ArrayList)):
            mask = [mask]
        r = ArrayMath.maskout(data.asarray(), x.asarray(), y.asarray(), mask)
        return MIArray(r)
        
def rmaskout(data, x, y, mask):
    """
    Maskout data by polygons - the elements outside polygons will be removed
    
    :param data: (*array_like*) Array data for maskout.
    :param x: (*array_like*) X coordinate array.
    :param y: (*array_like*) Y coordinate array.
    :param mask: (*list*) Polygon list as maskout borders.
    
    :returns: (*list*) Maskouted data, x and y array list.
    """
    if not isinstance(mask, (list, ArrayList)):
        mask = [mask]
    r = ArrayMath.maskout_Remove(data.asarray(), x.asarray(), y.asarray(), mask)
    return MIArray(r[0]), MIArray(r[1]), MIArray(r[2])  

def interp2d(*args, **kwargs):
    """
    Interpolate over a 2-D grid.
    
    :param x: (*array_like*) X coordinate array of the sample points.
    :param y: (*array_like*) Y coordinate array of the sample points.
    :param z: (*array_like*) 2-D value array of the sample points.
    :param xq: (*array_like*) X coordinate array of the query points.
    :param yq: (*array_like*) Y coordinate array of the query points.
    :param kind: (*string*) The kind of the interpolation method. ['linear' | 'nearest'].
    
    :returns: (*array_like*) Interpolated array.
    """
    if len(args) == 3:
        z = args[0]
        x = z.dimvalue(1)
        y = z.dimvalue(0)
        xq = args[1]
        yq = args[2]
    else:
        x = args[0]
        y = args[1]
        z = args[2]
        xq = args[3]
        yq = args[4]
    x = array(x).array
    y = array(y).array
    z = array(z).array
    xq = array(xq).array
    yq = array(yq).array
    kind = kwargs.pop('kind', 'linear')
    if kind == 'neareast':
        r = ArrayUtil.resample_Neighbor(z, x, y, xq, yq)
    else:
        r = ArrayUtil.resample_Bilinear(z, x, y, xq, yq)
    if r.getSize() == 1:
        return r.getDouble(0)
    else:
        return MIArray(r)

def interpn(points, values, xi):
    """
    Multidimensional interpolation on regular grids.
    
    :param points: (*list*) The points defining the regular grid in n dimensions.
    :param values: (*array_like*) The data on the regular grid in n dimensions.
    :param xi: (*list*) The coordinates to sample the gridded data at.
    
    :returns: (*float*) Interpolated value at input coordinates.
    """
    npoints = []
    for p in points:
        if isinstance(p, (MIArray, DimArray)):
            p = p.aslist()
        npoints.append(p)
        
    if isinstance(xi, (MIArray, DimArray)):
        xi = xi.aslist()
    nxi = []
    for x in xi:
        if isinstance(x, datetime.datetime):
            x = miutil.date2num(x)
        nxi.append(x)
        
    r = ArrayUtil.interpn(npoints, values.asarray(), nxi)
    return r
    
def griddata(points, values, xi=None, **kwargs):
    '''
    Interpolate scattered data to grid data.
    
    :param points: (*list*) The list contains x and y coordinate arrays of the scattered data.
    :param values: (*array_like*) The scattered data array.
    :param xi: (*list*) The list contains x and y coordinate arrays of the grid data. Default is ``None``,
        the grid x and y coordinate size were both 500.
    :param method: (*string*) The interpolation method. [idw | cressman | neareast | inside | inside_min
        | inside_max | inside_count | surface]
    :param fill_value: (*float*) Fill value, Default is ``nan``.
    :param pointnum: (*int*) Only used for 'idw' method. The number of the points to be used for each grid
        value interpolation.
    :param radius: (*float*) Used for 'idw', 'cressman' and 'neareast' methods. The searching raduis. Default 
        is ``None`` in 'idw' method, means no raduis was used. Default is ``[10, 7, 4, 2, 1]`` in cressman 
        method.
    :param convexhull: (*boolean*) If the convexhull will be used to mask result grid data. Default is ``False``.
    
    :returns: (*array*) Interpolated grid data (2-D array)
    '''
    method = kwargs.pop('method', 'idw')
    fill_value = kwargs.pop('fill_value', nan)
    x_s = points[0]
    y_s = points[1]
    if xi is None:
        xn = 500
        yn = 500
        x_g = linspace(x_s.min(), x_s.max(), xn)
        y_g = linspace(y_s.min(), y_s.max(), yn)        
    else:
        x_g = xi[0]
        y_g = xi[1]
    if isinstance(values, MIArray) or isinstance(values, DimArray):
        values = values.asarray()    
    if method == 'idw':
        pnum = kwargs.pop('pointnum', 2)
        radius = kwargs.pop('radius', None)
        if radius is None:
            r = ArrayUtil.interpolation_IDW_Neighbor(x_s.aslist(), y_s.aslist(), values, x_g.aslist(), y_g.aslist(), pnum)
        else:
            r = ArrayUtil.interpolation_IDW_Radius(x_s.aslist(), y_s.aslist(), values, x_g.aslist(), y_g.aslist(), pnum, radius)
    elif method == 'cressman':
        radius = kwargs.pop('radius', [10, 7, 4, 2, 1])
        if isinstance(radius, MIArray):
            radius = radius.aslist()
        r = ArrayUtil.cressman(x_s.aslist(), y_s.aslist(), values, x_g.aslist(), y_g.aslist(), radius)
    elif method == 'neareast':
        radius = kwargs.pop('radius', inf)
        r = ArrayUtil.interpolation_Nearest(x_s.aslist(), y_s.aslist(), values, x_g.aslist(), y_g.aslist(), radius)
    elif method == 'inside':
        r = ArrayUtil.interpolation_Inside(x_s.aslist(), y_s.aslist(), values, x_g.aslist(), y_g.aslist())
    elif method == 'inside_max':
        r = ArrayUtil.interpolation_Inside_Max(x_s.aslist(), y_s.aslist(), values, x_g.aslist(), y_g.aslist())
    elif method == 'inside_min':
        r = ArrayUtil.interpolation_Inside_Min(x_s.aslist(), y_s.aslist(), values, x_g.aslist(), y_g.aslist())
    elif method == 'inside_count':
        r = ArrayUtil.interpolation_Inside_Count(x_s.aslist(), y_s.aslist(), x_g.aslist(), y_g.aslist(), True)
        return MIArray(r[0]), x_g, y_g, MIArray(r[1])
    elif method == 'surface':        
        r = ArrayUtil.interpolation_Surface(x_s.asarray(), y_s.asarray(), values, x_g.asarray(), y_g.asarray())
    else:
        return None
    
    convexhull = kwargs.pop('convexhull', False)
    if convexhull:
        polyshape = ArrayUtil.convexHull(x_s.asarray(), y_s.asarray())
        x_gg, y_gg = meshgrid(x_g, y_g)
        r = maskout(MIArray(r), x=x_gg, y=y_gg, mask=polyshape)
        return r, x_g, y_g
    else:
        return MIArray(r), x_g, y_g

def projinfo(proj='longlat', **kwargs):
    """
    Create a projection object with Proj.4 parameters (http://proj4.org/)
    
    :param proj: (*string*) Projection name.
    :param lat_0: (*float*) Latitude of origin.
    :param lon_0: (*float*) Central meridian.
    :param lat_1: (*float*) Latitude of first standard paralle.
    :param lat_2: (*float*) Latitude of second standard paralle.
    :param lat_ts: (*float*) Latitude of true scale.
    :param k: (*float*) Scaling factor.
    :param x_0: (*float*) False easting.
    :param y_0: (*float*) False northing.
    :param h: (*float*) Height from earth surface.
    
    :returns: (*ProjectionInfo*) ProjectionInfo object.
    """
    if proj == 'longlat' and len(kwargs) == 0:
        return KnownCoordinateSystems.geographic.world.WGS1984
        
    origin = kwargs.pop('origin', (0, 0, 0))    
    lat_0 = origin[0]
    lon_0 = origin[1]
    lat_0 = kwargs.pop('lat_0', lat_0)
    lon_0 = kwargs.pop('lon_0', lon_0)
    lat_ts = kwargs.pop('truescalelat', 0)
    lat_ts = kwargs.pop('lat_ts', lat_ts)
    k = kwargs.pop('scalefactor', 1)
    k = kwargs.pop('k', k)
    paralles = kwargs.pop('paralles', (30, 60))
    lat_1 = paralles[0]
    if len(paralles) == 2:
        lat_2 = paralles[1]
    else:
        lat_2 = lat_1
    lat_1 = kwargs.pop('lat_1', lat_1)
    lat_2 = kwargs.pop('lat_2', lat_2)
    x_0 = kwargs.pop('falseeasting', 0)
    y_0 = kwargs.pop('falsenorthing', 0)
    x_0 = kwargs.pop('x_0', x_0)
    y_0 = kwargs.pop('y_0', y_0)
    h = kwargs.pop('h', 0)
    projstr = '+proj=' + proj \
        + ' +lat_0=' + str(lat_0) \
        + ' +lon_0=' + str(lon_0) \
        + ' +lat_1=' + str(lat_1) \
        + ' +lat_2=' + str(lat_2) \
        + ' +lat_ts=' + str(lat_ts) \
        + ' +k=' + str(k) \
        + ' +x_0=' + str(x_0) \
        + ' +y_0=' + str(y_0) \
        + ' +h=' + str(h)
        
    return ProjectionInfo(projstr)     
    
def project(x, y, fromproj=KnownCoordinateSystems.geographic.world.WGS1984, toproj=KnownCoordinateSystems.geographic.world.WGS1984):
    """
    Project geographic coordinates from one projection to another.
    
    :param x: (*array_like*) X coordinate values for projection.
    :param y: (*array_like*) Y coordinate values for projection.
    :param fromproj: (*ProjectionInfo*) From projection. Default is longlat projection.
    :param toproj: (*ProjectionInfo*) To projection. Default is longlat projection.
    
    :returns: (*array_like*, *array_like*) Projected geographic coordinates.
    """
    if isinstance(fromproj, str):
        fromproj = ProjectionInfo(fromproj)
    if isinstance(toproj, str):
        toproj = ProjectionInfo(toproj)
    if isinstance(x, (tuple, list)):
        x = array(x)
    if isinstance(y, (tuple, list)):
        y = array(y)
    if isinstance(x, (MIArray, DimArray)):
        outxy = ArrayUtil.reproject(x.asarray(), y.asarray(), fromproj, toproj)
        return MIArray(outxy[0]), MIArray(outxy[1])
    else:
        inpt = PointD(x, y)
        outpt = Reproject.reprojectPoint(inpt, fromproj, toproj)
        return outpt.X, outpt.Y
    
def projectxy(lon, lat, xnum, ynum, dx, dy, toproj, fromproj=None, pos='lowerleft'):
    """
    Get projected x, y coordinates by projection and a given lon, lat coordinate.
    
    :param lon: (*float*) Longitude value.
    :param lat: (*float*) Latitude value.
    :param xnum: (*int*) X number.
    :param ynum: (*int*) Y number.
    :param dx: (*float*) X delta.
    :param dy: (*float*) Y delta.
    :param toproj: (*ProjectionInfo*) To projection.
    :param fromproj: (*ProjectionInfo*) From projection. Default is longlat projection.
    :param pos: (*string*) ['lowerleft' | 'center'] Lon, lat coordinate position.

    :returns: (*array_like*, *array_like*) Projected x, y coordinates.
    """
    if fromproj is None:
        fromproj = KnownCoordinateSystems.geographic.world.WGS1984
    x, y = project(lon, lat, toproj, fromproj)
    if pos == 'lowerleft':
        xx = arange1(x, xnum, dx)
        yy = arange1(y, ynum, dy)
    else:
        llx = x - ((xnum - 1) * 0.5 * dx)
        lly = y - ((ynum - 1) * 0.5 * dy)
        xx = arange1(llx, xnum, dx)
        yy = arange1(lly, ynum, dy)
    return xx, yy
    
def pol2cart(theta, rho):
    '''
    Transform polar coordinates to Cartesian
    
    :param theta: (*array_like*) Theta value in polar coordinates
    :param rho: (*array_like*) Rho value in polar coordinates
    
    :returns: x and y value in Cartesian coordinates
    '''
    if isinstance(theta, (int, float)):
        r = ArrayMath.polarToCartesian(theta, rho)
        return r[0], r[1]
    else:
        theta = array(theta)
        rho = array(rho)
        r = ArrayMath.polarToCartesian(theta.array, rho.array)
        return MIArray(r[0]), MIArray(r[1])
        
def cart2pol(x, y):
    '''
    Transform Cartesian coordinates to polar
    
    :param x: (*array_like*) X value in Cartesian coordinates
    :param y: (*array_like*) Y value in Cartesian coordinates
    
    :returns: Theta and rho value in polar coordinates
    '''
    if isinstance(x, (int, float)):
        r = ArrayMath.cartesianToPolar(x, y)
        return r[0], r[1]
    else:
        x = array(x)
        y = array(y)
        r = ArrayMath.cartesianToPolar(x.array, y.array)
        return MIArray(r[0]), MIArray(r[1])
    
def addtimedim(infn, outfn, t, tunit='hours'):
    '''
    Add a time dimension to a netCDF data file.
    
    :param infn: (*string*) Input netCDF file name.
    :param outfn: (*string*) Output netCDF file name.
    :param t: (*DateTime*) A time value.
    :param tunit: (*string*) Time unite, Default is ``hours``.
    
    :returns: The new netCDF with time dimension.
    '''
    cal = Calendar.getInstance()
    cal.set(t.year, t.month - 1, t.day, t.hour, t.minute, t.second)
    nt = cal.getTime()
    NetCDFDataInfo.addTimeDimension(infn, outfn, nt, tunit)
        
def joinncfile(infns, outfn, tdimname):
    '''
    Join several netCDF files to one netCDF file.
    
    :param infns: (*list*) Input netCDF file name list.
    :param outfn: (*string*) Output netCDF file name.
    :param tdimname: (*string*) Time dimension name.
    
    :returns: Joined netCDF file.
    '''
    NetCDFDataInfo.joinDataFiles(infns, outfn, tdimname)
    
def binread(fn, dim, datatype=None, skip=0, byteorder='little_endian'):
    """
    Read data array from a binary file.
    
    :param fn: (*string*) The binary file name for data reading. 
    :param dim: (*list*) Dimensions.
    :param datatype: (*string*) Data type string.
    :param skip: (*int*) Skip bytes number.
    :param byteorder: (*string*) Byte order. ``little_endian`` or ``big_endian``.
    
    :returns: (*MIArray*) Data array
    """
    r = ArrayUtil.readBinFile(fn, dim, datatype, skip, byteorder);
    return MIArray(r)
        
def binwrite(fn, data, byteorder='little_endian', append=False):
    """
    Create a binary data file from an array variable.
    
    :param fn: (*string*) Path needed to locate binary file.
    :param data: (*array_like*) A numeric array variable of any dimensionality.
    :param byteorder: (*string*) Byte order. ``little_endian`` or ``big_endian``.
    :param append: (*boolean*) Append to an existing file or not.
    """
    ArrayUtil.saveBinFile(fn, data.asarray(), byteorder, append)    
    
# Get month abstract English name
def monthname(m):  
    '''
    Get month abstract English name.
    
    :param m: (*int*) Month number (1 to 12).
    '''
    mmm = 'jan'
    if m == 1:
        mmm = 'jan'
    elif m == 2:
        mmm = 'feb'
    elif m == 3:
        mmm = 'mar'
    elif m == 4:
        mmm = 'apr'
    elif m == 5:
        mmm = 'may'
    elif m == 6:
        mmm = 'jun'
    elif m == 7:
        mmm = 'jul'
    elif m == 8:
        mmm = 'aug'
    elif m == 9:
        mmm = 'sep'
    elif m == 10:
        mmm = 'oct'
    elif m == 11:
        mmm = 'nov'
    elif m == 12:
        mmm = 'dec'

    return mmm