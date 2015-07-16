#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2014-12-27
# Purpose: MeteoInfo Dataset module
# Note: Jython
#-----------------------------------------------------
from org.meteoinfo.projection import ProjectionInfo
from org.meteoinfo.data import GridData, StationData, ArrayMath, ArrayUtil
from org.meteoinfo.data.meteodata import DimensionType
from org.meteoinfo.layer import VectorLayer
from ucar.ma2 import Array, Range, MAMath
import miarray
from miarray import MIArray
import math

# Dimension array
class DimArray():
    
    # array must be MIArray
    def __init__(self, array=None, dims=None, fill_value=-9999.0, proj=None):
        self.array = array
        self.rank = array.rank
        self.shape = array.shape
        self.dims = dims
        self.ndim = len(dims)
        self.fill_value = fill_value
        self.proj = proj
        
    def asgriddata(self):
        xdata = self.dims[1].getDimValue()
        ydata = self.dims[0].getDimValue()
        gdata = GridData(self.array.array, xdata, ydata, self.fill_value, self.proj)
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
            k = indices[i]
            if isinstance(indices[i], int):
                sidx = k
                eidx = k
                step = 1                
            elif isinstance(k, slice):
                sidx = 0 if k.start is None else k.start
                eidx = self.dims[i].getDimLength()-1 if k.stop is None else k.stop
                step = 1 if k.step is None else k.step
            elif isinstance(k, tuple) or isinstance(k, list):
                dim = self.dims[i]
                sidx = dim.getValueIndex(k[0])
                if len(k) == 1:
                    eidx = sidx
                    step = 1
                else:                    
                    eidx = dim.getValueIndex(k[1])
                    if len(k) == 2:
                        step = 1
                    else:
                        step = int(k[2] / dim.getDeltaValue)
            else:
                print k
                return None
                
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
        data = DimArray(array, dims, self.fill_value, self.proj)
        return data
        
    def __setitem__(self, indices, value):
        #print type(indices) 
        if isinstance(indices, MIArray) or isinstance(indices, DimArray):
            ArrayMath.setValue(self.asarray(), indices.asarray(), value)
            return None
        
        if not isinstance(indices, tuple):
            inds = []
            inds.append(indices)
            indices = inds
        
        if self.rank == 0:
            self.array.array.setObject(0, value)
            return None
        
        if len(indices) != self.rank:
            print 'indices must be ' + str(self.rank) + ' dimensions!'
            return None

        ranges = []
        flips = []
        for i in range(0, self.rank):   
            if isinstance(indices[i], int):
                sidx = indices[i]
                eidx = indices[i]
                step = 1
            else:
                sidx = 0 if indices[i].start is None else indices[i].start
                eidx = self.shape[i]-1 if indices[i].stop is None else indices[i].stop
                step = 1 if indices[i].step is None else indices[i].step
            if step < 0:
                step = abs(step)
                flips.append(i)
            rr = Range(sidx, eidx, step)
            ranges.append(rr)

        ArrayMath.setSection(self.array.array, ranges, value)
        
    def __add__(self, other):
        r = None
        ArrayMath.fill_value = self.fill_value
        if isinstance(other, DimArray):      
            r = DimArray(self.array.__add__(other.array), self.dims, self.fill_value, self.proj)
        else:
            r = DimArray(self.array.__add__(other), self.dims, self.fill_value, self.proj)
        return r
        
    def __radd__(self, other):
        return DimArray.__add__(self, other)
        
    def __sub__(self, other):
        r = None
        if isinstance(other, DimArray): 
            r = DimArray(self.array.__sub__(other.array), self.dims, self.fill_value, self.proj)
        else:
            r = DimArray(self.array.__sub__(other), self.dims, self.fill_value, self.proj)
        return r
        
    def __rsub__(self, other):
        r = None
        if isinstance(other, DimArray): 
            r = DimArray(self.array.__rsub__(other.array), self.dims, self.fill_value, self.proj)
        else:
            r = DimArray(self.array.__rsub__(other), self.dims, self.fill_value, self.proj)
        return r
        
    def __mul__(self, other):
        r = None
        if isinstance(other, DimArray): 
            r = DimArray(self.array.__mul__(other.array), self.dims, self.fill_value, self.proj)
        else:
            r = DimArray(self.array.__mul__(other), self.dims, self.fill_value, self.proj)
        return r
        
    def __rmul__(self, other):
        return DimArray.__mul__(self, other)
        
    def __div__(self, other):
        r = None
        if isinstance(other, DimArray): 
            r = DimArray(self.array.__div__(other.array), self.dims, self.fill_value, self.proj)
        else:
            r = DimArray(self.array.__div__(other), self.dims, self.fill_value, self.proj)
        return r
        
    def __rdiv__(self, other):
        r = None
        if isinstance(other, DimArray): 
            r = DimArray(self.array.__rdiv__(other.array), self.dims, self.fill_value, self.proj)
        else:
            r = DimArray(self.array.__rdiv__(other), self.dims, self.fill_value, self.proj)
        return r
        
    def __pow__(self, other):
        r = DimArray(self.array.__pow__(other), self.dims, self.fill_value, self.proj)
        return r
        
    def __neg__(self):
        r = DimArray(self.array.__neg__(), self.dims, self.fill_value, self.proj)
        return r
        
    def __lt__(self, other):
        r = DimArray(self.array.__lt__(other), self.dims, self.fill_value, self.proj)
        return r
        
    def __le__(self, other):
        r = DimArray(self.array.__le__(other), self.dims, self.fill_value, self.proj)
        return r
        
    def __eq__(self, other):
        r = DimArray(self.array.__eq__(other), self.dims, self.fill_value, self.proj)
        return r
        
    def __ne__(self, other):
        r = DimArray(self.array.__ne__(other), self.dims, self.fill_value, self.proj)
        return r
        
    def __gt__(self, other):
        r = DimArray(self.array.__gt__(other), self.dims, self.fill_value, self.proj)
        return r
        
    def __ge__(self, other):
        r = DimArray(self.array.__ge__(other), self.dims, self.fill_value, self.proj)
        return r        
        
    # get dimension length
    def dimlen(self, idx):
        return self.dims[idx].getDimLength(idx)
        
    def dimvalue(self, idx):
        return self.dims[idx].getDimValue()
        
    def islondim(self, idx):
        dim = self.dims[idx]
        if dim.getDimType() == DimensionType.X and self.proj.isLonLat():
            return True
        else:
            return False
            
    def islatdim(self, idx):
        dim = self.dims[idx]
        if dim.getDimType() == DimensionType.Y and self.proj.isLonLat():
            return True
        else:
            return False
            
    def islonlatdim(self, idx):
        return self.islondim(idx) or self.islatdim(idx)
            
    def istimedim(self, idx):
        dim = self.dims[idx]
        if dim.getDimType() == DimensionType.T:
            return True
        else:
            return False
        
    def sqrt(self):
        r = DimArray(self.array.sqrt(), self.dims, self.fill_value, self.proj)
        return r
    
    def sin(self):
        r = DimArray(self.array.sin(), self.dims, self.fill_value, self.proj)
        return r
        
    def cos(self):
        r = DimArray(self.array.cos(), self.dims, self.fill_value, self.proj)
        return r
        
    def exp(self):
        r = DimArray(self.array.exp(), self.dims, self.fill_value, self.proj)
        return r
        
    def log(self):
        r = DimArray(self.array.log(), self.dims, self.fill_value, self.proj)
        return r
        
    def log10(self):
        r = DimArray(self.array.log10(), self.dims, self.fill_value, self.proj)
        return r
        
    def min(self):
        return self.array.min(self.fill_value)
        
    def max(self):
        return self.array.max(self.fill_value)
        
    def sum(self):
        return self.array.sum(self.fill_value)
        
    def ave(self):
        return self.array.ave(self.fill_value)
        
    def inpolygon(self, polygon):
        x = self.dims[1].getDimValue()
        y = self.dims[0].getDimValue()
        if isinstance(polygon, tuple):
            x_p = polygon[0]
            y_p = polygon[1]
            if isinstance(x_p, MIArray):
                x_p = x_p.aslist()
            if isinstance(y_p, MIArray):
                y_p = y_p.aslist()
            r = self.array.inpolygon(x, y, x_p, y_p)
        else:
            r = self.array.inpolygon(x, y, polygon)
        r = DimArray(r, self.dims, self.fill_value, self.proj)
        return r
        
    def maskout(self, polygon):
        x = self.dims[1].getDimValue()
        y = self.dims[0].getDimValue()
        r = DimArray(self.array.maskout(x, y, polygon, self.fill_value), self.dims, self.fill_value, self.proj)
        return r
     
    def aslist(self):
        return ArrayMath.asList(self.array.array)
        
    def asarray(self):
        return self.array.array
     
    def tostation(self, x, y):
        gdata = self.asgriddata()
        if isinstance(x, MIArray) or isinstance(x, DimArray):
            r = gdata.data.toStation(x.aslist(), y.aslist())
            return MIArray(ArrayUtil.array(r))
        else:
            return gdata.data.toStation(x, y)
    
       
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

        if isinstance(indices[0], int):
            sxidx = indices[0]
            exidx = indices[0]
            xstep = 1
        else:
            sxidx = 0 if indices[0].start is None else indices[0].start
            exidx = self.data.getXNum() if indices[0].stop is None else indices[0].stop
            xstep = 1 if indices[0].step is None else indices[0].step
        if isinstance(indices[1], int):
            syidx = indices[1]
            eyidx = indices[1]
            ystep = 1
        else:
            syidx = 0 if indices[1].start is None else indices[1].start
            eyidx = self.data.getYNum() if indices[1].stop is None else indices[1].stop
            ystep = 1 if indices[1].step is None else indices[1].step
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
        
    def min(self):
        return self.data.getMinValue()
        
    def max(self):
        return self.data.getMaxValue()  

    def interpolate(self):
        return PyGridData(self.data.interpolate())

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
        
    def min(self):
        return self.data.getMinValue()
        
    def max(self):
        return self.data.getMaxValue() 
        
    def maskout(self, polygon):
        return PyStationData(self.data.maskout(polygon))
        
    def maskin(self, polygon):
        return PyStationData(self.data.maskin(polygon))
        
    def filter(self, stations):
        return PyStationData(self.data.filter(stations))
        
    def join(self, other):
        return PyStationData(self.data.join(other.data))     

    def ave(self):
        return self.data.average()
        
    def sum(self):
        return self.data.sum()
        
    def griddata(self, xi=None, **kwargs):
        method = kwargs.pop('method', 'idw')
        fill_value = self.data.missingValue
        x_s = MIArray(ArrayUtil.array(self.data.getXList()))
        y_s = MIArray(ArrayUtil.array(self.data.getYList()))
        if xi is None:            
            xn = int(math.sqrt(len(x_s)))
            yn = xn
            x_g = MIArray(ArrayUtil.lineSpace(x_s.min(), x_s.max(), xn, True))
            y_g = MIArray(ArrayUtil.lineSpace(y_s.min(), y_s.max(), yn, True))     
        else:
            x_g = xi[0]
            y_g = xi[1]
        if isinstance(x_s, MIArray):
            x_s = x_s.aslist()
        if isinstance(y_s, MIArray):
            y_s = y_s.aslist()    
        if isinstance(x_g, MIArray):
            x_g = x_g.aslist()
        if isinstance(y_g, MIArray):
            y_g = y_g.aslist()
        if method == 'idw':
            pnum = kwargs.pop('pointnum', 2)
            radius = kwargs.pop('radius', None)
            if radius is None:
                r = self.data.interpolate_Neighbor(x_g, y_g, pnum, fill_value)
                return PyGridData(r)
            else:
                r = self.data.interpolate_Radius(x_g, y_g, pnum, radius, fill_value)
                return PyGridData(r)
        elif method == 'cressman':
            radius = kwargs.pop('radius', [10, 7, 4, 2, 1])
            if isinstance(radius, MIArray):
                radius = radius.aslist()
            r = self.data.interpolate_Cressman(x_g, y_g, radius, fill_value)
            return PyGridData(r)
        elif method == 'neareast':
            r = self.data.interpolate_Assign(x_g, y_g, fill_value)
            return PyGridData(r)
        else:
            return None
        
    def savedata(self, filename, fieldname='data', savemissingv=False):
        self.data.saveAsCSVFile(filename, fieldname, savemissingv)