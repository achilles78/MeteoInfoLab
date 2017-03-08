#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2017-3-7
# Purpose: MeteoInfo Series module
# Note: Jython
#-----------------------------------------------------

import miarray
from miarray import MIArray
import dimarray
from dimarray import DimArray
import minum as minum

from java.lang import Double
nan = Double.NaN

class Series(object):

    def __init__(self, data=None, index=None):
        '''
        One-dimensional array with axis labels (including time series).
        
        :param data: (*array_like*) One-dimensional array data.
        :param index: (*list*) Data index list. Values must be unique and hashable, same length as data.
        '''
        if isinstance(data, (list, tuple)):
            data = minum.array(data)
        self.data = data
        if index is None:
            index = range(0, len(data))
        if isinstance(index, (list, tuple)):
            index = minum.array(index)
        elif isinstance(index, DimArray):
            index = index.array
        self._index = index
        
    #---- Index property
    def get_index(self):
        return self._index
        
    def set_index(self, value):
        if isinstance(value, (list, tuple)):
            value = minum.array(value)
        self._index = value
        
    index = property(get_index, set_index)
        
    def __getitem__(self, key):
        ikey = self.__getkey(key)
        rdata = self.data.__getitem__(ikey)
        if isinstance(rdata, (list, MIArray, DimArray)):
            rindex = self.index.__getitem__(ikey)
            if isinstance(key, (list, MIArray, DimArray)) and isinstance(key[0], basestring):
                if len(rindex) < len(key):
                    nrdata = []
                    for k in key:
                        if k in rindex:
                            nrdata.append(rdata[rindex.index(k)])
                        else:
                            nrdata.append(nan)
                    rdata = nrdata
            r = Series(rdata, key)
            return r
        else:
            return rdata
        
    def __setitem__(self, key, value):
        key = self.__getkey(key)
        self.data.__setitem__(key, value)
    
    def __getkey(self, key):
        if isinstance(key, basestring):
            try:
                key = self.index.index(key)
            except:
                raise KeyError(key)
        elif isinstance(key, (list, tuple, MIArray, DimArray)) and isinstance(key[0], basestring):
            nkey = []
            for k in key:
                if k in self.index:
                    nkey.append(self.index.index(k))
            if len(nkey) == 0:
                raise KeyError()
            key = nkey
        return key
        
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