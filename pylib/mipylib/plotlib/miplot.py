# coding=utf-8
#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2014-12-26
# Purpose: MeteoInfoLab plot module
# Note: Jython
#-----------------------------------------------------
import os
import inspect
import datetime
import math

from org.meteoinfo.chart import ChartPanel, Location
from org.meteoinfo.data import XYListDataset, XYErrorSeriesData, XYYSeriesData, GridData, ArrayUtil
from org.meteoinfo.data.mapdata import MapDataManage
from org.meteoinfo.data.mapdata.webmap import WebMapProvider
from org.meteoinfo.data.meteodata import MeteoDataInfo, DrawMeteoData
from org.meteoinfo.chart.plot import Plot, Plot2D, PiePlot, PolarPlot, MapPlot, Plot3D, SeriesLegend, ChartPlotMethod, PlotOrientation, GraphicFactory
from org.meteoinfo.chart import Chart, ChartText, ChartLegend, LegendPosition, ChartWindArrow
from org.meteoinfo.chart.axis import LonLatAxis, TimeAxis, LogAxis
from org.meteoinfo.script import ChartForm, MapForm
from org.meteoinfo.legend import MapFrame, LineStyles, HatchStyle, BreakTypes, ColorBreak, PointBreak, PolylineBreak, PolygonBreak, BarBreak, LegendManage, LegendScheme, LegendType
from org.meteoinfo.drawing import PointStyle, MarkerType
from org.meteoinfo.global import Extent
from org.meteoinfo.global.colors import ColorUtil, ColorMap
from org.meteoinfo.global.image import AnimatedGifEncoder
from org.meteoinfo.layer import LayerTypes, MapLayer, WebMapLayer
from org.meteoinfo.layout import MapLayout
from org.meteoinfo.map import MapView
from org.meteoinfo.laboratory.gui import FrmMain
from org.meteoinfo.projection import ProjectionInfo
from org.meteoinfo.shape import Shape, ShapeTypes, Graphic, GraphicCollection

from javax.swing import WindowConstants
from java.awt import Color, Font

from mipylib.numeric.dimarray import DimArray, PyGridData, PyStationData
from mipylib.numeric.miarray import MIArray
import mipylib.numeric.minum as minum
import mipylib.geolib.migeo as migeo
from mipylib.geolib.milayer import MILayer, MIXYListData
import mipylib.miutil as miutil
from mipylib.plotlib.axes import Axes, MapAxes, PolarAxes, Axes3D
import plotutil
import mipylib.migl as migl

## Global ##
batchmode = False
isinteractive = False
maplayout = MapLayout()
chartpanel = None
gca = None

__all__ = [
    'gca','antialias','axes','axes3d','axesm','caxes','axis','axism','bar','barbs','barbsm','bgcolor','box',
    'boxplot','windrose','cla','clabel','clc','clear','clf','cll','cloudspec','colorbar','contour','contourf',
    'contourfm','contourm','display','draw','draw_if_interactive','errorbar',
    'figure','figsize','patch','rectangle','fill_between','webmap','geoshow','gifaddframe','gifanimation','giffinish',
    'grid','gridfm','hist','imshow','imshowm','legend','loglog','makecolors',
    'makelegend','makesymbolspec','map','masklayer','pie','plot','plot3','plotm','quiver',
    'quiverkey','quiverm','readlegend','savefig','savefig_jpeg','scatter','scatter3','scatterm',
    'semilogx','semilogy','set','show','stationmodel','streamplotm','subplot','subplots','suptitle',
    'surf','surfacem','surfacem_1','text','title','twinx','weatherspec','worldmap','xaxis',
    'xlabel','xlim','xreverse','xticks','yaxis','ylabel','ylim','yreverse','yticks','zlabel','zlim','zticks',
    'repaint','isinteractive'
    ]
 
def __getplotdata(data):
    if isinstance(data, (MIArray, DimArray)):
        return data.asarray()
    elif isinstance(data, (list, tuple)):
        if isinstance(data[0], datetime.datetime):
            dd = []
            for d in data:
                v = miutil.date2num(d)
                dd.append(v)
            return minum.array(dd).array
        else:
            return minum.array(data).array
    else:
        return minum.array([data]).array
        
def figsize():
    '''
    Get current figure size.
    
    :returns: Figure width and height.    
    '''
    if chartpanel is None:
        return None
    else:    
        width = chartpanel.getFigureWidth()
        height = chartpanel.getFigureHeight()
        return width, height

def draw_if_interactive():
    '''
    Draw current figure if is interactive model.
    '''
    if isinteractive:
		chartpanel.paintGraphics()
        
def draw():
    '''
    Draw the current figure.
    '''
    chartpanel.paintGraphics()
        
def plot(*args, **kwargs):
    """
    Plot lines and/or markers to the axes. *args* is a variable length argument, allowing
    for multiple *x, y* pairs with an optional format string.
    
    :param x: (*array_like*) Input x data.
    :param y: (*array_like*) Input y data.
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
    global gca
    
    xdatalist = []
    ydatalist = []    
    styles = []
    xaxistype = None
    isxylistdata = False
    if len(args) == 1:
        if isinstance(args[0], MIXYListData):
            dataset = args[0].data
            snum = args[0].size()
            isxylistdata = True
        else:
            ydata = args[0]
            if isinstance(args[0], DimArray):
                xdata = args[0].dimvalue(0)
                if args[0].islondim(0):
                    xaxistype = 'lon'
                elif args[0].islatdim(0):
                    xaxistype = 'lat'
                elif args[0].istimedim(0):
                    xaxistype = 'time'
            else:
                xdata = []
                for i in range(0, len(args[0])):
                    xdata.append(i)
            xdatalist.append(xdata)
            ydatalist.append(ydata)
    elif len(args) == 2:
        if isinstance(args[1], basestring):
            ydata = args[0]
            if isinstance(args[0], DimArray):
                xdata = args[0].dimvalue(0)
                if args[0].islondim(0):
                    xaxistype = 'lon'
                elif args[0].islatdim(0):
                    xaxistype = 'lat'
                elif args[0].istimedim(0):
                    xaxistype = 'time'
            else:
                xdata = []
                for i in range(0, len(args[0])):
                    xdata.append(i)
            styles.append(args[1])
        else:
            xdata = args[0]
            ydata = args[1]
        xdatalist.append(xdata)
        ydatalist.append(ydata)
    else:
        c = 'x'
        for arg in args: 
            if c == 'x':
                #xdatalist.append(__getplotdata(arg))    
                xdatalist.append(arg)
                c = 'y'
            elif c == 'y':
                #ydatalist.append(__getplotdata(arg))
                ydatalist.append(arg)
                c = 's'
            elif c == 's':
                if isinstance(arg, basestring):
                    styles.append(arg)
                    c = 'x'
                else:
                    styles.append('-')
                    #xdatalist.append(__getplotdata(arg))
                    xdatalist.append(arg)
                    c = 'y'
    if len(styles) == 0:
        styles = None
    else:
        while len(styles) < len(xdatalist):
            styles.append('-')
    
    #Set plot data styles
    lines = []
    legend = kwargs.pop('legend', None)
    if not legend is None:
        lbs = legend.getLegendBreaks()
        for i in range(0, snum):
            line = lbs[i]
            lines.append(line)
    else:
        if styles != None:
            for i in range(0, len(styles)):
                label = kwargs.pop('label', 'S_' + str(i + 1))
                line = __getplotstyle(styles[i], label, **kwargs)
                lines.append(line)
        else:
            snum = len(xdatalist)
            for i in range(0, snum):
                label = kwargs.pop('label', 'S_' + str(i + 1))
                line = __getlegendbreak('line', **kwargs)[0]
                line.setCaption(label)
                lines.append(line)
    
    #Create axes
    if gca is None:
        plot = Axes()
    else:
        if isinstance(gca, Axes):
            plot = gca
        else:
            plot = Axes()
    
    if not xaxistype is None:
        __setXAxisType(plot.axes, xaxistype)    
    timetickformat = kwargs.pop('timetickformat', None)
    if not timetickformat is None:
        if not xaxistype == 'time':
            plot.axes.setXAxis(TimeAxis('Time', True))
        plot.axes.getAxis(Location.BOTTOM).setTimeFormat(timetickformat)
        plot.axes.getAxis(Location.TOP).setTimeFormat(timetickformat)
    #plot.setDataset(dataset)     

    #Add graphics
    graphics = []
    if isxylistdata:
        graphic = GraphicFactory.createLineString(dataset, lines)
        plot.add_graphic(graphic)
        graphics.append(graphic)
    else:
        #Add data series
        snum = len(xdatalist)
        for i in range(0, snum):
            label = kwargs.pop('label', 'S_' + str(i + 1))
            xdata = __getplotdata(xdatalist[i])
            ydata = __getplotdata(ydatalist[i])
            graphic = GraphicFactory.createLineString(xdata, ydata, lines[i])
            plot.add_graphic(graphic)
            graphics.append(graphic)
    plot.axes.setAutoExtent()
    
    #Paint dataset
    if chartpanel is None:
        figure()
        
    chart = chartpanel.getChart()
    if gca is None or (not isinstance(gca, Axes)):
        chart.clearPlots()
        chart.setPlot(plot.axes)
    gca = plot
    #chart.setAntiAlias(True)
    chartpanel.setChart(chart)
    draw_if_interactive()
    if len(graphics) > 1:
        return graphics
    else:
        return graphics[0]
        
def plot3(x, y, z, *args, **kwargs):
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
    global gca
    if chartpanel is None:
        figure()
    chart = chartpanel.getChart()
    if gca is None:    
        gca = axes3d()
    else:
        if not isinstance(gca, Axes3D):
            gca = axes3d()
    
    return gca.plot(x, y, z, *args, **kwargs)
        
def semilogy(*args, **kwargs):
    """
    Make a plot with log scaling on the y axis.
    
    :param x: (*array_like*) Input x data.
    :param y: (*array_like*) Input y data.
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
    lines = plot(*args, **kwargs)
    global gca
    __setYAxisType(gca.axes, 'log')
    gca.axes.setAutoExtent()
    return lines
    
def semilogx(*args, **kwargs):
    """
    Make a plot with log scaling on the x axis.
    
    :param x: (*array_like*) Input x data.
    :param y: (*array_like*) Input y data.
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
    lines = plot(*args, **kwargs)
    global gca
    __setXAxisType(gca.axes, 'log')
    gca.axes.setAutoExtent()
    return lines
    
def loglog(*args, **kwargs):
    """
    Make a plot with log scaling on both x and y axis.
    
    :param x: (*array_like*) Input x data.
    :param y: (*array_like*) Input y data.
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
    lines = plot(*args, **kwargs)
    global gca
    __setXAxisType(gca.axes, 'log')
    __setYAxisType(gca.axes, 'log')
    gca.axes.setAutoExtent()
    return lines
        
def errorbar(x, y, yerr=None, xerr=None, fmt='', **kwargs):
    global gca  
    
    #Add data series
    label = kwargs.pop('label', 'S_0')
    xdata = __getplotdata(x)
    ydata = __getplotdata(y)
    if not yerr is None:
        if isinstance(yerr, (int, float)):
            ye = []
            for i in range(xdata.getSize()):
                ye.append(yerr)
            yerr = minum.array(ye).array
        else:
            yerr = __getplotdata(yerr)
    if not xerr is None:
        if isinstance(xerr, (int, float)):
            ye = []
            for i in range(xdata.getSize()):
                ye.append(xerr)
            xerr = minum.array(ye).array
        else:
            xerr = __getplotdata(xerr)
    
    #Get plot data style
    if fmt == '':
        line = __getlegendbreak('line', **kwargs)[0]
        line.setCaption(label)
    else:
        line = __getplotstyle(fmt, label, **kwargs)
    
    #Create graphics
    graphics = GraphicFactory.createErrorLineString(xdata, ydata, xerr, yerr, line)
    
    #Create Axes
    if gca is None:
        plot = Axes()
    else:
        if isinstance(gca, Axes):
            plot = gca
        else:
            plot = Axes()
    plot.add_graphic(graphics)
    plot.axes.setAutoExtent()
    
    #Chart panel
    if chartpanel is None:
        figure()
        
    chart = chartpanel.getChart()
    if gca is None or (not isinstance(gca, Axes)):
        chart.clearPlots()
        chart.setPlot(plot.axes)
    #chart.setAntiAlias(True)
    chartpanel.setChart(chart)
    gca = plot
    draw_if_interactive()
    return graphics 
    
def bar(*args, **kwargs):
    """
    Make a bar plot.
    
    Make a bar plot with rectangles bounded by:
        left, left + width, bottom, bottom + height
    
    :param left: (*array_like*) The x coordinates of the left sides of the bars.
    :param height: (*array_like*) The height of the bars.
    :param width: (*array_like*) Optional, the widths of the bars default: 0.8.
    :param bottom: (*array_like*) Optional, the y coordinates of the bars default: None
    :param color: (*Color*) Optional, the color of the bar faces.
    :param edgecolor: (*Color*) Optional, the color of the bar edge. Default is black color.
        Edge line will not be plotted if ``edgecolor`` is ``None``.
    :param linewidth: (*int*) Optional, width of bar edge.
    :param label: (*string*) Label of the bar series.
    :param hatch: (*string*) Hatch string.
    :param hatchsize: (*int*) Hatch size. Default is None (8).
    :param bgcolor: (*Color*) Background color, only valid with hatch.
    :param barswidth: (*float*) Bars width (0 - 1), only used for automatic bar with plot
        (only one argument widthout ``width`` augument). Defaul is 0.8.
    :param morepoints: (*boolean*) More points in bar rectangle. Defaul is False.
    
    :returns: Bar legend break.
    
    
    The following format string characters are accepted to control the hatch style:
      =========  ===========
      Character  Description
      =========  ===========
      '-'         horizontal hatch style
      '|'         vertical hatch style
      '\\'        forward_diagonal hatch style
      '/'         backward_diagonal hatch style
      '+'         cross hatch style
      'x'         diagonal_cross hatch style
      '.'         dot hatch style
      =========  ===========
      
    """
    #Get dataset
    global gca
    
    #Add data series
    label = kwargs.pop('label', 'S_0')
    xdata = None
    autowidth = True
    width = 0.8
    if len(args) == 1:
        ydata = args[0]
    elif len(args) == 2:
        if isinstance(args[1], (int, float)):
            ydata = args[0]
            width = args[1]
            autowidth = False
        else:
            xdata = args[0]
            ydata = args[1]
    else:
        xdata = args[0]
        ydata = args[1]
        width = args[2]
        autowidth = False        
    
    if xdata is None:
        xdata = []
        for i in range(1, len(args[0]) + 1):
            xdata.append(i)
    xdata = __getplotdata(xdata)
    ydata = __getplotdata(ydata)
    width = __getplotdata(width)
    yerr = kwargs.pop('yerr', None)
    if not yerr is None:
        if not isinstance(yerr, (int, float)):
            yerr = __getplotdata(yerr)
    bottom = kwargs.pop('bottom', None)   
    if not bottom is None:
        bottom = __getplotdata(bottom)
    
    #Set plot data styles
    fcobj = kwargs.pop('color', None)
    if fcobj is None:
        fcobj = kwargs.pop('facecolor', 'b')
    if isinstance(fcobj, (tuple, list)):
        colors = __getcolors(fcobj)
    else:
        color = __getcolor(fcobj)
        colors = [color]
    ecobj = kwargs.pop('edgecolor', 'k')
    edgecolor = __getcolor(ecobj)
    linewidth = kwargs.pop('linewidth', 1.0) 
    hatch = kwargs.pop('hatch', None)
    hatch = __gethatch(hatch) 
    hatchsize = kwargs.pop('hatchsize', None)
    bgcolor = kwargs.pop('bgcolor', None)
    bgcolor = __getcolor(bgcolor)
    ecolor = kwargs.pop('ecolor', 'k')
    ecolor = __getcolor(ecolor)
    morepoints = kwargs.pop('morepoints', False)
    barbreaks = []
    for color in colors:
        lb = BarBreak()
        lb.setCaption(label)
        lb.setColor(color)    
        if edgecolor is None:
            lb.setDrawOutline(False)
        else:
            lb.setOutlineColor(edgecolor)  
        lb.setOutlineSize(linewidth)   
        if not hatch is None:
            lb.setStyle(hatch)
            if not bgcolor is None:
                lb.setBackColor(bgcolor)
            if not hatchsize is None:
                lb.setStyleSize(hatchsize)
        lb.setErrorColor(ecolor)
        barbreaks.append(lb)
        
    #Create bar graphics
    if morepoints:
        graphics = GraphicFactory.createBars1(xdata, ydata, autowidth, width, not yerr is None, yerr, \
            not bottom is None, bottom, barbreaks)
    else:
        graphics = GraphicFactory.createBars(xdata, ydata, autowidth, width, not yerr is None, yerr, \
            not bottom is None, bottom, barbreaks)        
    
    #Create bar plot
    if gca is None:
        plot = Axes()
    else:
        if isinstance(gca, Axes):
            plot = gca
        else:
            plot = Axes()
    plot.add_graphic(graphics)
    plot.axes.setAutoExtent()
    if autowidth:
        barswidth = kwargs.pop('barswidth', 0.8)
        plot.axes.setBarsWidth(barswidth)
    
    #Create figure
    if chartpanel is None:
        figure()
    
    #Set chart
    chart = chartpanel.getChart()
    if gca is None or (not isinstance(gca, Axes)):
        chart.setCurrentPlot(plot.axes)
    chartpanel.setChart(chart)
    gca = plot
    draw_if_interactive()
    return barbreaks
          
def hist(x, bins=10, range=None, normed=False, cumulative=False,
        bottom=None, histtype='bar', align='mid',
        orientation='vertical', rwidth=None, log=False, **kwargs):
    """
    Plot a histogram.
    
    :param x: (*array_like*) Input values, this takes either a single array or a sequency of arrays 
        which are not required to be of the same length.
    :param bins: (*int*) If an integer is given, bins + 1 bin edges are returned.
    """
    #Get dataset
    global gca
    
    #Add data series
    label = kwargs.pop('label', 'S_0')
    
    #Set plot data styles
    fcobj = kwargs.pop('color', None)
    if fcobj is None:
        fcobj = kwargs.pop('facecolor', 'b')
    if isinstance(fcobj, (tuple, list)):
        colors = __getcolors(fcobj)
    else:
        color = __getcolor(fcobj)
        colors = [color]
    ecobj = kwargs.pop('edgecolor', 'k')
    edgecolor = __getcolor(ecobj)
    linewidth = kwargs.pop('linewidth', 1.0) 
    hatch = kwargs.pop('hatch', None)
    hatch = __gethatch(hatch) 
    hatchsize = kwargs.pop('hatchsize', None)
    bgcolor = kwargs.pop('bgcolor', None)
    bgcolor = __getcolor(bgcolor)
    ecolor = kwargs.pop('ecolor', 'k')
    ecolor = __getcolor(ecolor)
    barbreaks = []
    for color in colors:
        lb = BarBreak()
        lb.setCaption(label)
        lb.setColor(color)    
        if edgecolor is None:
            lb.setDrawOutline(False)
        else:
            lb.setOutlineColor(edgecolor)  
        lb.setOutlineSize(linewidth)   
        if not hatch is None:
            lb.setStyle(hatch)
            if not bgcolor is None:
                lb.setBackColor(bgcolor)
            if not hatchsize is None:
                lb.setStyleSize(hatchsize)
        lb.setErrorColor(ecolor)
        barbreaks.append(lb)
        
    #Create bar graphics
    x = __getplotdata(x)
    graphics = GraphicFactory.createHistBars(x, bins, barbreaks)        
    
    #Create bar plot
    if gca is None:
        plot = Axes()
    else:
        if isinstance(gca, Axes):
            plot = gca
        else:
            plot = Axes()
    plot.add_graphic(graphics)
    plot.axes.setAutoExtent()
    
    #Create figure
    if chartpanel is None:
        figure()
    
    #Set chart
    chart = chartpanel.getChart()
    if gca is None or (not isinstance(gca, Axes)):
        chart.setCurrentPlot(plot.axes)
    chartpanel.setChart(chart)
    gca = plot
    draw_if_interactive()
    return lb
    
def scatter(x, y, s=8, c='b', marker='o', norm=None, vmin=None, vmax=None,
            alpha=None, linewidth=None, verts=None, hold=None, **kwargs):
    """
    Make a scatter plot of x vs y, where x and y are sequence like objects of the same lengths.
    
    :param x: (*array_like*) Input x data.
    :param y: (*array_like*) Input y data.
    :param s: (*int*) Size of points.
    :param c: (*Color*) Color of the points. Or z vlaues.
    :param alpha: (*int*) The alpha blending value, between 0 (transparent) and 1 (opaque).
    :param marker: (*string*) Marker of the points.
    :param label: (*string*) Label of the points series.
    :param levs: (*array_like*) Optional. A list of floating point numbers indicating the level 
        points to draw, in increasing order.
    
    :returns: Points legend break.
    """
    global gca    
    
    #Add data series
    label = kwargs.pop('label', 'S_0')
    xdata = __getplotdata(x)
    ydata = __getplotdata(y)
    
    #Set plot data styles
    pb, isunique = __getlegendbreak('point', **kwargs)
    pb.setCaption(label)
    pstyle = __getpointstyle(marker)    
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
                    ls = __getlegendscheme([], c.min(), c.max(), **kwargs)
                else:
                    ls = __getlegendscheme([cnum], c.min(), c.max(), **kwargs)
            else:
                ls = __getlegendscheme([levels], c.min(), c.max(), **kwargs)
            ls = __setlegendscheme_point(ls, **kwargs)
            if isinstance(s, int):
                for lb in ls.getLegendBreaks():
                    lb.setSize(s)
            else:
                n = len(s)
                for i in range(0, n):
                    ls.getLegendBreaks()[i].setSize(s[i])
        #Create graphics
        graphics = GraphicFactory.createPoints(xdata, ydata, c.asarray(), ls)
    else:
        colors = __getcolors(c, alpha)   
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
        graphics = GraphicFactory.createPoints(xdata, ydata, pbs)
    
    if gca is None:
        plot = Axes()
    else:
        if isinstance(gca, Axes):
            plot = gca
        else:
            plot = Axes()
    plot.add_graphic(graphics)
    plot.axes.setAutoExtent()
    
    #Paint dataset
    if chartpanel is None:
        figure()
        
    chart = chartpanel.getChart()
    if gca is None or (not isinstance(gca, Axes)):
        chart.setCurrentPlot(plot.axes)
    chartpanel.setChart(chart)
    gca = plot
    draw_if_interactive()
    return graphics
    
