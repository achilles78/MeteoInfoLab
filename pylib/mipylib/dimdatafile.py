#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2014-12-27
# Purpose: MeteoInfo Dataset module
# Note: Jython
#-----------------------------------------------------
from org.meteoinfo.data.meteodata import MeteoDataInfo
from ucar.ma2 import Section, DataType
from ucar.nc2 import Attribute
import dimvariable
from dimvariable import DimVariable
import dimarray
from dimarray import DimArray, PyGridData, PyStationData
import milayer
from milayer import MILayer, MIXYListData
import miarray
from miarray import MIArray

from datetime import datetime

from java.util import Calendar
from java.lang import Float
import jarray

# Dimension dataset
class DimDataFile():
    
    # dataset must be org.meteoinfo.data.meteodata.MeteoDataInfo
    def __init__(self, dataset=None, ncfile=None, arldata=None, bufrdata=None):
        self.dataset = dataset
        if not dataset is None:
            self.filename = dataset.getFileName()
            self.nvar = dataset.getDataInfo().getVariableNum()
            self.fill_value = dataset.getMissingValue()
            self.proj = dataset.getProjectionInfo()
        self.ncfile = ncfile
        self.arldata = arldata
        self.bufrdata = bufrdata
        
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
        
    def close(self):
        if not self.dataset is None:
            self.dataset.close()
        elif not self.arldata is None:
            self.arldata.closeDataFile()
        elif not self.bufrdata is None:
            self.bufrdata.closeDataFile()
    
    def dimensions(self):
        return self.dataset.getDataInfo().getDimensions()
        
    def finddim(self, name):
        for dim in self.dataset.getDataInfo().getDimensions():
            if name == dim.getShortName():
                return dim
        return None
        
    def attributes(self):
        return self.dataset.getDataInfo().getGlobalAttributes()
    
    def attrvalue(self, key):
        attr = self.dataset.getDataInfo().findGlobalAttribute(key)
        if attr is None:
            return None
        v = MIArray(attr.getValues())
        return v
        
    def variables(self):
        return self.dataset.getDataInfo().getVariables()
        
    def varnames(self):
        return self.dataset.getDataInfo().getVariableNames()
        
    def read(self, varname, origin=None, size=None, stride=None):
        if origin is None:
            return self.dataset.read(varname)
        else:
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
            
    def stinfodata(self):
        if self.dataset.isStationData():
            sidata = self.dataset.getStationInfoData()
            return sidata
        else:
            return None
            
    def smodeldata(self, timeindex=0, levelindex=0):
        if self.dataset.isStationData():
            self.dataset.setTimeIndex(timeindex)
            self.dataset.setLevelIndex(levelindex)
            smdata = self.dataset.getStationModelData()
            return smdata
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
            
    def trajvardata(self, varidx, hourx=False):
        if self.dataset.isTrajData():
            if hourx:
                return MIXYListData(self.dataset.getDataInfo().getXYDataset_HourX(varidx))
            else:
                return MIXYListData(self.dataset.getDataInfo().getXYDataset(varidx))
        else:
            return None
    
    def timenum(self):
        """
        Get time dimension length
        
        :returns: (*int*) Time dimension length.
        """
        return self.dataset.getDataInfo().getTimeNum()
    
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
        if isinstance(t, datetime):
            cal = Calendar.getInstance()
            cal.set(t.year, t.month - 1, t.day, t.hour, t.minute, t.second)
            t = cal.getTime()
        if z is None:
            return self.dataset.toStation(varname, x, y, t)
        else:
            return self.dataset.toStation(varname, x, y, z, t)
    
    #Write netCDF data    
    def adddim(self, dimname, dimsize, group=None):
        return self.ncfile.addDimension(group, dimname, dimsize)
        
    def addgroupattr(self, attrname, attrvalue, group=None, float=False):
        if float:
            if isinstance(attrvalue, (list, tuple)):
                for i in range(len(attrvalue)):
                    attrvalue[i] = Float(attrvalue[i])
            else:
                attrvalue = Float(attrvalue)
        return self.ncfile.addGroupAttribute(group, Attribute(attrname, attrvalue))
 
    def __getdatatype(self, datatype):
        if isinstance(datatype, str):
            if datatype == 'string':
                dt = DataType.STRING
            elif datatype == 'int':
                dt = DataType.INT
            elif datatype == 'long':
                dt = DataType.LONG
            elif datatype == 'float':
                dt = DataType.FLOAT
            elif datatype == 'double':
                dt = DataType.DOUBLE
            elif datatype == 'char':
                dt = DataType.CHAR
            else:
                dt = DataType.STRING
            return dt
        else:
            return datatype
 
    def addvar(self, varname, datatype, dims, group=None):
        dt = self.__getdatatype(datatype)        
        return DimVariable(ncvariable=self.ncfile.addVariable(group, varname, dt, dims))
        
    def create(self):
        self.ncfile.create()
        
    def write(self, variable, value, origin=None):
        if isinstance(value, (DimArray, MIArray)):
            value = value.asarray()
        if origin is None:
            self.ncfile.write(variable.ncvariable, value)
        else:
            origin = jarray.array(origin, 'i')
            self.ncfile.write(variable.ncvariable, origin, value)
    def flush(self):
        self.ncfile.flush()
        
    def close(self):
        if not self.ncfile is None:
            self.ncfile.close()
        elif not self.arldata is None:
            self.arldata.closeDataFile()
        elif not self.bufrdata is None:
            self.bufrdata.closeDataFile()
        
    def largefile(self, islarge=True):
        self.ncfile.setLargeFile(islarge)
        
    # Write ARL data
    def setx(self, x):
        self.arldata.setX(x.aslist())
        
    def sety(self, y):
        self.arldata.setY(y.aslist())
        
    def setlevels(self, levels):
        if isinstance(levels, MIArray):
            levels = levels.aslist()
        if levels[0] != 1:
            levels.insert(0, 1)
        self.arldata.levels = levels
        
    def set2dvar(self, vnames):
        self.arldata.LevelVarList.add(vnames)
        
    def set3dvar(self, vnames):
        self.arldata.LevelVarList.add(vnames)
    
    def getdatahead(self, proj, model, vertical, icx=0, mn=0):
        return self.arldata.getDataHead(proj, model, vertical, icx, mn)
        
    def writeindexrec(self, t, datahead, ksums=None):
        cal = Calendar.getInstance()
        cal.set(t.year, t.month - 1, t.day, t.hour, t.minute, t.second)
        t = cal.getTime()
        self.arldata.writeIndexRecord(t, datahead, ksums)
        
    def writedatarec(self, t, lidx, vname, fhour, grid, data):
        cal = Calendar.getInstance()
        cal.set(t.year, t.month - 1, t.day, t.hour, t.minute, t.second)
        t = cal.getTime()
        ksum = self.arldata.writeGridData(t, lidx, vname, fhour, grid, data.asarray())
        return ksum
        
    # Write Bufr data
    def write_indicator(self, bufrlen, edition=3):
        return self.bufrdata.writeIndicatorSection(bufrlen, edition)
        
    def rewrite_indicator(self, bufrlen, edition=3):
        self.bufrdata.reWriteIndicatorSection(bufrlen, edition)
        
    def write_identification(self, **kwargs):
        length = kwargs.pop('length', 18)
        master_table = kwargs.pop('master_table', 0)
        subcenter_id = kwargs.pop('subcenter_id', 0)
        center_id = kwargs.pop('center_id', 74)
        update = kwargs.pop('update', 0)
        optional = kwargs.pop('optional', 0)
        category = kwargs.pop('category', 7)
        sub_category = kwargs.pop('sub_category', 0)
        master_table_version = kwargs.pop('master_table_version', 11)
        local_table_version = kwargs.pop('local_table_version', 1)
        year = kwargs.pop('year', 2016)
        month = kwargs.pop('month', 1)
        day = kwargs.pop('day', 1)
        hour = kwargs.pop('hour', 0)
        minute = kwargs.pop('minute', 0)
        return self.bufrdata.writeIdentificationSection(length, master_table, subcenter_id, center_id,\
            update, optional, category, sub_category, master_table_version,\
            local_table_version, year, month, day, hour, minute)
            
    def write_datadescription(self, n, datatype, descriptors):
        return self.bufrdata.writeDataDescriptionSection(n, datatype, descriptors)
        
    def write_datahead(self, len):
        return self.bufrdata.writeDataSectionHead(len)
        
    def rewrite_datahead(self, len):
        return self.bufrdata.reWriteDataSectionHead(len)
        
    def write_data(self, value, nbits=None):
        return self.bufrdata.write(value, nbits)
        
    def write_end(self):
        return self.bufrdata.writeEndSection()