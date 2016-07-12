#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2014-12-27
# Purpose: MeteoInfo numerical module
# Note: Jython
#-----------------------------------------------------
import os
import math
import datetime
from org.meteoinfo.data import GridData, GridArray, StationData, DataMath, TableData, TimeTableData, ArrayMath, ArrayUtil, TableUtil, DataTypes
from org.meteoinfo.data.meteodata import MeteoDataInfo, Dimension, DimensionType
from org.meteoinfo.data.meteodata.netcdf import NetCDFDataInfo
from org.meteoinfo.data.meteodata.arl import ARLDataInfo
from org.meteoinfo.data.mapdata import MapDataManage
from org.meteoinfo.data.mapdata.geotiff import GeoTiff
from org.meteoinfo.data.analysis import MeteoMath
from org.meteoinfo.geoprocess import GeoComputation
from org.meteoinfo.projection import KnownCoordinateSystems, ProjectionInfo, Reproject
from org.meteoinfo.global import PointD
from org.meteoinfo.shape import ShapeUtil
from org.meteoinfo.legend import BreakTypes
from ucar.nc2 import NetcdfFileWriter
from ucar.ma2 import Array

import dimdatafile
import dimvariable
import dimarray
import miarray
import milayer
import miutil
from dimdatafile import DimDataFile
from dimvariable import DimVariable
from dimarray import PyGridData, DimArray, PyStationData
from miarray import MIArray
from milayer import MILayer

from java.awt import Color
from java.lang import Math, Double
from java.util import Calendar, ArrayList

# Global variables
pi = Math.PI
e = Math.E
inf = Double.POSITIVE_INFINITY
nan = Double.NaN
meteodatalist = []
c_meteodata = None
currentfolder = None

def isgriddata(gdata):
    return isinstance(gdata, PyGridData)
    
def isstationdata(sdata):
    return isinstance(sdata, PyStationData)