def scatter3(x, y, z, s=8, c='b', marker='o', alpha=None, linewidth=None, 
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
    global gca
    if chartpanel is None:
        figure()
    chart = chartpanel.getChart()
    if gca is None:    
        gca = axes3d()
    else:
        if not isinstance(gca, Axes3D):
            gca = axes3d()   
    
    return gca.scatter(x, y, z, s, c, marker, alpha, linewidth, verts, **kwargs)

def patch(x, y=None, **kwargs):
    '''
    Create one or more filled polygons.
    
    :param x: (*array_like*) X coordinates for each vertex. X should be PolygonShape if y
        is None.
    :param y: (*array_like*) Y coordinates for each vertex.
    '''
    lbreak, isunique = __getlegendbreak('polygon', **kwargs)
    if y is None:
        graphics = Graphic(x, lbreak)
    else:
        x = __getplotdata(x)
        y = __getplotdata(y)
        graphics = GraphicFactory.createPolygons(x, y, lbreak)
    
    global gca 
    if gca is None:
        plot = Axes()
    else:
        if isinstance(gca, Axes):
            plot = gca
        else:
            plot = Axes()
    plot.add_graphic(graphics)
    plot.axes.setAutoExtent()
    
    #Paint dataset
    if chartpanel is None:
        figure()
        
    chart = chartpanel.getChart()
    if gca is None or (not isinstance(gca, Axes)):
        chart.setCurrentPlot(plot.axes)
    chartpanel.setChart(chart)
    gca = plot
    draw_if_interactive()
    return graphics
    
def rectangle(position, curvature=None, **kwargs):
    '''
    Create one or more filled polygons.
    
    :param position: (*list*) Position of the rectangle [x, y, width, height].
    :param curvature: (*list*) Curvature of the rectangle [x, y]. Default is None.
    '''
    lbreak, isunique = __getlegendbreak('polygon', **kwargs)
    if isinstance(curvature, (int, float)):
        curvature = [curvature, curvature]
    graphic = GraphicFactory.createRectangle(position, curvature, lbreak)
    
    global gca 
    if gca is None:
        plot = Axes()
    else:
        if isinstance(gca, Axes):
            plot = gca
        else:
            plot = Axes()
    plot.add_graphic(graphic)
    plot.axes.setAutoExtent()
    
    #Paint dataset
    if chartpanel is None:
        figure()
        
    chart = chartpanel.getChart()
    if gca is None or (not isinstance(gca, Axes)):
        chart.setCurrentPlot(plot.axes)
    chartpanel.setChart(chart)
    gca = plot
    draw_if_interactive()
    return graphic
    
def fill_between(x, y1, y2=0, where=None, **kwargs):
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
    xdata = __getplotdata(x)
    if isinstance(y1, (int, long, float)):
        yy = []
        for i in range(dn):
            yy.append(y1)
        y1 = minum.array(yy).array
    else:
        y1 = __getplotdata(y1)
    if isinstance(y2, (int, long, float)):
        yy = []
        for i in range(dn):
            yy.append(y2)
        y2 = minum.array(yy).array
    else:
        y2 = __getplotdata(y2)
    if not where is None:
        if isinstance(where, (tuple, list)):
            where = minum.array(where)
        where = where.asarray()
    
    #Set plot data styles
    pb, isunique = __getlegendbreak('polygon', **kwargs)
    pb.setCaption(label)
    pb.setDrawOutline(False)
    
    #Create graphics
    graphics = GraphicFactory.createFillBetweenPolygons(xdata, y1, y2, where, pb)    
    
    #Create axes
    if gca is None:
        plot = Axes()
    else:
        if isinstance(gca, Axes):
            plot = gca
        else:
            plot = Axes() 
    plot.add_graphic(graphics)
    plot.axes.setAutoExtent()
    
    #Paint dataset
    if chartpanel is None:
        figure()
        
    chart = chartpanel.getChart()
    if gca is None:
        chart.clearPlots()
        chart.setPlot(plot.axes)
    #chart.setAntiAlias(True)
    chartpanel.setChart(chart)
    gca = plot
    draw_if_interactive()
    return pb 
        
def pie(x, explode=None, labels=None, colors=None, autopct=None, pctdistance=0.6, shadow=False, 
    labeldistance=1.1, startangle=0, radius=None, hold=None, **kwargs):
    """
    Plot a pie chart.
    
    Make a pie chart of array *x*. The fraction area of each wedge is given by x/sum(x). If
    sum(x) <= 1, then the values of x give the fractional area directly and the array will not
    be normalized. The wedges are plotted counterclockwise, by default starting from the x-axis.
    
    :param explode: (*None | len(x)sequence) If not *None*, is a ``len(x)`` array which specifies
        the fraction of the radius with which to offset each wedge.
    :param labels: (*None | len(x) sequence of colors*] A sequence of strings providing the labels
        for each wedge.
    :param colors: (*None | color sequence*) A sequence of color args through which the pie chart
        will cycle.
    :param autopct: (*None | format string | format function) If not *None*, is a string or function
        used to label the wedges with their numeric value. The label will be placed inside the wedge.
        If it is a format string, the label will be ``fmt%pct``. If it is a function, it will be called.
    :param pctdistance: (*float*) The ratio between the center of each pie slice and the start of the
        text generated by *autopct*. Ignored if autopct is *None*; default is 0.6.
    :param labeldistance: (*float*) The ratial distance at which the pie labels are drawn.
    :param shadow: (*boolean*) Draw a shadow beneath the pie.
    :param startangle: (*float*) If not *0*, rotates the start of the pie chart by *angle* degrees
        counterclockwise from the x-axis.
    :radius: (*float*) The radius of the pie, if *radius* is *None* it will be set to 1.
    :param fontname: (*string*) Font name. Default is ``Arial`` .
    :param fontsize: (*int*) Font size. Default is ``14`` .
    
    :returns: (*tuple*) Patches and texts.
    """        
    n = len(x)
    x = __getplotdata(x)
    if colors is None:
        colors = makecolors(n)
    else:
        colors = __getcolors(colors)
        
    fontname = kwargs.pop('fontname', 'Arial')
    fontsize = kwargs.pop('fontsize', 14)
    bold = kwargs.pop('bold', False)
    fontcolor = kwargs.pop('fontcolor', 'black')
    if bold:
        font = Font(fontname, Font.BOLD, fontsize)
    else:
        font = Font(fontname, Font.PLAIN, fontsize)
    fontcolor = __getcolor(fontcolor)
    
    #Create graphics
    graphics = GraphicFactory.createPieArcs(x, colors, labels, startangle, explode, font, fontcolor, \
        autopct)
    
    #Get current axes
    global gca
    if gca is None:
        #plot = PieAxes()
        gca = axes()
    else:
        if gca.axestype != 'cartesian':
            gca = axes()
    gca.add_graphic(graphics)
    gca.axes.setAutoExtent()
    gca.axes.setAutoAspect(False)
    gca.axes.getAxis(Location.BOTTOM).setVisible(False)
    gca.axes.getAxis(Location.LEFT).setVisible(False)
    gca.axes.getAxis(Location.TOP).setVisible(False)
    gca.axes.getAxis(Location.RIGHT).setVisible(False)
    
    #Paint dataset
    if chartpanel is None:
        figure()
        chartpanel.getChart().addPlot(gca.axes)

    draw_if_interactive()
    return graphics
    
def boxplot(x, sym=None, positions=None, widths=None, color=None, showcaps=True, showfliers=True, showmeans=False, \
    meanline=False, boxprops=None, medianprops=None, meanprops=None, whiskerprops=None, capprops=None, flierprops=None):
    """
    Make a box and whisker plot.
    
    Make a box and whisker plot for each column of x or each vector in sequence x. The box extends from lower
    to upper quartile values of the data, with a line at the median. The whiskers extend from the box to show
    the range of the data. Flier points are those past the end of the whiskers.
    
    :param x: (*Array or a sequence of vectors*) The input data.
    :param sym: (*string*) The default symbol for flier points. Enter an empty string ('') if you don’t 
        want to show fliers. If None, then the fliers default to ‘b+’ If you want more control use the 
        flierprops kwarg.
    :param positions: (*array_like*) Sets the positions of the boxes. The ticks and limits are automatically 
        set to match the positions. Defaults to range(1, N+1) where N is the number of boxes to be drawn.
    :param widths: (*scalar or array_like*) Sets the width of each box either with a scalar or a sequence. 
        The default is 0.5, or 0.15*(distance between extreme positions), if that is smaller.
    :param color: (*Color*) Color for all parts of the box plot. Defaul is None.
    :param showcaps: (*boolean*) Show the caps on the ends of whiskers. Default is ``True``.
    :param showfliers: (*boolean*) Show the outliers beyond the caps. Defaul is ``True``.
    :param showmeans: (*boolean*) Default is ``False``. Show the mean or not.
    :param meanline: (*boolean*) Default is ``False``. If ``True`` (and showmeans is ``True``), will try to render
        the mean as a line spanning. Otherwise, means will be shown as points.
    :param boxprops: (*dict*) Specifies the style of the box.
    :param medianprops: (*dict*) Specifies the style of the median.
    :param meanprops: (*dict*) Specifies the style of the mean.
    :param whiskerprops: (*dict*) Specifies the style of the whiskers.
    :param capprops: (*dict*) Specifies the style of the caps.
    :param flierprops: (*dict*) Specifies the style of the fliers.
    """
    #Get current axes
    global gca   
    
    if isinstance(x, list):
        x1 = []
        for a in x:
            x1.append(__getplotdata(a))
        x = x1
    else:
        x = __getplotdata(x)
        x = [x]
    
    if not positions is None:
        if isinstance(positions, (MIArray, DimArray)):
            positions = positions.tolist()
    
    if not widths is None:
        if isinstance(widths, (int, float)):
            nwidths = []
            for i in range(len(x)):
                nwidths.append(widths)
            widths = nwidths
        elif isinstance(widths, (MIArray, DimArray)):
            widths = widths.tolist()
        
    #Get box plot properties
    if not color is None:
        color = __getcolor(color)
    if not sym is None:
        sym = __getplotstyle(sym, '')
        sym.setDrawFill(False)
        if not color is None:
            sym.setColor(color)
            sym.setOutlineColor(color)
    if boxprops is None:
        boxprops = PolygonBreak()
        boxprops.setDrawFill(False)
        boxprops.setOutlineColor(color is None and Color.blue or color)
    else:
        boxprops = __getlegendbreak('polygon', **boxprops)[0]
    if medianprops is None:
        medianprops = PolylineBreak()
        medianprops.setColor(color is None and Color.red or color)
    else:
        medianprops = __getlegendbreak('line', **medianprops)[0]
    if whiskerprops is None:
        whiskerprops = PolylineBreak()
        whiskerprops.setColor(color is None and Color.black or color)
        whiskerprops.setStyle(LineStyles.Dash)
    else:
        whiskerprops = __getlegendbreak('line', **whiskerprops)[0]
    if capprops is None:
        capprops = PolylineBreak()
        capprops.setColor(color is None and Color.black or color)
    else:
        capprops = __getlegendbreak('line', **capprops)[0]
    if meanline:
        if not meanprops is None:
            meanprops = __getlegendbreak('line', **meanprops)[0]
        else:
            meanprops = PolylineBreak()
            meanprops.setColor(color is None and Color.black or color)
    else:
        if meanprops is None:
            meanprops = PointBreak()
            meanprops.setStyle(PointStyle.Square)
            meanprops.setColor(color is None and Color.red or color)
            meanprops.setOutlineColor(color is None and Color.black or color)
        else:
            meanprops = __getlegendbreak('point', **meanprops)[0]
    if not flierprops is None:
        flierprops = __getlegendbreak('point', **flierprops)[0]
    else:
        flierprops = sym
    if flierprops is None:
        flierprops = PointBreak()
        flierprops.setColor(color is None and Color.red or color)
        flierprops.setStyle(PointStyle.Plus)
    
    #Create graphics
    graphics = GraphicFactory.createBox(x, positions, widths, showcaps, showfliers, showmeans, boxprops, \
        medianprops, whiskerprops, capprops, meanprops, flierprops)
    
    #Create XYPlot
    if gca is None:
        plot = Axes()
    else:
        if isinstance(gca, Axes):
            plot = gca
        else:
            plot = Axes()
    plot.add_graphic(graphics)
    plot.axes.setAutoExtent()
    
    #Paint dataset
    if chartpanel is None:
        figure()
        
    chart = chartpanel.getChart()
    if gca is None:
        chart.setCurrentPlot(plot.axes)
    elif not isinstance(gca, Axes):
        if isinstance(gca.axes, Plot):
            chart.removePlot(gca.axes)
        chart.setCurrentPlot(plot.axes)
    
    chartpanel.setChart(chart)
    gca = plot
    #xlim(0.5, len(x) + 0.5)
    #xticks(minum.arange(1, len(x) + 1, 1))
    draw_if_interactive()
    return graphics
    
def windrose(wd, ws, nwdbins=16, wsbins=None, degree=True, colors=None, cmap='matlab_jet', \
    alpha=0.7, rmax=None, rtickloc=None, rticks=None, rlabelpos=60, xticks=None, **kwargs):
    '''
    Plot windrose chart.
    
    :param wd: (*array_like*) Wind direction.
    :param ws: (*array_like*) Wind speed.
    :param nwdbins: (*int*) Number of wind direction bins [4 | 8 | 16].
    :param wsbins: (*array_like*) Wind speed bins.
    :param degree: (*boolean*) The unit of wind direction is degree or radians.
    :param colors: (*color list*) The colors.
    :param cmap: (*string*) Color map.
    :param alpha: (*float*) Color alpha (0 - 1).
    :param rmax: (*float*) Radial maximum value.
    :param rtickloc: (*list of float*) Radial tick locations.
    :param rticks: (*list of string*) Radial ticks.
    :param rlabelpos: (*float*) Radial label position in degree.
    :param xticks: (*list of string*) X ticks.
    
    :returns: Polar axes and bars
    '''    
    if not nwdbins in [4, 8, 16]:
        print 'nwdbins must be 4, 8 or 16!'
        raise ValueError(nwdbins)
        
    if isinstance(wd, list):
        wd = minum.array(wd)
    if isinstance(ws, list):
        ws = minum.array(ws)
    
    wdbins = minum.linspace(0.0, 2 * minum.pi, nwdbins + 1)    
    if wsbins is None:
        wsbins = minum.arange(0., ws.max(), 2.).tolist()
        wsbins.append(100)
        wsbins = minum.array(wsbins)            
    
    dwdbins = minum.degrees(wdbins)
    dwdbins = dwdbins - 90
    for i in range(len(dwdbins)):
        if dwdbins[i] < 0:
            dwdbins[i] += 360
    for i in range(len(dwdbins)):
        d = dwdbins[i]
        d = 360 - d
        dwdbins[i] = d
    rwdbins = minum.radians(dwdbins)
        
    N = len(wd)
    wdN = nwdbins
    wsN = len(wsbins) - 1
    if colors is None:
        colors = makecolors(wsN, cmap=cmap, alpha=alpha)
    
    wd = wd + 360./wdN/2
    wd[wd>360] = wd - 360
    rwd = minum.radians(wd)    
    
    global gca
    if gca is None:
        gca = axes(polar=True)
    else:
        if not isinstance(gca, PolarAxes):
            gca = axes(polar=True)
    
    width = kwargs.pop('width', 0.5)
    if width > 1:
        width = 1
    if width <= 0:
        width = 0.2
    theta = minum.ones(wdN)
    width = 2. * width * minum.pi / wdN
    for i in range(wdN):
        theta[i] = rwdbins[i] - width/2
        
    bars = []
    hhist = 0
    rrmax = 0       
    for i in range(wsN):
        idx = minum.where((ws>=wsbins[i]) * (ws<wsbins[i+1]))
        if idx is None:
            continue
        print wsbins[i], wsbins[i+1]
        s_wd = rwd[idx]
        wdhist = minum.histogram(s_wd, wdbins)[0].astype('float')
        wdhist = wdhist / N
        rrmax = max(rrmax, wdhist.max())
        lab = '%s - %s' % (wsbins[i], wsbins[i+1])
        bb = bar(theta, wdhist, width, bottom=hhist, color=colors[i], \
            edgecolor='gray', label=lab, morepoints=True)[0]
        bb.setStartValue(wsbins[i])
        bb.setEndValue(wsbins[i+1])
        bars.append(bb)
        hhist = hhist + wdhist
    
    if rmax is None:
        rmax = math.ceil(rrmax)
    gca.set_rmax(rmax)
    if not rtickloc is None:
        gca.set_rtick_locations(rtickloc)
    if not rticks is None:
        gca.set_rticks(rticks)
    gca.set_rtick_format('%')
    gca.set_rlabel_position(rlabelpos)
    gca.set_xtick_locations(minum.arange(0., 360., 360./wdN))
    step = 16 / nwdbins
    if xticks is None:
        xticks = ['E','ENE','NE','NNE','N','NNW','NW','WNW','W','WSW',\
            'SW','SSW','S','SSE','SE','ESE']
        xticks = xticks[::step]
    gca.set_xticks(xticks)       
    draw_if_interactive()
    return gca, bars
 
def figure(bgcolor=None, figsize=None, newfig=True):
    """
    Creates a figure.
    
    :param bgcolor: (*Color*) Optional, background color of the figure. Default is ``None`` .
    :param figsize: (*list*) Optional, width and height of the figure such as ``[600, 400]`` .
        Default is ``None`` with changable size same as *Figures* window.
    :param newfig: (*boolean*) Optional, if creates a new figure. Default is ``True`` .
    """
    global chartpanel
    chart = Chart()
    if not bgcolor is None:
        chart.setDrawBackground(True)
        chart.setBackground(__getcolor(bgcolor))
    if figsize is None:
        chartpanel = ChartPanel(chart)
    else:
        chartpanel = ChartPanel(chart, figsize[0], figsize[1])
    if not batchmode:
        show(newfig)
        
    return chartpanel
        
def show(newfig=True):
    if migl.milapp == None:
        if not batchmode:            
            form = ChartForm(chartpanel)
            chartpanel.paintGraphics()
            form.setSize(600, 500)
            form.setLocationRelativeTo(None)
            form.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE)
            form.setVisible(True)     
    else:
        figureDock = migl.milapp.getFigureDock()
        if newfig:
            figureDock.addFigure(chartpanel)
        else:
            if figureDock.getCurrentFigure() is None:
                figureDock.addFigure(chartpanel)
            else:
                figureDock.setCurrentFigure(chartpanel)
    
# Set figure background color
def bgcolor(color):
    '''
    Set figure background color
    
    :param color: (*Color*) Background color    
    '''
    chart = chartpanel.getChart()
    if color is None:
        chart.setDrawBackground(False)
    else:
        chart.setDrawBackground(True)
        chart.setBackground(__getcolor(color))
    draw_if_interactive()    
    
def caxes(ax=None):
    '''
    Set or get current axes.
    
    :param ax: (*Axes or int*) The axes to be set as current axes. Is None, get current
        axes.
    '''
    global gca
    chart = chartpanel.getChart()    
    if isinstance(ax, int):
        if chartpanel is None:
            figure()
                        
        gca = __get_axes(chart, ax)
        chart.setCurrentPlot(ax - 1)
    elif not ax is None:
        gca = ax
        chart.setCurrentPlot(chart.getPlotIndex(ax.axes))
    return gca
    
def subplot(nrows, ncols, plot_number, **kwargs):
    """
    Returen a subplot axes positioned by the given grid definition.
    
    :param nrows, nrows: (*int*) Whree *nrows* and *ncols* are used to notionally spli the 
        figure into ``nrows * ncols`` sub-axes.
    :param plot_number: (*int) Is used to identify the particular subplot that this function
        is to create within the notional gird. It starts at 1, increments across rows first
        and has a maximum of ``nrows * ncols`` .
    
    :returns: Current axes specified by ``plot_number`` .
    """
    if chartpanel is None:
        figure()
        
    global gca
    chart = chartpanel.getChart()
    chart.setRowNum(nrows)
    chart.setColumnNum(ncols)
    gca = None
    #if isinstance(plot_number, int):
    #    gca = chart.getPlot(plot_number)          
    isnew = gca is None
    if isnew:
        polar = kwargs.pop('polar', False)
        if polar:
            gca = PolarAxes()
        else:
            gca = Axes()
        gca.axes.isSubPlot = True        
        #gca.rowIndex = rowidx
        #gca.columnIndex = colidx
    else:
        chart.setCurrentPlot(plot_number - 1)  
    position = kwargs.pop('position', None)
    if position is None:
        if isnew:
            if isinstance(plot_number, (list, tuple)):
                i = 0
                for pnum in plot_number:
                    pnum -= 1
                    rowidx = pnum / ncols
                    colidx = pnum % ncols
                    width = 1. / ncols
                    height = 1. / nrows                    
                    x = width * colidx
                    y = 1. - height * (rowidx + 1)
                    if i == 0:
                        minx = x
                        miny = y
                        maxx = x + width
                        maxy = y + height
                    else:
                        minx = min(x, minx)
                        miny = min(y, miny)
                        maxx = max(x + width, maxx)
                        maxy = max(y + height, maxy)
                    i += 1
                x = minx
                y = miny
                width = maxx - minx
                height = maxy - miny
            else:
                plot_number -= 1
                rowidx = plot_number / ncols
                colidx = plot_number % ncols
                width = 1. / ncols
                height = 1. / nrows
                x = width * colidx
                y = 1. - height * (rowidx + 1)
            gca.set_position([x, y, width, height])
            gca.set_outerposition([x, y, width, height])
            gca.active_outerposition(True)
    else:
        gca.set_position(position)
        gca.active_outerposition(False)
    outerposition = kwargs.pop('outerposition', None)
    if not outerposition is None:
        gca.set_outerposition(outerposition)
        gca.active_outerposition(True)
        
    if isinstance(gca, MapAxes):
        __set_axesm(gca, **kwargs)
    else:
        __set_axes(gca, **kwargs)
        
    if isnew:
        chart.addPlot(gca.axes)
        chart.setCurrentPlot(chart.getPlots().size() - 1)
    
    return gca
    
