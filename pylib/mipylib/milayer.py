#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2015-9-20
# Purpose: MeteoInfoLab layer module
# Note: Jython
#-----------------------------------------------------
from org.meteoinfo.data import TableUtil
from org.meteoinfo.layer import LayerTypes
from java.util import Date, Calendar

from datetime import datetime

class MILayer():
    def __init__(self, layer):
        self.layer = layer
    
    def __repr__(self):
        return self.layer.getLayerInfo()
    
    def isvectorlayer(self):
        return self.layer.getLayerType() == LayerTypes.VectorLayer
    
    def cellvalue(self, fieldname, shapeindex):
        v = self.layer.getCellValue(fieldname, shapeindex)
        if isinstance(v, Date):
            cal = Calendar.getInstance()
            cal.setTime(v)
            year = cal.get(Calendar.YEAR)
            month = cal.get(Calendar.MONTH) + 1
            day = cal.get(Calendar.DAY_OF_MONTH)
            hour = cal.get(Calendar.HOUR_OF_DAY)
            minute = cal.get(Calendar.MINUTE)
            second = cal.get(Calendar.SECOND)
            dt = datetime(year, month, day, hour, minute, second)
            return dt
        else:
            return v
            
    def setcellvalue(self, fieldname, shapeindex, value):
        self.layer.editCellValue(fieldname, shapeindex, value)
            
    def shapes(self):
        return self.layer.getShapes()
        
    def shapenum(self):
        return self.layer.getShapeNum()
        
    def legend(self):
        return self.layer.getLegendScheme()
        
    def setlegend(self, legend):
        self.layer.setLegendScheme(legend)
    
    def addfield(self, name, dtype):
        dt = TableUtil.toDataTypes(dtype)
        self.layer.editAddField(name, dt)
        
    def getlabel(self, text):
        return self.layer.getLabel(text)
        
    def movelabel(self, label, x=0, y=0):
        self.layer.moveLabel(label, x, y)
        
    def clone(self):
        return MILayer(self.layer.clone())
        
class MIXYListData():
    def __init__(self, data):
        self.data = data
        
    def size(self):
        return self.data.getSeriesCount()