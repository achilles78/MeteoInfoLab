#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2014-12-27
# Purpose: MeteoInfo Dataset module
# Note: Jython
#-----------------------------------------------------
from org.meteoinfo.projection import ProjectionInfo
from org.meteoinfo.data import GridData, StationData, ArrayMath
from org.meteoinfo.layer import VectorLayer
from ucar.ma2 import Array, Range, MAMath
import miarray
from miarray import MIArray

# Dimension array
class DimArray():
    
    # array must be MIArray
    def __init__(self, array=None, dims=None, missingvalue=-9999.0, proj=None):
        self.array = array        
        self.dims = dims
        self.ndim = len(dims)
        self.missingvalue = missingvalue
        self.proj = proj
        
    def asgriddata(self):
        xdata = self.dims[1].getDimValue()
        ydata = self.dims[0].getDimValue()
        gdata = GridData(self.array.array, xdata, ydata, self.missingvalue, self.proj)
        return PyGridData(gdata)
        
    def __len__(self):
        shape = self.array.getshape()
        len = 1
        for l in shape:
            len = len * l
        return len
        
    def __str__(self):
        return self.array.__str__()
        
    def __repr__(self):
        return self.array.__repr__()
        
    def __getitem__(self, indices):
        #print type(indices)
        if not isinstance(indices, tuple):
            inds = []
            inds.append(indices)
            indices = inds
        
        if len(indices) != self.ndim:
            print 'indices must be ' + str(self.ndim) + ' dimensions!'
            return None
            
        #origin = []
        #size = []
        #stride = []
        dims = []
        ranges = []
        flips = []
        for i in range(0, self.ndim):   
            if isinstance(indices[i], int):
                sidx = indices[i]
                eidx = indices[i]
                step = 1
            else:
                sidx = 0 if indices[i].start is None else indices[i].start
                eidx = indices[i].stop is None and self.dims[i].getDimLength()-1 or indices[i].stop
                step = indices[i].step is None and 1 or indices[i].step
            if step < 0:
                step = abs(step)
                flips.append(i)
            rr = Range(sidx, eidx, step)
            ranges.append(rr)
            #origin.append(sidx)
            n = eidx - sidx + 1
            #size.append(n)
            #stride.append(step)
            if n > 1:
                dim = self.dims[i]
                dims.append(dim.extract(sidx, eidx, step))
                    
        #r = ArrayMath.section(self.array.array, origin, size, stride)
        r = ArrayMath.section(self.array.array, ranges)
        for i in flips:
            r = r.flip(i)
        rr = Array.factory(r.getDataType(), r.getShape());
        MAMath.copy(rr, r);
        array = MIArray(rr)
        data = DimArray(array, dims, self.missingvalue, self.proj)
        return data
        
    def __add__(self, other):
        r = None
        if isinstance(other, DimArray):      
            r = DimArray(self.array.__add__(other.array), self.dims, self.missingvalue, self.proj)
        else:
            r = DimArray(self.array.__add__(other), self.dims, self.missingvalue, self.proj)
        return r
        
    def __radd__(self, other):
        return DimArray.__add__(self, other)
        
    def __sub__(self, other):
        r = None
        if isinstance(other, DimArray): 
            r = DimArray(self.array.__sub__(other.array), self.dims, self.missingvalue, self.proj)
        else:
            r = DimArray(self.array.__sub__(other), self.dims, self.missingvalue, self.proj)
        return r
        
    def __rsub__(self, other):
        r = None
        if isinstance(other, DimArray): 
            r = DimArray(self.array.__rsub__(other.array), self.dims, self.missingvalue, self.proj)
        else:
            r = DimArray(self.array.__rsub__(other), self.dims, self.missingvalue, self.proj)
        return r
        
    def __mul__(self, other):
        r = None
        if isinstance(other, DimArray): 
            r = DimArray(self.array.__mul__(other.array), self.dims, self.missingvalue, self.proj)
        else:
            r = DimArray(self.array.__mul__(other), self.dims, self.missingvalue, self.proj)
        return r
        
    def __rmul__(self, other):
        return DimArray.__mul__(self, other)
        
    def __div__(self, other):
        r = None
        if isinstance(other, DimArray): 
            r = DimArray(self.array.__div__(other.array), self.dims, self.missingvalue, self.proj)
        else:
            r = DimArray(self.array.__div__(other), self.dims, self.missingvalue, self.proj)
        return r
        
    def __rdiv__(self, other):
        r = None
        if isinstance(other, DimArray): 
            r = DimArray(self.array.__rdiv__(other.array), self.dims, self.missingvalue, self.proj)
        else:
            r = DimArray(self.array.__rdiv__(other), self.dims, self.missingvalue, self.proj)
        return r
        
    def __pow__(self, other):
        r = DimArray(self.array.__pow__(other), self.dims, self.missingvalue, self.proj)
        return r
        
    # get dimension length
    def dimlen(self, idx):
        return self.dims[idx].getDimLength(idx)
        
    def dimvalue(self, idx):
        return self.dims[idx].getDimValue()
        
    def sqrt(self):
        r = DimArray(self.array.sqrt(), self.dims, self.missingvalue, self.proj)
        return r
    
    def sin(self):
        r = DimArray(self.array.sin(), self.dims, self.missingvalue, self.proj)
        return r
        
    def cos(self):
        r = DimArray(self.array.cos(), self.dims, self.missingvalue, self.proj)
        return r
        
    def exp(self):
        r = DimArray(self.array.exp(), self.dims, self.missingvalue, self.proj)
        return r
        
    def log(self):
        r = DimArray(self.array.log(), self.dims, self.missingvalue, self.proj)
        return r
        
    def log10(self):
        r = DimArray(self.array.log10(), self.dims, self.missingvalue, self.proj)
        return r
        
    def getminvalue(self):
        #return self.array.getminvalue(self.missingvalue)
        return self.array.getminvalue()
        
    def getmaxvalue(self):
        #return self.array.getmaxvalue(self.missingvalue)
        return self.array.getminvalue()
        
    def sum(self):
        return self.array.sum(self.missingvalue)
        
    def ave(self):
        return self.array.ave(self.missingvalue)
        
    def inpolygon(self, polygon):
        x = self.dims[1].getDimValue()
        y = self.dims[0].getDimValue()
        r = DimArray(self.array.inpolygon(x, y, polygon), self.dims, self.missingvalue, self.proj)
        return r
        
    def maskout(self, polygon):
        x = self.dims[1].getDimValue()
        y = self.dims[0].getDimValue()
        r = DimArray(self.array.maskout(x, y, polygon, self.missingvalue), self.dims, self.missingvalue, self.proj)
        return r
     
    def aslist(self):
        return ArrayMath.asList(self.array.array)
        
    def asarray(self):
        return self.array.array
     
    def tostation(self, x, y):
        gdata = self.asgriddata()
        r = gdata.data.toStation(x, y)
        return r
    
        