def subplots(nrows=1, ncols=1, position=None, sharex=False, sharey=False, \
    subplot_kw=None, wspace=None, hspace=None, axestype='Axes', **kwargs):
    '''
    Create a figure and a set of subplots.
    
    :param nrows: (*int*) Number of rows.
    :param ncols: (*int*) Number of cols.
    :param position: (*list*) All axes' position specified by *position=* [left, bottom, width
        height] in normalized (0, 1) units. Default is [0,0,1,1].
    :param sharex: (*boolean*) If share x axis.
    :param sharey: (*boolean*) If share y axis.
    :param subplot_kw: (*dict*) Subplot key words.
    :param wspace: (*float*) The amount of width reserved for blank space between subplots,
        expressed as a fraction of the average axis width.
    :param hspace: (*float*) The amount of height reserved for blank space between subplots,
        expressed as a fraction of the average axis height.
    :param axestype: (*string*) Axes type [Axes | Axes3D | MapAxes | PolarAxes].
    '''
    if position is None:
        if wspace is None and hspace is None:
            position = [0, 0, 1, 1]
        else:
            position = [0.13, 0.11, 0.775, 0.815]
    left = float(position[0])
    bottom = float(position[1])
    width = float(position[2])
    height = float(position[3])
    
    global chartpanel
    if chartpanel is None:
        figure()
        
    chart = chartpanel.getChart()
    chart.setRowNum(nrows)
    chart.setColumnNum(ncols)
    axs = []
    ax2d = nrows > 1 and ncols > 1
    w = width / ncols
    h = height / nrows
    iswspace = False
    ishspace = False
    if not wspace is None and ncols > 1:
        w = (width - wspace * (ncols - 1)) / ncols
        iswspace = True
    if not hspace is None and nrows > 1:
        h = (height - hspace * (nrows - 1)) / nrows
        ishspace = True
    axestype = axestype.lower()
    y = bottom + height - h
    for i in range(nrows):
        if ax2d:
            axs2d = []
        x = left
        if ishspace:
            if i > 0:
                y -= hspace
        for j in range(ncols):   
            if axestype == 'axes3d':
                ax = Axes3D()
                __set_axes3d(ax, **kwarg)
            elif axestype == 'mapaxes':
                ax = MapAxes()
                __set_axesm(ax, **kwargs)
            elif axestype == 'polaraxes':
                ax = PolarAxes()
            else:
                ax = Axes()
                __set_axes(ax, **kwargs)
            ax.axes.isSubPlot = True             
            if not iswspace and not ishspace:
                x = left + w * j
                y = (bottom + height) - h * (i + 1)
                ax.set_position([x, y, w, h])
                ax.set_outerposition([x, y, w, h])
                ax.active_outerposition(True)
            else:
                if iswspace:
                    if j > 0:
                        x += wspace                
                ax.set_position([x, y, w, h])
                ax.active_outerposition(False)
                x += w
            if sharex:
                if i < nrows - 1:
                    ax.axes.getAxis(Location.BOTTOM).setDrawTickLabel(False)
            if sharey:
                if j > 0:
                    ax.axes.getAxis(Location.LEFT).setDrawTickLabel(False)
            chart.addPlot(ax.axes)
            if ax2d:
                axs2d.append(ax)
            else:
                axs.append(ax)
        if ax2d:
            axs.append(tuple(axs2d))
        y -= h
        
    global gca
    if ax2d:
        gca = axs[0][0]
    else:
        gca = axs[0]
    return chartpanel, tuple(axs)
    
def currentplot(plot_number):
    if chartpanel is None:
        figure()
        
    global gca
    chart = chartpanel.getChart()
    gca = __get_axes(chart, plot_number)
    chart.setCurrentPlot(plot_number - 1)
    
    return plot
    
def __create_axes(*args, **kwargs):
    """
    Create an axes.
    
    :param position: (*list*) Optional, axes position specified by *position=* [left, bottom, width
        height] in normalized (0, 1) units. Default is [0.13, 0.11, 0.775, 0.815].
    :param outerposition: (*list*) Optional, axes size and location, including labels and margin.
    
    :returns: The axes.
    """        
    if len(args) > 0:
        position = args[0]
    else:
        position = kwargs.pop('position', None)    
    outerposition = kwargs.pop('outerposition', None)
    axestype = kwargs.pop('axestype', 'cartesian')
    polar = kwargs.pop('polar', False)
    if polar:
        axestype = 'polar'
    if axestype == 'polar':
        ax = PolarAxes()
    elif axestype == 'map':
        ax = MapAxes()
    elif axestype == '3d':
        ax = Axes3D()
    else:
        ax = Axes()
    if position is None:
        position = [0.13, 0.11, 0.775, 0.815]
        ax.active_outerposition(True)
    else:        
        ax.active_outerposition(False)        
    ax.set_position(position)   
    if not outerposition is None:
        ax.set_outerposition(outerposition)
        ax.active_outerposition(True)
    
    return ax
    
def __set_axes_common(ax, *args, **kwargs):
    if len(args) > 0:
        position = args[0]
    else:
        position = kwargs.pop('position', None)    
    outerposition = kwargs.pop('outerposition', None)
    if position is None:
        position = [0.13, 0.11, 0.775, 0.815]
        ax.active_outerposition(True)
    else:        
        ax.active_outerposition(False)        
    ax.set_position(position)   
    if not outerposition is None:
        ax.set_outerposition(outerposition)
        ax.active_outerposition(True)
    units = kwargs.pop('units', None)
    if not units is None:
        ax.axes.setUnits(units)
    
def __set_axes(ax, **kwargs):
    """
    Set an axes.

    :param aspect: (*string*) ['equal' | 'auto'] or a number. If a number the ratio of x-unit/y-unit in screen-space.
        Default is 'auto'.
    :param bgcolor: (*Color*) Optional, axes background color.
    :param axis: (*boolean*) Optional, set all axis visible or not. Default is ``True`` .
    :param bottomaxis: (*boolean*) Optional, set bottom axis visible or not. Default is ``True`` .
    :param leftaxis: (*boolean*) Optional, set left axis visible or not. Default is ``True`` .
    :param topaxis: (*boolean*) Optional, set top axis visible or not. Default is ``True`` .
    :param rightaxis: (*boolean*) Optional, set right axis visible or not. Default is ``True`` .
    :param xaxistype: (*string*) Optional, set x axis type as 'normal', 'lon', 'lat' or 'time'.
    :param xreverse: (*boolean*) Optional, set x axis reverse or not. Default is ``False`` .
    :param yreverse: (*boolean*) Optional, set yaxis reverse or not. Default is ``False`` .
    
    :returns: The axes.
    """        
    aspect = kwargs.pop('aspect', 'auto')
    axis = kwargs.pop('axis', True)
    b_axis = ax.get_axis(Location.BOTTOM)
    l_axis = ax.get_axis(Location.LEFT)
    t_axis = ax.get_axis(Location.TOP)
    r_axis = ax.get_axis(Location.RIGHT)
    if axis:
        bottomaxis = kwargs.pop('bottomaxis', True)
        leftaxis = kwargs.pop('leftaxis', True)
        topaxis = kwargs.pop('topaxis', True)
        rightaxis = kwargs.pop('rightaxis', True)
    else:
        bottomaxis = False
        leftaxis = False
        topaxis = False
        rightaxis = False
    xaxisloc = kwargs.pop('xaxislocation', 'bottom')    #or 'top'
    yaxisloc = kwargs.pop('yaxislocation', 'left')    #or 'right'
    xdir = kwargs.pop('xdir', 'normal')    #or 'reverse'
    ydir = kwargs.pop('ydir', 'normal')    #or 'reverse'
    xscale = kwargs.pop('xscale', 'linear')    #or 'log'
    yscale = kwargs.pop('yscale', 'linear')    #or 'log'
    xtick = kwargs.pop('xtick', [])
    ytick = kwargs.pop('ytick', [])
    xtickmode = kwargs.pop('xtickmode', 'auto')    #or 'manual'
    ytickmode = kwargs.pop('ytickmode', 'auto')    #or 'manual'
    xreverse = kwargs.pop('xreverse', False)
    yreverse = kwargs.pop('yreverse', False)
    xaxistype = kwargs.pop('xaxistype', None)
    bgcobj = kwargs.pop('bgcolor', None)        
    
    if aspect == 'equal':
        ax.axes.setAutoAspect(False)
    else:
        if isinstance(aspect, (int, float)):
            ax.axes.setAspect(aspect)
            ax.axes.setAutoAspect(False)
    if bottomaxis == False:
        b_axis.setVisible(False)
    if leftaxis == False:
        l_axis.setVisible(False)
    if topaxis == False:
        t_axis.setVisible(False)
    if rightaxis == False:
        r_axis.setVisible(False)
    if xreverse:
        b_axis.setInverse(True)
        t_axis.setInverse(True)
    if yreverse:
        l_axis.setInverse(True)
        r_axis.setInverse(True)        
    if not xaxistype is None:
        __setXAxisType(ax.axes, xaxistype)
    if not bgcobj is None:
        bgcolor = __getcolor(bgcobj)
        ax.axes.setDrawBackground(True)
        ax.axes.setBackground(bgcolor)
    tickline = kwargs.pop('tickline', True)
    b_axis.setDrawTickLine(tickline)
    t_axis.setDrawTickLine(tickline)
    l_axis.setDrawTickLine(tickline)
    r_axis.setDrawTickLine(tickline)
    tickfontname = kwargs.pop('tickfontname', 'Arial')
    tickfontsize = kwargs.pop('tickfontsize', 14)
    tickbold = kwargs.pop('tickbold', False)
    if tickbold:
        font = Font(tickfontname, Font.BOLD, tickfontsize)
    else:
        font = Font(tickfontname, Font.PLAIN, tickfontsize)
    ax.axes.setAxisLabelFont(font)
    
def __create_axesm(*args, **kwargs):  
    """
    Create an map axes.
    
    :param projinfo: (*ProjectionInfo*) Optional, map projection, default is longlat projection.
    :param position: (*list*) Optional, axes position specified by *position=* [left, bottom, width
        height] in normalized (0, 1) units. Default is [0.13, 0.11, 0.775, 0.815].
    
    :returns: The map axes.
    """       
    ax = MapAxes(**kwargs)
    if len(args) > 0:
        position = args[0]
    else:
        position = kwargs.pop('position', None)        
    if position is None:
       position = [0.13, 0.11, 0.775, 0.815]
    ax.set_position(position)    
    return ax
    
def __set_axesm(ax, **kwargs):  
    """
    Create an map axes.
    
    :param bgcolor: (*Color*) Optional, axes background color.
    :param axis: (*boolean*) Optional, set all axis visible or not. Default is ``True`` .
    :param bottomaxis: (*boolean*) Optional, set bottom axis visible or not. Default is ``True`` .
    :param leftaxis: (*boolean*) Optional, set left axis visible or not. Default is ``True`` .
    :param topaxis: (*boolean*) Optional, set top axis visible or not. Default is ``True`` .
    :param rightaxis: (*boolean*) Optional, set right axis visible or not. Default is ``True`` .
    :param xyscale: (*int*) Optional, set scale of x and y axis, default is 1. It is only
        valid in longlat projection.
    :param gridlabel: (*boolean*) Optional, set axis tick labels visible or not. Default is ``True`` .
    :param gridline: (*boolean*) Optional, set grid line visible or not. Default is ``False`` .
    :param griddx: (*float*) Optional, set x grid line interval. Default is 10 degree.
    :param griddy: (*float*) Optional, set y grid line interval. Default is 10 degree.
    :param frameon: (*boolean*) Optional, set frame visible or not. Default is ``False`` for lon/lat
        projection, ortherwise is ``True``.
    :param tickfontname: (*string*) Optional, set axis tick labels font name. Default is ``Arial`` .
    :param tickfontsize: (*int*) Optional, set axis tick labels font size. Default is 14.
    :param tickbold: (*boolean*) Optional, set axis tick labels font bold or not. Default is ``False`` .
    
    :returns: The map axes.
    """       
    axis = kwargs.pop('axis', True)
    if axis:
        bottomaxis = kwargs.pop('bottomaxis', True)
        leftaxis = kwargs.pop('leftaxis', True)
        topaxis = kwargs.pop('topaxis', True)
        rightaxis = kwargs.pop('rightaxis', True)
    else:
        bottomaxis = False
        leftaxis = False
        topaxis = False
        rightaxis = False
    xaxisloc = kwargs.pop('xaxislocation', 'bottom')    #or 'top'
    yaxisloc = kwargs.pop('yaxislocation', 'left')    #or 'right'
    xdir = kwargs.pop('xdir', 'normal')    #or 'reverse'
    ydir = kwargs.pop('ydir', 'normal')    #or 'reverse'
    xscale = kwargs.pop('xscale', 'linear')    #or 'log'
    yscale = kwargs.pop('yscale', 'linear')    #or 'log'
    xtick = kwargs.pop('xtick', [])
    ytick = kwargs.pop('ytick', [])
    xtickmode = kwargs.pop('xtickmode', 'auto')    #or 'manual'
    ytickmode = kwargs.pop('ytickmode', 'auto')    #or 'manual'  
        
    gridlabel = kwargs.pop('gridlabel', True)
    gridline = kwargs.pop('gridline', False)
    griddx = kwargs.pop('griddx', 10)
    griddy = kwargs.pop('griddy', 10)
    if ax.axes.getProjInfo().isLonLat():
        frameon = kwargs.pop('frameon', False)
    else:
        frameon = kwargs.pop('frameon', True)
    axison = kwargs.pop('axison', None)
    bgcobj = kwargs.pop('bgcolor', None)
    xyscale = kwargs.pop('xyscale', 1)     
    tickfontname = kwargs.pop('tickfontname', 'Arial')
    tickfontsize = kwargs.pop('tickfontsize', 14)
    tickbold = kwargs.pop('tickbold', False)
    if tickbold:
        font = Font(tickfontname, Font.BOLD, tickfontsize)
    else:
        font = Font(tickfontname, Font.PLAIN, tickfontsize)
        
    mapview = ax.axes.getMapView()
    mapview.setXYScaleFactor(xyscale)
    ax.axes.setAxisLabelFont(font)
    if not axison is None:
        ax.axes.setAxisOn(axison)
    else:
        if bottomaxis == False:
            ax.axes.getAxis(Location.BOTTOM).setVisible(False)
        if leftaxis == False:
            ax.axes.getAxis(Location.LEFT).setVisible(False)
        if topaxis == False:
            ax.axes.getAxis(Location.TOP).setVisible(False)
        if rightaxis == False:
            ax.axes.getAxis(Location.RIGHT).setVisible(False)
    mapframe = ax.axes.getMapFrame()
    mapframe.setDrawGridLabel(gridlabel)
    mapframe.setDrawGridTickLine(gridlabel)
    mapframe.setDrawGridLine(gridline)
    mapframe.setGridXDelt(griddx)
    mapframe.setGridYDelt(griddy)
    ax.axes.setDrawNeatLine(frameon)
    if not bgcobj is None:
        bgcolor = __getcolor(bgcobj)
        ax.axes.setDrawBackground(True)
        ax.axes.setBackground(bgcolor)
 
    return ax

def __create_axes3d(*args, **kwargs):
    """
    Create an axes.
    
    :param position: (*list*) Optional, axes position specified by *position=* [left, bottom, width
        height] in normalized (0, 1) units. Default is [0.13, 0.11, 0.775, 0.815].
    :param outerposition: (*list*) Optional, axes size and location, including labels and margin.
    
    :returns: The axes.
    """        
    if len(args) > 0:
        position = args[0]
    else:
        position = kwargs.pop('position', None)    
    outerposition = kwargs.pop('outerposition', None)
    ax = Axes3D(**kwargs)
    if position is None:
        position = [0.13, 0.11, 0.71, 0.815]
        ax.active_outerposition(True)
    else:        
        ax.active_outerposition(False)        
    ax.set_position(position)   
    if not outerposition is None:
        ax.set_outerposition(outerposition)
        ax.active_outerposition(True)
    
    return ax
    
def __set_axes3d(ax, **kwargs):
    """
    Set an axes.

    :param aspect: (*string*) ['equal' | 'auto'] or a number. If a number the ratio of x-unit/y-unit in screen-space.
        Default is 'auto'.
    :param bgcolor: (*Color*) Optional, axes background color.
    :param axis: (*boolean*) Optional, set all axis visible or not. Default is ``True`` .
    :param bottomaxis: (*boolean*) Optional, set bottom axis visible or not. Default is ``True`` .
    :param leftaxis: (*boolean*) Optional, set left axis visible or not. Default is ``True`` .
    :param topaxis: (*boolean*) Optional, set top axis visible or not. Default is ``True`` .
    :param rightaxis: (*boolean*) Optional, set right axis visible or not. Default is ``True`` .
    :param xaxistype: (*string*) Optional, set x axis type as 'normal', 'lon', 'lat' or 'time'.
    :param xreverse: (*boolean*) Optional, set x axis reverse or not. Default is ``False`` .
    :param yreverse: (*boolean*) Optional, set yaxis reverse or not. Default is ``False`` .
    
    :returns: The axes.
    """        
    return None
    
def __get_axes(chart, idx):
    ax = chart.getPlot(idx)
    if isinstance(ax, Plot2D):
        ax = Axes(ax)
    elif isinstance(ax, MapPlot):
        ax = MapAxes(ax)
    elif isinstance(ax, PolarAxes):
        ax = PolarAxes(ax)
    elif isinstance(ax, Plot3D):
        ax = Plot3D(ax)
    return ax
    
def axes(*args, **kwargs):
    """
    Add an axes to the figure.
    
    :param position: (*list*) Optional, axes position specified by *position=* [left, bottom, width
        height] in normalized (0, 1) units. Default is [0.13, 0.11, 0.775, 0.815].
    :param outerposition: (*list*) Optional, axes size and location, including labels and margin.
    :param aspect: (*string*) ['equal' | 'auto'] or a number. If a number the ratio of x-unit/y-unit in screen-space.
        Default is 'auto'.
    :param bgcolor: (*Color*) Optional, axes background color.
    :param axis: (*boolean*) Optional, set all axis visible or not. Default is ``True`` .
    :param bottomaxis: (*boolean*) Optional, set bottom axis visible or not. Default is ``True`` .
    :param leftaxis: (*boolean*) Optional, set left axis visible or not. Default is ``True`` .
    :param topaxis: (*boolean*) Optional, set top axis visible or not. Default is ``True`` .
    :param rightaxis: (*boolean*) Optional, set right axis visible or not. Default is ``True`` .
    :param xaxistype: (*string*) Optional, set x axis type as 'normal', 'lon', 'lat' or 'time'.
    :param xreverse: (*boolean*) Optional, set x axis reverse or not. Default is ``False`` .
    :param yreverse: (*boolean*) Optional, set yaxis reverse or not. Default is ``False`` .
    
    :returns: The axes.
    """
    global gca    
               
    axestype = kwargs.pop('axestype', 'cartesian')
    polar = kwargs.pop('polar', False)
    if polar:
        axestype = 'polar'
    if axestype == 'polar':
        ax = PolarAxes()
        __set_axes(ax, **kwargs)
    elif axestype == 'map':
        ax = MapAxes(**kwargs)
        __set_axesm(ax, **kwargs)
    elif axestype == '3d':
        ax = Axes3D(**kwargs)
        position = kwargs.pop('position', None)
        if position is None:
            kwargs['position'] = [0.13, 0.11, 0.71, 0.815]
        __set_axes3d(ax, **kwargs)
    else:
        ax = Axes()
        __set_axes(ax, **kwargs)
    __set_axes_common(ax, *args, **kwargs)
        
    #ax = __create_axes(*args, **kwargs)    
    
    if chartpanel is None:
        figure()
    chart = chartpanel.getChart()
    newaxes = kwargs.pop('newaxes', True)
    if not newaxes and gca is None:
        newaxes = True
    if newaxes:
        chart.addPlot(ax.axes)
    else:
        chart.setCurrentPlot(chart.getPlotIndex(gca.axes))
        if gca.axes.isSubPlot:
            ax.axes.isSubPlot = True
            position = kwargs.pop('position', None)
            if position is None:
                ax.set_position(gca.get_position())  
        chart.setCurrentPlot(ax.axes)
    gca = ax
    return ax

def axesm(*args, **kwargs):  
    """
    Add an map axes to the figure.
    
    :param projinfo: (*ProjectionInfo*) Optional, map projection, default is longlat projection.
    :param position: (*list*) Optional, axes position specified by *position=* [left, bottom, width
        height] in normalized (0, 1) units. Default is [0.13, 0.11, 0.775, 0.815].
    :param bgcolor: (*Color*) Optional, axes background color.
    :param axis: (*boolean*) Optional, set all axis visible or not. Default is ``True`` .
    :param bottomaxis: (*boolean*) Optional, set bottom axis visible or not. Default is ``True`` .
    :param leftaxis: (*boolean*) Optional, set left axis visible or not. Default is ``True`` .
    :param topaxis: (*boolean*) Optional, set top axis visible or not. Default is ``True`` .
    :param rightaxis: (*boolean*) Optional, set right axis visible or not. Default is ``True`` .
    :param xyscale: (*int*) Optional, set scale of x and y axis, default is 1. It is only
        valid in longlat projection.
    :param gridlabel: (*boolean*) Optional, set axis tick labels visible or not. Default is ``True`` .
    :param gridline: (*boolean*) Optional, set grid line visible or not. Default is ``False`` .
    :param griddx: (*float*) Optional, set x grid line interval. Default is 10 degree.
    :param griddy: (*float*) Optional, set y grid line interval. Default is 10 degree.
    :param frameon: (*boolean*) Optional, set frame visible or not. Default is ``False`` for lon/lat
        projection, ortherwise is ``True``.
    :param tickfontname: (*string*) Optional, set axis tick labels font name. Default is ``Arial`` .
    :param tickfontsize: (*int*) Optional, set axis tick labels font size. Default is 14.
    :param tickbold: (*boolean*) Optional, set axis tick labels font bold or not. Default is ``False`` .
    
    :returns: The map axes.
    """
    kwargs['axestype'] = 'map'
    return axes(*args, **kwargs)
    
def axes3d(*args, **kwargs):
    """
    Add an axes to the figure.
    
    :param position: (*list*) Optional, axes position specified by *position=* [left, bottom, width
        height] in normalized (0, 1) units. Default is [0.13, 0.11, 0.775, 0.815].
    :param outerposition: (*list*) Optional, axes size and location, including labels and margin.    
    
    :returns: The axes.
    """
    kwargs['axestype'] = '3d'
    return axes(*args, **kwargs)
    
def twinx(ax):
    """
    Make a second axes that shares the x-axis. The new axes will overlay *ax*. The ticks 
    for *ax2* will be placed on the right, and the *ax2* instance is returned.
    
    :param ax: Existing axes.
    
    :returns: The second axes
    """
    ax.axes.getAxis(Location.RIGHT).setVisible(False)
    ax.axes.setSameShrink(True)
    plot = Axes()
    plot.axes.setSameShrink(True)
    plot.axes.setPosition(ax.get_position())
    plot.axes.getAxis(Location.BOTTOM).setVisible(False)
    plot.axes.getAxis(Location.LEFT).setVisible(False)
    plot.axes.getAxis(Location.TOP).setVisible(False)
    axis = plot.axes.getAxis(Location.RIGHT)
    axis.setDrawTickLabel(True)
    axis.setDrawLabel(True)
    chartpanel.getChart().addPlot(plot.axes)
    global gca
    gca = plot
    return plot

