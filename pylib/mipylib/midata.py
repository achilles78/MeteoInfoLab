#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2014-12-27
# Purpose: MeteoInfo Dataset module
# Note: Jython
#-----------------------------------------------------
import os
import math
from org.meteoinfo.data import GridData, StationData, DataMath, TableData, ArrayMath, ArrayUtil
from org.meteoinfo.data.meteodata import MeteoDataInfo
from org.meteoinfo.data.mapdata import MapDataManage

import dimdatafile
import dimvariable
import dimarray
import miarray
from dimdatafile import DimDataFile
from dimvariable import DimVariable
from dimarray import PyGridData, DimArray, PyStationData
from miarray import MIArray

from java.awt import Color
from java.lang import Math, Double

# Global variables
pi = Math.PI
e = Math.E
inf = Double.POSITIVE_INFINITY
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
        
    def __getitem__(self, key):
        if isinstance(key, str):
            print key
            return self.data.getColumnData(key).getDataValues()
        return None
        
    def addcolumn(self, colname, dtype, coldata):
        self.data.addColumnData(colname, dtype, coldata)
        
    def savefile(self, filename):
        self.data.saveAsCSVFile(filename)

#################################################################  

def __getfilename(fname):
    if os.path.exists(fname):
        if os.path.isabs(fname):
            return fname
        else:
            return os.path.join(currentfolder, fname)
    else:
        if currentfolder != None:
            fname = os.path.join(currentfolder, fname)
            if os.path.isfile(fname):
                return fname
            else:
                print 'File not exist: ' + fname
                return None
        else:
            print 'File not exist: ' + fname
            return None
      
def addfile_grads(fname):
    fname = __getfilename(fname)
    meteodata = MeteoDataInfo()
    meteodata.openGrADSData(fname)
    __addmeteodata(meteodata)
    datafile = DimDataFile(meteodata)
    return datafile
    
def addfile(fname):
    fname = __getfilename(fname)
    if os.path.splitext(fname)[1] == '.ctl':
        return addfile_grads(fname)
    
    meteodata = MeteoDataInfo()
    meteodata.openData(fname)
    __addmeteodata(meteodata)
    datafile = DimDataFile(meteodata)
    return datafile
    
def addfile_nc(fname):
    fname = __getfilename(fname)
    meteodata = MeteoDataInfo()
    meteodata.openNetCDFData(fname)
    __addmeteodata(meteodata)
    datafile = DimDataFile(meteodata)
    return datafile
    
def addfile_arl(fname):
    fname = __getfilename(fname)
    meteodata = MeteoDataInfo()
    meteodata.openARLData(fname)
    __addmeteodata(meteodata)
    datafile = DimDataFile(meteodata)
    return datafile
    
def addfile_surfer(fname):
    fname = __getfilename(fname)
    meteodata = MeteoDataInfo()
    meteodata.openSurferGridData(fname)
    __addmeteodata(meteodata)
    datafile = DimDataFile(meteodata)
    return datafile
    
def addfile_mm5(fname):
    fname = __getfilename(fname)
    meteodata = MeteoDataInfo()
    meteodata.openMM5Data(fname)
    __addmeteodata(meteodata)
    datafile = DimDataFile(meteodata)
    return datafile
    
def addfile_micaps(fname):
    fname = __getfilename(fname)
    meteodata = MeteoDataInfo()
    meteodata.openMICAPSData(fname)
    __addmeteodata(meteodata)
    datafile = DimDataFile(meteodata)
    return datafile
    
def addfile_hyconc(fname):
    fname = __getfilename(fname)
    meteodata = MeteoDataInfo()
    meteodata.openHYSPLITConcData(fname)
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

def asciiread(filename, **kwargs):
    delimiter = kwargs.pop('delimiter', None)
    datatype = kwargs.pop('datatype', None)
    headerlines = kwargs.pop('headerlines', 0)
    shape = kwargs.pop('shape', None)    
    a = ArrayUtil.readASCIIFile(filename, delimiter, headerlines, datatype, shape)
    return MIArray(a)
        
def readtable(filename, **kwargs):
    delimiter = kwargs.pop('delimiter', ',')
    format = kwargs.pop('format', None)
    headerlines = kwargs.pop('headerlines', 0)
    encoding = kwargs.pop('encoding', 'UTF8')
    tdata = TableData()
    tdata.readASCIIFile(filename, delimiter, headerlines, format, encoding)
    return PyTableData(tdata)

def array(data):
    return MIArray(ArrayUtil.array(data))
    
def arange(*args):
    if len(args) == 1:
        start = 0
        stop = args[0]
        step = 1
    elif len(args) == 2:
        start = 0
        stop = args[0]
        step = args[1]
    else:
        start = args[0]
        stop = args[1]
        step = args[2]
    return MIArray(ArrayUtil.arrayRange(start, stop, step))
    
def arange1(start, n, step):
    return MIArray(ArrayUtil.arrayRange(start, n, step))
    
def linspace(start=0, stop=1, n=100, dtype=None):
    return MIArray(ArrayUtil.lineSpace(start, stop, n))
    
def zeros(n):
    return MIArray(ArrayUtil.zeros(n))
    
def ones(n):
    return MIArray(ArrayUtil.ones(n))
    
def sqrt(a):
    if isinstance(a, DimArray) or isinstance(a, MIArray):
        return a.sqrt()
    else:
        return math.sqrt(a)

def sin(a):
    if isinstance(a, DimArray) or isinstance(a, MIArray):
        return a.sin()
    else:
        return math.sin(a)
    
def cos(a):
    if isinstance(a, DimArray) or isinstance(a, MIArray):
        return a.cos()
    else:
        return math.cos(a)
    
def asgriddata(data, x=None, y=None, missingv=-9999.0):
    if x == None:    
        if isinstance(data, PyGridData):
            return data
        elif isinstance(data, DimArray):
            return data.asgriddata()
        else:
            return None
    else:
        gdata = GridData(data.array, x.array, y.array, missingv)
        return PyGridData(gdata)
        
def shaperead(fn):
    layer = MapDataManage.loadLayer(fn)
    pgb = layer.getLegendScheme().getLegendBreaks().get(0)
    pgb.setDrawFill(False)
    pgb.setOutlineColor(Color.darkGray) 
    return layer