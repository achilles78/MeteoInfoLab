#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2017-3-7
# Purpose: MeteoInfo DataFrame module
# Note: Jython
#-----------------------------------------------------

from org.meteoinfo.data.dataframe import DataFrame as MIDataFrame
from org.meteoinfo.data.dataframe import Series as MISeries
from ucar.ma2 import Range

import miarray
from miarray import MIArray
import dimarray
from dimarray import DimArray
import minum as minum
import series
from series import Series
import index
from index import Index

from java.lang import Double
nan = Double.NaN

class DataFrame(object):

    def __init__(self, data=None, index=None, columns=None, dataframe=None):
        '''
        Two-dimensional size-mutable, potentially heterogeneous tabular data structure with 
        labeled axes (rows and columns). Arithmetic operations align on both row and column 
        labels. Can be thought of as a dict-like container for Series objects.
        
        :param data: (*array_like*) Two-dimensional array data or list of one-dimensional arrays.
        :param index: (*list*) Data index list. Values must be unique and hashable, same length as data.
        :param columns: (*list*) Column labels to use for resulting frame. Will default to 
            arange(n) if no column labels are provided
        '''                         
        if dataframe is None:
            if isinstance(data, dict):
                columns = data.keys()
                dlist = []
                n = 1
                for v in data.values():
                    if isinstance(v, (list, tuple)):
                        n = len(v)
                        v = minum.array(v)                    
                    elif isinstance(v, MIArray):
                        n = len(v)
                    dlist.append(v)
                for i in range(len(dlist)):
                    d = dlist[i]
                    if not isinstance(d, MIArray):
                        d = [d] * n
                        d = minum.array(d)
                        dlist[i] = d
                data = dlist
                
            if isinstance(data, MIArray):
                n = len(data)
                data = data.array
            else:
                dlist = []
                n = len(data[0])
                for dd in data:
                    dlist.append(dd.array)
                data = dlist
                    
            if index is None:
                index = range(0, n)
            else:
                if n != len(index):
                    raise ValueError('Wrong length of index!')
            if isinstance(index, (MIArray, DimArray)):
                index = index.tolist()
                
            if isinstance(index, Index):
                self._index = index
            else:
                self._index = Index(index)
            self._dataframe = MIDataFrame(data, self._index._index, columns)
        else:
            self._dataframe = dataframe
            self._index = Index(index=self._dataframe.getIndex())
        
    #---- index property
    def get_index(self):
        return self._index
        
    def set_index(self, value):
        self._index = Index(value)
        self._dataframe.setIndex(self._index.data)
        
    index = property(get_index, set_index)
    
    #---- data property
    def get_data(self):
        return MIArray(self._dataframe.getData())
        
    def set_data(self, value):
        value = minum.array(value)
        self._dataframe.setData(value.array)
        
    data = property(get_data, set_data)
    values = property(get_data)
    
    #---- columns property
    def get_columns(self):
        return self._dataframe.getColumns()
        
    def set_columns(self, value):
        self._dataframe.setColumns(value)
        
    columns = property(get_columns, set_columns)
    
    #---- shape property
    def get_shape(self):
        s = self._dataframe.getShape()
        s1 = []
        for i in range(len(s)):
            s1.append(s[i])
        return tuple(s1)
        
    shape = property(get_shape)
    
    #---- dtypes property
    def get_dtypes(self):
        colnames = list(self.columns.getNames())
        datatypes = list(self.columns.getDataTypes())
        r = Series(datatypes, colnames, 'DataTypes')
        return r
        
    dtypes = property(get_dtypes)
        
    def __getitem__(self, key):
        if isinstance(key, basestring):
            data = self._dataframe.getColumnData(key)
            if data is None:
                return data
            idx = self._index[:]
            r = Series(MIArray(data), idx, key)
            return r
            
        hascolkey = True
        if isinstance(key, tuple): 
            ridx = key[0]
            cidx = key[1]
            if isinstance(ridx, int) and isinstance(cidx, int):
                if ridx < 0:
                    ridx = self.shape[0] + ridx
                if cidx < 0:
                    cidx = self.shape[1] + cidx
                return self._dataframe.getValue(ridx, cidx)
            elif isinstance(ridx, int) and isinstance(cidx, basestring):
                if ridx < 0:
                    ridx = self.shape[0] + ridx
                return self._dataframe.getValue(ridx, cidx)
        else:
            key = (key, slice(None))
            hascolkey = False
            
        k = key[0]
        if isinstance(k, int):
            sidx = k
            if sidx < 0:
                sidx = self.shape[0] + sidx
            eidx = sidx + 1
            step = 1
            rowkey = Range(sidx, eidx, step)
        elif isinstance(k, slice):
            if isinstance(k.start, basestring):
                sidx = self._index.index(k.start)
                if sidx < 0:
                    sidx = 0
            else:
                sidx = 0 if k.start is None else k.start
                if sidx < 0:
                    sidx = self.shape[0] + sidx
            if isinstance(k.stop, basestring):
                eidx = self._index.index(k.stop) + 1
                if eidx < 0:
                    eidx = self.shape[0]
            else:
                eidx = self.shape[0] if k.stop is None else k.stop
                if eidx < 0:
                    eidx = self.shape[0] + eidx                    
            step = 1 if k.step is None else k.step
            rowkey = Range(sidx, eidx, step)
        elif isinstance(k, list):
            if isinstance(k[0], int):
                rowkey = key
            else:
                tlist = []
                for tstr in k:
                    idx = self._index.index(tstr)
                    if idx >= 0:
                        tlist.append(idx)
                rowkey = tlist
        else:
            return None
                   
        if not hascolkey:
            colkey = Range(0, self.shape[1], 1)
        else:
            k = key[1]
            if isinstance(k, int):
                sidx = k
                if sidx < 0:
                    sidx = self.shape[1] + sidx
                eidx = sidx + 1
                step = 1
                colkey = Range(sidx, eidx, step)
            elif isinstance(k, slice):
                sidx = 0 if k.start is None else k.start
                if sidx < 0:
                    sidx = self.shape[1] + sidx
                eidx = self.shape[1] if k.stop is None else k.stop
                if eidx < 0:
                    eidx = self.shape[1] + eidx                    
                step = 1 if k.step is None else k.step
                colkey = Range(sidx, eidx, step)        
            elif isinstance(k, list):
                if isinstance(k[0], int):
                    colkey = key
                else:
                    colkey = self.columns.indexOf(k)               
            elif isinstance(k, basestring):
                col = self.columns.indexOf(k)
                colkey = Range(col, col + 1, 1)
            else:
                return None
        
        r = self._dataframe.select(rowkey, colkey)
        if r is None:
            return None
        if isinstance(r, MISeries):
            r = Series(series=r)
        else:
            r = DataFrame(dataframe=r)
        return r
        
    def __setitem__(self, key, value):
        ikey = self.__getkey(key)[0]
        self.data.__setitem__(ikey, value)
    
    def __getkey(self, key):
        if isinstance(key, basestring):
            rkey = self.index.get_indices(key)
            ikey = rkey[0]
            rindex = rkey[1]
            if len(ikey) == 1:
                ikey = ikey[0]
            elif len(ikey) > 1:
                ikey = list(ikey)
            else:
                raise KeyError(key)
            return ikey, rindex
        elif isinstance(key, (list, tuple, MIArray, DimArray)) and isinstance(key[0], basestring):
            if isinstance(key, (MIArray, DimArray)):
                key = key.asarray()            
            rkey = self.index.get_indices(key)
            ikey = rkey[0]
            rindex = rkey[1]
            rdata = rkey[2]
            rrindex = rkey[3]
            if len(ikey) == 0:
                raise KeyError()
            else:
                ikey = list(ikey)
            return ikey, rindex, rdata, rrindex
        else:
            return key, None
        
    def __iter__(self):
        """
        provide iteration over the values of the Series
        """
        #return iter(self.data)
        #return zip(iter(self.index), iter(self.data))
        return iter(self.index)
        
    def iteritems(self):
        """
        Lazily iterate over (index, value) tuples
        """
        return zip(iter(self.index), iter(self))
        
    def __len__(self):
        return self.shape[0]
        
    def __str__(self):
        return self._dataframe.toString() 
        
    def __repr__(self):
        return self._dataframe.toString()    
        
    def head(self, n=5):
        '''
        Get top rows
        
        :param n: (*int*) row number.
        
        :returns: Top rows
        '''
        print self._dataframe.head(n)
        
    def tail(self, n=5):
        '''
        Get bottom rows
        
        :param n: (*int*) row number.
        
        :returns: Bottom rows
        '''
        print self._dataframe.tail(n)
        
    def transpose(self):
        '''
        Transpose data frame.
        
        :returns: Transposed data frame.
        '''        
        r = self._dataframe.transpose()
        return DataFrame(dataframe=r)
        
    T = property(transpose)