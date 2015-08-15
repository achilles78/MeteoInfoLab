#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2014-12-27
# Purpose: MeteoInfo Dataset module
# Note: Jython
#-----------------------------------------------------
#import math
from org.meteoinfo.projection import ProjectionInfo
from org.meteoinfo.data import GridData, ArrayMath, ArrayUtil
from org.meteoinfo.data.meteodata import Dimension
from ucar.ma2 import Array, Range
        
# The encapsulate class of Array
class MIArray():
    
    # array must be a ucar.ma2.Array object
    def __init__(self, array):
        self.array = array
        self.rank = array.getRank()
        self.shape = array.getShape()
        
    def __len__(self):
        return int(self.array.getSize())
        
    def __str__(self):
        return ArrayUtil.convertToString(self.array)
        
    def __repr__(self):
        return ArrayUtil.convertToString(self.array)
    
    def __getitem__(self, indices):
        #print type(indices)            
        if not isinstance(indices, tuple):
            inds = []
            inds.append(indices)
            indices = inds
            
        if self.rank == 0:
            return self
        
        if len(indices) != self.rank:
            print 'indices must be ' + str(self.rank) + ' dimensions!'
            return None

        ranges = []
        flips = []
        iszerodim = True
        for i in range(0, self.rank):   
            if isinstance(indices[i], int):
                sidx = indices[i]
                eidx = indices[i]
                step = 1
            else:
                sidx = 0 if indices[i].start is None else indices[i].start
                eidx = self.getshape()[i]-1 if indices[i].stop is None else indices[i].stop
                step = 1 if indices[i].step is None else indices[i].step
            if sidx != eidx:
                iszerodim = False
            if step < 0:
                step = abs(step)
                flips.append(i)
            rr = Range(sidx, eidx, step)
            ranges.append(rr)
        r = ArrayMath.section(self.array, ranges)
        if iszerodim:
            return r.getObject(0)
        else:
            for i in flips:
                r = r.flip(i)
            return MIArray(r)
        
    def __setitem__(self, indices, value):
        #print type(indices) 
        if isinstance(indices, MIArray):
            ArrayMath.setValue(self.array, indices.array, value)
            return None
        
        if not isinstance(indices, tuple):
            inds = []
            inds.append(indices)
            indices = inds
        
        if self.rank == 0:
            self.array.setObject(0, value)
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
                eidx = self.getshape()[i]-1 if indices[i].stop is None else indices[i].stop
                step = 1 if indices[i].step is None else indices[i].step
            if step < 0:
                step = abs(step)
                flips.append(i)
            rr = Range(sidx, eidx, step)
            ranges.append(rr)

        ArrayMath.setSection(self.array, ranges, value)
    
    def __abs__(self):
        return MIArray(ArrayMath.abs(self.array))
    
    def __add__(self, other):
        r = None
        if isinstance(other, MIArray):      
            r = MIArray(ArrayMath.add(self.array, other.array))
        else:
            r = MIArray(ArrayMath.add(self.array, other))
        return r
        
    def __radd__(self, other):
        return MIArray.__add__(self, other)
        
    def __sub__(self, other):
        r = None
        if isinstance(other, MIArray):      
            r = MIArray(ArrayMath.sub(self.array, other.array))
        else:
            r = MIArray(ArrayMath.sub(self.array, other))
        return r
        
    def __rsub__(self, other):
        r = None
        if isinstance(other, MIArray):      
            r = MIArray(ArrayMath.sub(other.array, self.array))
        else:
            r = MIArray(ArrayMath.sub(other, self.array))
        return r
    
    def __mul__(self, other):
        r = None
        if isinstance(other, MIArray):      
            r = MIArray(ArrayMath.mul(self.array, other.array))
        else:
            r = MIArray(ArrayMath.mul(self.array, other))
        return r
        
    def __rmul__(self, other):
        return MIArray.__mul__(self, other)
        
    def __div__(self, other):
        r = None
        if isinstance(other, MIArray):      
            r = MIArray(ArrayMath.div(self.array, other.array))
        else:
            r = MIArray(ArrayMath.div(self.array, other))
        return r
        
    def __rdiv__(self, other):
        r = None
        if isinstance(other, MIArray):      
            r = MIArray(ArrayMath.div(other.array, self.array))
        else:
            r = MIArray(ArrayMath.div(other, self.array))
        return r
        
    # other must be a numeric data
    def __pow__(self, other):
        r = MIArray(ArrayMath.pow(self.array, other))
        return r
        
    def __neg__(self):
        r = MIArray(ArrayMath.sub(0, self.array))
        return r
        
    def __lt__(self, other):
        if isinstance(other, MIArray):
            r = MIArray(ArrayMath.lessThan(self.array, other.array))
        else:
            r = MIArray(ArrayMath.lessThan(self.array, other))
        return r
        
    def __le__(self, other):
        if isinstance(other, MIArray):
            r = MIArray(ArrayMath.lessThanOrEqual(self.array, other.array))
        else:
            r = MIArray(ArrayMath.lessThanOrEqual(self.array, other))
        return r
        
    def __eq__(self, other):
        if isinstance(other, MIArray):
            r = MIArray(ArrayMath.equal(self.array, other.array))
        else:
            r = MIArray(ArrayMath.equal(self.array, other))
        return r
        
    def __ne__(self, other):
        if isinstance(other, MIArray):
            r = MIArray(ArrayMath.notEqual(self.array, other.array))
        else:
            r = MIArray(ArrayMath.notEqual(self.array, other))
        return r
        
    def __gt__(self, other):
        if isinstance(other, MIArray):
            r = MIArray(ArrayMath.greaterThan(self.array, other.array))
        else:
            r = MIArray(ArrayMath.greaterThan(self.array, other))
        return r
        
    def __ge__(self, other):
        if isinstance(other, MIArray):
            r = MIArray(ArrayMath.greaterThanOrEqual(self.array, other.array))
        else:
            r = MIArray(ArrayMath.greaterThanOrEqual(self.array, other))
        return r
        
    def min(self, fill_value=None):
        if fill_value == None:
            return ArrayMath.getMinimum(self.array)
        else:
            return ArrayMath.getMinimum(self.array, fill_value)
        
    def max(self, fill_value=None):
        if fill_value == None:
            return ArrayMath.getMaximum(self.array)
        else:
            return ArrayMath.getMaximum(self.array, fill_value)
        
    def getshape(self):
        return self.array.getShape()
        
    def sum(self, fill_value=None):
        if fill_value == None:
            return ArrayMath.sumDouble(self.array)
        else:
            return ArrayMath.sumDouble(self.array, fill_value)
            
    def ave(self, fill_value=None):
        if fill_value == None:
            return ArrayMath.aveDouble(self.array)
        else:
            return ArrayMath.aveDouble(self.array, fill_value)
            
    def sqrt(self):
        return MIArray(ArrayMath.sqrt(self.array))
    
    def sin(self):
        return MIArray(ArrayMath.sin(self.array))
        
    def cos(self):
        return MIArray(ArrayMath.cos(self.array))
        
    def exp(self):
        return MIArray(ArrayMath.exp(self.array))
        
    def log(self):
        return MIArray(ArrayMath.log(self.array))
        
    def log10(self):
        return MIArray(ArrayMath.log10(self.array))
            
    def aslist(self):
        return ArrayMath.asList(self.array)
        
    def asarray(self):
        return self.array
        
    def asgriddata(self, x, y, fill_value=-9999.0):    
        gdata = GridData(self.array, x.array, y.array, fill_value)
        return PyGridData(gdata)
        
    def asdimarray(self, x, y, fill_value=-9999.0):
        dims = []
        ydim = Dimension(DimensionType.Y)
        ydim.setDimValues(y.aslist())
        dims.append(ydim)
        xdim = Dimension(DimensionType.X)
        xdim.setDimValues(x.aslist())
        dims.append(xdim)        
        return DimArray(self, dims, fill_value)
        
    def inpolygon(self, x, y, polygon):
        if isinstance(polygon, tuple):
            x_p = polygon[0]
            y_p = polygon[1]
            if isinstance(x_p, MIArray):
                x_p = x_p.aslist()
            if isinstance(y_p, MIArray):
                y_p = y_p.aslist()
            return MIArray(ArrayMath.inPolygon(self.array, x.aslist(), y.aslist(), x_p, y_p))
        else:
            return MIArray(ArrayMath.inPolygon(self.array, x.aslist(), y.aslist(), polygon))
        
    def maskout(self, x, y, polygon, missingv):
        if isinstance(x, MIArray):
            xl = x.aslist()
        else:
            xl = x
        if isinstance(y, MIArray):
            yl = y.aslist()
        else:
            yl = y
        return MIArray(ArrayMath.maskout(self.array, xl, yl, polygon, missingv))
        
    def savegrid(self, x, y, fname):
        gdata = GridData(self.array, x.array, y.array, -9999.0)
        gdata.saveAsSurferASCIIFile(fname)