def xaxis(ax=None, **kwargs):
    """
    Set x axis of the axes.
    
    :param ax: The axes.
    :param color: (*Color*) Color of the x axis. Default is 'black'.
    :param shift: (*int) X axis shif along x direction. Units is pixel. Default is 0.
    """
    if ax is None:
        ax = gca
    visible = kwargs.pop('visible', True)
    shift = kwargs.pop('shift', 0)
    color = kwargs.pop('color', 'black')
    c = __getcolor(color)
    tickline = kwargs.pop('tickline', True)
    tickline = kwargs.pop('tickvisible', tickline)
    ticklabel = kwargs.pop('ticklabel', None)
    minortick = kwargs.pop('minortick', False)
    tickin = kwargs.pop('tickin', True)
    axistype = kwargs.pop('axistype', None)
    timetickformat = kwargs.pop('timetickformat', None)
    if not axistype is None:
        if timetickformat is None:
            __setXAxisType(ax.axes, axistype)
        else:
            __setXAxisType(ax.axes, axistype, timetickformat)
        #ax.updateDrawExtent()
        ax.axes.setAutoExtent()
    tickfontname = kwargs.pop('tickfontname', 'Arial')
    tickfontsize = kwargs.pop('tickfontsize', 14)
    tickbold = kwargs.pop('tickbold', False)
    if tickbold:
        font = Font(tickfontname, Font.BOLD, tickfontsize)
    else:
        font = Font(tickfontname, Font.PLAIN, tickfontsize)
    location = kwargs.pop('location', 'both')
    if location == 'top':
        locs = [Location.TOP]
    elif location == 'bottom':
        locs = [Location.BOTTOM]
    else:
        locs = [Location.BOTTOM, Location.TOP]
    for loc in locs:    
        axis = ax.axes.getAxis(loc)
        axis.setVisible(visible)
        axis.setShift(shift)
        axis.setColor_All(c)
        axis.setDrawTickLine(tickline)
        if not ticklabel is None:
            axis.setDrawTickLabel(ticklabel)
        axis.setMinorTickVisible(minortick)
        axis.setInsideTick(tickin)
        axis.setTickLabelFont(font)
    draw_if_interactive()
    
def yaxis(ax=None, **kwargs):
    """
    Set y axis of the axes.
    
    :param ax: The axes.
    :param color: (*Color*) Color of the y axis. Default is 'black'.
    :param shift: (*int) Y axis shif along x direction. Units is pixel. Default is 0.
    """
    if ax is None:
        ax = gca
    visible = kwargs.pop('visible', None)
    shift = kwargs.pop('shift', 0)
    color = kwargs.pop('color', 'black')
    c = __getcolor(color)
    tickline = kwargs.pop('tickline', True)
    tickline = kwargs.pop('tickvisible', tickline)
    ticklabel = kwargs.pop('ticklabel', None)
    minortick = kwargs.pop('minortick', False)
    tickin = kwargs.pop('tickin', True)
    axistype = kwargs.pop('axistype', None)
    timetickformat = kwargs.pop('timetickformat', None)
    if not axistype is None:
        if timetickformat is None:
            __setYAxisType(ax.axes, axistype)
        else:
            __setYAxisType(ax.axes, axistype, timetickformat)
        ax.axes.updateDrawExtent()
    tickfontname = kwargs.pop('tickfontname', 'Arial')
    tickfontsize = kwargs.pop('tickfontsize', 14)
    tickbold = kwargs.pop('tickbold', False)
    if tickbold:
        font = Font(tickfontname, Font.BOLD, tickfontsize)
    else:
        font = Font(tickfontname, Font.PLAIN, tickfontsize)
    location = kwargs.pop('location', 'both')
    if location == 'left':
        locs = [Location.LEFT]
    elif location == 'right':
        locs = [Location.RIGHT]
    else:
        locs = [Location.LEFT, Location.RIGHT]
    for loc in locs:
        axis = ax.axes.getAxis(loc)
        if not visible is None:
            axis.setVisible(visible)
        if axis.isVisible():
            axis.setShift(shift)
            axis.setColor_All(c)
            axis.setDrawTickLine(tickline)
            if not ticklabel is None:
                axis.setDrawTickLabel(ticklabel)
            axis.setMinorTickVisible(minortick)
            axis.setInsideTick(tickin)
            axis.setTickLabelFont(font)
    draw_if_interactive()
    
def box(ax=None, on=None):
    """
    Display exes outline or not.
    
    :param ax: The axes. Current axes is used if ax is None.
    :param on: (*boolean*) Box on or off. If on is None, toggle state.
    """
    if ax is None:
        ax = gca
    locs_all = [Location.LEFT, Location.BOTTOM, Location.TOP, Location.RIGHT]
    locs = []
    for loc in locs_all:
        if not ax.axes.getAxis(loc).isDrawTickLabel():
            locs.append(loc)
    for loc in locs:
        axis = ax.axes.getAxis(loc)
        if on is None:
            axis.setVisible(not axis.isVisible())
        else:
            axis.setVisible(on)
    draw_if_interactive()
    
def antialias(b=None):
    """
    Set figure antialias or not.
    
    :param b: (*boolean*) Set figure antialias or not. Default is ``None``, means the opposite with 
        current status.
    """
    if chartpanel is None:
        figure()
    
    if b is None:
        b = not chartpanel.getChart().isAntiAlias()
    chartpanel.getChart().setAntiAlias(b)
    draw_if_interactive()
    
def savefig(fname, width=None, height=None, dpi=None, sleep=None):
    """
    Save the current figure.
    
    :param fname: (*string*) A string containing a path to a filename. The output format
        is deduced from the extention of the filename. Supported format: 'png', 'bmp',
        'jpg', 'eps' and 'pdf'.
    :param width: (*int*) Optional, width of the output figure with pixel units. Default
        is None, the output figure size is same as *figures* window.
    :param height: (*int*) Optional, height of the output figure with pixel units. Default
        is None, the output figure size is same as *figures* window.
    :param sleep: (*int*) Sleep seconds. For web map tiles loading.
    """
    #if (not width is None) and (not height is None):
    #    chartpanel.setSize(width, height)
    #chartpanel.paintGraphics()
    if dpi != None:
        if (not width is None) and (not height is None):
            chartpanel.saveImage(fname, dpi, width, height, sleep)
        else:
            chartpanel.saveImage(fname, dpi, sleep)
    else:
        if (not width is None) and (not height is None):
            chartpanel.saveImage(fname, width, height, sleep)
        else:
            chartpanel.saveImage(fname, sleep)  
        
def savefig_jpeg(fname, width=None, height=None, dpi=None):
    """
    Save the current figure as a jpeg file.
    
    :param fname: (*string*) A string containing a path to a filename. The output format
        is deduced from the extention of the filename. Supported format: 'jpg'.
    :param width: (*int*) Optional, width of the output figure with pixel units. Default
        is None, the output figure size is same as *figures* window.
    :param height: (*int*) Optional, height of the output figure with pixel units. Default
        is None, the output figure size is same as *figures* window.
    """
    #if (not width is None) and (not height is None):
    #    chartpanel.setSize(width, height)
    #chartpanel.paintGraphics()
    if not dpi is None:
        if (not width is None) and (not height is None):
            chartpanel.saveImage_Jpeg(fname, width, height, dpi)
        else:
            chartpanel.saveImage_Jpeg(fname, dpi)
    else:
        if (not width is None) and (not height is None):
            chartpanel.saveImage(fname, width, height)
        else:
            chartpanel.saveImage(fname)  

# Clear current axes
def cla():
    '''
    Clear current axes.
    '''
    global gca
    if not gca is None:
        if not chartpanel is None:
            chart = chartpanel.getChart()
            if not chart is None:
                chartpanel.getChart().removePlot(gca.axes)
        gca = None
        draw_if_interactive()

# Clear current figure    
def clf():
    '''
    Clear current figure.
    '''
    if chartpanel is None:
        return
    
    if chartpanel.getChart() is None:
        return
    
    chartpanel.getChart().setTitle(None)
    chartpanel.getChart().clearPlots()
    chartpanel.getChart().clearTexts()
    global gca
    gca = None
    draw_if_interactive()

# Clear last layer    
def cll():
    '''
    Clear last added layer or plot object.
    '''
    if not gca is None:
        if isinstance(gca, Axes):
            gca.axes.removeLastGraphic()
            gca.axes.setAutoExtent()
        elif isinstance(gca, MapAxes):
            gca.axes.removeLastLayer()
        draw_if_interactive()
        
def clc():
    '''
    Clear command window.
    '''
    if not migl.milapp is None:
        console = migl.milapp.getConsoleDockable().getConsole()
        console.getTextPane().setText('')

def __getplotstyle(style, caption, **kwargs):    
    linewidth = kwargs.pop('linewidth', 1.0)
    if style is None:
        color = kwargs.pop('color', 'red')
        c = __getcolor(color)
    else:
        c = __getcolor(style)
    pointStyle = __getpointstyle(style)
    lineStyle = __getlinestyle(style)
    if not pointStyle is None:
        fill = kwargs.pop('fill', True)        
        if lineStyle is None:           
            pb = PointBreak()
            pb.setCaption(caption)
            if '.' in style:
                pb.setSize(4)
                pb.setDrawOutline(False)
            else:
                pb.setSize(8)
            pb.setStyle(pointStyle)
            pb.setDrawFill(fill)
            if not c is None:
                pb.setColor(c)      
            edgecolor = kwargs.pop('edgecolor', pb.getColor())
            edgecolor = __getcolor(edgecolor)
            pb.setOutlineColor(edgecolor)
            return pb
        else:
            plb = PolylineBreak()
            plb.setCaption(caption)
            plb.setSize(linewidth)
            plb.setStyle(lineStyle)
            plb.setDrawSymbol(True)
            plb.setSymbolStyle(pointStyle)
            plb.setFillSymbol(fill)
            interval = kwargs.pop('markerinterval', 1)
            plb.setSymbolInterval(interval)
            if not c is None:
                plb.setColor(c)
            makercolor = kwargs.pop('makercolor', plb.getColor())
            makercolor = __getcolor(makercolor)
            plb.setSymbolColor(c)
            makerfillcolor = kwargs.pop('makerfillcolor', makercolor)
            makerfillcolor = __getcolor(makerfillcolor)
            plb.setSymbolFillColor(makerfillcolor)
            return plb
    else:
        plb = PolylineBreak()
        plb.setCaption(caption)
        plb.setSize(linewidth)
        if not c is None:
            plb.setColor(c)
        if not lineStyle is None:
            plb.setStyle(lineStyle)
        return plb
        
def __setplotstyle(plot, idx, style, n, **kwargs):    
    linewidth = kwargs.pop('linewidth', 1.0)
    color = kwargs.pop('color', 'red')
    c = __getcolor(color)
    #print 'Line width: ' + str(linewidth)
    caption = plot.getLegendBreak(idx).getCaption()
    if style is None:
        plot.setChartPlotMethod(ChartPlotMethod.LINE)
        plb = PolylineBreak()
        plb.setCaption(caption)
        plb.setSize(linewidth)
        if not c is None:
            plb.setColor(c)
        plot.setLegendBreak(idx, plb)
        return
        
    c = __getcolor(style)
    pointStyle = __getpointstyle(style)
    lineStyle = __getlinestyle(style)
    if not pointStyle is None:
        if lineStyle is None:
            #plot.setChartPlotMethod(ChartPlotMethod.POINT)            
            pb = PointBreak()
            pb.setCaption(caption)
            if '.' in style:
                pb.setSize(4)
                pb.setDrawOutline(False)
            else:
                pb.setSize(8)
            pb.setDrawOutline(False)
            pb.setStyle(pointStyle)
            if not c is None:
                pb.setColor(c)
            plot.setLegendBreak(idx, pb)
            return pb
        else:
            plot.setChartPlotMethod(ChartPlotMethod.LINE_POINT)
            plb = PolylineBreak()
            plb.setCaption(caption)
            plb.setSize(linewidth)
            plb.setStyle(lineStyle)
            plb.setDrawSymbol(True)
            plb.setSymbolStyle(pointStyle)
            plb.setSymbolInterval(__getsymbolinterval(n))
            plb.setFillSymbol(True)
            if not c is None:
                plb.setColor(c)
                plb.setSymbolColor(c)
                plb.setSymbolFillColor(c)
            plot.setLegendBreak(idx, plb)
            return plb
    else:
        plot.setChartPlotMethod(ChartPlotMethod.LINE)
        plb = PolylineBreak()
        plb.setCaption(caption)
        plb.setSize(linewidth)
        if not c is None:
            plb.setColor(c)
        if not lineStyle is None:
            plb.setStyle(lineStyle)
        plot.setLegendBreak(idx, plb)
        return plb
    
def __getlinestyle(style):
    if style is None:
        return None
        
    lineStyle = None
    if '--' in style:
        lineStyle = LineStyles.Dash
    elif ':' in style:
        lineStyle = LineStyles.Dot
    elif '-.' in style:
        lineStyle = LineStyles.DashDot
    elif '-' in style:
        lineStyle = LineStyles.Solid
    
    return lineStyle
    
def __getpointstyle(style):
    if style is None:
        return None
        
    pointStyle = None
    if 'o' in style:
        pointStyle = PointStyle.Circle
    elif '.' in style:
        pointStyle = PointStyle.Circle
    elif 'D' in style:
        pointStyle = PointStyle.Diamond
    elif '+' in style:
        pointStyle = PointStyle.Plus
    elif 'm' in style:
        pointStyle = PointStyle.Minus
    elif 's' in style:
        pointStyle = PointStyle.Square
    elif 'S' in style:
        pointStyle = PointStyle.Star
    elif '*' in style:
        pointStyle = PointStyle.StarLines
    elif '^' in style:
        pointStyle = PointStyle.UpTriangle
    elif 'x' in style:
        pointStyle = PointStyle.XCross
    
    return pointStyle
    
def __getcolor(style, alpha=None):
    if style is None:
        return None
        
    if isinstance(style, Color):
        c = style
        if not alpha is None:
            alpha = (int)(alpha * 255)
            c = Color(c.getRed(), c.getGreen(), c.getBlue(), alpha)
        return c
        
    c = Color.black
    if isinstance(style, str):
        if style == 'red':
            c = Color.red
        elif style == 'black':
            c = Color.black
        elif style == 'blue':
            c = Color.blue
        elif style == 'green':
            c = Color.green
        elif style == 'white':
            c = Color.white
        elif style == 'yellow':
            c = Color.yellow
        elif style == 'gray':
            c = Color.gray
        elif style == 'lightgray':
            c = Color.lightGray
        else:
            if 'r' in style:
                c = Color.red
            elif 'k' in style:
                c = Color.black
            elif 'b' in style:
                c = Color.blue
            elif 'g' in style:
                c = Color.green
            elif 'w' in style:
                c = Color.white
            elif 'c' in style:
                c = Color.cyan
            elif 'm' in style:
                c = Color.magenta
            elif 'y' in style:
                c = Color.yellow 
    elif isinstance(style, (tuple, list)):
        if len(style) == 3:
            c = Color(style[0], style[1], style[2])
        else:
            c = Color(style[0], style[1], style[2], style[3])
    
    if not alpha is None:
        alpha = (int)(alpha * 255)
        c = Color(c.getRed(), c.getGreen(), c.getBlue(), alpha)
    
    return c

def __getcolors(cs, alpha=None):
    colors = []
    if isinstance(cs, (tuple, list, MIArray)):
        if isinstance(cs[0], int):
            colors.append(__getcolor(cs, alpha))
        else:            
            for c in cs:
                colors.append(__getcolor(c, alpha))
    else:
        colors.append(__getcolor(cs, alpha))
    return colors
    
def __getcolors_value(v, n=None, cmap='matlab_jet'):
    min = v.min()
    max = v.max()
    cmap = __getcolormap(cmap=cmap)
    if n is None:
        cs = ColorUtil.createColors(cmap, min, max)
    else:
        cs = ColorUtil.createColors(cmap, min, max, n)
    colors = []
    for c in cs:
        colors.append(c)
    return colors
    
def __getsymbolinterval(n):
    i = 1
    v = 20
    if n < v:
        i = 1
    else:
        i = n / v
    
    return i

def __getfont(fontdic, **kwargs):
    basefont = kwargs.pop('basefont', None)
    if basefont is None:
        name = 'Arial'
        size = 14
        bold = False
        italic = False
    else:
        name = basefont.getName()
        size = basefont.getSize()
        bold = basefont.isBold()
        italic = basefont.isItalic()
    name = fontdic.pop('name', name)
    size = fontdic.pop('size', size)
    bold = fontdic.pop('bold', bold)
    italic = fontdic.pop('italic', italic)
    if bold:
        if italic:
            font = Font(name, Font.BOLD | Font.ITALIC, size)
        else:
            font = Font(name, Font.BOLD, size)
    else:
        if italic:
            font = Font(name, Font.ITALIC, size)
        else:
            font = Font(name, Font.PLAIN, size)
    return font
    
def __getfont_1(**kwargs):
    fontname = kwargs.pop('fontname', 'Arial')
    fontsize = kwargs.pop('fontsize', 14)
    bold = kwargs.pop('bold', False)
    if bold:
        font = Font(fontname, Font.BOLD, fontsize)
    else:
        font = Font(fontname, Font.PLAIN, fontsize)
    return font
    
def __gethatch(h):
    hatch = HatchStyle.NONE
    if h == '-' or h == 'horizontal':
        hatch = HatchStyle.HORIZONTAL
    elif h == '|' or h == 'vertical':
        hatch = HatchStyle.VERTICAL
    elif h == '\\' or h == 'forward_diagonal':
        hatch = HatchStyle.FORWARD_DIAGONAL
    elif h == '/' or h == 'backward_diagonal':
        hatch = HatchStyle.BACKWARD_DIAGONAL
    elif h == '+' or h == 'cross':
        hatch = HatchStyle.CROSS
    elif h == 'x' or h == 'diagonal_cross':
        hatch = HatchStyle.DIAGONAL_CROSS
    elif h == '.' or h == 'dot':
        hatch = HatchStyle.DOT    
    return hatch
    
def __setXAxisType(ax, axistype, timetickformat=None):
    if axistype == 'lon':
        b_axis = LonLatAxis(ax.getAxis(Location.BOTTOM))
        b_axis.setLabel('Longitude')
        b_axis.setLongitude(True)
        ax.setAxis(b_axis, Location.BOTTOM)
        t_axis = LonLatAxis(ax.getAxis(Location.TOP))
        t_axis.setLabel('Longitude')
        t_axis.setLongitude(True)
        ax.setAxis(t_axis, Location.TOP)
    elif axistype == 'lat':
        b_axis = LonLatAxis(ax.getAxis(Location.BOTTOM))
        b_axis.setLabel('Latitude')
        b_axis.setLongitude(False)
        ax.setAxis(b_axis, Location.BOTTOM)
        t_axis = LonLatAxis(ax.getAxis(Location.TOP))
        t_axis.setLabel('Latitude')
        t_axis.setLongitude(False)
        ax.setAxis(t_axis, Location.TOP)
    elif axistype == 'time':
        b_axis = TimeAxis(ax.getAxis(Location.BOTTOM))
        ax.setAxis(b_axis, Location.BOTTOM)
        t_axis = TimeAxis(ax.getAxis(Location.TOP))
        ax.setAxis(t_axis, Location.TOP)
        if not timetickformat is None:
            ax.getAxis(Location.BOTTOM).setTimeFormat(timetickformat)
            ax.getAxis(Location.TOP).setTimeFormat(timetickformat)
    elif axistype == 'log':
        b_axis = LogAxis(ax.getAxis(Location.BOTTOM))
        b_axis.setLabel('Log')
        b_axis.setMinorTickNum(10)
        ax.setAxis(b_axis, Location.BOTTOM)
        t_axis = LogAxis(ax.getAxis(Location.TOP))
        t_axis.setLabel('Log')
        t_axis.setMinorTickNum(10)
        ax.setAxis(t_axis, Location.TOP)        
                
def __setYAxisType(ax, axistype, timetickformat=None):
    if axistype == 'lon':
        b_axis = LonLatAxis(ax.getAxis(Location.LEFT))
        b_axis.setLabel('Longitude')
        b_axis.setLongitude(True)
        ax.setAxis(b_axis, Location.LEFT)
        t_axis = LonLatAxis(ax.getAxis(Location.RIGHT))
        t_axis.setLabel('Longitude')
        t_axis.setLongitude(True)
        ax.setAxis(t_axis, Location.RIGHT)
    elif axistype == 'lat':
        b_axis = LonLatAxis(ax.getAxis(Location.LEFT))
        b_axis.setLabel('Latitude')
        b_axis.setLongitude(False)
        ax.setAxis(b_axis, Location.LEFT)
        t_axis = LonLatAxis(ax.getAxis(Location.RIGHT))
        t_axis.setLabel('Latitude')
        t_axis.setLongitude(False)
        ax.setAxis(t_axis, Location.RIGHT)
    elif axistype == 'time':
        b_axis = TimeAxis(ax.getAxis(Location.LEFT))
        ax.setAxis(b_axis, Location.LEFT)
        t_axis = TimeAxis(ax.getAxis(Location.RIGHT))
        ax.setAxis(t_axis, Location.RIGHT)
        if not timetickformat is None:
            ax.getAxis(Location.LEFT).setTimeFormat(timetickformat)
            ax.getAxis(Location.RIGHT).setTimeFormat(timetickformat)
    elif axistype == 'log':
        l_axis = LogAxis(ax.getAxis(Location.LEFT))
        l_axis.setLabel('Log')
        l_axis.setMinorTickNum(10)
        ax.setAxis(l_axis, Location.LEFT)
        r_axis = LogAxis(ax.getAxis(Location.RIGHT))
        r_axis.setLabel('Log')
        r_axis.setMinorTickNum(10)
        ax.setAxis(r_axis, Location.RIGHT)

def title(title, fontname='Arial', fontsize=14, bold=True, color='black'):
    """
    Set a title of the current axes.
    
    :param title: (*string*) Title string.
    :param fontname: (*string*) Font name. Default is ``Arial`` .
    :param fontsize: (*int*) Font size. Default is ``14`` .
    :param bold: (*boolean*) Is bold font or not. Default is ``True`` .
    :param color: (*color*) Title string color. Default is ``black`` .    
    """
    if bold:
        font = Font(fontname, Font.BOLD, fontsize)
    else:
        font = Font(fontname, Font.PLAIN, fontsize)
    c = __getcolor(color)
    ctitile = ChartText(title, font)
    ctitile.setColor(c)
    gca.set_title(ctitile)
    draw_if_interactive()
    
def suptitle(title, fontname='Arial', fontsize=14, bold=True, color='black'):
    """
    Add a centered title to the figure.
    
    :param title: (*string*) Title string.
    :param fontname: (*string*) Font name. Default is ``Arial`` .
    :param fontsize: (*int*) Font size. Default is ``14`` .
    :param bold: (*boolean*) Is bold font or not. Default is ``True`` .
    :param color: (*color*) Title string color. Default is ``black`` .
    """
    if bold:
        font = Font(fontname, Font.BOLD, fontsize)
    else:
        font = Font(fontname, Font.PLAIN, fontsize)
    c = __getcolor(color)
    ctitile = ChartText(title, font)
    ctitile.setColor(c)
    chartpanel.getChart().setTitle(ctitile)
    draw_if_interactive()

