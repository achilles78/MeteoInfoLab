#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2014-12-27
# Purpose: MeteoInfo geo module
# Note: Jython
#-----------------------------------------------------

import os

from org.meteoinfo.data.mapdata.geotiff import GeoTiff
from org.meteoinfo.shape import ShapeUtil
from org.meteoinfo.legend import BreakTypes
from org.meteoinfo.geoprocess import GeoComputation
from org.meteoinfo.data import ArrayMath
from org.meteoinfo.data.mapdata import MapDataManage

import milayer
from milayer import MILayer
from mipylib.numeric.miarray import MIArray
from mipylib.numeric.dimarray import DimArray
import mipylib.migl as migl

from java.util import ArrayList

__all__ = [
    'arrayinpolygon','distance','georead','geotiffread','maplayer','inpolygon','maskout',
    'polyarea','polygon','rmaskout','shaperead'
    ]

def shaperead(fn, encoding=None):   
    '''
    Returns a layer readed from a shape file.
    
    :param fn: (*string*) The shape file name (.shp).
    :param encoding: (*string*) Encoding
    
    :returns: (*MILayer*) The created layer.
    '''
    if not fn.endswith('.shp'):
        fn = fn + '.shp'
    if not os.path.exists(fn):
        fn = os.path.join(migl.mapfolder, fn)
        
    if os.path.exists(fn):        
        try:
            if encoding is None:
                layer = MILayer(MapDataManage.readMapFile_ShapeFile(fn))
            else:
                layer = MILayer(MapDataManage.readMapFile_ShapeFile(fn, encoding))
            if not layer.legend() is None:
                lb = layer.legend().getLegendBreaks()[0]
                if lb.getBreakType() == BreakTypes.PolygonBreak:
                    lb.setDrawFill(False)
            return layer
        except:
            raise
    else:
        print 'File not exists: ' + fn
        raise
    
def georead(fn):
    '''
    Returns a layer readed from a supported geo-data file.
    
    :param fn: (*string*) The supported geo-data file name (shape file, wmp, geotiff, image, bil...).
    
    :returns: (*MILayer*) The created layer.
    '''
    if not os.path.exists(fn):
        fn = os.path.join(migl.mapfolder, fn)
        
    if os.path.exists(fn):        
        try:
            layer = MILayer(MapDataManage.loadLayer(fn))
            if not layer.legend() is None:
                lb = layer.legend().getLegendBreaks()[0]
                if lb.getBreakType() == BreakTypes.PolygonBreak:
                    lb.setDrawFill(False)
            return layer
        except:
            raise
    else:
        print 'File not exists: ' + fn
        raise IOError
    
def geotiffread(filename):
    '''
    Return data array from a GeoTiff data file.
    
    :param filename: (*string*) The GeoTiff file name.
    
    :returns: (*MIArray*) Readed data array.
    '''
    geotiff = GeoTiff(filename)
    geotiff.read()
    r = geotiff.readArray()
    return MIArray(r)
    
def maplayer(shapetype='polygon'):
    '''
    Create a new map layer.
    
    :param shapetype: (*string*) Shape type of the layer. ['point' | 'line' | 'polygon'].
    
    :returns: (*MILayer*) MILayer object.
    '''
    return MILayer(shapetype=shapetype)
    
def polygon(x, y = None):
    '''
    Create polygon from coordinate data.
    
    :param x: (*array_like*) X coordinate array. If y is ``None``, x should be 2-D array contains x and y.
    :param y: (*array_like*) Y coordinate array.
    
    :returns: (*PolygonShape*) Created polygon.
    '''
    if y is None:
        polygon = ShapeUtil.createPolygonShape(x)
    else:
        if isinstance(x, MIArray):
            x = x.aslist()
        if isinstance(y, MIArray):
            y = y.aslist()
        polygon = ShapeUtil.createPolygonShape(x, y)
    return polygon    
    
def inpolygon(x, y, polygon):
    '''
    Judge if a point is inside a polygon or not.
    
    :param x: (*float*) X coordinate of the point.
    :param y: (*float*) Y coordinate of the point.
    :param polygon: (*PolygonShape*) The polygon.
    
    :returns: (*boolean*) Inside or not.
    '''
    return GeoComputation.pointInPolygon(polygon, x, y)
    
