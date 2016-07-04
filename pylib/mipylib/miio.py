#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2016-7-4
# Purpose: MeteoInfo io module
# Note: Jython
#-----------------------------------------------------

import datetime
import minum
import miutil
import miarray
from miarray import MIArray
from org.meteoinfo.data.meteodata import Dimension, DimensionType

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
    
def dimension(dimvalue, dimname='null', dimtype=None):
    """
    Create a new Dimension.
    
    :param dimvalue: (*array_like*) Dimension value.
    :param dimname: (*string*) Dimension name.
    :param dimtype: (*DimensionType*) Dimension type.
    """
    if isinstance(dimvalue, (MIArray, DimArray)):
        dimvalue = dimvalue.aslist()
    dtype = DimensionType.Other
    if not dimtype is None:
        if dimtype.upper() == 'X':
            dtype = DimensionType.X
        elif dimtype.upper() == 'Y':
            dtype = DimensionType.Y
        elif dimtype.upper() == 'Z':
            dtype = DimensionType.Z
        elif dimtype.upper() == 'T':
            dtype = DimensionType.T
    dim = Dimension(dtype)
    dim.setDimValues(dimvalue)
    dim.setShortName(dimname)
    return dim
    
def ncwrite(fn, data, varname, dims=None, attrs=None):
    """
    Write a netCDF data file.
    
    :param: fn: (*string*) netCDF data file path.
    :param data: (*array_like*) A numeric array variable of any dimensionality.
    :param varname: (*string*) Variable name.
    :param dims: (*list of dimensions*) Dimension list.
    """
    if dims is None:
        if isinstance(data, MIArray):
            dims = []
            for s in data.shape:
                dimvalue = arange(s)
                dimname = 'dim' + str(len(dims))
                dims.append(dimension(dimvalue, dimname))
        else:
            dims = data.dims
    #New netCDF file
    ncfile = minum.addfile(fn, 'c')
    #Add dimensions
    ncdims = []
    for dim in dims:
        ncdims.append(ncfile.adddim(dim.getShortName(), dim.getLength()))
    #Add global attributes
    ncfile.addgroupattr('Conventions', 'CF-1.6')
    ncfile.addgroupattr('Tools', 'Created using MeteoInfo')
    #Add dimension variables
    dimvars = []
    for dim,midim in zip(ncdims,dims):
        dimtype = midim.getDimType()
        dimname = dim.getShortName()
        if dimtype == DimensionType.T:
            var = ncfile.addvar(dimname, 'int', [dim])
            var.addattr('units', 'hours since 1900-01-01 00:00:0.0')
            var.addattr('long_name', 'Time')
            var.addattr('standard_name', 'time')
            var.addattr('axis', 'T')
            tvar = var
        elif dimtype == DimensionType.Z:
            var = ncfile.addvar(dimname, 'float', [dim])
            var.addattr('axis', 'Z')
        elif dimtype == DimensionType.Y:
            var = ncfile.addvar(dimname, 'float', [dim])
            var.addattr('axis', 'Y')
        elif dimtype == DimensionType.X:
            var = ncfile.addvar(dimname, 'float', [dim])
            var.addattr('axis', 'X')
        else:
            var = ncfile.addvar(dim.getShortName(), 'float', [dim])
            var.addattr('axis', 'null')
        dimvars.append(var)
    #Add variable
    var = ncfile.addvar(varname, data.datatype, ncdims)
    if attrs is None:    
        var.addattr('name', varname)
    else:
        for key in attrs:
            var.addattr(key, attr[key])
    #Create netCDF file
    ncfile.create()
    #Write variable data
    for dimvar, dim in zip(dimvars, dims):
        if dim.getDimType() == DimensionType.T:
            sst = datetime.datetime(1900,1,1)
            tt = miutil.nums2dates(dim.getDimValue())
            hours = []
            for t in tt:
                hours.append((t - sst).total_seconds() // 3600)
            ncfile.write(dimvar, minum.array(hours))
        else:
            ncfile.write(dimvar, minum.array(dim.getDimValue()))
    ncfile.write(var, data)
    #Close netCDF file
    ncfile.close()