def xlabel(label, fontname='Arial', fontsize=14, bold=False, color='black'):
    """
    Set the x axis label of the current axes.
    
    :param label: (*string*) Label string.
    :param fontname: (*string*) Font name. Default is ``Arial`` .
    :param fontsize: (*int*) Font size. Default is ``14`` .
    :param bold: (*boolean*) Is bold font or not. Default is ``True`` .
    :param color: (*color*) Label string color. Default is ``black`` .
    """
    if bold:
        font = Font(fontname, Font.BOLD, fontsize)
    else:
        font = Font(fontname, Font.PLAIN, fontsize)
    c = __getcolor(color)
    plot = gca
    axis = plot.axes.getXAxis()
    axis.setLabel(label)
    axis.setDrawLabel(True)
    axis.setLabelFont(font)
    axis.setLabelColor(c)
    draw_if_interactive()
    
def ylabel(label, fontname='Arial', fontsize=14, bold=False, color='black'):
    """
    Set the y axis label of the current axes.
    
    :param label: (*string*) Label string.
    :param fontname: (*string*) Font name. Default is ``Arial`` .
    :param fontsize: (*int*) Font size. Default is ``14`` .
    :param bold: (*boolean*) Is bold font or not. Default is ``True`` .
    :param color: (*color*) Label string color. Default is ``black`` .
    """
    if bold:
        font = Font(fontname, Font.BOLD, fontsize)
    else:
        font = Font(fontname, Font.PLAIN, fontsize)
    c = __getcolor(color)
    plot = gca
    axis = plot.axes.getYAxis()
    axis.setLabel(label)
    axis.setDrawLabel(True)
    axis.setLabelFont(font)
    axis.setLabelColor(c)
    if not isinstance(plot, Axes3D):
        axis_r = plot.axes.getAxis(Location.RIGHT)
        axis_r.setLabel(label)
        axis_r.setLabelFont(font)
        axis_r.setLabelColor(c)
    draw_if_interactive()
    
def zlabel(label, fontname='Arial', fontsize=14, bold=False, color='black'):
    """
    Set the z axis label of the current axes.
    
    :param label: (*string*) Label string.
    :param fontname: (*string*) Font name. Default is ``Arial`` .
    :param fontsize: (*int*) Font size. Default is ``14`` .
    :param bold: (*boolean*) Is bold font or not. Default is ``True`` .
    :param color: (*color*) Label string color. Default is ``black`` .
    """
    global gca
    if not isinstance(gca, Axes3D):
        return
        
    if bold:
        font = Font(fontname, Font.BOLD, fontsize)
    else:
        font = Font(fontname, Font.PLAIN, fontsize)
    c = __getcolor(color)    
    axis = gca.axes.getZAxis()
    axis.setLabel(label)
    axis.setDrawLabel(True)
    axis.setLabelFont(font)
    axis.setLabelColor(c)
    draw_if_interactive()
    
def xticks(*args, **kwargs):
    """
    Set the x-limits of the current tick locations and labels.
    
    :param locs: (*array_like*) Tick locations.
    :param labels: (*string list*) Tick labels.
    :param fontname: (*string*) Font name. Default is ``Arial`` .
    :param fontsize: (*int*) Font size. Default is ``14`` .
    :param bold: (*boolean*) Is bold font or not. Default is ``True`` .
    :param color: (*color*) Tick label string color. Default is ``black`` .
    :param rotation: (*float*) Tick label rotation angle. Default is 0.
    """
    axis = gca.axes.getXAxis()
    if isinstance(gca, Axes3D):
        axis_t = None
    else:
        axis_t = gca.axes.getAxis(Location.TOP)
    if len(args) > 0:
        locs = args[0]
        if isinstance(locs, (MIArray, DimArray)):
            locs = locs.aslist()
        if isinstance(locs[0], datetime.datetime):
            for i in range(len(locs)):
                locs[i] = miutil.date2num(locs[i])
        axis.setTickLocations(locs)
        if not axis_t is None:
            axis_t.setTickLocations(locs)
        args = args[1:]
    if len(args) > 0:
        labels = args[0]
        if isinstance(labels, (MIArray, DimArray)):
            labels = labels.aslist()
            axis.setTickLabels_Number(labels)
            if not axis_t is None:
                axis_t.setTickLabels_Number(labels)
        else:
            axis.setTickLabels(labels)
            if not axis_t is None:
                axis_t.setTickLabels(labels)
    fontname = kwargs.pop('fontname', axis.getTickLabelFont().getName())
    fontsize = kwargs.pop('fontsize', axis.getTickLabelFont().getSize())
    bold =kwargs.pop('bold', axis.getTickLabelFont().isBold())
    if bold:
        font = Font(fontname, Font.BOLD, fontsize)
    else:
        font = Font(fontname, Font.PLAIN, fontsize)
    color = kwargs.pop('color', 'k')
    c = __getcolor(color)
    angle = kwargs.pop('rotation', 0)
    if angle == 'vertical':
        angle = 90
    axis.setTickLabelFont(font)
    axis.setTickLabelColor(c)
    axis.setTickLabelAngle(angle)
    if not axis_t is None:
        axis_t.setTickLabelFont(font)
        axis_t.setTickLabelColor(c)
        axis_t.setTickLabelAngle(angle)
    draw_if_interactive()
    
def yticks(*args, **kwargs):
    """
    Set the y-limits of the current tick locations and labels.
    
    :param locs: (*array_like*) Tick locations.
    :param labels: (*string list*) Tick labels.
    :param fontname: (*string*) Font name. Default is ``Arial`` .
    :param fontsize: (*int*) Font size. Default is ``14`` .
    :param bold: (*boolean*) Is bold font or not. Default is ``True`` .
    :param color: (*color*) Tick label string color. Default is ``black`` .
    :param rotation: (*float*) Tick label rotation angle. Default is 0.
    """
    axis = gca.axes.getYAxis()
    if isinstance(gca, Axes3D):
        axis_r = None
    else:
        axis_r = gca.axes.getAxis(Location.RIGHT)
    if len(args) > 0:
        locs = args[0]
        if isinstance(locs, MIArray):
            locs = locs.aslist()
        if isinstance(locs[0], datetime.datetime):
            for i in range(len(locs)):
                locs[i] = miutil.date2num(locs[i])
        axis.setTickLocations(locs)
        if not axis_r is None:
            axis_r.setTickLocations(locs)
        args = args[1:]
    if len(args) > 0:
        labels = args[0]
        if isinstance(labels, (MIArray, DimArray)):
            labels = labels.aslist()
            axis.setTickLabels_Number(labels)
            if not axis_r is None:
                axis_r.setTickLabels_Number(labels)
        else:
            axis.setTickLabels(labels)
            if not axis_r is None:
                axis_r.setTickLabels(labels)
    fontname = kwargs.pop('fontname', axis.getTickLabelFont().getName())
    fontsize = kwargs.pop('fontsize', axis.getTickLabelFont().getSize())
    bold =kwargs.pop('bold', axis.getTickLabelFont().isBold())
    if bold:
        font = Font(fontname, Font.BOLD, fontsize)
    else:
        font = Font(fontname, Font.PLAIN, fontsize)
    color = kwargs.pop('color', 'k')
    c = __getcolor(color)
    axis.setTickLabelFont(font)
    axis.setTickLabelColor(c)
    if not axis_r is None:
        axis_r.setTickLabelFont(font)
        axis_r.setTickLabelColor(c)
    draw_if_interactive()
    
def zticks(*args, **kwargs):
    """
    Set the z-limits of the current tick locations and labels.
    
    :param locs: (*array_like*) Tick locations.
    :param labels: (*string list*) Tick labels.
    :param fontname: (*string*) Font name. Default is ``Arial`` .
    :param fontsize: (*int*) Font size. Default is ``14`` .
    :param bold: (*boolean*) Is bold font or not. Default is ``True`` .
    :param color: (*color*) Tick label string color. Default is ``black`` .
    :param rotation: (*float*) Tick label rotation angle. Default is 0.
    """
    if not isinstance(gca, Axes3D):
        return
        
    axis = gca.axes.getZAxis()
    if len(args) > 0:
        locs = args[0]
        if isinstance(locs, MIArray):
            locs = locs.aslist()
        if isinstance(locs[0], datetime.datetime):
            for i in range(len(locs)):
                locs[i] = miutil.date2num(locs[i])
        axis.setTickLocations(locs)
        args = args[1:]
    if len(args) > 0:
        labels = args[0]
        if isinstance(labels, (MIArray, DimArray)):
            labels = labels.aslist()
            axis.setTickLabels_Number(labels)
        else:
            axis.setTickLabels(labels)
    fontname = kwargs.pop('fontname', axis.getTickLabelFont().getName())
    fontsize = kwargs.pop('fontsize', axis.getTickLabelFont().getSize())
    bold =kwargs.pop('bold', axis.getTickLabelFont().isBold())
    if bold:
        font = Font(fontname, Font.BOLD, fontsize)
    else:
        font = Font(fontname, Font.PLAIN, fontsize)
    color = kwargs.pop('color', 'k')
    c = __getcolor(color)
    axis.setTickLabelFont(font)
    axis.setTickLabelColor(c)
    draw_if_interactive()
    
def text(x, y, s, **kwargs):
    """
    Add text to the axes. Add text in string *s* to axis at location *x* , *y* , data
    coordinates.
    
    :param x: (*float*) Data x coordinate.
    :param y: (*float*) Data y coordinate.
    :param s: (*string*) Text.
    :param fontname: (*string*) Font name. Default is ``Arial`` .
    :param fontsize: (*int*) Font size. Default is ``14`` .
    :param bold: (*boolean*) Is bold font or not. Default is ``False`` .
    :param color: (*color*) Tick label string color. Default is ``black`` .
    :param coordinates=['axes'|'figure'|'data'|'inches']: (*string*) Coordinate system and units for 
        *X, Y*. 'axes' and 'figure' are normalized coordinate system with 0,0 in the lower left and 
        1,1 in the upper right, 'data' are the axes data coordinates (Default value); 'inches' is 
        position in the figure in inches, with 0,0 at the lower left corner.
    """
    fontname = kwargs.pop('fontname', 'Arial')
    fontsize = kwargs.pop('fontsize', 14)
    bold = kwargs.pop('bold', False)
    color = kwargs.pop('color', 'black')
    if bold:
        font = Font(fontname, Font.BOLD, fontsize)
    else:
        font = Font(fontname, Font.PLAIN, fontsize)
    c = __getcolor(color)
    text = ChartText(s, font)
    text.setColor(c)
    text.setX(x)
    text.setY(y)
    bbox = kwargs.pop('bbox', None)
    if not bbox is None:
        fill = bbox.pop('fill', None)
        if not fill is None:
            text.setFill(fill)
        facecolor = bbox.pop('facecolor', None)
        if not facecolor is None:
            facecolor = __getcolor(facecolor)
            text.setFill(True)
            text.setBackground(facecolor)
        edge = bbox.pop('edge', None)
        if not edge is None:
            text.setDrawNeatline(edge)
        edgecolor = bbox.pop('edgecolor', None)
        if not edgecolor is None:
            edgecolor = __getcolor(edgecolor)
            text.setNeatlineColor(edgecolor)
            text.setDrawNeatline(True)
        linewidth = bbox.pop('linewidth', None)
        if not linewidth is None:
            text.setNeatlineSize(linewidth)
            text.setDrawNeatline(True)
        gap = bbox.pop('gap', None)
        if not gap is None:
            text.setGap(gap)
    coordinates = kwargs.pop('coordinates', 'data')
    text.setCoordinates(coordinates)
    if coordinates == 'figure':
        chartpanel.getChart().addText(text)
    else:
        gca.axes.addText(text)
    draw_if_interactive()
    
def axis(limits):
    """
    Sets the min and max of the x and y axes, with ``[xmin, xmax, ymin, ymax]`` .
    
    :param limits: (*list*) Min and max of the x and y axes.
    """
    if len(limits) == 4:
        xmin = limits[0]
        xmax = limits[1]
        ymin = limits[2]
        ymax = limits[3]
        extent = Extent(xmin, xmax, ymin, ymax)
        gca.axes.setDrawExtent(extent)
        gca.axes.setExtent(extent.clone())
        draw_if_interactive()
    else:
        print 'The limits parameter must be a list with 4 elements: xmin, xmax, ymin, ymax!'
        
def axism(limits=None):
    """
    Sets the min and max of the x and y map axes, with ``[xmin, xmax, ymin, ymax]`` .
    
    :param limits: (*list*) Min and max of the x and y map axes.
    """
    if limits is None:
        gca.axes.setDrawExtent(gca.axes.getMapView().getExtent())
        gca.axes.setExtent(gca.axes.getDrawExtent().clone())
        draw_if_interactive()
    else:
        if len(limits) == 4:
            xmin = limits[0]
            xmax = limits[1]
            ymin = limits[2]
            ymax = limits[3]
            extent = Extent(xmin, xmax, ymin, ymax)
            gca.axes.setLonLatExtent(extent)
            gca.axes.setExtent(gca.axes.getDrawExtent().clone())
            draw_if_interactive()
        else:
            print 'The limits parameter must be a list with 4 elements: xmin, xmax, ymin, ymax!'

def grid(b=None, which='major', axis='both', **kwargs):
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
    plot = gca
    gridline = plot.axes.getGridLine()
    isDraw = gridline.isDrawXLine()
    if b is None:
        isDraw = not gridline.isDrawXLine()
    elif b == True or b == 'on':
        isDraw = True
    elif b == False or b == 'on':
        isDraw = False
    if axis == 'both':
        gridline.setDrawXLine(isDraw)
        gridline.setDrawYLine(isDraw)
    elif axis == 'x':
        gridline.setDrawXLine(isDraw)
    elif axis == 'y':
        gridline.setDrawYLine(isDraw)
    color = kwargs.pop('color', None)
    if not color is None:
        c = __getcolor(color)
        gridline.setColor(c)
    linewidth = kwargs.pop('linewidth', None)
    if not linewidth is None:
        gridline.setSize(linewidth)
    linestyle = kwargs.pop('linestyle', None)
    if not linestyle is None:
        linestyle = __getlinestyle(linestyle)
        gridline.setStyle(linestyle)
    top = kwargs.pop('top', None)
    if not top is None:
        gridline.setTop(top)
    draw_if_interactive()
    
def xlim(xmin, xmax):
    """
    Set the *x* limits of the current axes.
    
    :param xmin: (*float*) Minimum limit of the x axis.
    :param xmax: (*float*) Maximum limit of the x axis.
    """
    global gca
    
    if isinstance(xmin, datetime.datetime):
        xmin = miutil.date2num(xmin)
    if isinstance(xmax, datetime.datetime):
        xmax = miutil.date2num(xmax)    
        
    if isinstance(gca, Axes3D):
        gca.axes.setXMinMax(xmin, xmax)
    else:
        extent = gca.axes.getDrawExtent()
        extent.minX = xmin
        extent.maxX = xmax
        gca.axes.setDrawExtent(extent)
        gca.axes.setExtent(extent.clone())
    draw_if_interactive()
            
def ylim(ymin, ymax):
    """
    Set the *y* limits of the current axes.
    
    :param ymin: (*float*) Minimum limit of the y axis.
    :param ymax: (*float*) Maximum limit of the y axis.
    """
    global gca
    if isinstance(ymin, datetime.datetime):
        ymin = miutil.date2num(ymin)
    if isinstance(ymax, datetime.datetime):
        ymax = miutil.date2num(ymax) 
    
    if isinstance(gca, Axes3D):
        gca.axes.setYMinMax(ymin, ymax)
    else:
        extent = gca.axes.getDrawExtent()
        extent.minY = ymin
        extent.maxY = ymax
        gca.axes.setDrawExtent(extent)
        gca.axes.setExtent(extent.clone())
    draw_if_interactive()   
    
def zlim(zmin, zmax):
    """
    Set the *z* limits of the current axes.
    
    :param zmin: (*float*) Minimum limit of the z axis.
    :param zmax: (*float*) Maximum limit of the z axis.
    """
    global gca
    if isinstance(zmin, datetime.datetime):
        zmin = miutil.date2num(zmin)
    if isinstance(zmax, datetime.datetime):
        zmax = miutil.date2num(zmax) 
    
    if isinstance(gca, Axes3D):
        gca.axes.setZMinMax(zmin, zmax)
        draw_if_interactive()   

def xreverse():
    '''
    Reverse x axis.
    '''
    gca.axes.getXAxis().setInverse(True)
    draw_if_interactive()
    
def yreverse():
    '''
    Reverse y axis.
    '''
    gca.axes.getYAxis().setInverse(True)
    draw_if_interactive()
            
def legend(*args, **kwargs):
    """
    Places a legend on the axes.
    
    :param breaks: (*ColorBreak*) Legend breaks (optional).
    :param labels: (*list of string*) Legend labels (optional).
    :param orientation: (*string*) Colorbar orientation: ``vertical`` or ``horizontal``.
    :param loc: (*string*) The location of the legend, including: 'upper right', upper left',
        'lower left', 'lower right', 'right', 'ceter left', 'center right', lower center',
        'upper center', 'center' and 'custom'. Default is 'upper right'.
    :param x: (*float*) Location x in normalized (0, 1) units when ``loc=custom`` .
    :param y: (*float*) Location y in normalized (0, 1) units when ``loc=custom`` .
    :param frameon: (*boolean*) Control whether a frame should be drawn around the legend. Default
        is True.
    :param background: (*None or color*) Set draw background or not and/or background color.
        Default is None which set not draw background.
    :param fontname: (*string*) Font name. Default is ``Arial`` .
    :param fontsize: (*int*) Font size. Default is ``14`` .
    :param bold: (*boolean*) Is bold font or not. Default is ``False`` .
    :param labcolor: (*color*) Tick label string color. Default is ``black`` .
    """
    global gca  
    newlegend = kwargs.pop('newlegend', True)
    ols = gca.axes.getLegendScheme()
    if newlegend:
        clegend = ChartLegend(ols)
    else:
        clegend = gca.axes.getLegend()   
    ls = kwargs.pop('legend', None)
    if len(args) > 0 and isinstance(args[0], MILayer):
        ls = args[0].legend()
        args = args[1:]
    if ls is None:
        if len(args) > 0:
            lbs = []
            for lb in args[0]:
                if isinstance(lb, (Graphic, GraphicCollection)):
                    lbs.append(lb.getLegend())
                else:
                    lbs.append(lb)
            if len(args) == 2:
                for i in range(0, len(lbs)):
                    labels = args[1]
                    lbs[i].setCaption(labels[i])
            if isinstance(lbs[0], basestring):
                clegend.setTickLabels(lbs)
            else:
                ls = LegendScheme()
                for lb in lbs:
                    ls.addLegendBreak(lb)
                #ls.setLegendBreaks(lbs)
                if lbs[0].getStartValue() == lbs[1].getEndValue():
                    ls.setLegendType(LegendType.UniqueValue)
                else:
                    ls.setLegendType(LegendType.GraduatedColor)
                if clegend is None:
                    clegend = ChartLegend(ls)
                    gca.axes.setLegend(clegend)
                else:
                    clegend.setLegendScheme(ls)
    else:
        if clegend is None:
            clegend = ChartLegend(ls)
            gca.axes.setLegend(clegend)
        else:
            clegend.setLegendScheme(ls)
        
    loc = kwargs.pop('loc', 'upper right')    
    lp = LegendPosition.fromString(loc)
    clegend.setPosition(lp)
    if lp == LegendPosition.CUSTOM:
        x = kwargs.pop('x', 0)
        y = kwargs.pop('y', 0)
        clegend.setX(x)
        clegend.setY(y) 
    orien = 'vertical'
    if lp == LegendPosition.UPPER_CENTER_OUTSIDE or lp == LegendPosition.LOWER_CENTER_OUTSIDE:
        orien = 'horizontal'
    orientation = kwargs.pop('orientation', orien)
    if orientation == 'horizontal':
        clegend.setPlotOrientation(PlotOrientation.HORIZONTAL)
    else:
        clegend.setPlotOrientation(PlotOrientation.VERTICAL)
    frameon = kwargs.pop('frameon', True)
    clegend.setDrawNeatLine(frameon)
    bcobj = kwargs.pop('background', None)
    if bcobj is None:
        clegend.setDrawBackground(False)
    else:
        clegend.setDrawBackground(True)
        background = __getcolor(bcobj)
        clegend.setBackground(background)
    fontname = kwargs.pop('fontname', 'Arial')
    fontsize = kwargs.pop('fontsize', 14)
    bold = kwargs.pop('bold', False)
    labcolor = kwargs.pop('labcolor', 'black')
    labcolor = __getcolor(labcolor)
    if bold:
        font = Font(fontname, Font.BOLD, fontsize)
    else:
        font = Font(fontname, Font.PLAIN, fontsize)
    clegend.setLabelFont(font)
    clegend.setLabelColor(labcolor)
    markerscale = kwargs.pop('markerscale', None)
    if not markerscale is None:
        clegend.setSymbolScale(markerscale)
    markerwidth = kwargs.pop('markerwidth', None)
    markerheight = kwargs.pop('markerheight', None)
    if not markerwidth is None:
        clegend.setSymbolWidth(markerwidth)
    if not markerheight is None:
        clegend.setSymbolHeight(markerheight)
    ncol = kwargs.pop('ncol', None)
    if not ncol is None:
        clegend.setColumnNumber(ncol)
        clegend.setAutoRowColNum(False)
    xshift = kwargs.pop('xshift', None)
    if not xshift is None:
        clegend.setXShift(xshift)
    yshift = kwargs.pop('yshift', None)
    if not yshift is None:
        clegend.setYShift(yshift)
    if newlegend:
        gca.axes.addLegend(clegend)
    
    draw_if_interactive()
    
def readlegend(fn):
    """
    Read legend from a legend file (.lgs).
    
    :param fn: (*string*) Legend file name.
    
    :returns: (*LegendScheme*) Legend.
    """
    if os.path.exists(fn):
        ls = LegendScheme()
        ls.importFromXMLFile(fn, False)
        return ls
    else:
        print 'File not exists: ' + fn
        return None
        