def arrayinpolygon(a, polygon, x=None, y=None):
    '''
    Set array element value as 1 if inside a polygon or set value as -1.
    
    :param a: (*array_like*) The array.
    :param polygon: (*PolygonShape*) The polygon.
    :param x: (*float*) X coordinate of the point. Default is ``None``, for DimArray
    :param y: (*float*) Y coordinate of the point. Default is ``None``, for DimArray
    
    :returns: (*array_like*) Result array.
    '''
    if isinstance(a, DimArray):
        if x is None or y is None:
            x = self.dimvalue(1)
            y = self.dimvalue(0)
    if not x is None and not y is None:
        if isinstance(polygon, tuple):
            x_p = polygon[0]
            y_p = polygon[1]
            if isinstance(x_p, MIArray):
                x_p = x_p.aslist()
            if isinstance(y_p, MIArray):
                y_p = y_p.aslist()
            return MIArray(ArrayMath.inPolygon(a.asarray(), x.aslist(), y.aslist(), x_p, y_p))
        else:
            if isinstance(polygon, MILayer):
                polygon = polygon.layer
            return MIArray(ArrayMath.inPolygon(a.asarray(), x.aslist(), y.aslist(), polygon))
    else:
        return None
            
def distance(x, y, islonlat=False):
    """
    Get distance of a line.
    
    :param x: (*array_like*) X coordinates.
    :param y: (*array_like*) Y coordinates.
    :param islonlat: (*boolean*) x/y is longitude/latitude or not.
    
    :returns: Distance, meters for lon/lat.
    """
    if isinstance(x, (MIArray, DimArray)):
        x = x.aslist()
    if isinstance(y, (MIArray, DimArray)):
        y = y.aslist()
    r = GeoComputation.getDistance(x, y, islonlat)
    return r
    
def polyarea(*args, **kwargs):
    '''
    Calculate area of polygon.
    
    Parameter is a polygon object or x, y coordinate arrays.
    
    :return: The area of the polygon.
    '''
    islonlat = kwargs.pop('islonlat', False)
    if len(args) == 1:
        if islonlat:
            r = args[0].getSphericalArea()
        else:
            r = args[0].getArea()
    else:
        x = args[0]
        y = args[1]
        if isinstance(x, MIArray):
            x = x.aslist()
        if isinstance(y, MIArray):
            y = y.aslist()
        r = GeoComputation.getArea(x, y, islonlat)
    return r
    
def maskout(data, mask, x=None, y=None):
    """
    Maskout data by polygons - NaN values of elements outside polygons.
    
    :param data: (*array_like*) Array data for maskout.
    :param mask: (*list*) Polygon list as maskout borders.    
    :param x: (*array_like*) X coordinate array.
    :param y: (*array_like*) Y coordinate array.

    :returns: (*array_like*) Maskouted data array.
    """
    if mask is None:
        return data
    elif isinstance(mask, (MIArray, DimArray)):
        r = ArrayMath.maskout(data.asarray(), mask.asarray())
        return MIArray(r)
    if x is None or y is None:
        if isinstance(data, DimArray):
            return data.maskout(mask)
        else:
            return None
    else:
        if not isinstance(mask, (list, ArrayList)):
            mask = [mask]
        r = ArrayMath.maskout(data.asarray(), x.asarray(), y.asarray(), mask)
        return MIArray(r)
        
def rmaskout(data, x, y, mask):
    """
    Maskout data by polygons - the elements outside polygons will be removed
    
    :param data: (*array_like*) Array data for maskout.
    :param x: (*array_like*) X coordinate array.
    :param y: (*array_like*) Y coordinate array.
    :param mask: (*list*) Polygon list as maskout borders.
    
    :returns: (*list*) Maskouted data, x and y array list.
    """
    if not isinstance(mask, (list, ArrayList)):
        mask = [mask]
    r = ArrayMath.maskout_Remove(data.asarray(), x.asarray(), y.asarray(), mask)
    return MIArray(r[0]), MIArray(r[1]), MIArray(r[2])  