# coding=utf-8
#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2017-3-25
# Purpose: MeteoInfoLab axes module
# Note: Jython
#-----------------------------------------------------

from org.meteoinfo.chart import ChartText3D
from org.meteoinfo.chart.plot import Plot2D, MapPlot, PolarPlot, PiePlot, Plot3D, GraphicFactory
from org.meteoinfo.map import MapView
from org.meteoinfo.legend import LegendManage, BreakTypes
from org.meteoinfo.shape import ShapeTypes, Graphic
from org.meteoinfo.projection import ProjectionInfo
from org.meteoinfo.global import MIMath

from java.awt import Font

from mipylib.numeric.dimarray import DimArray
from mipylib.numeric.miarray import MIArray
from mipylib.geolib.milayer import MILayer
import plotutil
import miplot
import mipylib.numeric.minum as minum

class Axes(object):
    '''
    Axes with Cartesian coordinate.
    '''

    def __init__(self, axes=None):
        if axes is None:
            self.axes = Plot2D()
        else:
            self.axes = axes
        self.axestype = 'cartesian'
            
    def get_type(self):
        '''
        Get axes type
        
        :returns: Axes type
        '''
        return self.axes.getPlotType()
            
    def get_position(self):
        '''
        Get axes position             

        :returns: Axes position [left, bottom, width, height] in normalized (0, 1) units
        '''
        pos = self.axes.getPosition()
        return [pos.x, pos.y, pos.width, pos.height]
        
    def set_position(self, pos):
        '''
        Set axes position
        
        :param pos: (*list*) Axes position specified by *position=* [left, bottom, width,
            height] in normalized (0, 1) units
        '''
        self.axes.setPosition(pos)
        
    def get_outerposition(self):
        '''
        Get axes outer position
        
        :returns: Axes outer position [left, bottom, width, height] in normalized (0, 1) units
        '''
        pos = self.axes.getPosition()
        return [pos.x, pos.y, pos.width, pos.height]
        
    def set_outerposition(self, pos):
        '''
        Set axes outer position
        
        :param pos: (*list*) Axes outer position specified by *position=* [left, bottom, width,
            height] in normalized (0, 1) units
        '''
        self.axes.setPosition(pos)
        
    def active_outerposition(self, active):
        '''
        Set axes outer position active or not.
        
        :param active: (*boolean*) Active or not
        '''
        self.axes.setOuterPosActive(active)     
    
    def get_axis(self, loc):
        '''
        Get axis by location.
        
        :param loc: (*Location*) Location enum.
        
        :returns: Axis
        '''
        return self.axes.getAxis(loc)
        
    def get_title(self):
        '''
        Get title               
        '''
        return self.axes.getTitle()
        
    def set_title(self, title):
        '''
        Set title
        
        :param title: (*string*) Title
        '''
        self.axes.setTitle(title)
        
    def get_xticks(self):
        '''
        Get x axis tick locations.
        '''
        axis = self.axes.getXAxis()
        axis.updateTickLabels()
        return axis.getTickLocations()
        
    def set_xticks(self, locs):
        '''
        Set x axis tick locations.
        '''
        axis = self.axes.getXAxis()
        if isinstance(locs, (MIArray, DimArray)):
            locs = labels.aslist()
        axis.setTickLocations(locs)
        
    def get_yticks(self):
        '''
        Get y axis tick locations.
        '''
        axis = self.axes.getYAxis()
        axis.updateTickLabels()
        return axis.getTickLocations()
        
    def set_yticks(self, locs):
        '''
        Set y axis tick locations.
        '''
        axis = self.axes.getYAxis()
        if isinstance(locs, (MIArray, DimArray)):
            locs = labels.aslist()
        axis.setTickLocations(locs)
        
    def get_xticklabels(self):
        '''
        Get x axis tick labels.
        '''
        axis = self.axes.getXAxis()
        axis.updateTickLabels()
        return axis.getTickLabelText()
        
    def set_xticklabels(self, labels):
        '''
        Set x axis tick labels.
        '''
        axis = self.axes.getXAxis()
        if isinstance(labels, (MIArray, DimArray)):
            labels = labels.aslist()
        if isinstance(labels[0], (int, long, float)):
            axis.setTickLabels_Number(labels)
        else:
            axis.setTickLabelText(labels)
            
    def get_yticklabels(self):
        '''
        Get y axis tick labels.
        '''
        axis = self.axes.getYAxis()
        axis.updateTickLabels()
        return axis.getTickLabelText()
        
    def set_yticklabels(self, labels):
        '''
        Set y axis tick labels.
        '''
        axis = self.axes.getYAxis()
        if isinstance(labels, (MIArray, DimArray)):
            labels = labels.aslist()
        if isinstance(labels[0], (int, long, float)):
            axis.setTickLabels_Number(labels)
        else:
            axis.setTickLabelText(labels)
    
    def add_graphic(self, graphic):
        '''
        Add a graphic
        
        :param graphic: (*Graphic*) The graphic to be added.
        '''
        self.axes.addGraphic(graphic)
        
    def data2pixel(self, x, y, z=None):
        '''
        Transform data coordinate to screen coordinate
        
        :param x: (*float*) X coordinate.
        :param y: (*float*) Y coordinate.
        :param z: (*float*) Z coordinate - only used for 3-D axes.
        '''
        rect = self.axes.getPositionArea()
        r = self.axes.projToScreen(x, y, rect)
        sx = r[0] + rect.getX()
        sy = r[1] + rect.getY()
        sy = miplot.figsize()[1] - sy
        return sx, sy
        
    def get_xlim(self):
        '''
        Get x axis limits
        
        :returns: X axis limits
        '''
        extent = self.axes.getDrawExtent()
        return extent.minX, extent.maxX
        
    def get_ylim(self):
        '''
        Get y axis limits
        
        :returns: Y axis limits
        '''
        extent = self.axes.getDrawExtent()
        return extent.minY, extent.maxY
        

