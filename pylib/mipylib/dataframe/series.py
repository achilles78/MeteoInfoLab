#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2017-3-7
# Purpose: MeteoInfo Series module
# Note: Jython
#-----------------------------------------------------

from org.meteoinfo.data.dataframe import Series as MISeries

from mipylib.numeric.miarray import MIArray
from mipylib.numeric.dimarray import DimArray
import mipylib.numeric.minum as minum
import index
from index import Index

from java.lang import Double
nan = Double.NaN

class Series(object):

    def __init__(self, data=None, index=None, name=None, series=None):
        '''
        One-dimensional array with axis labels (including time series).
        
        :param data: (*array_like*) One-dimensional array data.
        :param index: (*list*) Data index list. Values must be unique and hashable, same length as data.
        :param name: (*string*) Series name.
        '''
        if series is None:
            if isinstance(data, (list, tuple)):
                data = minum.array(data)
            if index is None:
                index = range(0, len(data))
            else:
                if len(data) != len(index):
                    raise ValueError('Wrong length of index!')
            if isinstance(index, (MIArray, DimArray)):
                index = index.tolist()
            if isinstance(index, Index):
                self._index = index
            else:
                self._index = Index(index)
            self._data = data
            self._series = MISeries(data.array, self._index._index, name)
        else:
            self._series = series
            self._data = MIArray(self._series.getData())
        
    #---- index property
    def get_index(self):
        return self._index
        
    def set_index(self, value):
        self._index = Index(value)
        self._series.setIndex(self._index.data)
        
    index = property(get_index, set_index)
    
    #---- data property
    def get_data(self):
        return self._data
        
    def set_data(self, value):
        self._data = minum.array(value)
        self._series.setData(self._data.array)
        
    data = property(get_data, set_data)
    
    #---- name property
    def get_name(self):
        return self._series.getName()
        
    def set_name(self, value):
        self._series.setName(value)
        
    name = property(get_name, set_name)
    
    #---- dtype property
    def get_dtype(self):
        return self.data.dtype
        
    dtype = property(get_dtype)
        
    def __getitem__(self, key):
        rr = self.__getkey(key)
        ikey = rr[0]
        rdata = self.data.__getitem__(ikey)
        if isinstance(ikey, int): 
            return rdata
        else: 
            rindex = rr[1]
            if rindex is None:
                rindex = self.index.__getitem__(ikey)
            else:
                if len(rr) == 4:
                    rfdata = rr[2]
                    rindex = list(rr[3])
                    rdata = MIArray(self.index.fill_keylist(rdata, rfdata))
            r = Series(rdata, rindex)
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
        return self.data.__len__()
        
    def __str__(self):
        return self.__repr__()
        
    def __repr__(self):
        return self._series.toString()

    def head(self, n=5):
        '''
        Get top rows
        
        :param n: (*int*) row number.
        
        :returns: Top rows
        '''
        print self._series.head(n)
        
    def tail(self, n=5):
        '''
        Get bottom rows
        
        :param n: (*int*) row number.
        
        :returns: Bottom rows
        '''
        print self._series.tail(n)
        
    def mean(self):
        '''
        Return the mean of the values
        
        :returns: Mean value
        '''
        return self._data.mean()