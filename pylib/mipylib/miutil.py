#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2015-12-23
# Purpose: MeteoInfo util module
# Note: Jython
#-----------------------------------------------------

from org.meteoinfo.global.util import DateUtil
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