###############################################################        
#  The encapsulate class of TableData
class PyTableData():
    # Must be a TableData object
    def __init__(self, data=None):
        self.data = data
        if data is None:
            self.data = TableData()
        self.timedata = isinstance(data, TimeTableData)
        
    def __getitem__(self, key):
        if isinstance(key, (str, unicode)):     
            coldata = self.data.getColumnData(key)
            if coldata.getDataType().isNumeric():
                return MIArray(ArrayUtil.array(coldata.getDataValues()))
            elif coldata.getDataType() == DataTypes.Date:
                vv = coldata.getData()
                r = []
                cal = Calendar.getInstance()
                for v in vv:
                    cal.setTime(v)
                    year = cal.get(Calendar.YEAR)
                    month = cal.get(Calendar.MONTH) + 1
                    day = cal.get(Calendar.DAY_OF_MONTH)
                    hour = cal.get(Calendar.HOUR_OF_DAY)
                    minute = cal.get(Calendar.MINUTE)
                    second = cal.get(Calendar.SECOND)
                    dt = datetime.datetime(year, month, day, hour, minute, second)
                    r.append(dt)
                return r
            else:
                return coldata.getData()
        else:
            row = key[0]
            col = key[1]
            return self.data.getValue(row, col)
        return None
        
    def __setitem__(self, key, value):
        if isinstance(value, MIArray):
            self.data.setColumnData(key, value.aslist())
        else:
            self.data.setColumnData(key, value)
            
    def __repr__(self):
        return self.data.toString()
        
    def rownum(self):
        return self.data.getDataTable().getRowCount()
        
    def colnum(self):
        return self.data.getDataTable().getColumnCount()
    
    def colnames(self):
        return self.data.getDataTable().getColumnNames()
        
    def setcolname(self, col, colname):
        self.data.getDataTable().renameColumn(col, colname)
        
    def setcolnames(self, colnames):
        for i in range(len(colnames)):
            self.data.getDataTable().renameColumn(i, colnames[i])
    
    def coldata(self, key):
        if isinstance(key, str):
            print key     
            values = self.data.getColumnData(key).getDataValues()
            return MIArray(ArrayUtil.array(values))
        return None
        
    def getvalue(self, row, col):
        return self.data.getValue(row, col)

    def setvalue(self, row, col, value):
        self.data.setValue(row, col, value)
    
    def addcoldata(self, colname, dtype, coldata):
        if isinstance(coldata, MIArray):
            self.data.addColumnData(colname, dtype, coldata.aslist())
        else:
            self.data.addColumnData(colname, dtype, coldata)

    def addcol(self, colname, dtype, index=None):
        dtype = TableUtil.toDataTypes(dtype)
        if index is None:
            self.data.addColumn(colname, dtype)
        else:
            self.data.addColumn(index, colname, dtype)
    
    def delcol(self, colname):
        self.data.removeColumn(colname)
        
    def addrow(self, row=None):
        if row is None:
            self.data.addRow()
        else:
            self.data.addRow(row)
            
    def addrows(self, rows):
        self.data.addRows(rows)
        
    def getrow(self, index):
        return self.data.getRow(index)
        
    def getrows(self):
        return self.data.getRows()
        
    #Set time column
    def timecol(self, colname):
        tdata = TimeTableData(self.data.dataTable)
        tdata.setTimeColName(colname)
        self.data = tdata;
        self.timedata = True
        
    def join(self, other, colname, colname1=None):
        if colname1 == None:
            self.data.join(other.data, colname)
        else:
            self.data.join(other.data, colname, colname1)
    def join(self, other, colname):
        self.data.join(other.data, colname)
        
    def savefile(self, filename, delimiter=','):
        if delimiter == ',':
            self.data.saveAsCSVFile(filename)
        else:
            self.data.saveAsASCIIFile(filename)
            
    def ave(self, colnames):
        cols = self.data.findColumns(colnames)
        dtable = self.data.average(cols)
        return PyTableData(TableData(dtable))
        
    def ave_year(self, colnames, year=None):
        if not self.timedata:
            print 'There is no time column!'
            return None
        else:
            cols = self.data.findColumns(colnames)
            if year is None:
                dtable = self.data.ave_Year(cols)
            else:
                dtable = self.data.ave_Year(cols, year)
            return PyTableData(TableData(dtable))
            
    def ave_yearmonth(self, colnames, month):
        if not self.timedata:
            print 'There is no time column!'
            return None
        else:
            cols = self.data.findColumns(colnames)
            dtable = self.data.ave_YearMonth(cols, month)
            return PyTableData(TableData(dtable))
                  
    def ave_monthofyear(self, colnames):
        if not self.timedata:
            print 'There is no time column!'
            return None
        else:
            cols = self.data.findColumns(colnames)
            dtable = self.data.ave_MonthOfYear(cols)
            return PyTableData(TableData(dtable))
            
    def ave_seasonofyear(self, colnames):
        if not self.timedata:
            print 'There is no time column!'
            return None
        else:
            cols = self.data.findColumns(colnames)
            dtable = self.data.ave_SeasonOfYear(cols)
            return PyTableData(TableData(dtable))
            
    def ave_hourofday(self, colnames):
        if not self.timedata:
            print 'There is no time column!'
            return None
        else:
            cols = self.data.findColumns(colnames)
            dtable = self.data.ave_HourOfDay(cols)
            return PyTableData(TableData(dtable))
    
    def ave_month(self, colnames):
        if not self.timedata:
            print 'There is no time column!'
            return None
        else:
            cols = self.data.findColumns(colnames)
            dtable = self.data.ave_Month(cols)
            return PyTableData(TableData(dtable))
            
    def ave_day(self, colnames, day=None):
        if not self.timedata:
            print 'There is no time column!'
            return None
        else:
            cols = self.data.findColumns(colnames)
            dtable = self.data.ave_Day(cols)
            ttd = TimeTableData(dtable)
            ttd.setTimeColName('Date')
            return PyTableData(ttd)
            
    def ave_hour(self, colnames):
        if not self.timedata:
            print 'There is no time column!'
            return None
        else:
            cols = self.data.findColumns(colnames)
            dtable = self.data.ave_Hour(cols)
            ttd = TimeTableData(dtable)
            ttd.setTimeColName('Date')
            return PyTableData(ttd)
            
    def assinglerow(self):
        return PyTableData(TableData(self.data.toSingleRowTable(self.data.getDataTable())))
        
    def sql(self, expression):
        return PyTableData(self.data.sqlSelect(expression))
    
    def clone(self):
        return PyTableData(self.data.clone())

