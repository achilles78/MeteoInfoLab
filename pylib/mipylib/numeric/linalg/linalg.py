# coding=utf-8
#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2016-7-10
# Purpose: MeteoInfoLab linear algebra module
# Note: Jython
#-----------------------------------------------------

from org.meteoinfo.math.linalg import LinalgUtil

from mipylib.numeric.miarray import MIArray

__all__ = [
    'solve'
    ]

def solve(a, b):
    '''
    Solve a linear matrix equation, or system of linear scalar equations.
    
    Computes the “exact” solution, x, of the well-determined, i.e., full rank, linear 
    matrix equation ax = b.
    
    :param a: (*array_like*) Coefficient matrix.
    :param b: (*array_like*) Ordinate or “dependent variable” values.
    
    :returns: (*array_like*) Solution to the system a x = b. Returned shape is identical to b.
    '''
    x = LinalgUtil.solve(a.asarray(), b.asarray())
    return MIArray(x)