##############################################        
class MapAxes(Axes):
    '''
    Axes with geological map coordinate.
    '''
    
    def __init__(self, axes=None, **kwargs):
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
        sy = miplot.figsize()[1] - sy
        return sx, sy
            
###############################################
class PolarAxes(Axes):
    '''
    Axes with polar coordinate.
    '''
    
    def __init__(self, axes=None):
        if axes is None:
            self.axes = PolarPlot()
        else:
            self.axes = axes
        self.axestype = 'polar'
    
    def set_rmax(self, rmax):
        '''
        Set radial max circle.
        
        :param rmax: (*float*) Radial max value.
        '''
        self.axes.setRadius(rmax)
        
    def set_rlabel_position(self, pos):
        '''
        Updates the theta position of the radial labels.
        
        :param pos: (*float*) The angular position of the radial labels in degrees.
        '''
        if isinstance(pos, (DimArray, MIArray)):
            pos = pos.tolist()
        self.axes.setYTickLabelPos(pos)
        
    def set_rticks(self, ticks):
        '''
        Set radial ticks.
        
        :param ticks: (*string list*) Tick labels.
        '''
        self.axes.setYTickLabels(ticks)
        
    def set_rtick_format(self, fmt=''):
        '''
        Set radial tick format.
        
        :param ftm: (*string*) Tick format ['' | '%'].
        '''
        self.axes.setYTickFormat(fmt)
        
    def set_rtick_locations(self, loc):
        '''
        Set radial tick locations.
        
        :param loc: (*float list*) Tick locations.
        '''
        if isinstance(loc, (DimArray, MIArray)):
            loc = loc.tolist()
        self.axes.setYTickLocations(loc)
        
    def set_xtick_locations(self, loc):
        '''
        Set angular tick locations.
        
        :param loc: (*float list*) Tick locations.
        '''
        if isinstance(loc, (DimArray, MIArray)):
            loc = loc.tolist()
        self.axes.setXTickLocations(loc)
        
    def set_xticks(self, ticks):
        '''
        Set angular ticks.
        
        :param ticks: (*string list*) Tick labels.
        '''
        self.axes.setXTickLabels(ticks)
        
    def set_rtick_font(self, name=None, size=None, style=None):
        '''
        Set radial tick font.
        
        :param name: (*string*) Font name.
        :param size: (*int*) Font size.
        :param style: (*string*) Font style.
        '''
        font = self.axes.getYTickFont()
        if name is None:
            name = font.getName()
        if size is None:
            size = font.getSize()
        if style is None:
            style = font.getStyle()
        else:
            if style.lower() == 'bold':
                style = Font.BOLD
            elif style.lower() == 'italic':
                style = Font.ITALIC
            else:
                style = Font.PLAIN
        font = Font(name, style, size)
        self.axes.setYTickFont(font)
        
    def set_xtick_font(self, name=None, size=None, style=None):
        '''
        Set angular tick font.
        
        :param name: (*string*) Font name.
        :param size: (*int*) Font size.
        :param style: (*string*) Font style.
        '''
        font = self.axes.getXTickFont()
        if name is None:
            name = font.getName()
        if size is None:
            size = font.getSize()
        if style is None:
            style = font.getStyle()
        else:
            if style.lower() == 'bold':
                style = Font.BOLD
            elif style.lower() == 'italic':
                style = Font.ITALIC
            else:
                style = Font.PLAIN
        font = Font(name, style, size)
        self.axes.setXTickFont(font)
        
    def data2pixel(self, x, y, z=None):
        '''
        Transform data coordinate to screen coordinate
        
        :param x: (*float*) X coordinate.
        :param y: (*float*) Y coordinate.
        :param z: (*float*) Z coordinate - only used for 3-D axes.
        '''
        r = MIMath.polarToCartesian(x, y) 
        x = r[0]
        y = r[1]
        rect = self.axes.getPositionArea()
        r = self.axes.projToScreen(x, y, rect)
        sx = r[0] + rect.getX()
        sy = r[1] + rect.getY()
        sy = miplot.figsize()[1] - sy
        return sx, sy
        