#################################################################  

def __getfilename(fname):
    s5 = fname[0:5]
    isweb = False
    if s5 == 'http:' or s5 == 'https' or s5 == 'dods:' or s5 == 'dap4:':
        isweb = True
        return fname, isweb
    if os.path.exists(fname):
        if os.path.isabs(fname):
            return fname, isweb
        else:
            return os.path.join(currentfolder, fname), isweb
    else:
        if currentfolder != None:
            fname = os.path.join(currentfolder, fname)
            if os.path.isfile(fname):
                return fname, isweb
            else:
                print 'File not exist: ' + fname
                return None, isweb
        else:
            print 'File not exist: ' + fname
            return None, isweb
          
def addfile(fname, access='r', dtype='netcdf'):
    """
    Opens a data file that is written in a supported file format.
    
    :param fname: (*string*) The full or relative path of the data file to load.
    :param access: (*string*) The access right setting to the data file. Default is ``r``.
    :param dtype: (*string*) The data type of the data file. Default is ``netcdf``.
    
    :returns: (*DimDataFile*) Opened file object.
    """
    if access == 'r':
        fname = fname.strip()
        fname, isweb = __getfilename(fname)
        if fname is None:
            return None

        if isweb:
            return addfile_nc(fname, False)
        
        if not os.path.exists(fname):
            print 'File not exist: ' + fname
            return None
        
        fsufix = os.path.splitext(fname)[1].lower()
        if fsufix == '.ctl':
            return addfile_grads(fname, False)
        elif fsufix == '.tif':
            return addfile_geotiff(fname, False)
        elif fsufix == '.awx':
            return addfile_awx(fname, False)
        
        meteodata = MeteoDataInfo()
        meteodata.openData(fname)
        __addmeteodata(meteodata)
        datafile = DimDataFile(meteodata)
        return datafile
    elif access == 'c':
        if dtype == 'arl':
            arldata = ARLDataInfo()
            arldata.createDataFile(fname)
            datafile = DimDataFile(arldata=arldata)
        else:
            ncfile = NetcdfFileWriter.createNew(NetcdfFileWriter.Version.netcdf3, fname)
            datafile = DimDataFile(ncfile=ncfile)
        return datafile
    else:
        return None
    
def addfile_grads(fname, getfn=True):
    if getfn:
        fname, isweb = __getfilename(fname)
    meteodata = MeteoDataInfo()
    meteodata.openGrADSData(fname)
    __addmeteodata(meteodata)
    datafile = DimDataFile(meteodata)
    return datafile
    
def addfile_nc(fname, getfn=True):
    if getfn:
        fname, isweb = __getfilename(fname)
    meteodata = MeteoDataInfo()
    meteodata.openNetCDFData(fname)
    __addmeteodata(meteodata)
    datafile = DimDataFile(meteodata)
    return datafile
    
def addfile_arl(fname, getfn=True):
    if getfn:
        fname, isweb = __getfilename(fname)
    meteodata = MeteoDataInfo()
    meteodata.openARLData(fname)
    __addmeteodata(meteodata)
    datafile = DimDataFile(meteodata)
    return datafile
    
def addfile_surfer(fname, getfn=True):
    if getfn:
        fname, isweb = __getfilename(fname)
    meteodata = MeteoDataInfo()
    meteodata.openSurferGridData(fname)
    __addmeteodata(meteodata)
    datafile = DimDataFile(meteodata)
    return datafile
    