# The encapsulate class of GridData
class PyGridData():
    
    # griddata must be a GridData object
    def __init__(self, griddata=None):
        if griddata != None:
            self.data = griddata
        else:
            self.data = GridData()
    
    def __getitem__(self, indices):
        print type(indices)
        if not isinstance(indices, tuple):
            print 'indices must be tuple!'
            return None
        
        if len(indices) != 2:
            print 'indices must be 2 dimension!'
            return None
            
        sxidx = 0 if indices[0].start is None else indices[0].start
        exidx = indices[0].stop is None and self.data.getXNum() or indices[0].stop
        xstep = indices[0].step is None and 1 or indices[0].step
        syidx = 0 if indices[1].start is None else indices[1].start
        eyidx = indices[1].stop is None and self.data.getYNum() or indices[1].stop
        ystep = indices[1].step is None and 1 or indices[1].step
        gdata = PyGridData(self.data.extract(sxidx, exidx, xstep, syidx, eyidx, ystep))
        return gdata
    
    def add(self, other):
        gdata = None
        if isinstance(other, PyGridData):            
            gdata = PyGridData(self.data.add(other.data))
        else:
            gdata = PyGridData(self.data.add(other))
        return gdata
    
    def __add__(self, other):
        gdata = None
        print isinstance(other, PyGridData)
        if isinstance(other, PyGridData):            
            gdata = PyGridData(self.data.add(other.data))
        else:
            gdata = PyGridData(self.data.add(other))
        return gdata
        
    def __radd__(self, other):
        return PyGridData.__add__(self, other)
        
    def __sub__(self, other):
        gdata = None
        if isinstance(other, PyGridData):
            gdata = PyGridData(self.data.sub(other.data))
        else:
            gdata = PyGridData(self.data.sub(other))
        return gdata
        
    def __rsub__(self, other):
        gdata = None
        if isinstance(other, PyGridData):
            gdata = PyGridData(other.data.sub(self.data))
        else:
            gdata = PyGridData(DataMath.sub(other, self.data))
        return gdata
    
    def __mul__(self, other):
        gdata = None
        if isinstance(other, PyGridData):
            gdata = PyGridData(self.data.mul(other.data))
        else:
            gdata = PyGridData(self.data.mul(other))
        return gdata
        
    def __rmul__(self, other):
        return PyGridData.__mul__(self, other)
        
    def __div__(self, other):
        gdata = None
        if isinstance(other, PyGridData):
            gdata = PyGridData(self.data.div(other.data))
        else:
            gdata = PyGridData(self.data.div(other))
        return gdata
        
    def __rdiv__(self, other):
        gdata = None
        if isinstance(other, PyGridData):
            gdata = PyGridData(other.data.div(self.data))
        else:
            gdata = PyGridData(DataMath.div(other, self))
        return gdata
        
    # other must be a numeric data
    def __pow__(self, other):
        gdata = PyGridData(self.data.pow(other))
        return gdata
        
    def getminvalue(self):
        return self.data.getMinValue()
        
    def getmaxvalue(self):
        return self.data.getMaxValue()        

