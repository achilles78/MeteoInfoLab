# coding=utf-8
#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2016-7-10
# Purpose: MeteoInfoLab random module
# Note: Jython
#-----------------------------------------------------

from org.meteoinfo.math import RandomUtil

from mipylib.numeric.miarray import MIArray

__all__ = [
    'rand','randn'
    ]

def rand(*args):
    """
    Random values in a given shape.
    
    Create an array of the given shape and propagate it with random samples from a uniform 
        distribution over [0, 1).
    
    :param d0, d1, ..., dn: (*int*) optional. The dimensions of the returned array, should all
        be positive. If no argument is given a single Python float is returned.
        
    :returns: Random values array.
    """
    if len(args) == 0:
        return RandomUtil.rand()
    elif len(args) == 1:
        return MIArray(RandomUtil.rand(args[0]))
    else:
        return MIArray(RandomUtil.rand(args))
        
def randn(*args):
    """
    Return a sample (or samples) from the “standard normal” distribution.
    
    Create an array of the given shape and propagate it with random samples from a "normal" 
        (Gaussian) distribution of mean 0 and variance 1.
    
    :param d0, d1, ..., dn: (*int*) optional. The dimensions of the returned array, should all
        be positive. If no argument is given a single Python float is returned.
        
    :returns: Random values array.
    """
    if len(args) == 0:
        return RandomUtil.randn()
    elif len(args) == 1:
        return MIArray(RandomUtil.randn(args[0]))
    else:
        return MIArray(RandomUtil.randn(args))