def colorbar(mappable, **kwargs):
    """
    Add a colorbar to a plot.
    
    :param mappable: (*MapLayer | LegendScheme | List of ColorBreak*) The mappable in plot.
    :param cax: (*Plot*) None | axes object into which the colorbar will be drawn.
    :param cmap: (*string*) Color map name. Default is None.
    :param shrink: (*float*) Fraction by which to shrink the colorbar. Default is 1.0.
    :param orientation: (*string*) Colorbar orientation: ``vertical`` or ``horizontal``.
    :param aspect: (*int*) Ratio of long to short dimensions.
    :param fontname: (*string*) Font name. Default is ``Arial`` .
    :param fontsize: (*int*) Font size. Default is ``14`` .
    :param bold: (*boolean*) Is bold font or not. Default is ``False`` .
    :param label: (*string*) Label. Default is ``None`` .
    :param labelloc: (*string*) Label location ['in' | 'out' | 'top' | 'bottom' | 'left' | 'right'].
        Defaul is ``out``.
    :param extendrect: (*boolean*) If ``True`` the minimum and maximum colorbar extensions will be
        rectangular (the default). If ``False`` the extensions will be triangular.
    :param extendfrac: [None | 'auto' | length] If set to *None*, both the minimum and maximum triangular
        colorbar extensions with have a length of 5% of the interior colorbar length (the default). If
        set to 'auto', makes the triangular colorbar extensions the same lengths as the interior boxes
        . If a scalar, indicates the length of both the minimum and maximum triangle colorbar extensions
        as a fraction of the interior colorbar length.
    :param ticks: [None | list of ticks] If None, ticks are determined automatically from the input.
    """
    cax = kwargs.pop('cax', None)
    if cax is None:
        cax = gca
    cmap = kwargs.pop('cmap', None)
    shrink = kwargs.pop('shrink', 1)
    orientation = kwargs.pop('orientation', 'vertical')
    aspect = kwargs.pop('aspect', 20)
    tickfontdic = kwargs.pop('tickfont', None)
    if tickfontdic is None:
        tickfont = __getfont_1(**kwargs)    
    else:
        tickfont = __getfont(tickfontdic)
    labelfontdic = kwargs.pop('labelfont', None)
    if labelfontdic is None:
        labfontname = kwargs.pop('labelfontname', tickfont.getName())
        labfontsize = kwargs.pop('labelfontsize', tickfont.getSize())
        labbold = kwargs.pop('labelbold', tickfont.isBold())
        if labbold:
            labelfont = Font(labfontname, Font.BOLD, labfontsize)
        else:
            labelfont = Font(labfontname, Font.PLAIN, labfontsize)    
    else:
        labelfont = __getfont(labelfontdic)
    if isinstance(mappable, MILayer):
        ls = mappable.legend()
    elif isinstance(mappable, LegendScheme):
        ls = mappable
    elif isinstance(mappable, GraphicCollection):
        ls = mappable.getLegendScheme()
    else:
        ls = makelegend(mappable)
    
    newlegend = kwargs.pop('newlegend', True)
    if newlegend:
        legend = ChartLegend(ls)
        cax.axes.addLegend(legend)
    else:
        legend = cax.axes.getLegend()   
        if legend is None:
            legend = ChartLegend(ls)
            cax.axes.setLegend(legend)
        else:
            legend.setLegendScheme(ls)
    legend.setColorbar(True)   
    legend.setShrink(shrink)
    legend.setAspect(aspect)
    legend.setTickFont(tickfont)
    legend.setLabelFont(labelfont)
    label = kwargs.pop('label', None)
    if not label is None:
        legend.setLabel(label)
    labelloc = kwargs.pop('labelloc', None)
    if not labelloc is None:
        legend.setLabelLocation(labelloc)
    if orientation == 'horizontal':
        legend.setPlotOrientation(PlotOrientation.HORIZONTAL)
        legend.setPosition(LegendPosition.LOWER_CENTER_OUTSIDE)
    else:
        legend.setPlotOrientation(PlotOrientation.VERTICAL)
        legend.setPosition(LegendPosition.RIGHT_OUTSIDE)
    legend.setDrawNeatLine(False)
    extendrect = kwargs.pop('extendrect', True)
    legend.setExtendRect(extendrect)
    extendfrac = kwargs.pop('extendfrac', None)
    if extendfrac == 'auto':
        legend.setAutoExtendFrac(True)
    ticks = kwargs.pop('ticks', None)
    if not ticks is None:
        legend.setTickLabels(ticks)
    xshift = kwargs.pop('xshift', None)
    if not xshift is None:
        legend.setXShift(xshift)
    yshift = kwargs.pop('yshift', None)
    if not yshift is None:
        legend.setYShift(yshift)
    vmintick = kwargs.pop('vmintick', False)
    vmaxtick = kwargs.pop('vmaxtick', False)
    legend.setDrawMinLabel(vmintick)
    legend.setDrawMaxLabel(vmaxtick)
    #cax.axes.setDrawLegend(True)
    draw_if_interactive()

def set(obj, **kwargs):
    '''
    Set properties to an object. Used to change the plot parameters.
    '''
    if isinstance(obj, Axes):
        xminortick = kwargs.pop('xminortick', None)
        if not xminortick is None:
            locs = [Location.BOTTOM, Location.TOP]
            for loc in locs:
                axis = obj.axes.getAxis(loc)
                axis.setMinorTickVisible(xminortick)
        yminortick = kwargs.pop('yminortick', None)
        if not yminortick is None:
            locs = [Location.LEFT, Location.RIGHT]
            for loc in locs:
                axis = obj.axes.getAxis(loc)
                axis.setMinorTickVisible(yminortick)
        tickin = kwargs.pop('tickin', None)
        if not tickin is None:
            obj.axes.setInsideTick(tickin)
    draw_if_interactive()
    
def __getcolormap(**kwargs):
    colors = kwargs.pop('colors', None)
    issingle = False
    if colors is None:
        colors = kwargs.pop('color', None)
        issingle = True
    if not colors is None:
        if issingle or isinstance(colors, str):
            c = __getcolor(colors)
            cmap = ColorMap(c)
        else:
            cs = []
            for cc in colors:
                c = __getcolor(cc)
                cs.append(c)
            cmap = ColorMap(cs)
    else:
        cmapstr = kwargs.pop('cmap', 'matlab_jet')
        if cmapstr is None:
            cmapstr = 'matlab_jet'
        alpha = kwargs.pop('alpha', None)
        if alpha is None:
            cmap = ColorUtil.getColorMap(cmapstr)
        else:
            alpha = (int)(alpha * 255)
            cmap = ColorUtil.getColorMap(cmapstr, alpha)
    reverse = kwargs.pop('cmapreverse', False)
    if reverse:
        cmap.reverse()
    return cmap
    
def __getlegendscheme(args, min, max, **kwargs):
    ls = kwargs.pop('symbolspec', None)
    if ls is None:
        cmap = __getcolormap(**kwargs)        
        if len(args) > 0:
            level_arg = args[0]
            if isinstance(level_arg, int):
                cn = level_arg
                ls = LegendManage.createLegendScheme(min, max, cn, cmap)
            else:
                if isinstance(level_arg, MIArray):
                    level_arg = level_arg.aslist()
                ls = LegendManage.createLegendScheme(min, max, level_arg, cmap)
        else:    
            ls = LegendManage.createLegendScheme(min, max, cmap)
        ecobj = kwargs.pop('edgecolor', None)
        if not ecobj is None:
            edgecolor = __getcolor(ecobj)
            ls = ls.convertTo(ShapeTypes.Polygon)
            for lb in ls.getLegendBreaks():
                lb.setDrawOutline(True)
                lb.setOutlineColor(edgecolor)
    return ls
    
def __setlegendscheme(ls, **kwargs):
    st = ls.getShapeType()
    if st == ShapeTypes.Point:
        __setlegendscheme_point(ls, **kwargs)
    elif st == ShapeTypes.Polyline:
        __setlegendscheme_line(ls, **kwargs)
    elif st == ShapeTypes.Polygon:
        __setlegendscheme_polygon(ls, **kwargs)
    else:
        __setlegendscheme_image(ls, **kwargs)

def __setlegendscheme_image(ls, **kwargs):
    cobj = kwargs.pop('color', None)
    if not cobj is None:
        color = __getcolor(cobj)    
        for lb in ls.getLegendBreaks():
            lb.setColor(color)
    return ls
        
def __setlegendscheme_point(ls, **kwargs):
    ls = ls.convertTo(ShapeTypes.Point)    
    for lb in ls.getLegendBreaks():
        __setpointlegendbreak(lb, **kwargs)
    return ls
    
def __setlegendscheme_line(ls, **kwargs):
    ls = ls.convertTo(ShapeTypes.Polyline)
    size = kwargs.pop('size', 1)
    lsobj = kwargs.pop('linestyle', '-')
    linestyle = __getlinestyle(lsobj)
    cobj = kwargs.pop('color', None)
    if cobj is None:
        color = None
    else:
        color = __getcolor(cobj)    
    for lb in ls.getLegendBreaks():
        if not color is None:
            lb.setColor(color)
        lb.setStyle(linestyle)
        lb.setSize(size)
    return ls
    
def __setlegendscheme_polygon(ls, **kwargs):
    ls = ls.convertTo(ShapeTypes.Polygon)
    fcobj = kwargs.pop('facecolor', None)
    if fcobj is None:
        facecolor = None
    else:
        facecolor = __getcolor(fcobj)
    ecobj = kwargs.pop('edgecolor', 'k')
    edgecolor = __getcolor(ecobj)
    edgesize = kwargs.pop('edgesize', 1)
    fill = kwargs.pop('fill', True)
    edge = kwargs.pop('edge', True)
    for lb in ls.getLegendBreaks():
        if not facecolor is None:
            lb.setColor(facecolor)
        lb.setOutlineSize(edgesize)        
        lb.setOutlineColor(edgecolor)        
        lb.setDrawFill(fill)        
        lb.setDrawOutline(edge)
    return ls

def imshow(*args, **kwargs):
    """
    Display an image on the axes.
    
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
    #Get dataset
    global gca
    
    n = len(args)
    cmap = __getcolormap(**kwargs)
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
    
    if isrgb:
        if isinstance(rgbdata, (list, tuple)):
            rgbd = []
            for d in rgbdata:
                rgbd.append(d.asarray())
            rgbdata = rgbd
        else:
            rgbdata = rgbdata.asarray()
        x = __getplotdata(x)
        y = __getplotdata(y)
        igraphic = GraphicFactory.createImage(x, y, rgbdata)
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
            ls = __getlegendscheme(args, gdata.min(), gdata.max(), **kwargs)
        ls = ls.convertTo(ShapeTypes.Image)
            
        igraphic = GraphicFactory.createImage(gdata, ls)
    
    #Create plot
    if gca is None:
        plot = Axes()
    else:
        if isinstance(gca, Axes):
            plot = gca
        else:
            plot = Axes()
    if not xaxistype is None:
        __setXAxisType(plot.axes, xaxistype)
        plot.axes.updateDrawExtent()
    plot.add_graphic(igraphic)
    plot.axes.setAutoExtent()
    
    #Create figure
    if chartpanel is None:
        figure()
    
    #Set chart
    chart = chartpanel.getChart()
    if gca is None or (not isinstance(gca, Axes)):
        chart.setCurrentPlot(plot.axes)
    chartpanel.setChart(chart)
    gca = plot
    draw_if_interactive()
    if ls is None:
        return igraphic
    else:
        return ls    
      
def contour(*args, **kwargs):
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
    #Get dataset
    global gca
    
    n = len(args)
    cmap = __getcolormap(**kwargs)
    fill_value = kwargs.pop('fill_value', -9999.0)
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
    __setlegendscheme(ls, **kwargs)
    
    smooth = kwargs.pop('smooth', True)
    igraphic = GraphicFactory.createContourLines(gdata.data, ls, smooth)
    
    #Create plot
    if gca is None:
        plot = Axes()
    else:
        if isinstance(gca, Axes):
            plot = gca
        else:
            plot = Axes()
    if not xaxistype is None:
        __setXAxisType(plot.axes, xaxistype)
        plot.axes.updateDrawExtent()
    plot.add_graphic(igraphic)
    #plot.axes.setAutoExtent()
    plot.axes.setExtent(igraphic.getExtent())
    plot.axes.setDrawExtent(igraphic.getExtent())
    
    #Create figure
    if chartpanel is None:
        figure()
    
    #Set chart
    chart = chartpanel.getChart()
    if gca is None or (not isinstance(gca, Axes)):
        chart.setCurrentPlot(plot.axes)
    chartpanel.setChart(chart)
    gca = plot
    draw_if_interactive()
    return igraphic
    
def contourf(*args, **kwargs):
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
    
    :returns: (*VectoryLayer*) Contour filled VectoryLayer created from array data.
    """
    #Get dataset
    global gca
    
    n = len(args)    
    cmap = __getcolormap(**kwargs)
    fill_value = kwargs.pop('fill_value', -9999.0)
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
    smooth = kwargs.pop('smooth', True)
    igraphic = GraphicFactory.createContourPolygons(gdata.data, ls, smooth)
    
    visible = kwargs.pop('visible', True)
    if visible:
        #Create plot
        if gca is None:
            plot = Axes()
        else:
            if isinstance(gca, Axes):
                plot = gca
            else:
                plot = Axes()
        if not xaxistype is None:
            __setXAxisType(plot.axes, xaxistype)
            plot.axes.updateDrawExtent()
        plot.add_graphic(igraphic)
        #plot.setAutoExtent()
        plot.axes.setExtent(igraphic.getExtent())
        plot.axes.setDrawExtent(igraphic.getExtent())
        
        #Create figure
        if chartpanel is None:
            figure()
        
        #Set chart
        chart = chartpanel.getChart()
        if gca is None or (not isinstance(gca, Axes)):
            chart.setCurrentPlot(plot.axes)
        chartpanel.setChart(chart)
        gca = plot
        draw_if_interactive()    
    return igraphic
    
def quiver(*args, **kwargs):
    """
    Plot a 2-D field of arrows.
    
    :param x: (*array_like*) Optional. X coordinate array.
    :param y: (*array_like*) Optional. Y coordinate array.
    :param u: (*array_like*) U component of the arrow vectors (wind field) or wind direction.
    :param v: (*array_like*) V component of the arrow vectors (wind field) or wind speed.
    :param z: (*array_like*) Optional, 2-D z value array.
    :param levs: (*array_like*) Optional. A list of floating point numbers indicating the level 
        vectors to draw, in increasing order.
    :param cmap: (*string*) Color map string.
    :param fill_value: (*float*) Fill_value. Default is ``-9999.0``.
    :param isuv: (*boolean*) Is U/V or direction/speed data array pairs. Default is True.
    :param size: (*float*) Base size of the arrows.
    :param order: (*int*) Z-order of created layer for display.
    
    :returns: (*VectoryLayer*) Created quiver VectoryLayer.
    """
    global gca
    
    cmap = __getcolormap(**kwargs)
    fill_value = kwargs.pop('fill_value', -9999.0)
    order = kwargs.pop('order', None)
    isuv = kwargs.pop('isuv', True)
    n = len(args) 
    iscolor = False
    cdata = None
    xaxistype = None
    if n < 4 or (n == 4 and isinstance(args[3], int)):
        x = args[0].dimvalue(1)
        y = args[0].dimvalue(0)
        x, y = minum.meshgrid(x, y)
        u = args[0]
        v = args[1]
        if args[0].islondim(1):
            xaxistype = 'lon'
        elif args[0].islatdim(1):
            xaxistype = 'lat'
        elif args[0].istimedim(1):
            xaxistype = 'time'
        args = args[2:]
        if len(args) > 0:
            cdata = args[0]
            iscolor = True
            args = args[1:]
    elif n <= 6:
        x = args[0]
        y = args[1]
        u = args[2]
        v = args[3]
        args = args[4:]
        if len(args) > 0:
            cdata = args[0]
            iscolor = True
            args = args[1:]
    x = __getplotdata(x)
    y = __getplotdata(y)
    u = __getplotdata(u)
    v = __getplotdata(v)    
    
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
    ls = __setlegendscheme_point(ls, **kwargs)
    
    if not cdata is None:
        cdata = __getplotdata(cdata)
    igraphic = GraphicFactory.createArrows(x, y, u, v, cdata, ls, isuv)
    
    #Create plot
    if gca is None:
        plot = Axes()
    else:
        if isinstance(gca, Axes):
            plot = gca
        else:
            plot = Axes()
    if not xaxistype is None:
        __setXAxisType(plot.axes, xaxistype)
        plot.axes.updateDrawExtent()
    plot.add_graphic(igraphic)
    plot.axes.setAutoExtent()
    #plot.axes.setExtent(igraphic.getExtent())
    #plot.axes.setDrawExtent(igraphic.getExtent())
    
    #Create figure
    if chartpanel is None:
        figure()
    
    #Set chart
    chart = chartpanel.getChart()
    if gca is None or (not isinstance(gca, Axes)):
        chart.setCurrentPlot(plot.axes)
    chartpanel.setChart(chart)
    gca = plot
    draw_if_interactive()
    return igraphic
    
def barbs(*args, **kwargs):
    """
    Plot a 2-D field of barbs.
    
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
    :param order: (*int*) Z-order of created layer for display.
    
    :returns: (*VectoryLayer*) Created barbs VectoryLayer.
    """
    global gca
    
    cmap = __getcolormap(**kwargs)
    fill_value = kwargs.pop('fill_value', -9999.0)
    order = kwargs.pop('order', None)
    isuv = kwargs.pop('isuv', True)
    n = len(args) 
    iscolor = False
    cdata = None
    xaxistype = None
    if n <= 3 or (n == 4 and isinstance(args[3], int)):
        x = args[0].dimvalue(1)
        y = args[0].dimvalue(0)
        x, y = minum.meshgrid(x, y)
        u = args[0]
        v = args[1]
        if args[0].islondim(1):
            xaxistype = 'lon'
        elif args[0].islatdim(1):
            xaxistype = 'lat'
        elif args[0].istimedim(1):
            xaxistype = 'time'
        args = args[2:]
        if len(args) > 0:
            cdata = args[0]
            iscolor = True
            args = args[1:]
    elif n <= 5:
        x = args[0]
        y = args[1]
        u = args[2]
        v = args[3]
        args = args[4:]
        if len(args) > 0:
            cdata = args[0]
            iscolor = True
            args = args[1:]
    x = __getplotdata(x)
    y = __getplotdata(y)
    u = __getplotdata(u)
    v = __getplotdata(v)    
    
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
                    levs = levs.aslist()
                ls = LegendManage.createLegendScheme(cdata.min(), cdata.max(), levs, cmap)
    else:    
        if cmap.getColorCount() == 1:
            c = cmap.getColor(0)
        else:
            c = Color.black
        ls = LegendManage.createSingleSymbolLegendScheme(ShapeTypes.Point, c, 10)
    ls = __setlegendscheme_point(ls, **kwargs)
    
    if not cdata is None:
        cdata = __getplotdata(cdata)
    igraphic = GraphicFactory.createBarbs(x, y, u, v, cdata, ls, isuv)
    
    #Create plot
    if gca is None:
        plot = Axes()
    else:
        if isinstance(gca, Axes):
            plot = gca
        else:
            plot = Axes()
    if not xaxistype is None:
        __setXAxisType(plot.axes, xaxistype)
        plot.axes.updateDrawExtent()
    plot.add_graphic(igraphic)
    plot.axes.setAutoExtent()
    #plot.axes.setExtent(igraphic.getExtent())
    #plot.axes.setDrawExtent(igraphic.getExtent())
    
    #Create figure
    if chartpanel is None:
        figure()
    
    #Set chart
    chart = chartpanel.getChart()
    if gca is None or (not isinstance(gca, Axes)):
        chart.setCurrentPlot(plot.axes)
    chartpanel.setChart(chart)
    gca = plot
    draw_if_interactive()
    return igraphic
    
def __plot_griddata(gdata, ls, type, xaxistype=None):
    #print 'GridData...'
    if type == 'contourf':
        layer = DrawMeteoData.createShadedLayer(gdata.data, ls, 'layer', 'data', True)
    elif type == 'contour':
        layer = DrawMeteoData.createContourLayer(gdata.data, ls, 'layer', 'data', True)
    elif type == 'imshow':
        layer = DrawMeteoData.createRasterLayer(gdata, 'layer', ls)
    
    #Create Axes
    global gca
    if gca is None:
        mapview = MapView()
        plot = MapAxes(mapview)
    else:
        if isinstance(gca, Axes):
            plot = gca
        else:
            mapview = MapView()
            plot = MapAxes(mapview)
    
    if xaxistype == 'lon':
        plot.axes.setXAxis(LonLatAxis('Longitude', True))
    elif xaxistype == 'lat':
        plot.axes.setXAxis(LonLatAxis('Latitude', False))
    elif xaxistype == 'time':
        plot.axes.setXAxis(TimeAxis('Time', True))
    
    plot.add_layer(layer)
    plot.axes.setDrawExtent(layer.getExtent().clone())
    
    if chartpanel is None:
        figure()
        
    chart = chartpanel.getChart()
    if gca is None or (not isinstance(gca, Axes)):
        chart.setCurrentPlot(plot.axes)
    gca = plot
    #chart.setAntiAlias(True)
    chartpanel.setChart(chart)
    draw_if_interactive()
    return layer
    
def __plot_uvgriddata(udata, vdata, cdata, ls, type, isuv):
    #print 'GridData...'
    if type == 'quiver':
        if cdata == None:
            layer = DrawMeteoData.createGridVectorLayer(udata.data, vdata.data, ls, 'layer', isuv)
        else:
            layer = DrawMeteoData.createGridVectorLayer(udata.data, vdata.data, cdata.data, ls, 'layer', isuv)
    elif type == 'barbs':
        if cdata == None:
            layer = DrawMeteoData.createGridBarbLayer(udata.data, vdata.data, ls, 'layer', isuv)
        else:
            layer = DrawMeteoData.createGridBarbLayer(udata.data, vdata.data, cdata.data, ls, 'layer', isuv)
    
    shapetype = layer.getShapeType()
    mapview = MapView()
    plot = MapAxes(mapview)
    plot.add_layer(layer)
    plot.axes.setDrawExtent(layer.getExtent().clone())
    
    if chartpanel is None:
        figure()
    
    chart = Chart(plot.axes)
    #chart.setAntiAlias(True)
    chartpanel.setChart(chart)
    global gca
    gca = plot
    draw_if_interactive()
    return layer
    
def scatterm(*args, **kwargs):
    """
    Make a scatter plot on a map.
    
    :param x: (*array_like*) Input x data.
    :param y: (*array_like*) Input y data.
    :param z: (*array_like*) Input z data.
    :param levs: (*array_like*) Optional. A list of floating point numbers indicating the level curves 
        to draw, in increasing order.
    :param cmap: (*string*) Color map string.
    :param colors: (*list*) If None (default), the colormap specified by cmap will be used. If a 
        string, like ‘r’ or ‘red’, all levels will be plotted in this color. If a tuple of matplotlib 
        color args (string, float, rgb, etc), different levels will be plotted in different colors in 
        the order specified.
    :param size: (*int*) Marker size.
    :param marker: (*string*) Marker of the points.
    :param fill: (*boolean*) Fill markers or not. Default is True.
    :param edge: (*boolean*) Draw edge of markers or not. Default is True.
    :param facecolor: (*Color*) Fill color of markers. Default is black.
    :param edgecolor: (*Color*) Edge color of markers. Default is black.
    :param fill_value: (*float*) Fill_value. Default is ``-9999.0``.
    :param proj: (*ProjectionInfo*) Map projection of the data. Default is None.
    :param order: (*int*) Z-order of created layer for display.
    
    :returns: (*VectoryLayer*) Point VectoryLayer.
    """
    plot = gca
    fill_value = kwargs.pop('fill_value', -9999.0)
    proj = kwargs.pop('proj', None)    
    order = kwargs.pop('order', None)
    n = len(args) 
    if n == 1:
        if isinstance(args[0], PyStationData):
            gdata = args[0]
        else:
            gdata = minum.asgriddata(args[0])
        args = []
    elif n <=4:
        x = args[0]
        y = args[1]
        if not isinstance(x, (DimArray, MIArray)):
            x = minum.array(x)
        if not isinstance(y, (DimArray, MIArray)):
            y = minum.array(y)
        if n == 2:
            a = x
            args = []
        else:
            a = args[2]
            if not isinstance(a, (DimArray, MIArray)):
                a = minum.array(a)
            args = args[3:]                
        if a.ndim == 1:
            gdata = minum.asstationdata(a, x, y, fill_value)
        else:
            if a.asarray().getSize() == x.asarray().getSize():
                gdata = minum.asstationdata(a, x, y, fill_value)                
            else:
                gdata = minum.asgriddata(a, x, y, fill_value)
    
    ls = kwargs.pop('symbolspec', None)
    isplot = kwargs.pop('isplot', True)
    if ls is None:
        ls = __getlegendscheme(args, gdata.min(), gdata.max(), **kwargs)
        ls = __setlegendscheme_point(ls, **kwargs)    
    if isinstance(gdata, PyGridData):
        layer = __plot_griddata_m(plot, gdata, ls, 'scatter', proj=proj, order=order, isplot=isplot)
    else:
        layer = __plot_stationdata_m(plot, gdata, ls, 'scatter', proj=proj, order=order, isplot=isplot)
    gdata = None
    return MILayer(layer)
    