#########################################################
class Axes3D(Axes):
    '''
    Axes with 3 dimensional.
    '''
    
    def __init__(self, axes=None, **kwargs):
        if axes is None:        
            self.axes = Plot3D()
        else:
            self.axes = axes
        self.axestype = '3d'
        self.projector = self.axes.getProjector()
        #distance = kwargs.pop('distance', 10000)
        #self.projector.setDistance(distance)
        rotation_angle = kwargs.pop('rotation', 225)
        self.projector.setRotationAngle(rotation_angle)
        elevation_angle = kwargs.pop('elevation', 30)
        self.projector.setElevationAngle(elevation_angle)
        xyaxis = kwargs.pop('xyaxis', True)
        self.axes.setDisplayXY(xyaxis)
        zaxis = kwargs.pop('zaxis', True)
        self.axes.setDisplayZ(zaxis)
        grid = kwargs.pop('grid', True)
        self.axes.setDisplayGrids(grid)
        boxed = kwargs.pop('boxed', True)
        self.axes.setBoxed(boxed)
        bbox = kwargs.pop('bbox', False)
        self.axes.setDrawBoundingBox(bbox)
        
    def get_distance(self):
        '''
        Get distance to object.
        
        :returns: Distance to object.
        '''
        return self.projector.getDistance()
        
    def set_distance(self, dis):
        '''
        Set distance to object.
        
        :param dis: (*float*) Distance to object.
        '''
        self.projector.setDistance(dis)
        miplot.draw_if_interactive()
        
    def get_rotation(self):
        '''
        Get rotation angle.
        
        :returns: Rotation angle.
        '''
        return self.projector.getRotationAngle()
        
    def set_rotation(self, rotation):
        '''
        Set rotation angle.
        
        :param rotation: (*float*) Rotation angle.
        '''
        self.projector.setRotationAngle(rotation)
        miplot.draw_if_interactive()
        
    def get_elevation(self):
        '''
        Get elevation angle.
        
        :returns: Elevation angle.
        '''
        return self.projector.getElevationAngle()
        
    def set_elevation(self, elevation):
        '''
        Set elevation angle.
        
        :param elevation: (*float*) Elevation angle.
        '''
        self.projector.setElevationAngle(elevation)
        miplot.draw_if_interactive()
        
    def set_draw_xy(self, dxy):
        '''
        Set draw xy axis or not.
        
        :param dxy: (*boolean*) Draw xy axis or not.
        '''
        self.axes.setDisplayXY(dxy)
        miplot.draw_if_interactive()
        
    def set_draw_z(self, dz):
        '''
        Set draw z axis or not.
        
        :param dz: (*boolean*) Draw z axis or not.
        '''
        self.axes.setDisplayZ(dz)
        miplot.draw_if_interactive()
        
    def set_draw_box(self, db):
        '''
        Set draw 3D box or not.
        
        :param db: (*boolean*) Draw 3D box or not.
        '''
        self.axes.setBoxed(db)
        miplot.draw_if_interactive()
        
    def set_draw_bbox(self, bbox):
        '''
        Set draw bounding box or not.
        
        :param db: (*boolean*) Draw bounding box or not.
        '''
        self.axes.setDrawBoundingBox(bbox)
        miplot.draw_if_interactive()
        
    def plot(self, x, y, z, *args, **kwargs):
        """
        Plot 3D lines and/or markers to the axes. *args* is a variable length argument, allowing
        for multiple *x, y* pairs with an optional format string.
        
        :param x: (*array_like*) Input x data.
        :param y: (*array_like*) Input y data.
        :param z: (*array_like*) Input z data.
        :param style: (*string*) Line style for plot.
        
        :returns: Legend breaks of the lines.
        
        The following format string characters are accepted to control the line style or marker:
        
          =========  ===========
          Character  Description
          =========  ===========
          '-'         solid line style
          '--'        dashed line style
          '-.'        dash-dot line style
          ':'         dotted line style
          '.'         point marker
          ','         pixel marker
          'o'         circle marker
          'v'         triangle_down marker
          '^'         triangle_up marker
          '<'         triangle_left marker
          '>'         triangle_right marker
          's'         square marker
          'p'         pentagon marker
          '*'         star marker
          'x'         x marker
          'D'         diamond marker
          =========  ===========
          
        The following color abbreviations are supported:
          
          =========  =====
          Character  Color  
          =========  =====
          'b'        blue
          'g'        green
          'r'        red
          'c'        cyan
          'm'        magenta
          'y'        yellow
          'k'        black
          =========  =====
        """      
        xdata = plotutil.getplotdata(x)
        ydata = plotutil.getplotdata(y)
        zdata = plotutil.getplotdata(z)  
        style = None
        if len(args) > 0:
            style = args[0]
        
        #Set plot data styles
        label = kwargs.pop('label', 'S_1')
        if style is None:
            line = plotutil.getlegendbreak('line', **kwargs)[0]
            line.setCaption(label)
        else:
            line = plotutil.getplotstyle(style, label, **kwargs)   

        #Add graphics
        graphics = GraphicFactory.createLineString(xdata, ydata, zdata, line)
        visible = kwargs.pop('visible', True)
        if visible:
            self.add_graphic(graphics)
            miplot.draw_if_interactive()
        return graphics
        
    def scatter(self, x, y, z, s=8, c='b', marker='o', alpha=None, linewidth=None, 
                verts=None, **kwargs):
        """
        Make a 3D scatter plot of x, y and z, where x, y and z are sequence like objects of the same lengths.
        
        :param x: (*array_like*) Input x data.
        :param y: (*array_like*) Input y data.
        :param z: (*array_like*) Input z data.
        :param s: (*int*) Size of points.
        :param c: (*Color*) Color of the points. Or z vlaues.
        :param alpha: (*int*) The alpha blending value, between 0 (transparent) and 1 (opaque).
        :param marker: (*string*) Marker of the points.
        :param label: (*string*) Label of the points series.
        :param levs: (*array_like*) Optional. A list of floating point numbers indicating the level 
            points to draw, in increasing order.
        
        :returns: Points legend break.
        """        
        #Add data series
        label = kwargs.pop('label', 'S_0')
        xdata = plotutil.getplotdata(x)
        ydata = plotutil.getplotdata(y)
        zdata = plotutil.getplotdata(z)
        
        #Set plot data styles
        pb, isunique = plotutil.getlegendbreak('point', **kwargs)
        pb.setCaption(label)
        pstyle = plotutil.getpointstyle(marker)    
        pb.setStyle(pstyle)
        isvalue = False
        if len(c) > 1:
            if isinstance(c, (MIArray, DimArray)):
                isvalue = True
            elif isinstance(c[0], (int, long, float)):
                isvalue = True            
        if isvalue:
            ls = kwargs.pop('symbolspec', None)
            if ls is None:        
                if isinstance(c, (list, tuple)):
                    c = minum.array(c)
                levels = kwargs.pop('levs', None)
                if levels is None:
                    levels = kwargs.pop('levels', None)
                if levels is None:
                    cnum = kwargs.pop('cnum', None)
                    if cnum is None:
                        ls = plotutil.getlegendscheme([], c.min(), c.max(), **kwargs)
                    else:
                        ls = plotutil.getlegendscheme([cnum], c.min(), c.max(), **kwargs)
                else:
                    ls = plotutil.getlegendscheme([levels], c.min(), c.max(), **kwargs)
                ls = plotutil.setlegendscheme_point(ls, **kwargs)
                if isinstance(s, int):
                    for lb in ls.getLegendBreaks():
                        lb.setSize(s)
                else:
                    n = len(s)
                    for i in range(0, n):
                        ls.getLegendBreaks()[i].setSize(s[i])
            #Create graphics
            graphics = GraphicFactory.createPoints3D(xdata, ydata, zdata, c.asarray(), ls)
        else:
            colors = plotutil.getcolors(c, alpha)   
            pbs = []
            if isinstance(s, int):   
                pb.setSize(s)
                if len(colors) == 1:
                    pb.setColor(colors[0])
                    pbs.append(pb)
                else:
                    n = len(colors)
                    for i in range(0, n):
                        npb = pb.clone()
                        npb.setColor(colors[i])
                        pbs.append(npb)
            else:
                n = len(s)
                if len(colors) == 1:
                    pb.setColor(colors[0])
                    for i in range(0, n):
                        npb = pb.clone()
                        npb.setSize(s[i])
                        pbs.append(npb)
                else:
                    for i in range(0, n):
                        npb = pb.clone()
                        npb.setSize(s[i])
                        npb.setColor(colors[i])
                        pbs.append(npb)
            #Create graphics
            graphics = GraphicFactory.createPoints3D(xdata, ydata, zdata, pbs)
        
        visible = kwargs.pop('visible', True)
        if visible:
            self.add_graphic(graphics)
            miplot.draw_if_interactive()
        return graphics
        
    def plot_wireframe(self, *args, **kwargs):
        '''
        creates a three-dimensional wireframe plot
        
        :param x: (*array_like*) Optional. X coordinate array.
        :param y: (*array_like*) Optional. Y coordinate array.
        :param z: (*array_like*) 2-D z value array.
        :param cmap: (*string*) Color map string.
        :param xyaxis: (*boolean*) Draw x and y axis or not.
        :param zaxis: (*boolean*) Draw z axis or not.
        :param grid: (*boolean*) Draw grid or not.
        :param boxed: (*boolean*) Draw boxed or not.
        :param mesh: (*boolean*) Draw mesh line or not.
        
        :returns: Legend
        '''        
        if len(args) == 1:
            x = args[0].dimvalue(1)
            y = args[0].dimvalue(0)
            x, y = minum.meshgrid(x, y)
            z = args[0]    
            args = args[1:]
        else:
            x = args[0]
            y = args[1]
            z = args[2]
            args = args[3:]
 
        line = plotutil.getlegendbreak('line', **kwargs)[0]
        graphics = GraphicFactory.createWireframe(x.asarray(), y.asarray(), z.asarray(), line)
        visible = kwargs.pop('visible', True)
        if visible:
            self.add_graphic(graphics)
            miplot.draw_if_interactive()
        return graphics
        
    def plot_surface(self, *args, **kwargs):
        '''
        creates a three-dimensional surface plot
        
        :param x: (*array_like*) Optional. X coordinate array.
        :param y: (*array_like*) Optional. Y coordinate array.
        :param z: (*array_like*) 2-D z value array.
        :param cmap: (*string*) Color map string.
        :param xyaxis: (*boolean*) Draw x and y axis or not.
        :param zaxis: (*boolean*) Draw z axis or not.
        :param grid: (*boolean*) Draw grid or not.
        :param boxed: (*boolean*) Draw boxed or not.
        :param mesh: (*boolean*) Draw mesh line or not.
        
        :returns: Legend
        '''        
        if len(args) <= 2:
            x = args[0].dimvalue(1)
            y = args[0].dimvalue(0)
            x, y = minum.meshgrid(x, y)
            z = args[0]    
            args = args[1:]
        else:
            x = args[0]
            y = args[1]
            z = args[2]
            args = args[3:]
        cmap = plotutil.getcolormap(**kwargs)
        if len(args) > 0:
            level_arg = args[0]
            if isinstance(level_arg, int):
                cn = level_arg
                ls = LegendManage.createLegendScheme(z.min(), z.max(), cn, cmap)
            else:
                if isinstance(level_arg, MIArray):
                    level_arg = level_arg.aslist()
                ls = LegendManage.createLegendScheme(z.min(), z.max(), level_arg, cmap)
        else:    
            ls = LegendManage.createLegendScheme(z.min(), z.max(), cmap)
        ls = ls.convertTo(ShapeTypes.Polygon)
        edge = kwargs.pop('edge', True)
        kwargs['edge'] = edge
        plotutil.setlegendscheme(ls, **kwargs)
        graphics = GraphicFactory.createMeshPolygons(x.asarray(), y.asarray(), z.asarray(), ls)
        visible = kwargs.pop('visible', True)
        if visible:
            self.add_graphic(graphics)
            miplot.draw_if_interactive()
        return graphics
        
    def contour(self, *args, **kwargs):
        """
        Plot contours.
        
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
        :param smooth: (*boolean*) Smooth countour lines or not.
        
        :returns: (*VectoryLayer*) Contour VectoryLayer created from array data.
        """
        n = len(args)
        cmap = plotutil.getcolormap(**kwargs)
        fill_value = kwargs.pop('fill_value', -9999.0)
        offset = kwargs.pop('offset', 0)
        xaxistype = None
        if n <= 2:
            gdata = minum.asgriddata(args[0])
            if isinstance(args[0], DimArray):
                if args[0].islondim(1):
                    xaxistype = 'lon'
                elif args[0].islatdim(1):
                    xaxistype = 'lat'
                elif args[0].istimedim(1):
                    xaxistype = 'time'
            args = args[1:]
        elif n <=4:
            x = args[0]
            y = args[1]
            a = args[2]
            gdata = minum.asgriddata(a, x, y, fill_value)
            args = args[3:]
        if len(args) > 0:
            level_arg = args[0]
            if isinstance(level_arg, int):
                cn = level_arg
                ls = LegendManage.createLegendScheme(gdata.min(), gdata.max(), cn, cmap)
            else:
                if isinstance(level_arg, MIArray):
                    level_arg = level_arg.aslist()
                ls = LegendManage.createLegendScheme(gdata.min(), gdata.max(), level_arg, cmap)
        else:    
            ls = LegendManage.createLegendScheme(gdata.min(), gdata.max(), cmap)
        ls = ls.convertTo(ShapeTypes.Polyline)
        plotutil.setlegendscheme(ls, **kwargs)
        
        smooth = kwargs.pop('smooth', True)
        zdir = kwargs.pop('zdir', 'z')
        if zdir == 'xy':
            sepoint = kwargs.pop('sepoint', [0,0,1,1])
            igraphic = GraphicFactory.createContourLines(gdata.data, offset, zdir, ls, smooth, \
                sepoint)
        else:
            igraphic = GraphicFactory.createContourLines(gdata.data, offset, zdir, ls, smooth)
        visible = kwargs.pop('visible', True)
        if visible:
            self.add_graphic(igraphic)
            miplot.draw_if_interactive()
        return igraphic
        
    def contourf(self, *args, **kwargs):
        """
        Plot filled contours.
        
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
        :param smooth: (*boolean*) Smooth countour lines or not.
        
        :returns: (*VectoryLayer*) Contour VectoryLayer created from array data.
        """
        n = len(args)
        cmap = plotutil.getcolormap(**kwargs)
        fill_value = kwargs.pop('fill_value', -9999.0)
        offset = kwargs.pop('offset', 0)
        xaxistype = None
        if n <= 2:
            gdata = minum.asgriddata(args[0])
            if isinstance(args[0], DimArray):
                if args[0].islondim(1):
                    xaxistype = 'lon'
                elif args[0].islatdim(1):
                    xaxistype = 'lat'
                elif args[0].istimedim(1):
                    xaxistype = 'time'
            args = args[1:]
        elif n <=4:
            x = args[0]
            y = args[1]
            a = args[2]
            gdata = minum.asgriddata(a, x, y, fill_value)
            args = args[3:]
        if len(args) > 0:
            level_arg = args[0]
            if isinstance(level_arg, int):
                cn = level_arg
                ls = LegendManage.createLegendScheme(gdata.min(), gdata.max(), cn, cmap)
            else:
                if isinstance(level_arg, MIArray):
                    level_arg = level_arg.aslist()
                ls = LegendManage.createLegendScheme(gdata.min(), gdata.max(), level_arg, cmap)
        else:    
            ls = LegendManage.createLegendScheme(gdata.min(), gdata.max(), cmap)
        ls = ls.convertTo(ShapeTypes.Polygon)
        edge = kwargs.pop('edge', None)
        if edge is None:
            kwargs['edge'] = False
        else:
            kwargs['edge'] = edge
        plotutil.setlegendscheme(ls, **kwargs)
        
        smooth = kwargs.pop('smooth', True)
        zdir = kwargs.pop('zdir', 'z')
        if zdir == 'xy':
            sepoint = kwargs.pop('sepoint', [0,0,1,1])
            igraphic = GraphicFactory.createContourPolygons(gdata.data, offset, zdir, ls, smooth, \
                sepoint)
        else:
            igraphic = GraphicFactory.createContourPolygons(gdata.data, offset, zdir, ls, smooth)
        visible = kwargs.pop('visible', True)
        if visible:
            self.add_graphic(igraphic)
            miplot.draw_if_interactive()
        return igraphic
        
    def imshow(self, *args, **kwargs):
        """
        Display an image on the 3D axes.
        
        :param x: (*array_like*) Optional. X coordinate array.
        :param y: (*array_like*) Optional. Y coordinate array.
        :param z: (*array_like*) 2-D or 3-D (RGB) z value array.
        :param levs: (*array_like*) Optional. A list of floating point numbers indicating the level curves 
            to draw, in increasing order.
        :param cmap: (*string*) Color map string.
        :param colors: (*list*) If None (default), the colormap specified by cmap will be used. If a 
            string, like ‘r’ or ‘red’, all levels will be plotted in this color. If a tuple of matplotlib 
            color args (string, float, rgb, etc), different levels will be plotted in different colors in 
            the order specified.
        
        :returns: (*RasterLayer*) RasterLayer created from array data.
        """
        n = len(args)
        cmap = plotutil.getcolormap(**kwargs)
        fill_value = kwargs.pop('fill_value', -9999.0)
        xaxistype = None
        isrgb = False
        if n <= 2:
            if isinstance(args[0], (list, tuple)):
                isrgb = True
                rgbdata = args[0]
                if isinstance(rgbdata[0], MIArray):
                    x = minum.arange(0, rgbdata[0].shape[1])
                    y = minum.arange(0, rgbdata[0].shape[0])
                else:
                    x = rgbdata[0].dimvalue(1)
                    y = rgbdata[0].dimvalue(0)
            elif args[0].ndim > 2:
                isrgb = True
                rgbdata = args[0]
                if isinstance(rgbdata, MIArray):
                    x = minum.arange(0, rgbdata.shape[1])
                    y = minum.arange(0, rgbdata.shape[0])
                else:
                    x = rgbdata.dimvalue(1)
                    y = rgbdata.dimvalue(0)
            else:
                gdata = minum.asgridarray(args[0])
                if isinstance(args[0], DimArray):
                    if args[0].islondim(1):
                        xaxistype = 'lon'
                    elif args[0].islatdim(1):
                        xaxistype = 'lat'
                    elif args[0].istimedim(1):
                        xaxistype = 'time'
                args = args[1:]
        elif n <=4:
            x = args[0]
            y = args[1]
            a = args[2]
            if isinstance(a, (list, tuple)):
                isrgb = True
                rgbdata = a
            elif a.ndim > 2:
                isrgb = True
                rgbdata = a
            else:
                gdata = minum.asgridarray(a, x, y, fill_value)
                args = args[3:]   
        
        offset = kwargs.pop('offset', 0)
        zdir = kwargs.pop('zdir', 'z')
        if isrgb:
            if isinstance(rgbdata, (list, tuple)):
                rgbd = []
                for d in rgbdata:
                    rgbd.append(d.asarray())
                rgbdata = rgbd
            else:
                rgbdata = rgbdata.asarray()
            x = plotutil.getplotdata(x)
            y = plotutil.getplotdata(y)
            graphics = GraphicFactory.createImage(x, y, rgbdata, offset, zdir)
            ls = None
        else:
            if len(args) > 0:
                level_arg = args[0]
                if isinstance(level_arg, int):
                    cn = level_arg
                    ls = LegendManage.createImageLegend(gdata, cn, cmap)
                else:
                    if isinstance(level_arg, MIArray):
                        level_arg = level_arg.aslist()
                    ls = LegendManage.createImageLegend(gdata, level_arg, cmap)
            else:
                ls = plotutil.getlegendscheme(args, gdata.min(), gdata.max(), **kwargs)
            ls = ls.convertTo(ShapeTypes.Image)
            plotutil.setlegendscheme(ls, **kwargs)
            if zdir == 'xy':
                sepoint = kwargs.pop('sepoint', [0,0,1,1])
            else:
                sepoint = None
            graphics = GraphicFactory.createImage(gdata, ls, offset, zdir, sepoint)
                
        visible = kwargs.pop('visible', True)
        if visible:
            self.add_graphic(graphics)
            miplot.draw_if_interactive()
        return graphics
        
    def plot_layer(self, layer, **kwargs):
        '''
        Plot a layer in 3D axes.
        
        :param layer: (*MILayer*) The layer to be plotted.
        
        :returns: Graphics.
        '''
        ls = kwargs.pop('symbolspec', None)
        layer = layer.layer
        if ls is None:
            ls = layer.getLegendScheme()
            if len(kwargs) > 0 and layer.getLegendScheme().getBreakNum() == 1:
                lb = layer.getLegendScheme().getLegendBreaks().get(0)
                btype = lb.getBreakType()
                geometry = 'point'
                if btype == BreakTypes.PolylineBreak:
                    geometry = 'line'
                elif btype == BreakTypes.PolygonBreak:
                    geometry = 'polygon'
                lb, isunique = plotutil.getlegendbreak(geometry, **kwargs)
                ls.getLegendBreaks().set(0, lb)

        plotutil.setlegendscheme(ls, **kwargs)
        layer.setLegendScheme(ls)
            
        offset = kwargs.pop('offset', 0)
        xshift = kwargs.pop('xshift', 0)
        graphics = GraphicFactory.createGraphicsFromLayer(layer, offset, xshift)
        
        visible = kwargs.pop('visible', True)
        if visible:
            self.add_graphic(graphics)
            miplot.draw_if_interactive()
        return graphics
        
    def fill_between(self, x, y1, y2=0, where=None, **kwargs):
        """
        Make filled polygons between two curves (y1 and y2) where ``where==True``.
        
        :param x: (*array_like*) An N-length array of the x data.
        :param y1: (*array_like*) An N-length array (or scalar) of the y data.
        :param y2: (*array_like*) An N-length array (or scalar) of the y data.
        :param where: (*array_like*) If None, default to fill between everywhere. If not None, it is an 
            N-length boolean array and the fill will only happen over the regions where ``where==True``.
        """
        #Get dataset
        global gca   
        
        #Add data series
        label = kwargs.pop('label', 'S_0')
        dn = len(x)
        xdata = plotutil.getplotdata(x)
        if isinstance(y1, (int, long, float)):
            yy = []
            for i in range(dn):
                yy.append(y1)
            y1 = minum.array(yy).array
        else:
            y1 = plotutil.getplotdata(y1)
        if isinstance(y2, (int, long, float)):
            yy = []
            for i in range(dn):
                yy.append(y2)
            y2 = minum.array(yy).array
        else:
            y2 = plotutil.getplotdata(y2)
        if not where is None:
            if isinstance(where, (tuple, list)):
                where = minum.array(where)
            where = where.asarray()
        
        #Set plot data styles
        if not 'fill' in kwargs:
            kwargs['fill'] = True
        if not 'edge' in kwargs:
            kwargs['edge'] = False
        pb, isunique = plotutil.getlegendbreak('polygon', **kwargs)
        pb.setCaption(label)
        
        #Create graphics
        offset = kwargs.pop('offset', 0)
        zdir = kwargs.pop('zdir', 'z')
        if zdir == 'xy':
            y = kwargs.pop('y', x)
            ydata = plotutil.getplotdata(y)
            graphics = GraphicFactory.createFillBetweenPolygons(xdata, ydata, y1, y2, where, pb, \
                offset, zdir) 
        else:
            graphics = GraphicFactory.createFillBetweenPolygons(xdata, y1, y2, where, pb, \
                offset, zdir) 
            
        visible = kwargs.pop('visible', True)
        if visible:
            self.add_graphic(graphics)
            miplot.draw_if_interactive()
        return graphics
        
    def text(self, x, y, z, s, zdir=None, **kwargs):
        '''
        Add text to the plot. kwargs will be passed on to text, except for the zdir 
        keyword, which sets the direction to be used as the z direction.
        
        :param x: (*float*) X coordinate.
        :param y: (*float*) Y coordinate.
        :param z: (*float*) Z coordinate.
        :param s: (*string*) Text string.
        :param zdir: Z direction.
        '''
        fontname = kwargs.pop('fontname', 'Arial')
        fontsize = kwargs.pop('fontsize', 14)
        bold = kwargs.pop('bold', False)
        color = kwargs.pop('color', 'black')
        if bold:
            font = Font(fontname, Font.BOLD, fontsize)
        else:
            font = Font(fontname, Font.PLAIN, fontsize)
        c = plotutil.getcolor(color)
        text = ChartText3D()
        text.setText(s)
        text.setFont(font)
        text.setColor(c)
        text.setPoint(x, y, z)
        ha = kwargs.pop('horizontalalignment', None)
        if ha is None:
            ha = kwargs.pop('ha', None)
        if not ha is None:
            text.setXAlign(ha)
        va = kwargs.pop('verticalalignment', None)
        if va is None:
            va = kwargs.pop('va', None)
        if not va is None:
            text.setYAlign(va)
        bbox = kwargs.pop('bbox', None)
        if not bbox is None:
            fill = bbox.pop('fill', None)
            if not fill is None:
                text.setFill(fill)
            facecolor = bbox.pop('facecolor', None)
            if not facecolor is None:
                facecolor = plotutil.getcolor(facecolor)
                text.setFill(True)
                text.setBackground(facecolor)
            edge = bbox.pop('edge', None)
            if not edge is None:
                text.setDrawNeatline(edge)
            edgecolor = bbox.pop('edgecolor', None)
            if not edgecolor is None:
                edgecolor = plotutil.getcolor(edgecolor)
                text.setNeatlineColor(edgecolor)
                text.setDrawNeatline(True)
            linewidth = bbox.pop('linewidth', None)
            if not linewidth is None:
                text.setNeatlineSize(linewidth)
                text.setDrawNeatline(True)
            gap = bbox.pop('gap', None)
            if not gap is None:
                text.setGap(gap)
        if not zdir is None:
            if isinstance(zdir, (list, tuple)):
                text.setZDir(zdir[0], zdir[1], zdir[2])
            else:
                text.setZDir(zdir)
        graphic = Graphic(text, None)
        visible = kwargs.pop('visible', True)
        if visible:
            self.add_graphic(graphic)
            miplot.draw_if_interactive()
        return graphic
        
    def data2pixel(self, x, y, z=None):
        '''
        Transform data coordinate to screen coordinate
        
        :param x: (*float*) X coordinate.
        :param y: (*float*) Y coordinate.
        :param z: (*float*) Z coordinate - only used for 3-D axes.
        '''
        r = self.axes.project(x, y, z) 
        x = r.x
        y = r.y
        rect = self.axes.getPositionArea()
        r = self.axes.projToScreen(x, y, rect)
        sx = r[0] + rect.getX()
        sy = r[1] + rect.getY()
        sy = miplot.figsize()[1] - sy
        return sx, sy
        
        
########################################################3
class Test():
    def test():
        print 'Test...'