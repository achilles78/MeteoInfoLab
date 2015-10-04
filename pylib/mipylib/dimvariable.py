#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2014-12-27
# Purpose: MeteoInfo Dataset module
# Note: Jython
#-----------------------------------------------------
from org.meteoinfo.data.meteodata import Variable, Dimension
from org.meteoinfo.data import ArrayMath
from ucar.nc2 import Attribute
import dimarray
from dimarray import DimArray, PyGridData
import miarray
from miarray import MIArray

# Dimension variable
class DimVariable():
    
    # variable must be org.meteoinfo.data.meteodata.Variable
    # dataset is DimDataFile
    def __init__(self, variable=None, dataset=None, ncvariable=None):
        self.variable = variable
        self.dataset = dataset
        self.ncvariable = ncvariable
        if not variable is None:
            self.name = variable.getName()
            self.dims = variable.getDimensions()
            self.ndim = variable.getDimNumber()
            self.fill_value = variable.getFillValue()
            self.scale_factor = variable.getScaleFactor()
            self.add_offset = variable.getAddOffset()
        if not dataset is None:
            self.proj = dataset.proj
            
    def __len__(self):
        len = 1;
        if not self.variable is None:
            for dim in self.variable.getDimensions():
                len = len * dim.getDimLength()            
        return len
        
    def __getitem__(self, indices):
        #print type(indices)
        if not isinstance(indices, tuple):
            inds = []
            inds.append(indices)
            indices = inds
        
        if len(indices) != self.ndim:
            print 'indices must be ' + str(self.ndim) + ' dimensions!'
            return None
            
        origin = []
        size = []
        stride = []
        dims = []
        for i in range(0, self.ndim):   
            k = indices[i]
            if isinstance(k, int):
                sidx = k
                eidx = k
                step = 1
            elif isinstance(k, slice):
                sidx = 0 if k.start is None else k.start
                eidx = self.dimlen(i)-1 if k.stop is None else k.stop
                step = 1 if k.step is None else k.step
            elif isinstance(k, tuple) or isinstance(k, list):
                dim = self.variable.getDimension(i)
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
            origin.append(sidx)
            n = eidx - sidx + 1
            size.append(n)
            stride.append(step)            
            if n > 1:
                dim = self.variable.getDimension(i)
                dims.append(dim.extract(sidx, eidx, step))
        rr = self.dataset.read(self.name, origin, size, stride).reduce()
        ArrayMath.missingToNaN(rr, self.fill_value)
        array = MIArray(rr)
        data = DimArray(array, dims, self.fill_value, self.dataset.proj)
        return data
        
    # get dimension length
    def dimlen(self, idx):
        return self.variable.getDimLength(idx)
        
    def adddim(self, dimtype, dimvalue):
        if isinstance(dimvalue, MIArray):
            dimvalue = dimvalue.aslist()
        self.variable.addDimension(dimtype, dimvalue)
        self.ndim = self.variable.getDimNumber()
    def setdim(self, dimtype, dimvalue, index=None):
        if isinstance(dimvalue, MIArray):
            dimvalue = dimvalue.aslist()
        if index is None:
            self.variable.setDimension(dimtype, dimvalue)
        else:
            self.variable.setDimension(dimtype, dimvalue, index)
        self.ndim = self.variable.getDimNumber()
        
    def addattr(self, attrname, attrvalue):
        self.ncvariable.addAttribute(Attribute(attrname, attrvalue))