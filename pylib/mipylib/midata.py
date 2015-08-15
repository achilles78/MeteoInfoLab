#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2014-12-27
# Purpose: MeteoInfo Dataset module
# Note: Jython
#-----------------------------------------------------
import os
import math
from org.meteoinfo.data import GridData, StationData, DataMath, TableData, TimeTableData, ArrayMath, ArrayUtil, TableUtil
from org.meteoinfo.data.meteodata import MeteoDataInfo
from org.meteoinfo.data.mapdata import MapDataManage
from org.meteoinfo.data.analysis import MeteoMath
from org.meteoinfo.geoprocess import GeoComputation
from org.meteoinfo.projection import KnownCoordinateSystems, ProjectionInfo, Reproject
from org.meteoinfo.global import PointD
from org.meteoinfo.shape import ShapeUtil

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
        self.timedata = isinstance(data, TimeTableData)
        
    def __getitem__(self, key):
        if isinstance(key, str):
            print key     
            coldata = self.data.getColumnData(key)
            if coldata.getDataType().isNumeric():
                return MIArray(ArrayUtil.array(coldata.getDataValues()))
            else:
                return coldata.getData()
        return None
        
    def __setitem__(self, key, value):
        if isinstance(value, MIArray):
            self.data.setColumnData(key, value.aslist())
        else:
            self.data.setColumnData(key, value)
    
    def colnames(self):
        return self.data.getDataTable().getColumnNames()
    
    def coldata(self, key):
        if isinstance(key, str):
            print key     
            values = self.data.getColumnData(key).getDataValues()
            return MIArray(ArrayUtil.array(values))
        return None
    
    def addcol(self, colname, dtype, coldata):
        if isinstance(coldata, MIArray):
            self.data.addColumnData(colname, dtype, coldata.aslist())
        else:
            self.data.addColumnData(colname, dtype, coldata)
        
    def delcol(self, colname):
        self.data.removeColumn(colname)
        
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
        
    def ave_year(self, colnames):
        if not self.timedata:
            print 'There is no time column!'
            return None
        else:
            cols = self.data.findColumns(colnames)
            dtable = self.data.ave_Year(cols)
            return PyTableData(TableData(dtable))
            
    def ave_yearmonth(self, colnames, month):
        if not self.timedata:
            print 'There is no time column!'
            return None
        else:
            cols = self.data.findColumns(colnames)
            dtable = self.data.ave_YearMonth(cols, month)
            return PyTableData(TableData(dtable))
            
    def clone(self):
        return PyTableData(self.data.clone())

#################################################################  

def __getfilename(fname):
    s5 = fname[0:5]
    isweb = False
    if s5 == 'http:' or s5 == 'dods:' or s5 == 'dap4:':
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
          
def addfile(fname):
    fname = fname.strip()
    fname, isweb = __getfilename(fname)
    if fname is None:
        return None

    if isweb:
        return addfile_nc(fname, False)
    
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
    tdata = TableUtil.readASCIIFile(filename, delimiter, headerlines, format, encoding)
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
    return MIArray(ArrayUtil.arrayRange1(start, n, step))
    
def linspace(start=0, stop=1, n=100, endpoint=True, retstep=False, dtype=None):
    return MIArray(ArrayUtil.lineSpace(start, stop, n, endpoint))
    
def zeros(shape, dtype='float'):
    shapelist = []
    if isinstance(shape, int):
        shapelist.append(shape)
    else:
        shapelist = shape
    return MIArray(ArrayUtil.zeros(shapelist, dtype))
    
def ones(shape, dtype='float'):
    shapelist = []
    if isinstance(shape, int):
        shapelist.append(shape)
    else:
        shapelist = shape
    return MIArray(ArrayUtil.ones(shapelist, dtype))
    
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
        
def exp(a):
    if isinstance(a, DimArray) or isinstance(a, MIArray):
        return a.exp()
    else:
        return math.exp(a)
        
def log(a):
    if isinstance(a, DimArray) or isinstance(a, MIArray):
        return a.log()
    else:
        return math.log(a)
        
def log10(a):
    if isinstance(a, DimArray) or isinstance(a, MIArray):
        return a.log10()
    else:
        return math.log10(a)
        
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
        
def linregress(x, y):
    if isinstance(x, list):
        xl = x
    else:
        xl = x.asarray()
    if isinstance(y, list):
        yl = y
    else:
        yl = y.asarray()
    r = ArrayMath.lineRegress(xl, yl)
    return r[0], r[1], r[2]
    
def polyval(p, x):
    return ArrayMath.polyVal(p, x.asarray())
    
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
        return MeteoMath.dewpoint2rh(dewpoint, temp)