def plotm(*args, **kwargs):
    """
    Plot lines and/or markers to the map.
    
    :param x: (*array_like*) Input x data.
    :param y: (*array_like*) Input y data.
    :param style: (*string*) Line style for plot.
    :param linewidth: (*float*) Line width.
    :param color: (*Color*) Line color.
    
    :returns: (*VectoryLayer*) Line VectoryLayer.
    """
    plot = gca
    fill_value = kwargs.pop('fill_value', -9999.0)
    proj = kwargs.pop('proj', None)    
    order = kwargs.pop('order', None)
    n = len(args) 
    xdatalist = []
    ydatalist = []    
    styles = []
    isxylistdata = False
    if n == 1:
        if isinstance(args[0], MIXYListData):
            dataset = args[0]
            snum = args[0].size()
            isxylistdata = True
        else:
            ydata = __getplotdata(args[0])
            if isinstance(args[0], DimArray):
                xdata = args[0].dimvalue(0)
            else:
                xdata = []
                for i in range(0, len(args[0])):
                    xdata.append(i)
            xdatalist.append(minum.asarray(xdata))
            ydatalist.append(minum.asarray(ydata))
    elif n == 2:
        if isinstance(args[1], basestring):
            ydata = __getplotdata(args[0])
            if isinstance(args[0], DimArray):
                xdata = args[0].dimvalue(0)
            else:
                xdata = []
                for i in range(0, len(args[0])):
                    xdata.append(i)
            styles.append(args[1])
        else:
            xdata = __getplotdata(args[0])
            ydata = __getplotdata(args[1])
        xdatalist.append(minum.asarray(xdata))
        ydatalist.append(minum.asarray(ydata))
    else:
        c = 'x'
        for arg in args: 
            if c == 'x':    
                xdatalist.append(minum.asarray(arg))
                c = 'y'
            elif c == 'y':
                ydatalist.append(minum.asarray(arg))
                c = 's'
            elif c == 's':
                if isinstance(arg, basestring):
                    styles.append(arg)
                    c = 'x'
                else:
                    styles.append('-')
                    xdatalist.append(minum.asarray(arg))
                    c = 'y'
    
    if not isxylistdata:
        snum = len(xdatalist)
        
    if len(styles) == 0:
        styles = None
    else:
        while len(styles) < snum:
            styles.append('-')
    
    #Get plot data styles - Legend
    lines = []
    ls = kwargs.pop('legend', None) 
    if ls is None:
        if styles != None:
            for i in range(0, len(styles)):
                line = __getplotstyle(styles[i], str(i), **kwargs)
                lines.append(line)
        else:
            for i in range(0, snum):
                line = __getplotstyle(None, str(i), **kwargs)
                lines.append(line)
        ls = LegendScheme(lines)
    
    if isxylistdata:
        layer = DrawMeteoData.createPolylineLayer(dataset.data, ls, \
            'Plot_lines', 'ID', -180, 180)
    else:
        layer = DrawMeteoData.createPolylineLayer(xdatalist, ydatalist, ls, \
            'Plot_lines', 'ID', -180, 180)
    if (proj != None):
        layer.setProjInfo(proj)
 
    gca.add_layer(layer)
    gca.axes.setDrawExtent(layer.getExtent())
    
    if chartpanel is None:
        figure()

    draw_if_interactive()
    return MILayer(layer)
    
def stationmodel(smdata, **kwargs):
    """
    Plot station model data on the map.
    
    :param smdata: (*StationModelData*) Station model data.
    :param surface: (*boolean*) Is surface data or not. Default is True.
    :param size: (*float*) Size of the station model symbols. Default is 12.
    :param proj: (*ProjectionInfo*) Map projection of the data. Default is None.
    :param order: (*int*) Z-order of created layer for display.
    
    :returns: (*VectoryLayer*) Station model VectoryLayer.
    """
    proj = kwargs.pop('proj', None)
    size = kwargs.pop('size', 12)
    surface = kwargs.pop('surface', True)
    ls = LegendManage.createSingleSymbolLegendScheme(ShapeTypes.Point, Color.blue, size)
    layer = DrawMeteoData.createStationModelLayer(smdata, ls, 'stationmodel', surface)
    if (proj != None):
        layer.setProjInfo(proj)
 
    gca.add_layer(layer)
    gca.axes.setDrawExtent(layer.getExtent())
    
    if chartpanel is None:
        figure()

    draw_if_interactive()
    return MILayer(layer)
        
def imshowm(*args, **kwargs):
    """
    Display an image on the map.
    
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
    :param fill_color: (*color*) Fill_color. Default is None (white color).
    :param proj: (*ProjectionInfo*) Map projection of the data. Default is None.
    :param order: (*int*) Z-order of created layer for display.
    
    :returns: (*RasterLayer*) RasterLayer created from array data.
    """
    plot = gca
    cmap = __getcolormap(**kwargs)
    fill_value = kwargs.pop('fill_value', -9999.0)
    proj = kwargs.pop('proj', None)
    order = kwargs.pop('order', None)
    ls = kwargs.pop('symbolspec', None)
    n = len(args) 
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
            x = rgbdata.dimvalue(1)
            y = rgbdata.dimvalue(0)
        else:
            gdata = minum.asgridarray(args[0])
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
    
    isplot = True
    if isrgb:
        if isinstance(rgbdata, (list, tuple)):
            rgbd = []
            for d in rgbdata:
                rgbd.append(d.asarray())
            rgbdata = rgbd
        else:
            rgbdata = rgbdata.asarray()
        x = __getplotdata(x)
        y = __getplotdata(y)
        igraphic = GraphicFactory.createImage(x, y, rgbdata)
        layer = DrawMeteoData.createImageLayer(x, y, igraphic, 'layer_image')
        if (proj != None):
            layer.setProjInfo(proj)
            
        if isplot:
            shapetype = layer.getShapeType()
            if order is None:
                if shapetype == ShapeTypes.Polygon or shapetype == ShapeTypes.Image:
                    plot.add_layer(layer, 0)
                else:
                    plot.add_layer(layer)
            else:
                plot.add_layer(layer, order)
            plot.axes.setDrawExtent(layer.getExtent().clone())
            plot.axes.setExtent(layer.getExtent().clone())

            draw_if_interactive()
    else:
        if len(args) > 0:
            if ls is None:
                level_arg = args[0]
                if isinstance(level_arg, int):
                    cn = level_arg
                    ls = LegendManage.createImageLegend(gdata, cn, cmap)
                else:
                    if isinstance(level_arg, MIArray):
                        level_arg = level_arg.aslist()
                    ls = LegendManage.createImageLegend(gdata, level_arg, cmap)
        else:    
            if ls is None:
                #ls = LegendManage.createLegendScheme(gdata.getminvalue(), gdata.getmaxvalue(), cmap)
                ls = LegendManage.createImageLegend(gdata, cmap)
        fill_color = kwargs.pop('fill_color', None)
        if not fill_color is None:
            cb = ls.getLegendBreaks().get(ls.getBreakNum() - 1)
            if cb.isNoData():
                cb.setColor(__getcolor(fill_color))
            # else:  
                # cb = ColorBreak()
                # cb.setColor(__getcolor(fill_color))
                # cb.setNoData(True)
                # ls.addLegendBreak(cb)
        layer = __plot_griddata_m(plot, gdata, ls, 'imshow', proj=proj, order=order)
        gdata = None
    return MILayer(layer)
    
def contourm(*args, **kwargs):  
    """
    Plot contours on the map.
    
    :param x: (*array_like*) Optional. X coordinate array.
    :param y: (*array_like*) Optional. Y coordinate array.
    :param z: (*array_like*) 2-D z value array.
    :param levs: (*array_like*) Optional. A list of floating point numbers indicating the level curves 
        to draw, in increasing order.
    :param cmap: (*string*) Color map string.
    :param colors: (*list*) If None (default), the colormap specified by cmap will be used. If a 
        string, like ``r`` or ``red``, all levels will be plotted in this color. If a tuple of matplotlib 
        color args (string, float, rgb, etc), different levels will be plotted in different colors in 
        the order specified.
    :param fill_value: (*float*) Fill_value. Default is ``-9999.0``.
    :param proj: (*ProjectionInfo*) Map projection of the data. Default is None.
    :param isplot: (*boolean*) Plot layer or not. Default is ``True``.
    :param order: (*int*) Z-order of created layer for display.
    :param smooth: (*boolean*) Smooth countour lines or not.
    :param select: (*boolean*) Set the return layer as selected layer or not.
    
    :returns: (*VectoryLayer*) Contour VectoryLayer created from array data.
    """
    fill_value = kwargs.pop('fill_value', -9999.0)      
    proj = kwargs.pop('proj', None)
    order = kwargs.pop('order', None)
    n = len(args) 
    if n <= 2:
        gdata = minum.asgriddata(args[0])
        args = args[1:]
    elif n <=4:
        x = args[0]
        y = args[1]
        a = args[2]
        gdata = minum.asgriddata(a, x, y, fill_value)
        args = args[3:]
    ls = __getlegendscheme(args, gdata.min(), gdata.max(), **kwargs)
    ls = ls.convertTo(ShapeTypes.Polyline)
    __setlegendscheme(ls, **kwargs)
    isplot = kwargs.pop('isplot', True)
    if isplot:
        plot = gca
    else:
        plot = None
    smooth = kwargs.pop('smooth', True)
    layer = __plot_griddata_m(plot, gdata, ls, 'contour', proj=proj, order=order, smooth=smooth)
    select = kwargs.pop('select', True)
    if select:
        plot.axes.setSelectedLayer(layer)
    gdata = None
    return MILayer(layer)
        
def contourfm(*args, **kwargs):
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
    :param fill_value: (*float*) Fill_value. Default is ``-9999.0``.
    :param proj: (*ProjectionInfo*) Map projection of the data. Default is None.
    :param isplot: (*boolean*) Plot layer or not. Default is ``True``.
    :param order: (*int*) Z-order of created layer for display.
    :param smooth: (*boolean*) Smooth countour lines or not.
    :param select: (*boolean*) Set the return layer as selected layer or not.
    
    :returns: (*VectoryLayer*) Contour filled VectoryLayer created from array data.
    """    
    fill_value = kwargs.pop('fill_value', -9999.0)
    interpolate = kwargs.pop('interpolate', False)
    proj = kwargs.pop('proj', None)
    order = kwargs.pop('order', None)
    n = len(args) 
    if n <= 2:
        gdata = minum.asgriddata(args[0])
        args = args[1:]
    elif n <=4:
        x = args[0]
        y = args[1]
        a = args[2]
        gdata = minum.asgriddata(a, x, y, fill_value)
        args = args[3:]
    ls = __getlegendscheme(args, gdata.min(), gdata.max(), **kwargs)
    if interpolate:
        gdata = gdata.interpolate()
    isplot = kwargs.pop('isplot', True)
    plot = gca
    smooth = kwargs.pop('smooth', True)
    layer = __plot_griddata_m(plot, gdata, ls, 'contourf', proj=proj, order=order, smooth=smooth, isplot=isplot)
    select = kwargs.pop('select', True)
    if select:
        plot.axes.setSelectedLayer(layer)
    gdata = None
    return MILayer(layer)
    
def gridfm(*args, **kwargs):
    """
    Plot grid data as grid rectangles polygons.
    
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
    
    :returns: (*VectoryLayer*) Grid VectoryLayer created from array data.
    """    
    plot = gca
    fill_value = kwargs.pop('fill_value', -9999.0)
    interpolate = kwargs.pop('interpolate', False)
    proj = kwargs.pop('proj', None)
    order = kwargs.pop('order', None)
    n = len(args) 
    if n <= 2:
        gdata = minum.asgriddata(args[0])
        args = args[1:]
    elif n <=4:
        x = args[0]
        y = args[1]
        a = args[2]
        gdata = minum.asgriddata(a, x, y, fill_value)
        args = args[3:]
    ls = __getlegendscheme(args, gdata.min(), gdata.max(), **kwargs)
    if interpolate:
        gdata = gdata.interpolate()
    layer = __plot_griddata_m(plot, gdata, ls, 'gridf', proj=proj, order=order)
    select = kwargs.pop('select', True)
    if select:
        plot.axes.setSelectedLayer(layer)
    gdata = None
    return MILayer(layer)
    
def surfacem_1(*args, **kwargs):
    plot = gca
    fill_value = kwargs.pop('fill_value', -9999.0)
    proj = kwargs.pop('proj', None)    
    order = kwargs.pop('order', None)
    n = len(args) 
    if n <= 2:
        if isinstance(args[0], PyStationData):
            gdata = args[0]
        else:
            gdata = minum.asgriddata(args[0])
        args = args[1:]
    elif n <=4:
        x = args[0]
        y = args[1]
        a = args[2]
        if a.ndim == 2 and a.asarray().getSize() != x.asarray().getSize():            
            gdata = minum.asgriddata(a, x, y, fill_value)
        else:
            if not plot.getProjInfo().isLonLat():
                x, y = minum.project(x, y, plot.getProjInfo())
            a, x_g, y_g = minum.griddata([x, y], a, method='surface')
            gdata = minum.asgriddata(a, x_g, y_g, fill_value)
        
        args = args[3:]
    ls = __getlegendscheme(args, gdata.min(), gdata.max(), **kwargs)
    symbolspec = kwargs.pop('symbolspec', None)
    if symbolspec is None:
        ls = __setlegendscheme_point(ls, **kwargs)    
          
    layer = __plot_griddata_m(plot, gdata, ls, 'imshow', proj=plot.getProjInfo(), order=order)
    select = kwargs.pop('select', True)
    if select:
        plot.axes.setSelectedLayer(layer)
    gdata = None
    return MILayer(layer)
    
def surfacem(*args, **kwargs):
    """
    Plot irregular grid data as polygons.
    
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
    fill_value = kwargs.pop('fill_value', -9999.0)
    proj = kwargs.pop('proj', None)    
    order = kwargs.pop('order', None)
    n = len(args) 
    if n <= 2:
        a = args[0]
        y = a.dimvalue(0)
        x = a.dimvalue(1)
        args = args[1:]
    elif n <=4:
        x = args[0]
        y = args[1]
        a = args[2]
        args = args[3:]
    if a.ndim == 2 and x.ndim == 1:            
        x, y = minum.meshgrid(x, y)            
    ls = __getlegendscheme(args, a.min(), a.max(), **kwargs)   
    ls = ls.convertTo(ShapeTypes.Polygon)
    plotutil.setlegendscheme(ls, **kwargs)
        
    #if plot.axes.getProjInfo().isLonLat():
    #    lonlim = 90
    #else:
    #    lonlim = 0
        #x, y = minum.project(x, y, toproj=plot.axes.getProjInfo())
    #layer = ArrayUtil.meshLayer(x.asarray(), y.asarray(), a.asarray(), ls, lonlim)
    layer = ArrayUtil.meshLayer(x.asarray(), y.asarray(), a.asarray(), ls)
    if not proj is None:
        layer.setProjInfo(proj)
        
    # Add layer
    visible = kwargs.pop('visible', True)
    if visible:
        global gca
        shapetype = layer.getShapeType()
        if order is None:
            if shapetype == ShapeTypes.Polygon or shapetype == ShapeTypes.Image:
                gca.add_layer(layer, 0)
            else:
                gca.add_layer(layer)
        else:
            gca.add_layer(layer, order)
        gca.axes.setDrawExtent(layer.getExtent().clone())
        gca.axes.setExtent(layer.getExtent().clone())
        select = kwargs.pop('select', True)
        if select:
            gca.axes.setSelectedLayer(layer)
            
        draw_if_interactive()
    return MILayer(layer)
    
def quiverm(*args, **kwargs):
    """
    Plot a 2-D field of arrows in a map.
    
    :param x: (*array_like*) Optional. X coordinate array.
    :param y: (*array_like*) Optional. Y coordinate array.
    :param u: (*array_like*) U component of the arrow vectors (wind field) or wind direction.
    :param v: (*array_like*) V component of the arrow vectors (wind field) or wind speed.
    :param z: (*array_like*) Optional, 2-D z value array.
    :param levs: (*array_like*) Optional. A list of floating point numbers indicating the level 
        vectors to draw, in increasing order.
    :param cmap: (*string*) Color map string.
    :param fill_value: (*float*) Fill_value. Default is ``-9999.0``.
    :param isuv: (*boolean*) Is U/V or direction/speed data array pairs. Default is True.
    :param size: (*float*) Base size of the arrows.
    :param proj: (*ProjectionInfo*) Map projection of the data. Default is None.
    :param order: (*int*) Z-order of created layer for display.
    :param select: (*boolean*) Set the return layer as selected layer or not.
    
    :returns: (*VectoryLayer*) Created quiver VectoryLayer.
    """
    plot = gca
    cmap = __getcolormap(**kwargs)
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
            if isinstance(args[0], (DimArray, MIArray)):
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
    ls = __setlegendscheme_point(ls, **kwargs)
    layer = __plot_uvdata_m(plot, x, y, u, v, cdata, ls, 'quiver', isuv, proj=proj)
    select = kwargs.pop('select', True)
    if select:
        plot.axes.setSelectedLayer(layer)
    udata = None
    vdata = None
    cdata = None
    return MILayer(layer)
    
def quiverkey(*args, **kwargs):
    """
    Add a key to a quiver plot.
    
    :param Q: (*MILayer or GraphicCollection*) The quiver layer instance returned by a call to quiver/quiverm.
    :param X: (*float*) The location x of the key.
    :param Y: (*float*) The location y of the key.
    :param U: (*float*) The length of the key.
    :param label: (*string*) A string with the length and units of the key.
    :param coordinates=['axes'|'figure'|'data'|'inches']: (*string*) Coordinate system and units for 
        *X, Y*. 'axes' and 'figure' are normalized coordinate system with 0,0 in the lower left and 
        1,1 in the upper right, 'data' are the axes data coordinates (used for the locations of the 
        vectors in the quiver plot itself); 'inches' is position in the figure in inches, with 0,0 
        at the lower left corner.
    :param color: (*Color*) Overrides face and edge colors from Q.
    :param labelpos=['N'|'S'|'E'|'W']: (*string*) Position the label above, below, to the right, to
        the left of the arrow, respectively.
    :param labelsep: (*float*) Distance in inches between the arrow and the label. Default is 0.1.
    :param labelcolor: (*Color*) Label color. Default to default is black.
    :param fontproperties: (*dict*) A dictionary with keyword arguments accepted by the FontProperties
        initializer: *family, style, variant, size, weight*.
    """
    wa = ChartWindArrow()
    Q = args[0]
    if isinstance(Q, MILayer):
        wa.setLayer(Q.layer)
    else:
        wa.setLayer(Q)
    X = args[1]
    Y = args[2]
    wa.setX(X)
    wa.setY(Y)
    U = args[3]
    wa.setLength(U)
    if len(args) == 5:
        label = args[4]
        wa.setLabel(label)
    cobj = kwargs.pop('color', 'b')
    color = __getcolor(cobj)
    wa.setColor(color)
    lcobj = kwargs.pop('labelcolor', 'b')
    lcolor = __getcolor(lcobj)
    wa.setLabelColor(lcolor)
    bbox = kwargs.pop('bbox', None)
    if not bbox is None:
        fill = bbox.pop('fill', None)
        if not fill is None:
            wa.setFill(fill)
        facecolor = bbox.pop('facecolor', None)
        if not facecolor is None:
            facecolor = __getcolor(facecolor)
            wa.setFill(True)
            wa.setBackground(facecolor)
        edge = bbox.pop('edge', None)
        if not edge is None:
            wa.setDrawNeatline(edge)
        edgecolor = bbox.pop('edgecolor', None)
        if not edgecolor is None:
            edgecolor = __getcolor(edgecolor)
            wa.setNeatlineColor(edgecolor)
            wa.setDrawNeatline(True)
        linewidth = bbox.pop('linewidth', None)
        if not linewidth is None:
            wa.setNeatlineSize(linewidth)
            wa.setDrawNeatline(True)
    gca.axes.setWindArrow(wa)
    draw_if_interactive()
    
def barbsm(*args, **kwargs):
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
    plot = gca
    cmap = __getcolormap(**kwargs)
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
    ls = __setlegendscheme_point(ls, **kwargs)
    layer = __plot_uvdata_m(plot, x, y, u, v, cdata, ls, 'barbs', isuv, proj=proj)
    select = kwargs.pop('select', True)
    if select:
        plot.axes.setSelectedLayer(layer)
    udata = None
    vdata = None
    cdata = None
    return MILayer(layer)
    