def addfile_mm5(fname, getfn=True):
    if getfn:
        fname, isweb = __getfilename(fname)
    meteodata = MeteoDataInfo()
    meteodata.openMM5Data(fname)
    __addmeteodata(meteodata)
    datafile = DimDataFile(meteodata)
    return datafile
    
def addfile_lonlat(fname, getfn=True, missingv=-9999.0):
    if getfn:
        fname, isweb = __getfilename(fname)
    meteodata = MeteoDataInfo()
    meteodata.openLonLatData(fname)
    meteodata.getDataInfo().setMissingValue(missingv)
    __addmeteodata(meteodata)
    datafile = DimDataFile(meteodata)
    return datafile
    
def addfile_micaps(fname, getfn=True):
    if getfn:
        fname, isweb = __getfilename(fname)
    meteodata = MeteoDataInfo()
    meteodata.openMICAPSData(fname)
    __addmeteodata(meteodata)
    datafile = DimDataFile(meteodata)
    return datafile

def addfile_hytraj(fname, getfn=True):
    if isinstance(fname, basestring):
        if getfn:
            fname, isweb = __getfilename(fname)
    meteodata = MeteoDataInfo()
    meteodata.openHYSPLITTrajData(fname)
    __addmeteodata(meteodata)
    datafile = DimDataFile(meteodata)
    return datafile
    
def addfile_hyconc(fname, getfn=True):
    if getfn:
        fname, isweb = __getfilename(fname)
    meteodata = MeteoDataInfo()
    meteodata.openHYSPLITConcData(fname)
    __addmeteodata(meteodata)
    datafile = DimDataFile(meteodata)
    return datafile
    
def addfile_geotiff(fname, getfn=True):
    if getfn:
        fname, isweb = __getfilename(fname)
    meteodata = MeteoDataInfo()
    meteodata.openGeoTiffData(fname)
    __addmeteodata(meteodata)
    datafile = DimDataFile(meteodata)
    return datafile
    
def addfile_awx(fname, getfn=True):
    if getfn:
        fname, isweb = __getfilename(fname)
    meteodata = MeteoDataInfo()
    meteodata.openAWXData(fname)
    __addmeteodata(meteodata)
    datafile = DimDataFile(meteodata)
    return datafile
    
def addfile_ascii_grid(fname, getfn=True):
    if getfn:
        fname, isweb = __getfilename(fname)
    if not os.path.exists(fname):
        print 'File not exist: ' + fname
        return None
    meteodata = MeteoDataInfo()
    meteodata.openASCIIGridData(fname)
    __addmeteodata(meteodata)
    datafile = DimDataFile(meteodata)
    return datafile

def __addmeteodata(meteodata):
    global c_meteodata, meteodatalist
    meteodatalist.append(meteodata)
    c_meteodata = meteodata
    #print 'Current meteodata: ' + c_meteodata.toString()        
    
def getgriddata(varname='var', timeindex=0, levelindex=0, yindex=None, xindex=None):
    if c_meteodata.isGridData():
        c_meteodata.setTimeIndex(timeindex)
        c_meteodata.setLevelIndex(levelindex)
        gdata = PyGridData(c_meteodata.getGridData(varname))
        return gdata
    else:
        return None
        
def getstationdata(varname='var', timeindex=0, levelindex=0):
    if c_meteodata.isStationData():
        c_meteodata.setTimeIndex(timeindex)
        c_meteodata.setLevelIndex(levelindex)
        sdata = PyStationData(c_meteodata.getStationData(varname))
        return sdata
    else:
        return None

def numasciirow(filename):
    nrow = ArrayUtil.numASCIIRow(filename)
    return nrow
    
def numasciicol(filename, delimiter=None, headerlines=0):
    ncol = ArrayUtil.numASCIICol(filename, delimiter, headerlines)
    return ncol
        
def asciiread(filename, **kwargs):
    delimiter = kwargs.pop('delimiter', None)
    datatype = kwargs.pop('datatype', None)
    headerlines = kwargs.pop('headerlines', 0)
    shape = kwargs.pop('shape', None)    
    a = ArrayUtil.readASCIIFile(filename, delimiter, headerlines, datatype, shape)
    return MIArray(a)
        
