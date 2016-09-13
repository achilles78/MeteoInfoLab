#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2014-12-27
# Purpose: MeteoInfo Dataset module
# Note: Jython
#-----------------------------------------------------
from org.meteoinfo.data.meteodata import Variable, Dimension, DimensionType
from org.meteoinfo.data import ArrayMath, ArrayUtil
from org.meteoinfo.global import PointD
from org.meteoinfo.projection import KnownCoordinateSystems, Reproject
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
            self.datatype = variable.getDataType()
            self.dims = variable.getDimensions()
            self.ndim = variable.getDimNumber()
            self.fill_value = variable.getFillValue()
            self.scale_factor = variable.getScaleFactor()
            self.add_offset = variable.getAddOffset()
        elif not ncvariable is None:
            self.name = ncvariable.getShortName()
            self.dims = ncvariable.getDimensions()
            self.ndim = len(self.dims)
        if not dataset is None:
            self.proj = dataset.proj
            
    def __len__(self):
        len = 1;
        if not self.variable is None:
            for dim in self.variable.getDimensions():
                len = len * dim.getLength()            
        return len
        
    def __getitem__(self, indices):
        if indices is None:
            rr = self.dataset.read(self.name)
            if rr.getDataType().isNumeric():
                ArrayMath.missingToNaN(rr, self.fill_value)
                array = MIArray(rr)
                data = DimArray(array, self.dims, self.fill_value, self.dataset.proj)
                return data
            else:
                return rr
                
        if isinstance(indices, str):    #metadata
            rr = self.dataset.read(self.name)
            m = rr.findMember(indices)
            data = rr.getArray(0, m)
            return MIArray(data)
        
        if not isinstance(indices, tuple):
            inds = []
            inds.append(indices)
            indices = inds
        
        if len(indices) != self.ndim:
            print 'indices must be ' + str(self.ndim) + ' dimensions!'
            return None
            
        if not self.proj is None and not self.proj.isLonLat():
            xlim = None
            ylim = None
            xidx = -1
            yidx = -1
            for i in range(0, self.ndim):
                dim = self.dims[i]
                if dim.getDimType() == DimensionType.X:                    
                    k = indices[i]
                    if isinstance(k, (tuple, list)):
                        xlim = k
                        xidx = i
                elif dim.getDimType() == DimensionType.Y:
                    k = indices[i]
                    if isinstance(k, (tuple, list)):
                        ylim = k
                        yidx = i
            if not xlim is None and not ylim is None:                
                fromproj=KnownCoordinateSystems.geographic.world.WGS1984
                inpt = PointD(xlim[0], ylim[0])
                outpt1 = Reproject.reprojectPoint(inpt, fromproj, self.proj)
                inpt = PointD(xlim[1], ylim[1])
                outpt2 = Reproject.reprojectPoint(inpt, fromproj, self.proj)
                xlim = [outpt1.X, outpt2.X]
                ylim = [outpt1.Y, outpt2.Y]
                indices1 = []
                for i in range(0, self.ndim):
                    if i == xidx:
                        indices1.append(xlim)
                    elif i == yidx:
                        indices1.append(ylim)
                    else:
                        indices1.append(indices[i])
                indices = indices1
        
        origin = []
        size = []
        stride = []
        dims = []
        for i in range(0, self.ndim):  
            dimlen = self.dimlen(i)
            k = indices[i]
            if isinstance(k, int):
                sidx = k
                eidx = k
                step = 1
            elif isinstance(k, slice):
                sidx = 0 if k.start is None else k.start
                eidx = self.dimlen(i)-1 if k.stop is None else k.stop
                step = 1 if k.step is None else k.step
            elif isinstance(k, (tuple, list)):
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
                    if sidx > eidx:
                        iidx = eidx
                        eidx = sidx
                        sidx = iidx
            else:
                print k
                return None
            if eidx >= dimlen:
                print 'Index out of range!'
                return None
            origin.append(sidx)
            n = eidx - sidx + 1
            size.append(n)                   
            if n > 1:
                dim = self.variable.getDimension(i)
                if dim.isReverse():
                    step = -step
                dims.append(dim.extract(sidx, eidx, step))
            stride.append(step) 
        rr = self.dataset.read(self.name, origin, size, stride).reduce()
        if rr.getSize() == 1:
            return rr.getObject(0)
        ArrayMath.missingToNaN(rr, self.fill_value)
        array = MIArray(rr)
        data = DimArray(array, dims, self.fill_value, self.dataset.proj)
        return data
    
    def read(self):
        return MIArray(self.dataset.read(self.name))
    
    # get dimension length
    def dimlen(self, idx):
        return self.dims[idx].getLength()
        
    def dimvalue(self, idx):
        return MIArray(ArrayUtil.array(self.dims[idx].getDimValue()))
        
    def attrvalue(self, key):
        attr = self.variable.findAttribute(key)
        if attr is None:
            return None
        v = MIArray(attr.getValues())
        return v
        
    def xdim(self):
        for dim in self.dims:
            if dim.getDimType() == DimensionType.X:
                return dim        
        return None
        
    def ydim(self):
        for dim in self.dims:
            if dim.getDimType() == DimensionType.Y:
                return dim        
        return None
        
    def zdim(self):
        for dim in self.dims:
            if dim.getDimType() == DimensionType.Z:
                return dim        
        return None
        
    def tdim(self):
        for dim in self.dims:
            if dim.getDimType() == DimensionType.T:
                return dim        
        return None
        
    def adddim(self, dimtype, dimvalue):
        if isinstance(dimvalue, MIArray):
            dimvalue = dimvalue.aslist()
        self.variable.addDimension(dimtype, dimvalue)
        self.ndim = self.variable.getDimNumber()
        
    def setdim(self, dimtype, dimvalue, index=None, reverse=False):
        if isinstance(dimvalue, MIArray):
            dimvalue = dimvalue.aslist()
        if index is None:
            self.variable.setDimension(dimtype, dimvalue, reverse)
        else:
            self.variable.setDimension(dimtype, dimvalue, reverse, index)
        self.ndim = self.variable.getDimNumber()
        
    def setdimrev(self, idx, reverse):
        self.dims[idx].setReverse(reverse)
        
    def addattr(self, attrname, attrvalue):
        self.ncvariable.addAttribute(Attribute(attrname, attrvalue))