def streamplotm(*args, **kwargs):
    """
    Plot streamline in a map.
    
    :param x: (*array_like*) Optional. X coordinate array.
    :param y: (*array_like*) Optional. Y coordinate array.
    :param u: (*array_like*) U component of the arrow vectors (wind field) or wind direction.
    :param v: (*array_like*) V component of the arrow vectors (wind field) or wind speed.
    :param z: (*array_like*) Optional, 2-D z value array.
    :param color: (*Color*) Streamline color. Default is blue.
    :param fill_value: (*float*) Fill_value. Default is ``-9999.0``.
    :param isuv: (*boolean*) Is U/V or direction/speed data array pairs. Default is True.
    :param density: (*int*) Streamline density. Default is 4.
    :param proj: (*ProjectionInfo*) Map projection of the data. Default is None.
    :param order: (*int*) Z-order of created layer for display.
    :param select: (*boolean*) Set the return layer as selected layer or not.
    
    :returns: (*VectoryLayer*) Created streamline VectoryLayer.
    """
    plot = gca
    cmap = __getcolormap(**kwargs)
    fill_value = kwargs.pop('fill_value', -9999.0)
    proj = kwargs.pop('proj', None)
    cobj = kwargs.pop('color', 'b')
    color = __getcolor(cobj)
    isuv = kwargs.pop('isuv', True)
    density = kwargs.pop('density', 4)
    n = len(args)
    if n < 4:
        udata = minum.asgriddata(args[0])
        vdata = minum.asgriddata(args[1])
        args = args[2:]
    elif n <= 6:
        x = args[0]
        y = args[1]
        u = args[2]
        v = args[3]
        udata = minum.asgriddata(u, x, y, fill_value)
        vdata = minum.asgriddata(v, x, y, fill_value)
        args = args[4:]  
    ls = LegendManage.createSingleSymbolLegendScheme(ShapeTypes.Polyline, color, 1)
    layer = __plot_uvgriddata_m(plot, udata, vdata, None, ls, 'streamplot', isuv, proj=proj, density=density)
    select = kwargs.pop('select', True)
    if select:
        plot.axes.setSelectedLayer(layer)
    udata = None
    vdata = None
    return MILayer(layer)
        
def __plot_griddata_m(plot, gdata, ls, type, proj=None, order=None, smooth=True, isplot=True):
    #print 'GridData...'
    if type == 'contourf':
        layer = DrawMeteoData.createShadedLayer(gdata.data, ls, 'layer', 'data', smooth)
    elif type == 'contour':
        layer = DrawMeteoData.createContourLayer(gdata.data, ls, 'layer', 'data', smooth)
    elif type == 'imshow':
        layer = DrawMeteoData.createRasterLayer(gdata, 'layer', ls)      
    elif type == 'scatter':
        layer = DrawMeteoData.createGridPointLayer(gdata.data, ls, 'layer', 'data')
    elif type == 'gridf':
        layer = DrawMeteoData.createGridFillLayer(gdata.data, ls, 'layer', 'data')
    else:
        layer = None
        return layer
    
    if (proj != None):
        layer.setProjInfo(proj)
        
    if isplot:
        shapetype = layer.getShapeType()
        if order is None:
            if shapetype == ShapeTypes.Polygon or shapetype == ShapeTypes.Image:
                plot.add_layer(layer, 0)
            else:
                plot.add_layer(layer)
        else:
            plot.add_layer(layer, order)
        plot.axes.setDrawExtent(layer.getExtent().clone())
        plot.axes.setExtent(layer.getExtent().clone())
        
        if chartpanel is None:
            figure()
        
        #chart = Chart(plot)
        #chart.setAntiAlias(True)
        #chartpanel.setChart(chart)
        #global gca
        #gca = plot
        draw_if_interactive()
    return layer
    
def __plot_stationdata_m(plot, stdata, ls, type, proj=None, order=None, isplot=True):
    #print 'GridData...'
    if type == 'scatter':
        layer = DrawMeteoData.createSTPointLayer(stdata.data, ls, 'layer', 'data')
    elif type == 'surface':
        layer = DrawMeteoData
    else:
        layer = None
        return layer
    
    if (proj != None):
        layer.setProjInfo(proj)
 
    if isplot:
        if order is None:
            plot.add_layer(layer)
        else:
            plot.add_layer(layer, order)
        plot.axes.setDrawExtent(layer.getExtent().clone())
        plot.axes.setExtent(layer.getExtent().clone())
        
        if chartpanel is None:
            figure()
        
        #chart = Chart(plot)
        #chart.setAntiAlias(True)
        #chartpanel.setChart(chart)
        #global gca
        #gca = plot
        draw_if_interactive()
    return layer

def __plot_uvdata_m(plot, x, y, u, v, z, ls, type, isuv, proj=None, density=4):
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
    plot.add_layer(layer)
    plot.axes.setDrawExtent(layer.getExtent().clone())
    plot.axes.setExtent(layer.getExtent().clone())
    
    if chartpanel is None:
        figure()

    draw_if_interactive()
    return layer
    
def __plot_uvgriddata_m(plot, udata, vdata, cdata, ls, type, isuv, proj=None, density=4):
    #print 'GridData...'
    if type == 'quiver':
        if cdata == None:
            layer = DrawMeteoData.createGridVectorLayer(udata.data, vdata.data, ls, 'layer', isuv)
        else:
            layer = DrawMeteoData.createGridVectorLayer(udata.data, vdata.data, cdata.data, ls, 'layer', isuv)
    elif type == 'barbs':
        if cdata == None:
            layer = DrawMeteoData.createGridBarbLayer(udata.data, vdata.data, ls, 'layer', isuv)
        else:
            layer = DrawMeteoData.createGridBarbLayer(udata.data, vdata.data, cdata.data, ls, 'layer', isuv)
    elif type == 'streamplot':
        layer = DrawMeteoData.createStreamlineLayer(udata.data, vdata.data, density, ls, 'layer', isuv)
    
    if (proj != None):
        layer.setProjInfo(proj)
    
    shapetype = layer.getShapeType()
    plot.add_layer(layer)
    plot.axes.setDrawExtent(layer.getExtent().clone())
    plot.axes.setExtent(layer.getExtent().clone())
    
    if chartpanel is None:
        figure()
    
    #chart = Chart(plot)
    #chart.setAntiAlias(True)
    #chartpanel.setChart(chart)
    #global gca
    #gca = plot
    draw_if_interactive()
    return layer
    
def clabel(layer, **kwargs):
    '''
    Add contour layer labels.
    
    :param layer: (*MILayer*) The contour layer.
    :param fontname, fontsize: The font auguments.
    :param color: (*color*) The label color. Default is ``None``, the label color will be set as
        same as color of the line.
    :param dynamic: (*boolean*) Draw labels dynamic or not. Default is ``True``.
    :param drawshadow: (*boolean*) Draw shadow under labels or not.
    :param fieldname: (*string*) The field name used for label.
    :param xoffset: (*int*) X offset of the labels.
    :param yoffset: (int*) Y offset of the labels.
    :param avoidcoll: (*boolean*) Avoid labels collision or not.
    '''    
    color = kwargs.pop('color', None)    
    gc = layer
    if isinstance(layer, MILayer):
        gc = layer.layer   
    dynamic = kwargs.pop('dynamic', True)
    if gc.getShapeType() != ShapeTypes.Polyline:
        dynamic = False
    drawshadow = kwargs.pop('drawshadow', dynamic)    
    labelset = gc.getLabelSet()
    if isinstance(gc, MapLayer):
        fieldname = kwargs.pop('fieldname', labelset.getFieldName())
        if fieldname is None:
            fieldname = gc.getFieldName(0)
        labelset.setFieldName(fieldname)
    fontdic = kwargs.pop('font', None)
    if not fontdic is None:
        font = __getfont(fontdic)
        labelset.setLabelFont(font)
    else:
        font = __getfont_1(**kwargs)
        labelset.setLabelFont(font)
    if color is None:
        labelset.setColorByLegend(True)
    else:
        labelset.setColorByLegend(False)
        color = __getcolor(color)
        labelset.setLabelColor(color)
    labelset.setDrawShadow(drawshadow)
    xoffset = kwargs.pop('xoffset', 0)
    labelset.setXOffset(xoffset)
    yoffset = kwargs.pop('yoffset', 0)
    labelset.setYOffset(yoffset)
    avoidcoll = kwargs.pop('avoidcoll', True)
    labelset.setAvoidCollision(avoidcoll)    
    if dynamic:
        gc.addLabelsContourDynamic(gc.getExtent())
    else:
        gc.addLabels()
    draw_if_interactive()
        
def worldmap():
    '''
    Return a map plot.
    '''
    mapview = MapView()
    mapview.setXYScaleFactor(1.0)
    #print 'Is GeoMap: ' + str(mapview.isGeoMap())
    plot = MapAxes(mapview)
    chart = chartpanel.getChart()
    chart.clearPlots()
    chart.setPlot(plot.axes)
    global gca
    gca = plot
    return plot

def webmap(provider='OpenStreetMap', order=0):
    '''
    Add a new web map layer.
    
    :param provider: (*string*) Web map provider.
    :param order: (*int*) Layer order.
    
    :returns: Web map layer
    '''
    layer = WebMapLayer()
    provider = WebMapProvider.valueOf(provider)
    layer.setWebMapProvider(provider)
    gca.add_layer(layer, order)
    draw_if_interactive()
    return MILayer(layer)
        
def geoshow(*args, **kwargs):
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
    plot = gca
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
                plot.add_layer(layer)
            else:
                plot.add_layer(layer, order)
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
                    lb, isunique = __getlegendbreak(geometry, **kwargs)
                    layer.getLegendScheme().getLegendBreaks().set(0, lb)
            else:
                layer.setLegendScheme(ls)
            if order is None:
                plot.add_layer(layer)
            else:
                plot.add_layer(layer, order)
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
        plot.axes.setDrawExtent(layer.getExtent().clone())
        plot.axes.setExtent(layer.getExtent().clone())
        draw_if_interactive()
    else:
        if isinstance(args[0], Graphic):
            graphic = args[0]
            displaytype = 'point'
            stype = graphic.getShape().getShapeType()
            if stype == ShapeTypes.Polyline:
                displaytype = 'line'
            elif stype == ShapeTypes.Polygon:
                displaytype = 'polygon'
            lbreak, isunique = __getlegendbreak(displaytype, **kwargs)
            graphic.setLegend(lbreak)
            plot.add_graphic(graphic)            
            draw_if_interactive()
        elif isinstance(args[0], Shape):
            shape = args[0]
            displaytype = 'point'
            stype = shape.getShapeType()
            if stype == ShapeTypes.Polyline:
                displaytype = 'line'
            elif stype == ShapeTypes.Polygon:
                displaytype = 'polygon'
            lbreak, isunique = __getlegendbreak(displaytype, **kwargs)
            graphic = Graphic(shape, lbreak)
            plot.add_graphic(graphic)            
            draw_if_interactive()
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

            lbreak, isunique = __getlegendbreak(displaytype, **kwargs)
            if displaytype == 'point':
                graphic = plot.axes.addPoint(lat, lon, lbreak)
            elif displaytype == 'polyline' or displaytype == 'line':
                graphic = plot.axes.addPolyline(lat, lon, lbreak)
            elif displaytype == 'polygon':
                graphic = plot.axes.addPolygon(lat, lon, lbreak)
            draw_if_interactive()
            return graphic
            
def surf(*args, **kwargs):
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
    global gca
    if chartpanel is None:
        figure()
    chart = chartpanel.getChart()
    if gca is None:    
        gca = axes3d()
    else:
        if not isinstance(gca, Axes3D):
            gca = axes3d()

    return gca.plot_surface(*args, **kwargs)
    
def makecolors(n, cmap='matlab_jet', reverse=False, alpha=None):
    '''
    Make colors.
    
    :param n: (*int*) Colors number.
    :param cmap: (*string*) Color map name. Default is ``matlab_jet``.
    :param reverse: (*boolean*) Reverse the colors or not. Default is ``False``.
    :param alpha: (*float*) Alpha value (0 - 1) of the colors. Defaul is ``None``.

    :returns: (*list*) Created colors.
    '''
    if isinstance(n, list):
        cols = __getcolors(n, alpha)
    else:
        ocmap = ColorUtil.getColorMap(cmap)
        if reverse:
            ocmap.reverse()
        if alpha is None:
            cols = ocmap.getColorList(n)    
        else:
            alpha = (int)(alpha * 255)
            cols = ocmap.getColorList(n, alpha)
    return list(cols)

def makelegend(source):
    '''
    Make a legend.
    
    :param souce: Legend file name or list of the legen breaks.
    
    :returns: Created legend.
    '''
    if isinstance(source, basestring):
        ls = LegendScheme()
        ls.importFromXMLFile(source, False)
    else:
        ls = LegendScheme(source)
    return ls
    
def makesymbolspec(geometry, *args, **kwargs):
    '''
    Make a legend.
    
    :param geometry: (*string*) Geometry type. [point | line | polygon].
    :param levels: (*array_like*) Value levels. Default is ``None``, not used.
    :param colors: (*list*) Colors. Defaul is ``None``, not used.
    :param legend break parameter maps: (*map*) Legend breaks.
    :param field: (*string*) The field of to be used in the legend.
    
    :returns: Created legend.
    '''
    shapetype = ShapeTypes.Image
    if geometry == 'point':
        shapetype = ShapeTypes.Point
    elif geometry == 'line':
        shapetype = ShapeTypes.Polyline
    elif geometry == 'polygon':
        shapetype = ShapeTypes.Polygon  
    else:
        shapetype = ShapeTypes.Image
        
    levels = kwargs.pop('levels', None)
    cols = kwargs.pop('colors', None)
    if not levels is None and not cols is None:
        if isinstance(levels, MIArray):
            levels = levels.aslist()
        colors = []
        for cobj in cols:
            colors.append(__getcolor(cobj))
        ls = LegendManage.createLegendScheme(shapetype, levels, colors)
        __setlegendscheme(ls, **kwargs)
        field = kwargs.pop('field', '')    
        ls.setFieldName(field)
        return ls
    
    ls = LegendScheme(shapetype)
    field = kwargs.pop('field', '')    
    ls.setFieldName(field)
    n = len(args)
    isunique = True
    for arg in args:
        lb, isu = __getlegendbreak(geometry, **arg)
        if isunique  and not isu:
            isunique = False
        ls.addLegendBreak(lb)
        
    if ls.getBreakNum() > 1:
        if isunique:
            ls.setLegendType(LegendType.UniqueValue)
        else:
            ls.setLegendType(LegendType.GraduatedColor)
            
    return ls
    
def weatherspec(weather='all', size=20, color='b'):
    '''
    Make a weather symbol legend.
    
    :param weather: (*string or list*) The weather index list. Defaul is ``all``, used all weathers.
    :param size: (*string*) The weather symbol size.
    :param color: (*color*) The weather symbol color.
    
    :returns: Weather symbol legend.
    '''
    if isinstance(weather, str):
        wlist = DrawMeteoData.getWeatherTypes(weather)
    else:
        wlist = weather
    c = __getcolor(color)
    return DrawMeteoData.createWeatherLegendScheme(wlist, size, c)
    
def cloudspec(size=12, color='b'):
    '''
    Make a cloud amount symbol legend.

    :param size: (*string*) The symbol size.
    :param color: (*color*) The symbol color.
    
    :returns: Cloud amount symbol legend.
    '''
    c = __getcolor(color)
    return DrawMeteoData.createCloudLegendScheme(size, c)
    
def __getpointlegendbreak(**kwargs):
    lb = PointBreak()        
    marker = kwargs.pop('marker', 'o')
    if marker == 'image':
        imagepath = kwargs.pop('imagepath', None)
        if not imagepath is None:
            lb.setMarkerType(MarkerType.Image)
            lb.setImagePath(imagepath)
    elif marker == 'font':
        fontname = kwargs.pop('fontname', 'Weather')
        lb.setMarkerType(MarkerType.Character)
        lb.setFontName(fontname)
        charindex = kwargs.pop('charindex', 0)
        lb.setCharIndex(charindex)
    else:
        pstyle = __getpointstyle(marker)
        lb.setStyle(pstyle)
    size = kwargs.pop('size', 6)
    lb.setSize(size)
    ecobj = kwargs.pop('edgecolor', 'k')
    edgecolor = __getcolor(ecobj)
    lb.setOutlineColor(edgecolor)
    fill = kwargs.pop('fill', True)
    lb.setDrawFill(fill)
    edge = kwargs.pop('edge', True)
    lb.setDrawOutline(edge)
    return lb
    
def __setpointlegendbreak(lb, **kwargs):       
    marker = kwargs.pop('marker', 'o')
    if marker == 'image':
        imagepath = kwargs.pop('imagepath', None)
        if not imagepath is None:
            lb.setMarkerType(MarkerType.Image)
            lb.setImagePath(imagepath)
    elif marker == 'font':
        fontname = kwargs.pop('fontname', 'Weather')
        lb.setMarkerType(MarkerType.Character)
        lb.setFontName(fontname)
        charindex = kwargs.pop('charindex', 0)
        lb.setCharIndex(charindex)
    else:
        pstyle = __getpointstyle(marker)
        lb.setStyle(pstyle)
    size = kwargs.pop('size', 6)
    lb.setSize(size)
    ecobj = kwargs.pop('edgecolor', 'k')
    edgecolor = __getcolor(ecobj)
    lb.setOutlineColor(edgecolor)
    fill = kwargs.pop('fill', True)
    lb.setDrawFill(fill)
    edge = kwargs.pop('edge', True)
    lb.setDrawOutline(edge)

def __getlegendbreak(geometry, **kwargs): 
    cobj = kwargs.pop('color', None)
    if cobj is None:
        cobj = kwargs.pop('facecolor', None)
    color = None
    if not cobj is None:
        color = __getcolor(cobj)
    if geometry == 'point':
        lb = PointBreak()        
        marker = kwargs.pop('marker', 'o')
        if marker == 'image':
            imagepath = kwargs.pop('imagepath', None)
            if not imagepath is None:
                lb.setMarkerType(MarkerType.Image)
                lb.setImagePath(imagepath)
        elif marker == 'font':
            fontname = kwargs.pop('fontname', 'Weather')
            lb.setMarkerType(MarkerType.Character)
            lb.setFontName(fontname)
            charindex = kwargs.pop('charindex', 0)
            lb.setCharIndex(charindex)
        else:
            pstyle = __getpointstyle(marker)
            lb.setStyle(pstyle)
        size = kwargs.pop('size', 6)
        lb.setSize(size)
        ecobj = kwargs.pop('edgecolor', 'k')
        edgecolor = __getcolor(ecobj)
        lb.setOutlineColor(edgecolor)
        fill = kwargs.pop('fill', True)
        lb.setDrawFill(fill)
        edge = kwargs.pop('edge', True)
        lb.setDrawOutline(edge)
    elif geometry == 'line':
        lb = PolylineBreak()
        size = kwargs.pop('size', 1.0)
        size = kwargs.pop('linewidth', size)
        lb.setSize(size)
        lsobj = kwargs.pop('linestyle', '-')
        linestyle = __getlinestyle(lsobj)
        lb.setStyle(linestyle)
        marker = kwargs.pop('marker', None)
        if not marker is None:
            pstyle = __getpointstyle(marker)
            lb.setDrawSymbol(True)
            lb.setSymbolStyle(pstyle)
            markersize = kwargs.pop('markersize', 8)
            lb.setSymbolSize(markersize)
            markercolor = kwargs.pop('markercolor', None)
            if markercolor is None:
                makercolor = color
            else:
                makercolor = __getcolor(makercolor)
            lb.setSymbolColor(makercolor)
            fillcolor = kwargs.pop('makerfillcolor', None)
            if not fillcolor is None:
                lb.setFillSymbol(True)
                lb.setSymbolFillColor(__getcolor(fillcolor))
            else:
                lb.setSymbolFillColor(markercolor)
            interval = kwargs.pop('markerinterval', 1)
            lb.setSymbolInterval(interval)
    elif geometry == 'polygon':
        lb = PolygonBreak()
        ecobj = kwargs.pop('edgecolor', 'k')
        edgecolor = __getcolor(ecobj)
        lb.setOutlineColor(edgecolor)
        fill = kwargs.pop('fill', None)
        if fill is None:
            if color is None:
                lb.setDrawFill(False)
            else:
                lb.setDrawFill(True)
        else:
            lb.setDrawFill(fill)
        edge = kwargs.pop('edge', True)
        lb.setDrawOutline(edge)
        size = kwargs.pop('size', 1)
        lb.setOutlineSize(size)
    else:
        lb = ColorBreak()
    caption = kwargs.pop('caption', None)
    if not caption is None:
        lb.setCaption(caption) 
    if not color is None:
        lb.setColor(color)
    alpha = kwargs.pop('alpha', None)
    if not alpha is None:
        lb.setColor(__getcolor(lb.getColor(), alpha))
    value = kwargs.pop('value', None)
    isunique = True
    if not value is None:
        if isinstance(value, (tuple, list)):
            lb.setStartValue(value[0])
            lb.setEndValue(value[1])
            isunique = False
        else:
            lb.setStartValue(value)
            lb.setEndValue(value)
    return lb, isunique
    
def masklayer(mobj, layers):
    '''
    Mask layers.
    
    :param mobj: (*layer or polgyons*) Mask object.
    :param layers: (*list*) The layers will be masked.       
    '''
    plot = gca
    mapview = plot.axes.getMapView()
    mapview.getMaskOut().setMask(True)
    mapview.getMaskOut().setMaskLayer(mobj.layer.getLayerName())
    for layer in layers:
        layer.layer.setMaskout(True)
    draw_if_interactive()
    
def display(data):
    '''
    Old one - should not be used.
    '''
    if not ismap:
        map()
    
    if c_meteodata is None:
        print 'The current meteodata is None!'
        return
    
    if isinstance(data, PyGridData):
        print 'PyGridData'
        layer = DrawMeteoData.createContourLayer(data.data, 'layer', 'data')
        mapview = MapView()
        mapview.setLockViewUpdate(True)
        mapview.addLayer(layer)
        mapview.setLockViewUpdate(False)
        plot = MapPlot(mapview)
        chart = Chart(plot)
        #chart.setAntiAlias(True)
        chartpanel.setChart(chart)
        if isinteractive:
            chartpanel.paintGraphics()
    elif isinstance(data, basestring):
        if c_meteodata.isGridData():
            gdata = c_meteodata.getGridData(data)
            layer = DrawMeteoData.createContourLayer(gdata, data, data)
            #if maplayout is None:
                #maplayout = MapLayout()
            mapFrame = maplayout.getActiveMapFrame()
            mapView = mapFrame.getMapView()
            mapView.setLockViewUpdate(True)
            mapFrame.addLayer(layer)
            maplayout.getActiveLayoutMap().zoomToExtentLonLatEx(mapView.getMeteoLayersExtent())
            mapView.setLockViewUpdate(False)
            if isinteractive:
                maplayout.paintGraphics()
    else:
        print 'Unkown data type!'
        print type(data)
        
def gifanimation(filename, repeat=0, delay=1000):
    """
    Create a gif animation file
    
    :param: repeat: (*int, Default 0*) Animation repeat time number. 0 means repeat forever.
    :param: delay: (*int, Default 1000*) Animation frame delay time with units of millsecond.
    
    :returns: Gif animation object.
    """
    encoder = AnimatedGifEncoder()
    encoder.setRepeat(repeat)
    encoder.setDelay(delay)
    encoder.start(filename)
    return encoder

def gifaddframe(animation):
    """
    Add a frame to an gif animation object
    
    :param animation: Gif animation object
    """
    #chartpanel.paintGraphics()
    animation.addFrame(chartpanel.paintViewImage())
    
def giffinish(animation):
    """
    Finish a gif animation object and write gif animation image file
    
    :param animation: Gif animation object
    """
    animation.finish()
        
def clear():
    """
    Clear all variables.
    """
    migl.milapp.delVariables()