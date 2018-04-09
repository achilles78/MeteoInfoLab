# coding=utf-8
#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2018-4-5
# Purpose: MeteoInfoLab mapaxes module
# Note: Jython
#-----------------------------------------------------

import os

from org.meteoinfo.chart.plot import MapPlot
from org.meteoinfo.data import ArrayUtil
from org.meteoinfo.data.meteodata import DrawMeteoData
from org.meteoinfo.map import MapView
from org.meteoinfo.legend import BreakTypes, LegendManage
from org.meteoinfo.shape import Shape, ShapeTypes, Graphic
from org.meteoinfo.projection import ProjectionInfo
from org.meteoinfo.global import Extent
from org.meteoinfo.layer import LayerTypes, WebMapLayer
from org.meteoinfo.data.mapdata.webmap import WebMapProvider

from java.awt import Font

from axes import Axes
from mipylib.numeric.dimarray import DimArray
from mipylib.numeric.miarray import MIArray
from mipylib.geolib.milayer import MILayer
import mipylib.geolib.migeo as migeo
import plotutil
import mipylib.numeric.minum as minum
import mipylib.migl as migl

##############################################        
class MapAxes(Axes):
    '''
    Axes with geological map coordinate.
    '''
    
    def __init__(self, axes=None, figure=None, **kwargs):
        self.figure = figure
        if axes is None:      
            projinfo = kwargs.pop('projinfo', None)
            if projinfo == None:
                proj = kwargs.pop('proj', 'longlat')
                origin = kwargs.pop('origin', (0, 0, 0))    
                lat_0 = origin[0]
                lon_0 = origin[1]
                lat_0 = kwargs.pop('lat_0', lat_0)
                lon_0 = kwargs.pop('lon_0', lon_0)
                lat_ts = kwargs.pop('truescalelat', 0)
                lat_ts = kwargs.pop('lat_ts', lat_ts)
                k = kwargs.pop('scalefactor', 1)
                k = kwargs.pop('k', k)
                paralles = kwargs.pop('paralles', (30, 60))
                lat_1 = paralles[0]
                if len(paralles) == 2:
                    lat_2 = paralles[1]
                else:
                    lat_2 = lat_1
                lat_1 = kwargs.pop('lat_1', lat_1)
                lat_2 = kwargs.pop('lat_2', lat_2)
                x_0 = kwargs.pop('falseeasting', 0)
                y_0 = kwargs.pop('falsenorthing', 0)
                x_0 = kwargs.pop('x_0', x_0)
                y_0 = kwargs.pop('y_0', y_0)
                h = kwargs.pop('h', 0)
                projstr = '+proj=' + proj \
                    + ' +lat_0=' + str(lat_0) \
                    + ' +lon_0=' + str(lon_0) \
                    + ' +lat_1=' + str(lat_1) \
                    + ' +lat_2=' + str(lat_2) \
                    + ' +lat_ts=' + str(lat_ts) \
                    + ' +k=' + str(k) \
                    + ' +x_0=' + str(x_0) \
                    + ' +y_0=' + str(y_0) \
                    + ' +h=' + str(h)
                projinfo = ProjectionInfo(projstr)   
                
            mapview = MapView(projinfo)     
            self.axes = MapPlot(mapview)
        else:
            self.axes = axes
        self.axestype = 'map'
        self.proj = self.axes.getProjInfo()
        
    def islonlat(self):
        '''
        Get if the map axes is lonlat projection or not.
        
        :returns: (*boolean*) Is lonlat projection or not.
        '''
        return self.proj.isLonLat()
            
    def add_layer(self, layer, zorder=None):
        '''
        Add a map layer
        
        :param layer: (*MapLayer*) The map layer.
        :param zorder: (*int*) Layer z order.
        '''
        if isinstance(layer, MILayer):
            layer = layer.layer
        if zorder is None:
            self.axes.addLayer(layer)
        else:
            self.axes.addLayer(zorder, layer)
            
    def set_active_layer(self, layer):
        '''
        Set active layer
        
        :param layer: (*MILayer*) The map layer.
        '''
        self.axes.setSelectedLayer(layer.layer)
        
    def add_circle(self, xy, radius=5, **kwargs):
        '''
        Add a circle patch
        '''
        lbreak, isunique = plotutil.getlegendbreak('polygon', **kwargs)
        circle = self.axes.addCircle(xy[0], xy[1], radius, lbreak)
        return circle
        
    def grid(self, b=None, which='major', axis='both', **kwargs):
        """
        Turn the aexs grids on or off.
        
        :param b: If b is *None* and *len(kwargs)==0* , toggle the grid state. If *kwargs*
            are supplied, it is assumed that you want a grid and *b* is thus set to *True* .
        :param which: *which* can be 'major' (default), 'minor', or 'both' to control
            whether major tick grids, minor tick grids, or both are affected.
        :param axis: *axis* can be 'both' (default), 'x', or 'y' to control which set of
            gridlines are drawn.
        :param kwargs: *kwargs* are used to set the grid line properties.
        """
        if self.islonlat():
            super(MapAxes, self).grid(b, which, axis, **kwargs)
        else:
            mapframe = self.axes.getMapFrame()
            gridline = mapframe.isDrawGridLine()
            if b is None:
                gridline = not gridline
            else:
                gridline = b
            griddx = kwargs.pop('griddx', None)
            griddy = kwargs.pop('griddy', None)            
            if not gridline is None:
                mapframe.setDrawGridLine(gridline)
            if not griddx is None:
                mapframe.setGridXDelt(griddx)
            if not griddy is None:
                mapframe.setGridYDelt(griddy)
            color = kwargs.pop('color', None)
            if not color is None:
                c = plotutil.getcolor(color)
                mapframe.setGridLineColor(c)
            linewidth = kwargs.pop('linewidth', None)
            if not linewidth is None:
                mapframe.setGridLineSize(linewidth)
            linestyle = kwargs.pop('linestyle', None)
            if not linestyle is None:
                linestyle = plotutil.getlinestyle(linestyle)
                mapframe.setGridLineStyle(linestyle)
                
    def xylim(self, limits=None):
        """
        Sets the min and max of the x and y map axes, with ``[xmin, xmax, ymin, ymax]`` .
        
        :param limits: (*list*) Min and max of the x and y map axes.
        """
        if limits is None:
            self.axes.setDrawExtent(self.axes.getMapView().getExtent())
            self.axes.setExtent(self.axes.getDrawExtent().clone())
            return True
        else:
            if len(limits) == 4:
                xmin = limits[0]
                xmax = limits[1]
                ymin = limits[2]
                ymax = limits[3]
                extent = Extent(xmin, xmax, ymin, ymax)
                self.axes.setLonLatExtent(extent)
                self.axes.setExtent(self.axes.getDrawExtent().clone())
                return True
            else:
                print 'The limits parameter must be a list with 4 elements: xmin, xmax, ymin, ymax!'
                return None
        
    def data2pixel(self, x, y, z=None):
        '''
        Transform data coordinate to screen coordinate
        
        :param x: (*float*) X coordinate.
        :param y: (*float*) Y coordinate.
        :param z: (*float*) Z coordinate - only used for 3-D axes.
        '''
        if not self.axes.isLonLatMap():
            x, y = minum.project(x, y, toproj=self.proj)  
            
        rect = self.axes.getPositionArea()
        r = self.axes.projToScreen(x, y, rect)
        sx = r[0] + rect.getX()
        sy = r[1] + rect.getY()
        sy = self.figure.get_size()[1] - sy
        return sx, sy
        
    def loadmip(self, mipfn, mfidx=0):
        '''
        Load one map frame from a MeteoInfo project file.
        
        :param mipfn: (*string*) MeteoInfo project file name.
        :param mfidx: (*int*) Map frame index.
        '''
        self.axes.loadMIProjectFile(mipfn, mfidx)
        
    def geoshow(self, *args, **kwargs):
        '''
        Display map layer or longitude latitude data.
        
        Syntax:
        --------    
            geoshow(shapefilename) - Displays the map data from a shape file.
            geoshow(layer) - Displays the map data from a map layer which may created by ``shaperead`` function.
            geoshow(S) - Displays the vector geographic features stored in S as points, multipoints, lines, or 
              polygons.
            geoshow(lat, lon) - Displays the latitude and longitude vectors.
        '''
        islayer = False
        if isinstance(args[0], basestring):
            fn = args[0]
            if not fn.endswith('.shp'):
                fn = fn + '.shp'
            if not os.path.exists(fn):
                fn = os.path.join(migl.mapfolder, fn)
            if os.path.exists(fn):
                layer = migeo.shaperead(fn)
                islayer = True
            else:
                raise IOError('File not exists: ' + fn)
        elif isinstance(args[0], MILayer):
            layer = args[0]
            islayer = True
        
        if islayer:    
            layer = layer.layer   
            visible = kwargs.pop('visible', True)
            layer.setVisible(visible)
            order = kwargs.pop('order', None)
            if layer.getLayerType() == LayerTypes.ImageLayer:
                if order is None:
                    self.add_layer(layer)
                else:
                    self.add_layer(layer, order)
            else:
                #LegendScheme
                ls = kwargs.pop('symbolspec', None)
                if ls is None:
                    if len(kwargs) > 0 and layer.getLegendScheme().getBreakNum() == 1:
                        lb = layer.getLegendScheme().getLegendBreaks().get(0)
                        btype = lb.getBreakType()
                        geometry = 'point'
                        if btype == BreakTypes.PolylineBreak:
                            geometry = 'line'
                        elif btype == BreakTypes.PolygonBreak:
                            geometry = 'polygon'
                        lb, isunique = plotutil.getlegendbreak(geometry, **kwargs)
                        layer.getLegendScheme().getLegendBreaks().set(0, lb)
                else:
                    layer.setLegendScheme(ls)
                if order is None:
                    self.add_layer(layer)
                else:
                    self.add_layer(layer, order)
                #Labels        
                labelfield = kwargs.pop('labelfield', None)
                if not labelfield is None:
                    labelset = layer.getLabelSet()
                    labelset.setFieldName(labelfield)
                    fontname = kwargs.pop('fontname', 'Arial')
                    fontsize = kwargs.pop('fontsize', 14)
                    bold = kwargs.pop('bold', False)
                    if bold:
                        font = Font(fontname, Font.BOLD, fontsize)
                    else:
                        font = Font(fontname, Font.PLAIN, fontsize)
                    labelset.setLabelFont(font)
                    lcolor = kwargs.pop('labelcolor', None)
                    if not lcolor is None:
                        lcolor = miutil.getcolor(lcolor)
                        labelset.setLabelColor(lcolor)
                    xoffset = kwargs.pop('xoffset', 0)
                    labelset.setXOffset(xoffset)
                    yoffset = kwargs.pop('yoffset', 0)
                    labelset.setYOffset(yoffset)
                    avoidcoll = kwargs.pop('avoidcoll', True)
                    decimals = kwargs.pop('decimals', None)
                    if not decimals is None:
                        labelset.setAutoDecimal(False)
                        labelset.setDecimalDigits(decimals)
                    labelset.setAvoidCollision(avoidcoll)
                    layer.addLabels()  
            self.axes.setDrawExtent(layer.getExtent().clone())
            self.axes.setExtent(layer.getExtent().clone())
            return MILayer(layer)
        else:
            if isinstance(args[0], Graphic):
                graphic = args[0]
                displaytype = 'point'
                stype = graphic.getShape().getShapeType()
                if stype == ShapeTypes.Polyline:
                    displaytype = 'line'
                elif stype == ShapeTypes.Polygon:
                    displaytype = 'polygon'
                lbreak, isunique = plotutil.getlegendbreak(displaytype, **kwargs)
                graphic.setLegend(lbreak)
                self.add_graphic(graphic)            
            elif isinstance(args[0], Shape):
                shape = args[0]
                displaytype = 'point'
                stype = shape.getShapeType()
                if stype == ShapeTypes.Polyline:
                    displaytype = 'line'
                elif stype == ShapeTypes.Polygon:
                    displaytype = 'polygon'
                lbreak, isunique = plotutil.getlegendbreak(displaytype, **kwargs)
                graphic = Graphic(shape, lbreak)
                self.add_graphic(graphic)            
            elif len(args) == 2:
                lat = args[0]
                lon = args[1]
                displaytype = kwargs.pop('displaytype', 'line')
                if isinstance(lat, (int, float)):
                    displaytype = 'point'
                else:
                    if len(lat) == 1:
                        displaytype = 'point'
                    else:
                        if isinstance(lon, (MIArray, DimArray)):
                            lon = lon.aslist()
                        if isinstance(lat, (MIArray, DimArray)):
                            lat = lat.aslist()

                lbreak, isunique = plotutil.getlegendbreak(displaytype, **kwargs)
                iscurve = kwargs.pop('iscurve', False)
                if displaytype == 'point':
                    graphic = self.axes.addPoint(lat, lon, lbreak)
                elif displaytype == 'polyline' or displaytype == 'line':
                    graphic = self.axes.addPolyline(lat, lon, lbreak, iscurve)
                elif displaytype == 'polygon':
                    graphic = self.axes.addPolygon(lat, lon, lbreak)
            return graphic
        
    def pcolor(self, *args, **kwargs):
        """
        Create a pseudocolor plot of a 2-D array in a MapAxes.
        
        :param x: (*array_like*) Optional. X coordinate array.
        :param y: (*array_like*) Optional. Y coordinate array.
        :param z: (*array_like*) 2-D z value array.
        :param levs: (*array_like*) Optional. A list of floating point numbers indicating the level curves 
            to draw, in increasing order.
        :param cmap: (*string*) Color map string.
        :param colors: (*list*) If None (default), the colormap specified by cmap will be used. If a 
            string, like ‘r’ or ‘red’, all levels will be plotted in this color. If a tuple of matplotlib 
            color args (string, float, rgb, etc), different levels will be plotted in different colors in 
            the order specified.
        :param fill_value: (*float*) Fill_value. Default is ``-9999.0``.
        :param proj: (*ProjectionInfo*) Map projection of the data. Default is None.
        :param isplot: (*boolean*) Plot layer or not. Default is ``True``.
        :param order: (*int*) Z-order of created layer for display.
        :param select: (*boolean*) Set the return layer as selected layer or not.
        
        :returns: (*VectoryLayer*) Polygon VectoryLayer created from array data.
        """    
        proj = kwargs.pop('proj', None)    
        order = kwargs.pop('order', None)
        n = len(args) 
        if n <= 2:
            a = args[0]
            y = a.dimvalue(0)
            x = a.dimvalue(1)
            args = args[1:]
        else:
            x = args[0]
            y = args[1]
            a = args[2]
            args = args[3:]
            
        if a.ndim == 2 and x.ndim == 1:            
            x, y = minum.meshgrid(x, y)  
            
        ls = plotutil.getlegendscheme(args, a.min(), a.max(), **kwargs)   
        ls = ls.convertTo(ShapeTypes.Polygon)
        plotutil.setlegendscheme(ls, **kwargs)
            
        if proj is None or proj.isLonLat():
            lonlim = 90
        else:
            lonlim = 0
            x, y = minum.project(x, y, toproj=proj)
        layer = ArrayUtil.meshLayer(x.asarray(), y.asarray(), a.asarray(), ls, lonlim)
        #layer = ArrayUtil.meshLayer(x.asarray(), y.asarray(), a.asarray(), ls)
        if not proj is None:
            layer.setProjInfo(proj)
            
        # Add layer
        visible = kwargs.pop('visible', True)
        if visible:
            shapetype = layer.getShapeType()
            if order is None:
                if shapetype == ShapeTypes.Polygon or shapetype == ShapeTypes.Image:
                    self.add_layer(layer, 0)
                else:
                    self.add_layer(layer)
            else:
                self.add_layer(layer, order)
            self.axes.setDrawExtent(layer.getExtent().clone())
            self.axes.setExtent(layer.getExtent().clone())
            select = kwargs.pop('select', True)
            if select:
                self.axes.setSelectedLayer(layer)

        return MILayer(layer)
        
    def barbs(self, *args, **kwargs):
        """
        Plot a 2-D field of barbs in a map.
        
        :param x: (*array_like*) Optional. X coordinate array.
        :param y: (*array_like*) Optional. Y coordinate array.
        :param u: (*array_like*) U component of the arrow vectors (wind field) or wind direction.
        :param v: (*array_like*) V component of the arrow vectors (wind field) or wind speed.
        :param z: (*array_like*) Optional, 2-D z value array.
        :param levs: (*array_like*) Optional. A list of floating point numbers indicating the level 
            barbs to draw, in increasing order.
        :param cmap: (*string*) Color map string.
        :param fill_value: (*float*) Fill_value. Default is ``-9999.0``.
        :param isuv: (*boolean*) Is U/V or direction/speed data array pairs. Default is True.
        :param size: (*float*) Base size of the arrows.
        :param proj: (*ProjectionInfo*) Map projection of the data. Default is None.
        :param order: (*int*) Z-order of created layer for display.
        :param select: (*boolean*) Set the return layer as selected layer or not.
        
        :returns: (*VectoryLayer*) Created barbs VectoryLayer.
        """
        cmap = plotutil.getcolormap(**kwargs)
        fill_value = kwargs.pop('fill_value', -9999.0)
        proj = kwargs.pop('proj', None)
        order = kwargs.pop('order', None)
        isuv = kwargs.pop('isuv', True)
        n = len(args) 
        iscolor = False
        cdata = None
        onlyuv = True
        if n >= 4 and isinstance(args[3], (DimArray, MIArray)):
            onlyuv = False
        if onlyuv:
            u = minum.asmiarray(args[0])
            v = minum.asmiarray(args[1])
            xx = args[0].dimvalue(1)
            yy = args[0].dimvalue(0)
            x, y = minum.meshgrid(xx, yy)
            args = args[2:]
            if len(args) > 0:
                cdata = minum.asmiarray(args[0])
                iscolor = True
                args = args[1:]
        else:
            x = minum.asmiarray(args[0])
            y = minum.asmiarray(args[1])
            u = minum.asmiarray(args[2])
            v = minum.asmiarray(args[3])
            args = args[4:]
            if len(args) > 0:
                cdata = minum.asmiarray(args[0])
                iscolor = True
                args = args[1:]
        if iscolor:
            if len(args) > 0:
                cn = args[0]
                ls = LegendManage.createLegendScheme(cdata.min(), cdata.max(), cn, cmap)
            else:
                levs = kwargs.pop('levs', None)
                if levs is None:
                    ls = LegendManage.createLegendScheme(cdata.min(), cdata.max(), cmap)
                else:
                    if isinstance(levs, MIArray):
                        levs = levs.tolist()
                    ls = LegendManage.createLegendScheme(cdata.min(), cdata.max(), levs, cmap)
        else:    
            if cmap.getColorCount() == 1:
                c = cmap.getColor(0)
            else:
                c = Color.black
            ls = LegendManage.createSingleSymbolLegendScheme(ShapeTypes.Point, c, 10)
        ls = plotutil.setlegendscheme_point(ls, **kwargs)
        layer = self._plot_uvdata(x, y, u, v, cdata, ls, 'barbs', isuv, proj=proj)
        select = kwargs.pop('select', True)
        if select:
            self.axes.setSelectedLayer(layer)
        udata = None
        vdata = None
        cdata = None
        return MILayer(layer)
        
    def _plot_uvdata(self, x, y, u, v, z, ls, type, isuv, proj=None, density=4):
        if x.ndim == 1 and u.ndim == 2:
            x, y = minum.meshgrid(x, y)
        zv = z
        if not z is None:
            zv = z.array
        if type == 'quiver':
            layer = DrawMeteoData.createVectorLayer(x.array, y.array, u.array, v.array, zv, ls, 'layer', isuv)
        elif type == 'barbs':
            layer = DrawMeteoData.createBarbLayer(x.array, y.array, u.array, v.array, zv, ls, 'layer', isuv)
        
        if (proj != None):
            layer.setProjInfo(proj)
        
        shapetype = layer.getShapeType()
        self.add_layer(layer)
        self.axes.setDrawExtent(layer.getExtent().clone())
        self.axes.setExtent(layer.getExtent().clone())
        return layer
        
    def webmap(self, provider='OpenStreetMap', order=0):
        '''
        Add a new web map layer.
        
        :param provider: (*string*) Web map provider.
        :param order: (*int*) Layer order.
        
        :returns: Web map layer
        '''
        layer = WebMapLayer()
        provider = WebMapProvider.valueOf(provider)
        layer.setWebMapProvider(provider)
        self.add_layer(layer, order)
        return MILayer(layer)

########################################################3
class Test():
    def test():
        print 'Test...'        