###############################################################         
# The encapsulate class of StationData
class PyStationData():
    
    # data must be a StationData object
    def __init__(self, data=None):
        self.data = data
    
    def __len__(self):
        return self.data.getStNum()
    
    def add(self, other):
        gdata = None
        if isinstance(other, PyStationData):            
            gdata = PyStationData(self.data.add(other.data))
        else:
            gdata = PyStationData(self.data.add(other))
        return gdata
    
    def __add__(self, other):
        gdata = None
        print isinstance(other, PyStationData)
        if isinstance(other, PyStationData):            
            gdata = PyStationData(self.data.add(other.data))
        else:
            gdata = PyStationData(self.data.add(other))
        return gdata
        
    def __radd__(self, other):
        return PyStationData.__add__(self, other)
        
    def __sub__(self, other):
        gdata = None
        if isinstance(other, PyStationData):
            gdata = PyStationData(self.data.sub(other.data))
        else:
            gdata = PyStationData(self.data.sub(other))
        return gdata
        
    def __rsub__(self, other):
        gdata = None
        if isinstance(other, PyStationData):
            gdata = PyStationData(other.data.sub(self.data))
        else:
            gdata = PyStationData(DataMath.sub(other, self.data))
        return gdata
    
    def __mul__(self, other):
        gdata = None
        if isinstance(other, PyStationData):
            gdata = PyStationData(self.data.mul(other.data))
        else:
            gdata = PyStationData(self.data.mul(other))
        return gdata
        
    def __rmul__(self, other):
        return PyStationData.__mul__(self, other)
        
    def __div__(self, other):
        gdata = None
        if isinstance(other, PyStationData):
            gdata = PyStationData(self.data.div(other.data))
        else:
            gdata = PyStationData(self.data.div(other))
        return gdata
        
    def __rdiv__(self, other):
        gdata = None
        if isinstance(other, PyStationData):
            gdata = PyStationData(other.data.div(self.data))
        else:
            gdata = PyStationData(DataMath.div(other, self))
        return gdata
        
    # other must be a numeric data
    def __pow__(self, other):
        gdata = PyStationData(self.data.pow(other))
        return gdata        
        
    def getminvalue(self):
        return self.data.getMinValue()
        
    def getmaxvalue(self):
        return self.data.getMaxValue() 
        
    def maskout(self, polygon):
        return PyStationData(self.data.maskout(polygon))
        
    def maskin(self, polygon):
        return PyStationData(self.data.maskin(polygon))
        
    def filter(self, stations):
        return PyStationData(self.data.filter(stations))
        
    def join(self, other):
        return PyStationData(self.data.join(other.data))
        
    def savedata(self, filename, fieldname='data', savemissingv=False):
        self.data.saveAsCSVFile(filename, fieldname, savemissingv)