# Performs a centered difference operation on a grid data in the x or y direction    
def cdiff(a, isx):
    if isinstance(isx, str):
        if isx.lower() == 'x':
            isx = True
        else:
            isx = False
    if isinstance(a, DimArray):
        r = ArrayMath.cdiff(a.asarray(), isx)
        return DimArray(MIArray(r), a.dims, a.fill_value, a.proj)
    else:
        return MIArray(ArrayMath.cdiff(a.asarray(), isx))

# Calculates the vertical component of the curl (ie, vorticity)    
def hcurl(u, v):
    if isinstance(u, DimArray) and isinstance(v, DimArray):
        ydim = u.dims[0]
        xdim = u.dims[1]
        r = ArrayMath.hcurl(u.asarray(), v.asarray(), xdim.getDimValue(), ydim.getDimValue())
        return DimArray(MIArray(r), u.dims, u.fill_value, u.proj)

#  Calculates the horizontal divergence using finite differencing        
def hdivg(u, v):
    if isinstance(u, DimArray) and isinstance(v, DimArray):
        ydim = u.dims[0]
        xdim = u.dims[1]
        r = ArrayMath.hdivg(u.asarray(), v.asarray(), xdim.getDimValue(), ydim.getDimValue())
        return DimArray(MIArray(r), u.dims, u.fill_value, u.proj)
        
#  Calculates the horizontal divergence using finite differencing        
def magnitude(u, v):
    if isinstance(u, DimArray) and isinstance(v, DimArray):
        r = ArrayMath.magnitude(u.asarray(), v.asarray())
        return DimArray(MIArray(r), u.dims, u.fill_value, u.proj)
    
def asgriddata(data, x=None, y=None, fill_value=-9999.0):
    if x is None:    
        if isinstance(data, PyGridData):
            return data
        elif isinstance(data, DimArray):
            return data.asgriddata()
        else:
            return None
    else:
        gdata = GridData(data.asarray(), x.asarray(), y.asarray(), fill_value)
        return PyGridData(gdata)
        
def asstationdata(data, x, y, fill_value=-9999.0):
    stdata = StationData(data.asarray(), x.asarray(), y.asarray(), fill_value)
    return PyStationData(stdata)
        
def shaperead(fn):
    layer = MapDataManage.loadLayer(fn) 
    return layer
    
def georead(fn):
    layer = MapDataManage.loadLayer(fn) 
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
            r = ArrayUtil.interpolation_IDW_Neighbor(x_s.aslist(), y_s.aslist(), values, x_g.aslist(), y_g.aslist(), pnum, fill_value)
            return MIArray(r), x_g, y_g
        else:
            r = ArrayUtil.interpolation_IDW_Radius(x_s.aslist(), y_s.aslist(), values, x_g.aslist(), y_g.aslist(), pnum, radius, fill_value)
            return MIArray(r), x_g, y_g
    elif method == 'cressman':
        radius = kwargs.pop('radius', [10, 7, 4, 2, 1])
        if isinstance(radius, MIArray):
            radius = radius.aslist()
        r = ArrayUtil.cressman(x_s.aslist(), y_s.aslist(), values, x_g.aslist(), y_g.aslist(), fill_value, radius)
        return MIArray(r), x_g, y_g
    elif method == 'neareast':
        radius = kwargs.pop('radius', inf)
        r = ArrayUtil.interpolation_Nearest(x_s.aslist(), y_s.aslist(), values, x_g.aslist(), y_g.aslist(), radius, fill_value)
        return MIArray(r), x_g, y_g
    elif method == 'inside':
        r = ArrayUtil.interpolation_Inside(x_s.aslist(), y_s.aslist(), values, x_g.aslist(), y_g.aslist(), fill_value)
        return MIArray(r), x_g, y_g    
    elif method == 'surface':        
        r = ArrayUtil.interpolation_Surface(x_s.asarray(), y_s.asarray(), values, x_g.asarray(), y_g.asarray(), fill_value)
        return MIArray(r), x_g, y_g
    else:
        return None

def projinfo(proj='longlat', **kwargs):
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
    if isinstance(fromproj, str):
        fromproj = ProjectionInfo(fromproj)
    if isinstance(toproj, str):
        toproj = ProjectionInfo(toproj)
    if isinstance(x, MIArray) or isinstance(x, DimArray):
        outxy = ArrayUtil.reproject(x.asarray(), y.asarray(), fromproj, toproj)
        return MIArray(outxy[0]), MIArray(outxy[1])
    else:
        inpt = PointD(x, y)
        outpt = Reproject.reprojectPoint(inpt, fromproj, toproj)
        return outpt.X, outpt.Y
    
def projectxy(lllon, lllat, xnum, ynum, dx, dy, toproj, fromproj=None):
    x, y = project(lllon, lllat, toproj, fromproj)
    xx = arange1(x, xnum, dx)
    yy = arange1(y, ynum, dy)
    return xx, yy