#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2014-12-27
# Purpose: MeteoInfo Dataset module
# Note: Jython
#-----------------------------------------------------
#import math
from org.meteoinfo.projection import ProjectionInfo
from org.meteoinfo.data import GridData, GridArray, ArrayMath, ArrayUtil
from org.meteoinfo.data.meteodata import Dimension
from org.meteoinfo.math import Complex
from org.meteoinfo.math.linalg import LinalgUtil
from ucar.ma2 import Array, Range, MAMath, DataType
import jarray
import numbers

#import milayer
#from milayer import MILayer
import mipylib.miutil

from java.lang import Double
import datetime
        
# The encapsulate class of Array
class MIArray(object):
        
    # array must be a ucar.ma2.Array object
    def __init__(self, array):
        self.array = array
        self.ndim = array.getRank()
        s = array.getShape()
        s1 = []
        for i in range(len(s)):
            s1.append(s[i])
        self._shape = tuple(s1)
        self.dtype = array.getDataType()
        if self.ndim > 0:
            self.sizestr = str(self.shape[0])
            if self.ndim > 1:
                for i in range(1, self.ndim):
                    self.sizestr = self.sizestr + '*%s' % self.shape[i]
    
    #---- shape property
    def get_shape(self):
        return self._shape
        
    def set_shape(self, value):
        if -1 in value:
            nvalue = list(value)
            l = 1
            for i in nvalue:
                if i >= 0:
                    l *= i
            idx = nvalue.index(-1)
            nvalue[idx] = int(self.array.getSize() / l)
            value = tuple(nvalue)
        self._shape = value
        nshape = jarray.array(value, 'i')
        self.__init__(self.array.reshape(nshape))
        
    shape = property(get_shape, set_shape)
        
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
            
        if self.ndim == 0:
            return self
        
        if len(indices) != self.ndim:
            print 'indices must be ' + str(self.ndim) + ' dimensions!'
            raise IndexError()

        ranges = []
        flips = []
        onlyrange = True
        alllist = True
        isempty = False
        nshape = []
        for i in range(0, self.ndim):  
            k = indices[i]
            if isinstance(k, int):
                if k < 0:
                    k = self.getshape()[i] + k
                sidx = k
                eidx = k
                step = 1
                alllist = False
            elif isinstance(k, slice):
                sidx = 0 if k.start is None else k.start
                if sidx < 0:
                    sidx = self.getshape()[i] + sidx
                eidx = self.getshape()[i] if k.stop is None else k.stop
                if eidx < 0:
                    eidx = self.getshape()[i] + eidx
                eidx -= 1                    
                step = 1 if k.step is None else k.step
                alllist = False
            elif isinstance(k, (list, tuple, MIArray)):
                if isinstance(k, MIArray):
                    k = k.aslist()
                onlyrange = False
                ranges.append(k)
                continue
            else:
                print k
                return None
            if step < 0:
                step = abs(step)
                flips.append(i)
                if eidx < sidx:
                    tempidx = sidx
                    sidx = eidx + 2
                    eidx = tempidx
            if sidx >= self.shape[i]:
                raise IndexError()
            if eidx < sidx:
                isempty = True
            else:
                rr = Range(sidx, eidx, step)
                ranges.append(rr)
            nshape.append(eidx - sidx + 1 if eidx - sidx >= 0 else 0)

        if isempty:
            r = ArrayUtil.zeros(nshape, 'int')
            return MIArray(r)
            
        if onlyrange:
            r = ArrayMath.section(self.array, ranges)
        else:
            if alllist:
                r = ArrayMath.takeValues(self.array, ranges)
            else:
                r = ArrayMath.take(self.array, ranges)
        if r.getSize() == 1:
            r = r.getObject(0)
            if isinstance(r, Complex):
                return complex(r.getReal(), r.getImaginary())
            else:
                return r
        else:
            for i in flips:
                r = r.flip(i)
            rr = Array.factory(r.getDataType(), r.getShape());
            MAMath.copy(rr, r);
            return MIArray(rr)
        
    def __setitem__(self, indices, value):
        #print type(indices) 
        if isinstance(indices, MIArray):
            if isinstance(value, MIArray):
                value = value.asarray()
            ArrayMath.setValue(self.array, indices.array, value)
            return None
        
        if not isinstance(indices, tuple):
            inds = []
            inds.append(indices)
            indices = inds
        
        if self.ndim == 0:
            self.array.setObject(0, value)
            return None
        
        if len(indices) != self.ndim:
            print 'indices must be ' + str(self.ndim) + ' dimensions!'
            return None

        ranges = []
        flips = []
        for i in range(0, self.ndim):   
            if isinstance(indices[i], int):
                sidx = indices[i]                
                if sidx < 0:
                    sidx = self.getshape()[i] + sidx                
                eidx = sidx
                step = 1
            else:
                sidx = 0 if indices[i].start is None else indices[i].start
                if sidx < 0:
                    sidx = self.getshape()[i] + sidx
                eidx = self.getshape()[i] if indices[i].stop is None else indices[i].stop
                if eidx < 0:
                    eidx = self.getshape()[i] + eidx
                eidx -= 1
                step = 1 if indices[i].step is None else indices[i].step
            if step < 0:
                step = abs(step)
                flips.append(i)
            rr = Range(sidx, eidx, step)
            ranges.append(rr)

        if isinstance(value, MIArray):
            value = value.asarray()
        r = ArrayMath.setSection(self.array, ranges, value)
        self.array = r
    
    def __value_other(self, other):
        if not isinstance(other, numbers.Number):
            other = other.asarray()
        return other
    
    def __abs__(self):
        return MIArray(ArrayMath.abs(self.array))
    
    def __add__(self, other):
        other = MIArray.__value_other(self, other)
        r = ArrayMath.add(self.array, other)        
        if r is None:
            raise ValueError('Dimension missmatch, can not broadcast!')
        return MIArray(r)
        
    def __radd__(self, other):
        return MIArray.__add__(self, other)
        
    def __sub__(self, other):
        other = MIArray.__value_other(self, other)
        r = ArrayMath.sub(self.array, other)        
        if r is None:
            raise ValueError('Dimension missmatch, can not broadcast!')
        return MIArray(r)
        
    def __rsub__(self, other):
        other = MIArray.__value_other(self, other)
        r = ArrayMath.sub(other, self.array)        
        if r is None:
            raise ValueError('Dimension missmatch, can not broadcast!')
        return MIArray(r)
    
    def __mul__(self, other):
        other = MIArray.__value_other(self, other)
        r = ArrayMath.mul(self.array, other)
        if r is None:
            raise ValueError('Dimension missmatch, can not broadcast!')
        return MIArray(r)
        
    def __rmul__(self, other):
        return MIArray.__mul__(self, other)
        
    def __div__(self, other):
        other = MIArray.__value_other(self, other)
        r = ArrayMath.div(self.array, other)        
        if r is None:
            raise ValueError('Dimension missmatch, can not broadcast!')
        return MIArray(r)
        
    def __rdiv__(self, other):
        other = MIArray.__value_other(self, other)
        r = ArrayMath.div(other, self.array)        
        if r is None:
            raise ValueError('Dimension missmatch, can not broadcast!')
        return MIArray(r)
        
    def __pow__(self, other):
        other = MIArray.__value_other(self, other)
        r = ArrayMath.pow(self.array, other)        
        if r is None:
            raise ValueError('Dimension missmatch, can not broadcast!')
        return MIArray(r)
        
    def __rpow__(self, other):
        other = MIArray.__value_other(self, other)
        r = ArrayMath.pow(other, self.array)        
        if r is None:
            raise ValueError('Dimension missmatch, can not broadcast!')
        return MIArray(r)
        
    def __neg__(self):
        r = MIArray(ArrayMath.sub(0, self.array))
        return r
        
    def __lt__(self, other):
        other = MIArray.__value_other(self, other)
        r = MIArray(ArrayMath.lessThan(self.array, other))
        return r
        
    def __le__(self, other):
        other = MIArray.__value_other(self, other)
        r = MIArray(ArrayMath.lessThanOrEqual(self.array, other))        
        return r
        
    def __eq__(self, other):
        other = MIArray.__value_other(self, other)
        r = MIArray(ArrayMath.equal(self.array, other))
        return r
        
    def __ne__(self, other):
        other = MIArray.__value_other(self, other)
        r = MIArray(ArrayMath.notEqual(self.array, other))
        return r
        
    def __gt__(self, other):
        other = MIArray.__value_other(self, other)
        r = MIArray(ArrayMath.greaterThan(self.array, other))
        return r
        
    def __ge__(self, other):
        other = MIArray.__value_other(self, other)
        r = MIArray(ArrayMath.greaterThanOrEqual(self.array, other))
        return r
        
    def __and__(self, other):
        other = MIArray.__value_other(self, other)
        r = MIArray(ArrayMath.bitAnd(self.array, other))
        return r
        
    def __or__(self, other):
        other = MIArray.__value_other(self, other)
        r = MIArray(ArrayMath.bitOr(self.array, other))
        return r
        
    def __xor__(self, other):
        other = MIArray.__value_other(self, other)
        r = MIArray(ArrayMath.bitXor(self.array, other))
        return r
        
    def __invert__(self):
        other = MIArray.__value_other(self, other)
        r = MIArray(ArrayMath.bitInvert(self.array))
        return r
        
    def __lshift__(self, other):
        other = MIArray.__value_other(self, other)
        r = MIArray(ArrayMath.leftShift(self.array, other))
        return r
        
    def __rshift__(self, other):
        other = MIArray.__value_other(self, other)
        r = MIArray(ArrayMath.rightShift(self.array, other))
        return r           
    
    def getsize():
        if name == 'size':
            sizestr = str(self.shape[0])
            if self.ndim > 1:
                for i in range(1, self.ndim):
                    sizestr = sizestr + '*%s' % self.shape[i]
            return sizestr
    
    def astype(self, dtype):
        if dtype == 'int' or dtype is int:
            r = MIArray(ArrayUtil.toInteger(self.array))
        elif dtype == 'float' or dtype is float:
            r = MIArray(ArrayUtil.toFloat(self.array))
        else:
            r = self
        return r
        
    def min(self, fill_value=None):
        '''
        Get minimum value.
        
        :param fill_value: (*float*) Fill value.
        
        :returns: Minimum value.
        '''
        if fill_value == None:
            return ArrayMath.getMinimum(self.array)
        else:
            return ArrayMath.getMinimum(self.array, fill_value)
            
    def argmin(self, axis=None):
        '''
        Returns the indices of the minimum values along an axis.
        
        :param axis: (*int*) By default, the index is into the flattened array, otherwise 
            along the specified axis.
            
        :returns: Array of indices into the array. It has the same shape as a.shape with the 
            dimension along axis removed.
        '''
        if axis is None:
            r = ArrayMath.argMin(self.array)
            return r
        else:
            r = ArrayMath.argMin(self.array, axis)
            return MIArray(r)
            
    def argmax(self, axis=None):
        '''
        Returns the indices of the minimum values along an axis.
        
        :param axis: (*int*) By default, the index is into the flattened array, otherwise 
            along the specified axis.
            
        :returns: Array of indices into the array. It has the same shape as a.shape with the 
            dimension along axis removed.
        '''
        if axis is None:
            r = ArrayMath.argMax(self.array)
            return r
        else:
            r = ArrayMath.argMax(self.array, axis)
            return MIArray(r)
        
    def max(self, fill_value=None):
        '''
        Get maximum value.
        
        :param fill_value: (*float*) Fill value.
        
        :returns: Maximum value.
        '''
        if fill_value == None:
            return ArrayMath.getMaximum(self.array)
        else:
            return ArrayMath.getMaximum(self.array, fill_value)
        
    def getshape(self):
        return self.array.getShape()
        
    def sum(self, fill_value=None):
        '''
        Get summarize value.
        
        :param fill_value: (*float*) Fill value.
        
        :returns: Summarize value.
        '''
        if fill_value == None:
            return ArrayMath.sum(self.array)
        else:
            return ArrayMath.sum(self.array, fill_value)
            
    def prod(self):
        '''
        Return the product of array elements.
        
        :returns: (*float*) Produce value.
        '''
        return ArrayMath.prodDouble(self.array)
        
    def abs(self):
        '''
        Calculate the absolute value element-wise.
        
        :returns: An array containing the absolute value of each element in x. 
            For complex input, a + ib, the absolute value is \sqrt{ a^2 + b^2 }.
        '''
        return MIArray(ArrayMath.abs(self.array))
            
    def ave(self, fill_value=None):
        if fill_value == None:
            return ArrayMath.aveDouble(self.array)
        else:
            return ArrayMath.aveDouble(self.array, fill_value)
            
    def mean(self, fill_value=None):
        if fill_value == None:
            return ArrayMath.aveDouble(self.array)
        else:
            return ArrayMath.aveDouble(self.array, fill_value)
            
    def median(self, axis=None):
        if axis is None:
            return ArrayMath.median(self.array)
        else:
            return MIArray(ArrayMath.median(self.array, axis))
            
    def sqrt(self):
        return MIArray(ArrayMath.sqrt(self.array))
    
    def sin(self):
        return MIArray(ArrayMath.sin(self.array))
        
    def cos(self):
        return MIArray(ArrayMath.cos(self.array))
        
    def tan(self):
        return MIArray(ArrayMath.tan(self.array))
        
    def asin(self):
        return MIArray(ArrayMath.asin(self.array))
        
    def acos(self):
        return MIArray(ArrayMath.acos(self.array))
        
    def atan(self):
        return MIArray(ArrayMath.atan(self.array))
        
    def exp(self):
        return MIArray(ArrayMath.exp(self.array))
        
    def log(self):
        return MIArray(ArrayMath.log(self.array))
        
    def log10(self):
        return MIArray(ArrayMath.log10(self.array))
            
    def aslist(self):
        r = ArrayMath.asList(self.array)
        return list(r)
        
    def tolist(self):
        '''
        Convert to a list
        '''
        r = ArrayMath.asList(self.array)
        return list(r)
        
    def index(self, v):
        '''
        Get index of a value in the array.
        
        :param v: (*object*) Value object.
        
        :returns: (*int*) Value index.
        '''
        return self.tolist().index(v)
        
    def asarray(self):
        return self.array
        
    def reshape(self, *args):
        if len(args) == 1:
            shape = args[0]
            if isinstance(shape, int):
                shape = [shape]
        else:
            shape = []
            for arg in args:
                shape.append(arg)
        shape = jarray.array(shape, 'i')
        return MIArray(self.array.reshape(shape))
        
    def transpose(self):
        '''
        Transpose 2-D array.
        
        :returns: Transposed array.
        '''
        if self.ndim == 1:
            return self[:]
        dim1 = 0
        dim2 = 1
        r = ArrayMath.transpose(self.asarray(), dim1, dim2)
        return MIArray(r)
        
    T = property(transpose)
    
    def inv(self):
        '''
        Calculate inverse matrix array.
        
        :returns: Inverse matrix array.
        '''
        r = LinalgUtil.inv(self.array)
        return MIArray(r)
        
    I = property(inv)
        
    def flatten(self):
        '''
        Return a copy of the array collapsed into one dimension.
        
        :returns: (*MIArray*) A copy of the input array, flattened to one dimension.
        '''
        r = self.reshape(int(self.array.getSize()))
        return r
        
    def repeat(self, repeats, axis=None):
        '''
        Repeat elements of an array.
        
        :param repeats: (*int or list of ints*) The number of repetitions for each 
            element. repeats is broadcasted to fit the shape of the given axis.
        :param axis: (*int*) The axis along which to repeat values. By default, use 
            the flattened input array, and return a flat output array.
        
        :returns: (*array_like*) Repeated array.
        '''
        if isinstance(repeats, int):
            repeats = [repeats]
        if axis is None:
            r = ArrayUtil.repeat(self.array, repeats)
        else:
            r = ArrayUtil.repeat(self.array, repeats, axis)
        return MIArray(r)
        
    def take(self, indices):
        '''
        Take elements from an array along an axis.
        
        :param indices: (*array_like*) The indices of the values to extract.
        
        :returns: (*array*) The returned array has the same type as a.
        '''
        ilist = [indices]
        r = ArrayMath.take(self.array, ilist)
        return MIArray(r)
    
    def asdimarray(self, x, y, fill_value=-9999.0):
        dims = []
        ydim = Dimension(DimensionType.Y)
        ydim.setDimValues(y.aslist())
        dims.append(ydim)
        xdim = Dimension(DimensionType.X)
        xdim.setDimValues(x.aslist())
        dims.append(xdim)        
        return DimArray(self, dims, fill_value)
        
    def join(self, b, dimidx):
        r = ArrayMath.join(self.array, b.array, dimidx)
        return MIArray(r)
        
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
            if isinstance(polygon, MILayer):
                polygon = polygon.layer
            return MIArray(ArrayMath.inPolygon(self.array, x.aslist(), y.aslist(), polygon))
        
    # def maskout(self, mask, x=None, y=None, fill_value=Double.NaN):
        # if isinstance(mask, MIArray):
            # r = ArrayMath.maskout(self.array, mask.asarray(), fill_value)
            # return MIArray(r)
        # else:
            # if isinstance(x, MIArray):
                # xl = x.aslist()
            # else:
                # xl = x
            # if isinstance(y, MIArray):
                # yl = y.aslist()
            # else:
                # yl = y
            # if isinstance(mask, MILayer):
                # mask = mask.layer
            # return MIArray(ArrayMath.maskout(self.array, xl, yl, mask, fill_value))
        
    def savegrid(self, x, y, fname, format='surfer', **kwargs):
        gdata = GridArray(self.array, x.array, y.array, -9999.0)
        if format == 'surfer':
            gdata.saveAsSurferASCIIFile(fname)
        elif format == 'bil':
            gdata.saveAsBILFile(fname)
        elif format == 'esri_ascii':
            gdata.saveAsESRIASCIIFile(fname)
        elif format == 'micaps4':
            desc = kwargs.pop('description', 'var')
            date = kwargs.pop('date', datetime.datetime.now())
            date = miutil.jdate(date)
            hours = kwargs.pop('hours', 0)
            level = kwargs.pop('level', 0)
            smooth = kwargs.pop('smooth', 1)
            boldvalue =kwargs.pop('boldvalue', 0)
            proj = kwargs.pop('proj', None)
            if proj is None:
                gdata.saveAsMICAPS4File(fname, desc, date, hours, level, smooth, boldvalue)
            else:
                if proj.isLonLat():
                    gdata.saveAsMICAPS4File(fname, desc, date, hours, level, smooth, boldvalue)
                else:
                    gdata.saveAsMICAPS4File(fname, desc, date, hours, level, smooth, boldvalue, proj)
