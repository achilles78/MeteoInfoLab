#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2017-3-7
# Purpose: MeteoInfo Series module
# Note: Jython
#-----------------------------------------------------

from org.meteoinfo.data import SeriesUtil

import miarray
from miarray import MIArray
import dimarray
from dimarray import DimArray
import minum as minum

from java.lang import Double
nan = Double.NaN

class Series(object):

    def __init__(self, data=None, index=None, name=None):
        '''
        One-dimensional array with axis labels (including time series).
        
        :param data: (*array_like*) One-dimensional array data.
        :param index: (*list*) Data index list. Values must be unique and hashable, same length as data.
        :param name: (*string*) Series name.
        '''
        if isinstance(data, (list, tuple)):
            data = minum.array(data)
        self.data = data
        if index is None:
            index = range(0, len(data))
        else:
            if len(data) != len(index):
                raise ValueError('Wrong length of index!')
        # if isinstance(index, (list, tuple)):
            # index = minum.array(index)
        if isinstance(index, (MIArray, DimArray)):
            index = index.tolist()
        self._index = index
        self.name = name
        
    #---- Index property
    def get_index(self):
        return self._index
        
    def set_index(self, value):
        # if isinstance(value, (list, tuple)):
            # value = minum.array(value)
        self._index = value
        
    index = property(get_index, set_index)
        
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
                    rdata = MIArray(SeriesUtil.fillKeyList(rdata.asarray(), rfdata))
            r = Series(rdata, rindex)
            return r
        
    def __setitem__(self, key, value):
        ikey = self.__getkey(key)[0]
        self.data.__setitem__(ikey, value)
    
    def __getkey(self, key):
        ii = self.index
        if isinstance(ii, (MIArray, DimArray)):
            ii = ii.tolist()
        if isinstance(key, basestring):
            rkey = SeriesUtil.getIndices(ii, key)
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
            rkey = SeriesUtil.getIndices(ii, key)
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
        r = ''
        for i, v in zip(self.index, self.data):
            r += str(i) + '    ' + str(v)
            r += '\n'
        r += 'dtype: ' + str(self.data.dtype)
        return r
        
    def __repr__(self):
        r = ''
        n = 0
        for i, v in zip(self.index, self.data):
            r += str(i) + '    ' + str(v)
            r += '\n'
            n += 1
            if n > 100:
                r += '...\n'
                break
        r += 'dtype: ' + str(self.data.dtype)
        return r        