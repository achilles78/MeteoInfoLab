#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2018-7-18
# Purpose: MeteoInfo index module
# Note: Jython
#-----------------------------------------------------

from org.meteoinfo.data.dataframe import Index as MIIndex
from org.meteoinfo.data.dataframe import DateTimeIndex as MIDateTimeIndex

import datetime

import miarray
from miarray import MIArray
import mipylib.miutil as miutil

class Index(object):
    
    def __init__(self, data=None, index=None):
        if index is None:
            if isinstance(data, MIArray):
                data = data.aslist()
            self.data = data
            self._index = MIIndex(data)
        else:
            self._index = index
            self.data = list(self._index.getValues())
        
    def __len__(self):
        return self._index.size()
        
    def __iter__(self):
        """
        provide iteration over the values of the Index
        """
        return iter(self._index)
        
    def __str__(self):
        return self.__repr__()
        
    def __repr__(self):
        return self._index.toString()
        
    def __getitem__(self, k):
        if isinstance(k, int):
            return self.data[k]
        else:
            sidx = 0 if k.start is None else k.start
            if sidx < 0:
                sidx = self.__len__() + sidx
            eidx = self.__len__() if k.stop is None else k.stop
            if eidx < 0:
                eidx = self.__len__() + eidx                    
            step = 1 if k.step is None else k.step
            r = self._index.subIndex(sidx, eidx, step)
            return Index(index=r)
            
    def index(self, v):
        '''
        Get index of a value.
        
        :param v: (*object*) value
        
        :returns: (*int*) Value index
        '''
        return self._index.indexOf(v)

    def get_indices(self, key):
        return self._index.getIndices(key)
        
    def fill_keylist(self, rdata, rfdata):
        return self._index.fillKeyList(rdata.asarray(), rfdata)
        
############################################
class DateTimeIndex(Index):
    
    def __init__(self, data=None, start=None, end=None, periods=None, freq='D', index=None):
        if index is None:
            if not data is None:
                if isinstance(data, MIArray):
                    data = data.aslist()
                self.data = data
                self._index = MIDateTimeIndex(miutil.jdate(data))
            else:
                if start is None:
                    self._index = MIDateTimeIndex(periods, end, freq)
                elif end is None:
                    self._index = MIDateTimeIndex(start, periods, freq)
                else:
                    self._index = MIDateTimeIndex(start, end, freq)
                self.data = miutil.pydate(list(self._index.getDateValues()))
        else:
            self._index = index
            self.data = list(self._index.getValues())
            
    def index(self, v):
        '''
        Get index of a value.
        
        :param v: (*datetime or string*) Date time value
        
        :returns: (*int*) Value index
        '''
        if isinstance(v, datetime.datetime):
            v = miutil.str2jdate(v)
        return self._index.indexOf(v)
        
#############################################
def date_range(start=None, end=None, periods=None, freq='D'):
    '''
    Create DateTimeIndex by date range.
    
    :param start: (*string or datetime*) Start date time.
    :param end: (*string or datetime*) End date time.
    :param periods: (*int*) Periods number.
    :param freq: (*string*) Date time frequent value [ Y | M | D | H | m | S ]. 
    
    :returns: (*DateTimeIndex*) DateTimeIndex
    '''
    r = DateTimeIndex(start=start, end=end, periods=periods, freq=freq)
    return r
    