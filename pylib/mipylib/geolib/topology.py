# coding=utf-8
#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2014-12-26
# Purpose: MeteoInfoLab topology module
# Note: Jython
#-----------------------------------------------------

from org.meteoinfo.data import ArrayUtil
from org.meteoinfo.shape import Graphic

__all__ = [
    'buffer','contains','convexhull','coveredby','covers','crosses','difference',
    'disjoint','equals','intersection','overlaps','reform','union','symdifference',
    'split','touches','within','asshape'
    ]
            
def asshape(a):
    if isinstance(a, Graphic):
        return a.getShape()
    else:
        return a

def buffer(a, dis):
    ap = asshape(a)
    r = ap.buffer(dis)
    return r
    
def contains(a, b):
    ap = asshape(a)
    bp = asshape(b)
    return ap.contains(bp)
    
def convexhull(*args):
    if len(args) == 1:
        a = args[0]
        ap = asshape(a)
        r = ap.convexHull()
        return r
    else:
        x = args[0]
        y = args[1]
        r = ArrayUtil.convexHull(x.asarray(), y.asarray())
        return r    

def coveredby(a, b):
    ap = asshape(a)
    bp = asshape(b)
    return ap.coveredBy(bp)
    
def covers(a, b):
    ap = asshape(a)
    bp = asshape(b)
    return ap.covers(bp)
    
def crosses(a, b):
    ap = asshape(a)
    bp = asshape(b)
    return ap.crosses(bp)

def difference(a, b):
    ap = asshape(a)
    bp = asshape(b)
    r = ap.difference(bp)
    return r  

def disjoint(a, b):
    ap = asshape(a)
    bp = asshape(b)
    return ap.disjoint(bp)
    
def equals(a, b):
    ap = asshape(a)
    bp = asshape(b)
    return ap.equals(bp)
    
def intersection(a, b):
    ap = asshape(a)
    bp = asshape(b)
    r = ap.intersection(bp)
    return r
    
def intersects(a, b):
    ap = asshape(a)
    bp = asshape(b)
    return ap.intersects(bp)
    
def overlaps(a, b):
    ap = asshape(a)
    bp = asshape(b)
    return ap.overlaps(bp)
    
def reform(a, b):
    ap = asshape(a)
    bp = asshape(b)
    r = ap.reform(bp)
    return r
    
def union(a, b):
    ap = asshape(a)
    bp = asshape(b)
    r = ap.union(bp)
    return r
    
def symdifference(a, b):
    ap = asshape(a)
    bp = asshape(b)
    r = ap.symDifference(bp)
    return r
    
def split(a, b):
    ap = asshape(a)
    bp = asshape(b)
    r = ap.split(bp)
    return r
    
def touches(a, b):
    ap = asshape(a)
    bp = asshape(b)
    return ap.touches(bp)
    
def within(a, b):
    ap = asshape(a)
    bp = asshape(b)
    return ap.within(bp)