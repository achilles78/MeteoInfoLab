#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2014-12-27
# Purpose: MeteoInfo Dataset module
# Note: Jython
#-----------------------------------------------------
from org.meteoinfo.data.meteodata import MeteoDataInfo
from ucar.ma2 import Section
from ucar.nc2 import Attribute
from ucar.ma2 import DataType
import dimvariable
from dimvariable import DimVariable
import dimarray
from dimarray import PyGridData, PyStationData
import milayer
from milayer import MILayer, MIXYListData

from datetime import datetime

from java.util import Calendar
import jarray

# Dimension dataset
class DimDataFile():
    
    # dataset must be org.meteoinfo.data.meteodata.MeteoDataInfo
    def __init__(self, dataset=None, ncfile=None):
        self.dataset = dataset
        if not dataset is None:
            self.filename = dataset.getFileName()
            self.nvar = dataset.getDataInfo().getVariableNum()
            self.fill_value = dataset.getMissingValue()
            self.proj = dataset.getProjectionInfo()
        self.ncfile = ncfile
        
    def __getitem__(self, key):
        if isinstance(key, str):
            #print key
            return DimVariable(self.dataset.getDataInfo().getVariable(key), self)
        return None
        
    def __str__(self):
        return self.dataset.getInfoText()
        
    def __repr__(self):
        if self.dataset is None:
            return 'None'
        return self.dataset.getInfoText()
        
    def read(self, varname, origin, size, stride):
        return self.dataset.read(varname, origin, size, stride)
        
    def dump(self):
        print self.dataset.getInfoText()
        
    def griddata(self, varname='var', timeindex=0, levelindex=0, yindex=None, xindex=None):
        if self.dataset.isGridData():
            self.dataset.setTimeIndex(timeindex)
            self.dataset.setLevelIndex(levelindex)
            gdata = PyGridData(self.dataset.getGridData(varname))
            return gdata
        else:
            return None
        
    def stationdata(self, varname='var', timeindex=0, levelindex=0):
        if self.dataset.isStationData():
            self.dataset.setTimeIndex(timeindex)
            self.dataset.setLevelIndex(levelindex)
            sdata = PyStationData(self.dataset.getStationData(varname))
            return sdata
        else:
            return None
            
    def trajlayer(self):
        if self.dataset.isTrajData():
            return MILayer(self.dataset.getDataInfo().createTrajLineLayer())
        else:
            return None
            
    def trajplayer(self):
        if self.dataset.isTrajData():
            return MILayer(self.dataset.getDataInfo().createTrajPointLayer())
        else:
            return None
            
    def trajsplayer(self):
        if self.dataset.isTrajData():
            return MILayer(self.dataset.getDataInfo().createTrajStartPointLayer())
        else:
            return None
            
    def trajvardata(self, varidx):
        if self.dataset.isTrajData():
            return MIXYListData(self.dataset.getDataInfo().getXYDataset(varidx))
        else:
            return None
            
    def gettime(self, idx):
        date = self.dataset.getDataInfo().getTimes().get(idx)
        cal = Calendar.getInstance()
        cal.setTime(date)
        year = cal.get(Calendar.YEAR)
        month = cal.get(Calendar.MONTH) + 1
        day = cal.get(Calendar.DAY_OF_MONTH)
        hour = cal.get(Calendar.HOUR_OF_DAY)
        minute = cal.get(Calendar.MINUTE)
        second = cal.get(Calendar.SECOND)
        dt = datetime(year, month, day, hour, minute, second)
        return dt
        
    def bigendian(self, big_endian):
        if self.dataset.getDataInfo().getDataType().isGrADS():
            self.dataset.getDataInfo().setBigEndian(big_endian)
            
    def tostation(self, varname, x, y, z, t):
        cal = Calendar.getInstance()
        cal.set(t.year, t.month - 1, t.day, t.hour, t.minute, t.second)
        nt = cal.getTime()
        if z is None:
            return self.dataset.toStation(varname, x, y, nt)
        else:
            return self.dataset.toStation(varname, x, y, z, nt)
            
    def adddim(self, dimname, dimsize, group=None):
        return self.ncfile.addDimension(group, dimname, dimsize)
        
    def addgroupattr(self, attrname, attrvalue, group=None):
        return self.ncfile.addGroupAttribute(group, Attribute(attrname, attrvalue))
 
    def __getdatatype(self, datatype):
        if datatype == 'string':
            dt = DataType.STRING
        elif datatype == 'int':
            dt = DataType.INT
        elif datatype == 'float':
            dt = DataType.FLOAT
        elif datatype == 'double':
            dt = DataType.DOUBLE
        elif datatype == 'char':
            dt = DataType.CHAR
        else:
            dt = DataType.STRING
        return dt
 
    def addvar(self, varname, datatype, dims, group=None):
        dt = self.__getdatatype(datatype)
        return DimVariable(ncvariable=self.ncfile.addVariable(group, varname, dt, dims))
        
    def create(self):
        self.ncfile.create()
        
    def write(self, variable, value, origin=None):
        if origin is None:
            self.ncfile.write(variable.ncvariable, value.asarray())
        else:
            origin = jarray.array(origin, 'i')
            self.ncfile.write(variable.ncvariable, origin, value.asarray())
    def flush(self):
        self.ncfile.flush()
        
    def close(self):
        self.ncfile.close()
        
    def largefile(self, islarge=True):
        self.ncfile.setLargeFile(islarge)