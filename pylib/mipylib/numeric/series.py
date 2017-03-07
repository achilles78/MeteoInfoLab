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

class Series():

    def __init__(self, data=None, index=None):
        '''
        One-dimensional array with axis labels (including time series).
        
        :param data: (*array_like*) One-dimensional array data.
        :param index: (*list*) Data index list. Values must be unique and hashable, same length as data.
        '''
        self.data = data
        if index is None:
            index = range(0, len(data))
        if isinstance(index, (MIArray, DimArray)):
            index = index.tolist()
        self.index = index
        
    def __getitem__(self, key):
        if isinstance(key, (str, unicode)):
            key = self.index.index(key)
        elif isinstance(key, (list, tuple, MIArray, DimArray)) and isinstance(key[0], (str, unicode)):
            nkey = []
            for k in key:
                nkey.append(self.index.index(k))
            key = nkey
        return self.data.__getitem__(key)