def readtable(filename, **kwargs):
    delimiter = kwargs.pop('delimiter', None)
    format = kwargs.pop('format', None)
    headerlines = kwargs.pop('headerlines', 0)
    encoding = kwargs.pop('encoding', 'UTF8')
    readvarnames = kwargs.pop('readvarnames', True)
    readrownames = kwargs.pop('readrownames', False)
    tdata = TableUtil.readASCIIFile(filename, delimiter, headerlines, format, encoding)
    r = PyTableData(tdata)
    colnames = kwargs.pop('colnames', None)
    if not colnames is None:
        r.setcolnames(colnames)
    return r
    
def geotiffread(filename):
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
    return MIArray(ArrayUtil.array(object))
    
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
        
def pow(x1, x2):
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
            return math.pow(x1, x2)
            
def power(x1, x2):
    return pow(x1, x2)

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
        return math.log10(x)
        
def mean(x, axis=None):
    """
    Compute tha arithmetic mean
    
    :param x: (*array_like or list*) Input values.
    
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
            return None
    else:
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
    if isinstance(x1, (MIArray, DimArray)):
        return MIArray(ArrayMath.maximum(x1.asarray(), x2.asarray()))
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
    if isinstance(x1, (MIArray, DimArray)):
        return MIArray(ArrayMath.fmax(x1.asarray(), x2.asarray()))
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
    if isinstance(x1, (MIArray, DimArray)):
        return MIArray(ArrayMath.minimum(x1.asarray(), x2.asarray()))
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
    if isinstance(x1, (MIArray, DimArray)):
        return MIArray(ArrayMath.fmin(x1.asarray(), x2.asarray()))
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
                
def sort(a, axis=-1):
    """
    Return a sorted copy of an array.
    
    :param a: (*array_like*) Array to be sorted.
    :param axis: (*int or None*) Optional. Axis along which to sort. If None, the array is
        flattened after sorting. The default is ``-1`` , which sorts along the last axis.
        
    :returns: (*MIArray*) Sorted array.
    """
    if isinstance(a, list):
        a = array(a)
    r = ArrayUtil.sort(a.asarray(), axis)
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
        
def meshgrid(x, y):
    if isinstance(x, list):
        x = array(x)
    if isinstance(y, list):
        y = array(y)
        
    if x.rank != 1 or y.rank != 1:
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
    if isinstance(x, list):
        x = array(x)
    if isinstance(y, list):
        y = array(y)
    r = ArrayMath.lineRegress(x.asarray(), y.asarray())
    return r[0], r[1], r[2], r[3], r[4]
    
def polyval(p, x):
    return MIArray(ArrayMath.polyVal(p, x.asarray()))
    
def transpose(a, dim1=0, dim2=1):
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
    
    if y.rank == 1:
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
            for i in range(y.rank):
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
        
def p2h(press):
    """
    Pressure to height
    
    press: number
        Pressure - hPa
    
    return: number
        Height - meter
    """
    if isinstance(press, MIArray):
        return MIArray(ArrayMath.press2Height(press.asarray()))
    elif isinstance(press, DimArray):
        return DimArray(MIArray(ArrayMath.press2Height(press.asarray())), press.dims, press.fill_value, press.proj)
    else:
        return MeteoMath.press2Height(press)

# Performs a centered difference operation on a array in a specific direction    
def cdiff(a, dimidx):
    if isinstance(a, DimArray):
        r = ArrayMath.cdiff(a.asarray(), dimidx)
        return DimArray(MIArray(r), a.dims, a.fill_value, a.proj)
    else:
        return MIArray(ArrayMath.cdiff(a.asarray(), dimidx))

# Calculates the vertical component of the curl (ie, vorticity)    
def hcurl(u, v):
    if isinstance(u, DimArray) and isinstance(v, DimArray):
        ydim = u.ydim()
        xdim = u.xdim()
        r = ArrayMath.hcurl(u.asarray(), v.asarray(), xdim.getDimValue(), ydim.getDimValue())
        return DimArray(MIArray(r), u.dims, u.fill_value, u.proj)

#  Calculates the horizontal divergence using finite differencing        
def hdivg(u, v):
    if isinstance(u, DimArray) and isinstance(v, DimArray):
        ydim = u.ydim()
        xdim = u.xdim()
        r = ArrayMath.hdivg(u.asarray(), v.asarray(), xdim.getDimValue(), ydim.getDimValue())
        return DimArray(MIArray(r), u.dims, u.fill_value, u.proj)
        
#  Calculates the horizontal divergence using finite differencing        
def magnitude(u, v):
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
    if isinstance(data, Array):
        return data
    elif isinstance(data, (DimArray, MIArray)):
        return data.asarray()
    else:
        return array(data).asarray()

def asmiarray(data):
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
        
def shaperead(fn):
    layer = MILayer(MapDataManage.loadLayer(fn))
    lb = layer.legend().getLegendBreaks()[0]
    if lb.getBreakType() == BreakTypes.PolygonBreak:
        lb.setDrawFill(False)
    return layer
    
def georead(fn):
    layer = MILayer(MapDataManage.loadLayer(fn))
    if layer.isvectorlayer():
        lb = layer.legend().getLegendBreaks()[0]
        if lb.getBreakType() == BreakTypes.PolygonBreak:
            lb.setDrawFill(False)
    return layer
    
def polygon(*args):
    if len(args) == 1:
        polygon = ShapeUtil.createPolygonShape(args[0])
    else:
        x = args[0]
        y = args[1]
        if isinstance(x, MIArray):
            x = x.aslist()
        if isinstance(y, MIArray):
            y = y.aslist()
        polygon = ShapeUtil.createPolygonShape(x, y)
    return polygon
    
def inpolygon(x, y, polygon):
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
    
def maskout(data, x=None, y=None, mask=None):
    """
    Maskout data by polygons - NaN values of elements outside polygons.
    
    :param data: (*array_like*) Array data for maskout.
    :param x: (*array_like*) X coordinate array.
    :param y: (*array_like*) Y coordinate array.
    :param mask: (*list*) Polygon list as maskout borders.

    :returns: (*array_like*) Maskouted data array.
    """
    if mask is None:
        return data
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
    
def griddata(points, values, xi=None, **kwargs):
    method = kwargs.pop('method', 'idw')
    fill_value = kwargs.pop('file_value', nan)
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
    
def addtimedim(infn, outfn, t, tunit='hours'):
    cal = Calendar.getInstance()
    cal.set(t.year, t.month - 1, t.day, t.hour, t.minute, t.second)
    nt = cal.getTime()
    NetCDFDataInfo.addTimeDimension(infn, outfn, nt, tunit)
        
def joinncfile(infns, outfn, tdimname):
    NetCDFDataInfo.joinDataFiles(infns, outfn, tdimname)
    
def binread(fn, dim, datatype=None, skip=0, byteorder='little_endian'):
    """
    Read data array from a binary file.
    
    :param dim: (*list*) Dimensions.
    :param datatype: (*string*) Data type string.
    :param skip: (*int*) Skip bytes number.
    :param byteorder: (*string*) Byte order. ``little_endian`` or ``big_endian``.
    
    :returns: (*MIArray*) Data array
    """
    r = ArrayUtil.readBinFile(fn, dim, datatype, skip, byteorder);
    return MIArray(r)
        
def binwrite(fn, data, byteorder='little_endian'):
    """
    Create a binary data file from an array variable.
    
    :param fn: (*string*) Path needed to locate binary file.
    :param data: (*array_like*) A numeric array variable of any dimensionality.
    :param byteorder: (*string*) Byte order. ``little_endian`` or ``big_endian``.
    """
    ArrayUtil.saveBinFile(fn, data.asarray(), byteorder)    
    
# Get month abstract English name
def monthname(m):  
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