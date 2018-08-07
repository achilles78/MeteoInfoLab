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
                self._index = Index.factory(index)
            self._data = data
            self._series = MISeries(data.array, self._index._index, name)
        else:
            self._series = series
            self._data = MIArray(self._series.getData())
            self._index = Index.factory(index=self._series.getIndex())
        
    #---- index property
    def get_index(self):
        return self._index
        
    def set_index(self, value):
        self._index = Index(value)
        self._series.setIndex(self._index.data)
        
    index = property(get_index, set_index)
    
    #---- values property
    def get_values(self):
        return self._data
        
    def set_values(self, value):
        self._data = minum.array(value)
        self._series.setData(self._data.array)
        
    values = property(get_values, set_values)
    
    #---- name property
    def get_name(self):
        return self._series.getName()
        
    def set_name(self, value):
        self._series.setName(value)
        
    name = property(get_name, set_name)
    
    #---- dtype property
    def get_dtype(self):
        return self.values.dtype
        
    dtype = property(get_dtype)
        
    def __getitem__(self, key):
        if isinstance(key, int):
            if key < 0 or key >= self.__len__():
                raise KeyError(key)
            return self._series.getValue(key)
        elif isinstance(key, (list, tuple, MIArray)):
            if isinstance(key, MIArray):
                key = key.aslist()
            if isinstance(key[0], int):
                r = self._series.getValues(key)
            else:
                r = self._series.getValuesByIndex(key)
            return Series(series=r)
        elif isinstance(key, slice):
            if isinstance(key.start, basestring):
                sidx = self._index.index(key.start)
                if sidx < 0:
                    sidx = 0
            else:
                sidx = 0 if key.start is None else key.start
                if sidx < 0:
                    sidx = self.__len__() + sidx
            if isinstance(key.stop, basestring):
                eidx = self._index.index(key.stop)
                if eidx < 0:
                    eidx = self.__len__()
            else:
                eidx = self.__len__() - 1 if k.stop is None else k.stop - 1
                if eidx < 0:
                    eidx = self.__len__() + eidx                    
            step = 1 if k.step is None else k.step
            rowkey = Range(sidx, eidx, step)   
            r = self._series.getValues(rowkey)
            return Series(series=r)
        else:
            i = self._series.getIndex().indexOf(key)
            if i < 0:
                raise KeyError(key)
            return self._series.getValue(i)
        
    def __setitem__(self, key, value):
        if isinstance(key, Series):
            self._series.setValue(key._series, value)
            return None
            
        ikey = self.__getkey(key)[0]
        self.values.__setitem__(ikey, value)
    
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
        #return iter(self.values)
        #return zip(iter(self.index), iter(self.values))
        return iter(self.index)
        
    def iteritems(self):
        """
        Lazily iterate over (index, value) tuples
        """
        return zip(iter(self.index), iter(self))
        
    def __len__(self):
        return self.values.__len__()
        
    def __str__(self):
        return self.__repr__()
        
    def __repr__(self):
        return self._series.toString()
        
    def __eq__(self, other):
        r = Series(series=self._series.equal(other))
        return r
        
    def __lt__(self, other):        
        r = Series(series=self._series.lessThan(other))
        return r
        
    def __le__(self, other):        
        r = Series(series=self._series.lessThanOrEqual(other))
        return r
        
    def __gt__(self, other):        
        r = Series(series=self._series.greaterThan(other))
        return r
        
    def __ge__(self, other):        
        r = Series(series=self._series.greaterThanOrEqual(other))
        return r

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
        r = self._series.mean()
        if isinstance(r, (MISeries)):
            return Series(series=r)
        else:
            return r
            
    def max(self):
        '''
        Return the maximum of the values
        
        :returns: Maximum value
        '''
        r = self._series.max()
        if isinstance(r, (MISeries)):
            return Series(series=r)
        else:
            return r
            
    def min(self):
        '''
        Return the minimum of the values
        
        :returns: Minimum value
        '''
        r = self._series.min()
        if isinstance(r, (MISeries)):
            return Series(series=r)
        else:
            return r
        
    def groupby(self, by=None):
        '''
        Group Series.
        
        :param by: Used to determine the groups for the groupby.
        
        :returns: Grouped series
        '''
        r = self._series.groupBy(by)
        return Series(series=r)
        
    def resample(self, by):
        '''
        Group series by date time index.
        
        :param by: Used to determine the groups for the groupby.
        
        :returns: Grouped Series
        '''
        df = self._series.resample(by)
        return Series(series=df)
        
#################################################################