#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2014-12-27
# Purpose: MeteoInfo Dataset module
# Note: Jython
#-----------------------------------------------------
from org.meteoinfo.projection import ProjectionInfo
from org.meteoinfo.data import GridData, ArrayMath
from ucar.ma2 import Array
        
# The encapsulate class of Array
class MIArray():
    
    # array must be a ucar.ma2.Array object
    def __init__(self, array):
        self.array = array
        
    def __len__(self):
        return int(self.array.getSize())
        
    def __str__(self):
        return self.array.toString()
        
    def __repr__(self):
        return self.array.toString()
    
    def __getitem__(self, indices):
        #print type(indices)
        if not isinstance(indices, tuple):
            print 'indices must be tuple!'
            return None
        
        if len(indices) != self.ndim:
            print 'indices must be ' + str(self.ndim) + ' dimensions!'
            return None
            
        origin = []
        size = []
        stride = []
        dims = []
        for i in range(0, self.ndim):   
            if isinstance(indices[i], int):
                sidx = indices[i]
                eidx = indices[i]
                step = 1
            else:
                sidx = 0 if indices[i].start is None else indices[i].start
                eidx = indices[i].stop is None and self.getshape()[i]-1 or indices[i].stop
                step = indices[i].step is None and 1 or indices[i].step
            origin.append(sidx)
            n = eidx - sidx + 1
            size.append(n)
            stride.append(step)                    
        r = ArrayMath.section(self.array, origin, size, stride)
        return MIArray(r)
    
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
        
    def getminvalue(self):
        return self.array.getMinimum()
        
    def getmaxvalue(self):
        return self.array.getMaximum()
        
    def getshape(self):
        return self.array.getShape()
        
    def sum(self, missingv=None):
        if missingv == None:
            return ArrayMath.sumDouble(self.array)
        else:
            return ArrayMath.sumDouble(self.array, missingv)
            
    def ave(self, missingv=None):
        if missingv == None:
            return ArrayMath.aveDouble(self.array)
        else:
            return ArrayMath.aveDouble(self.array, missingv)
            
    def aslist(self):
        return ArrayMath.asList(self.array)