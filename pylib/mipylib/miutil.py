#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2015-12-23
# Purpose: MeteoInfo util module
# Note: Jython
#-----------------------------------------------------

from org.meteoinfo.global import PointD
from org.meteoinfo.global.util import DateUtil
from org.meteoinfo.shape import PointShape, PolylineShape, PolygonShape, ShapeUtil
from java.util import Calendar
import datetime
import minum

def pydate(t):    
    """
    Convert java date to python date.
    
    :param t: Java date
    
    :returns: Python date
    """
    cal = Calendar.getInstance()
    cal.setTime(t)
    year = cal.get(Calendar.YEAR)
    month = cal.get(Calendar.MONTH) + 1
    day = cal.get(Calendar.DAY_OF_MONTH)
    hour = cal.get(Calendar.HOUR_OF_DAY)
    minute = cal.get(Calendar.MINUTE)
    second = cal.get(Calendar.SECOND)
    dt = datetime.datetime(year, month, day, hour, minute, second)
    return dt
    
def jdate(t):
    """
    Convert python date to java date.
    
    :param t: Python date
    
    :returns: Java date
    """
    cal = Calendar.getInstance()
    if isinstance(t, list):
        r = []
        for tt in t:
            cal.set(tt.year, tt.month - 1, tt.day, tt.hour, tt.minute, tt.second)
            r.append(cal.getTime())
        return r
    else:
        cal.set(t.year, t.month - 1, t.day, t.hour, t.minute, t.second)
        return cal.getTime()
    
def date2num(t):
    """
    Convert python date to numerical value.
    
    :param t: Python date.
    
    :returns: Numerical value
    """
    tt = jdate(t)
    v = DateUtil.toOADate(tt)
    return v

def makeshapes(x, y, type=None):
    """
    Make shapes by x and y coordinates.
    
    :param x: (*array_like*) X coordinates.
    :param y: (*array_like*) Y coordinates.
    :param type: (*string*) Shape type [point | line | polygon].
    
    :returns: Shapes
    """
    shapes = []   
    if isinstance(x, (int, float)):
        shape = PointShape()
        shape.setPoint(PointD(x, y))
        shapes.append(shape)    
    else:
        if not isinstance(x, list):
            x = x.asarray()
        if not isinstance(y, list):
            y = y.asarray()
        if type == 'point':
            shapes = ShapeUtil.createPointShapes(x, y)
        elif type == 'line':
            shapes = ShapeUtil.createPolylineShapes(x, y)
        elif type == 'polygon':
            shapes = ShapeUtil.createPolygonShapes(x, y)
    return shapes    
    
def grib2nc(infn, outfn):
    """
    Convert GRIB data file to netCDF data file.
    
    :param infn: (*string*) Input GRIB data file name.
    :param outfn: (*string*) Output netCDF data file name.
    """
    #Open GRIB file
    f = minum.addfile(infn)
    #New netCDF file
    ncfile = minum.addfile(outfn, 'c')
    #Add dimensions
    for dim in f.dimensions():
        ncfile.adddim(dim.getShortName(), dim.getLength())
    #Add global attributes
    for attr in f.attributes():
        ncfile.addgroupattr(attr.getName(), attr.getValues())
    #Add variables
    variables = []
    for var in f.variables():    
        #print 'Variable: ' + var.getShortName()
        nvar = ncfile.addvar(var.getShortName(), var.getDataType(), var.getDimensions())
        for attr in var.getAttributes():
            nvar.addattr(attr.getName(), attr.getValues())
        variables.append(nvar)
    #Create netCDF file
    ncfile.create()
    #Write data
    for var in variables:
        print 'Variable: ' + var.name
        data = f[str(var.name)].read()
        ncfile.write(var, data)
    #Close netCDF file
    ncfile.close()
    print 'Convert finished!'
    
def grads2nc(infn, outfn, big_endian=None):
    """
    Convert GrADS data file to netCDF data file.
    
    :param infn: (*string*) Input GrADS data file name.
    :param outfn: (*string*) Output netCDF data file name.
    :param big_endian: (*boolean*) Is GrADS data big_endian or not.
    """
    #Open GrADS file
    f = minum.addfile_grads(infn)
    if not big_endian is None:
        f.bigendian(big_endian)

    #New netCDF file
    ncfile = minum.addfile(outfn, 'c')

    #Add dimensions
    dims = []
    for dim in f.dimensions():
        dims.append(ncfile.adddim(dim.getShortName(), dim.getLength()))
    xdim = f.finddim('X')
    ydim = f.finddim('Y')
    tdim = f.finddim('T')
    xnum = xdim.getLength()
    ynum = ydim.getLength()
    tnum = tdim.getLength()

    #Add global attributes
    ncfile.addgroupattr('Conventions', 'CF-1.6')
    for attr in f.attributes():
        ncfile.addgroupattr(attr.getName(), attr.getValues())

    #Add dimension variables
    dimvars = []
    for dim in dims:
        dname = dim.getShortName()
        if dname == 'T':
            var = ncfile.addvar('time', 'int', [dim])
            var.addattr('units', 'hours since 1900-01-01 00:00:0.0')
            var.addattr('long_name', 'Time')
            var.addattr('standard_name', 'time')
            var.addattr('axis', dname)
            tvar = var
        elif dname == 'Z':
            var = ncfile.addvar('level', 'float', [dim])
            var.addattr('axis', dname)
        else:
            var = ncfile.addvar(dim.getShortName(), 'float', [dim])
            if 'Z' in dname:
                var.addattr('axis', 'Z')
            else:
                var.addattr('axis', dname)
        dimvars.append(var)

    #Add variables
    variables = []
    for var in f.variables():    
        print 'Variable: ' + var.getShortName()
        vdims = []
        for vdim in var.getDimensions():
            for dim in dims:
                if vdim.getShortName() == dim.getShortName():
                    vdims.append(dim)
        #print vdims
        nvar = ncfile.addvar(var.getShortName(), var.getDataType(), vdims)
        nvar.addattr('fill_value', -9999.0)
        for attr in var.getAttributes():
            nvar.addattr(attr.getName(), attr.getValues())
        variables.append(nvar)

    #Create netCDF file
    ncfile.create()

    #Write variable data
    for dimvar, dim in zip(dimvars, f.dimensions()):
        if dim.getShortName() != 'T':
            ncfile.write(dimvar, minum.array(dim.getDimValue()))

    sst = datetime.datetime(1900,1,1)
    for t in range(0, tnum):
        st = f.gettime(t)
        print st.strftime('%Y-%m-%d %H:00')
        hours = (st - sst).total_seconds() // 3600
        origin = [t]
        ncfile.write(tvar, minum.array([hours]), origin=origin)
        for var in variables:
            print 'Variable: ' + var.name
            if var.ndim == 3:
                data = f[str(var.name)][t,:,:]    
                data[data==minum.nan] = -9999.0        
                origin = [t, 0, 0]
                shape = [1, ynum, xnum]
                data = data.reshape(shape)
                ncfile.write(var, data, origin=origin)
            else:
                znum = var.dims[1].getLength()
                for z in range(0, znum):
                    data = f[str(var.name)][t,z,:,:]
                    data[data==minum.nan] = -9999.0
                    origin = [t, z, 0, 0]
                    shape = [1, 1, ynum, xnum]
                    data = data.reshape(shape)
                    ncfile.write(var, data, origin=origin)

    #Close netCDF file
    ncfile.close()
    print 'Convert finished!'