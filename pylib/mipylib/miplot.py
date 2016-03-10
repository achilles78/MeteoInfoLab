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

from org.meteoinfo.chart import ChartPanel, Location
from org.meteoinfo.data import XYListDataset, XYErrorSeriesData, GridData, ArrayUtil
from org.meteoinfo.data.mapdata import MapDataManage
from org.meteoinfo.data.meteodata import MeteoDataInfo, DrawMeteoData
from org.meteoinfo.chart.plot import Plot, XY1DPlot, BarPlot, XY2DPlot, MapPlot, SeriesLegend, ChartPlotMethod, PlotOrientation
from org.meteoinfo.chart import Chart, ChartText, ChartLegend, LegendPosition, ChartWindArrow
from org.meteoinfo.chart.axis import LonLatAxis, TimeAxis
from org.meteoinfo.script import ChartForm, MapForm
from org.meteoinfo.legend import MapFrame, LineStyles, HatchStyle, BreakTypes, ColorBreak, PointBreak, PolylineBreak, PolygonBreak, LegendManage, LegendScheme, LegendType
from org.meteoinfo.drawing import PointStyle
from org.meteoinfo.global import Extent
from org.meteoinfo.global.colors import ColorUtil, ColorMap
from org.meteoinfo.global.image import AnimatedGifEncoder
from org.meteoinfo.layer import LayerTypes
from org.meteoinfo.layout import MapLayout
from org.meteoinfo.map import MapView
from org.meteoinfo.laboratory.gui import FrmMain
from org.meteoinfo.projection import ProjectionInfo
from org.meteoinfo.shape import ShapeTypes

from javax.swing import WindowConstants
from java.awt import Color, Font

import dimarray
from dimarray import DimArray, PyGridData, PyStationData
import miarray
from miarray import MIArray
import minum
import milayer
from milayer import MILayer, MIXYListData
import miutil

## Global ##
milapp = None
batchmode = False
isinteractive = False
maplayout = MapLayout()
chartpanel = None
isholdon = True
gca = None
ismap = False
maplayer = None
#mapfn = os.path.join(inspect.getfile(inspect.currentframe()), '../../../map/country1.shp')
mapfn = os.path.join(inspect.getfile(inspect.currentframe()), 'D:/Temp/map/country1.shp')
mapfn = os.path.abspath(mapfn)
""""
if os.path.exists(mapfn):
    print 'Default map file: ' + mapfn
    maplayer = MapDataManage.loadLayer(mapfn)
    pgb = maplayer.getLegendScheme().getLegendBreaks().get(0)
    pgb.setDrawFill(False)
    pgb.setOutlineColor(Color.darkGray)    
"""
    
def map(map=True):
    global ismap
    if map:
        ismap = True
        print 'Switch to map mode'
    else:
        ismap = False
        print 'Switch to figure mode'

def hold(ishold):
    global isholdon
    isholdon = ishold
 
def __getplotdata(data):
    if isinstance(data, MIArray):
        return data.array
    elif isinstance(data, DimArray):
        return data.array.array
    elif isinstance(data, (list, tuple)):
        if isinstance(data[0], datetime.datetime):
            dd = []
            for d in data:
                v = miutil.date2num(d)
                dd.append(v)
            return dd
        else:
            return data
    else:
        return [data]

def draw_if_interactive():
    if isinteractive:
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
    if isholdon:
        if gca == None:
            dataset = XYListDataset()
        else:
            if not isinstance(gca, XY1DPlot):
                dataset = XYListDataset()
            else:
                dataset = gca.getDataset()
                if dataset is None:
                    dataset = XYListDataset()
    else:
        dataset = XYListDataset()
    
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
    
    if not isxylistdata:
        #Add data series
        snum = len(xdatalist)
        for i in range(0, snum):
            label = kwargs.pop('label', 'S_' + str(i + 1))
            xdata = __getplotdata(xdatalist[i])
            ydata = __getplotdata(ydatalist[i])
            dataset.addSeries(label, xdata, ydata)
    
    #Create XY1DPlot
    if gca is None:
        plot = XY1DPlot()
    else:
        if isinstance(gca, XY1DPlot):
            plot = gca
        else:
            plot = XY1DPlot()
    
    if xaxistype == 'lon':
        plot.setXAxis(LonLatAxis('Longitude', True, True))
    elif xaxistype == 'lat':
        plot.setXAxis(LonLatAxis('Latitude', True, False))
    elif xaxistype == 'time':
        plot.setXAxis(TimeAxis('Time', True))
    timetickformat = kwargs.pop('timetickformat', None)
    if not timetickformat is None:
        if not xaxistype == 'time':
            plot.setXAxis(TimeAxis('Time', True))
        plot.getAxis(Location.BOTTOM).setTimeFormat(timetickformat)
        plot.getAxis(Location.TOP).setTimeFormat(timetickformat)
    plot.setDataset(dataset)
            
    #Set plot data styles
    lines = []
    legend = kwargs.pop('legend', None)
    if not legend is None:
        lbs = legend.getLegendBreaks()
        for i in range(0, snum):
            line = lbs[i]
            plot.setLegendBreak(i, line)
            lines.append(line)
    else:
        if styles != None:
            for i in range(0, len(styles)):
                idx = dataset.getSeriesCount() - len(styles) + i
                #print 'Series index: ' + str(idx)
                line = __setplotstyle(plot, idx, styles[i], len(xdatalist[i]), **kwargs)
                lines.append(line)
        else:
            for i in range(0, snum):
                idx = dataset.getSeriesCount() - snum + i
                line = __setplotstyle(plot, idx, None, 1, **kwargs)
                lines.append(line)
    
    #Paint dataset
    if chartpanel is None:
        figure()
        
    chart = chartpanel.getChart()
    if gca is None or (not isinstance(gca, XY1DPlot)):
        chart.clearPlots()
        chart.setPlot(plot)
    gca = plot
    #chart.setAntiAlias(True)
    chartpanel.setChart(chart)
    draw_if_interactive()
    if len(lines) > 1:
        return lines
    else:
        return lines[0]

def errorbar(x, y, yerr=None, xerr=None, fmt='', **kwargs):
    global gca
    if gca is None:
        dataset = XYListDataset()
    else:
        dataset = gca.getDataset()
        if dataset is None:
            dataset = XYListDataset()    
    
    #Add data series
    label = kwargs.pop('label', 'S_0')
    xdata = __getplotdata(x)
    ydata = __getplotdata(y)
    esdata = XYErrorSeriesData()
    esdata.setKey(label)
    esdata.setXdata(xdata)
    esdata.setYdata(ydata)
    if not yerr is None:
        if not isinstance(yerr, (int, float)):
            yerr = __getplotdata(yerr)
        esdata.setYerror(yerr)
    if not xerr is None:
        if not isinstance(xerr, (int, float)):
            xerr = __getplotdata(xerr)
        esdata.setXerror(xerr)
    dataset.addSeries(esdata)
    
    #Create XY1DPlot
    if gca is None:
        plot = XY1DPlot(dataset)
    else:
        plot = gca
        plot.setDataset(dataset)
    
    #Set plot data styles
    idx = dataset.getSeriesCount() - 1
    if fmt == '':
        line = __setplotstyle(plot, idx, None, 1, **kwargs)
    else:
        line = __setplotstyle(plot, idx, fmt, len(x), **kwargs)
    
    #Paint dataset
    if chartpanel is None:
        figure()
        
    chart = chartpanel.getChart()
    if gca is None:
        chart.clearPlots()
        chart.setPlot(plot)
    #chart.setAntiAlias(True)
    chartpanel.setChart(chart)
    gca = plot
    draw_if_interactive()
    return line 
        
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
    :param edgecolor: (*Color*) Optional, the color of the bar edge.
    :param linewidth: (*int*) Optional, width of bar edge.
    :param label: (*string*) Label of the bar series.
    :param hatch: (*string*) Hatch string.
    :param hatchsize: (*int*) Hatch size. Default is None (8).
    :param bgcolor: (*Color*) Background color, only valid with hatch.
    
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
    if gca is None:
        dataset = XYListDataset()
    else:
        dataset = gca.getDataset()
        if dataset is None:
            dataset = XYListDataset()
    
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
    else:
        xdata = __getplotdata(xdata)
    ydata = __getplotdata(ydata)
    esdata = XYErrorSeriesData()
    esdata.setKey(label)
    esdata.setXdata(xdata)
    esdata.setYdata(ydata)
    yerr = kwargs.pop('yerr', None)
    if not yerr is None:
        if not isinstance(yerr, (int, float)):
            yerr = __getplotdata(yerr)
        esdata.setYerror(yerr)
    bottom = kwargs.pop('bottom', None)
    if not bottom is None:
        esdata.setBottom(bottom)
    dataset.addSeries(esdata)   

    #Create bar plot
    if gca is None:
        plot = XY1DPlot()
    else:
        if isinstance(gca, XY1DPlot):
            plot = gca
        else:
            plot = XY1DPlot()
    plot.setDataset(dataset)
    if not autowidth:
        plot.setAutoBarWidth(autowidth)
        plot.setBarWidth(width)
    
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
    slb = SeriesLegend()
    for color in colors:
        lb = PolygonBreak()
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
        slb.addLegendBreak(lb)
    slb.setPlotMethod(ChartPlotMethod.BAR)
    ecolor = kwargs.pop('ecolor', 'k')
    ecolor = __getcolor(ecolor)
    slb.setErrorColor(ecolor)
    plot.setLegendBreak(dataset.getSeriesCount() - 1, slb)
    
    #Create figure
    if chartpanel is None:
        figure()
    
    #Set chart
    chart = chartpanel.getChart()
    if gca is None or (not isinstance(gca, XY1DPlot)):
        chart.setCurrentPlot(plot)
    chartpanel.setChart(chart)
    gca = plot
    draw_if_interactive()
    return lb
        
def hist(x, bins=10, range=None, normed=False, cumulative=False,
        bottom=None, histtype='bar', align='mid',
        orientation='vertical', rwidth=None, log=False, **kwargs):
    
    return None
    
def scatter(x, y, s=8, c='b', marker='o', cmap=None, norm=None, vmin=None, vmax=None,
            alpha=None, linewidth=None, verts=None, hold=None, **kwargs):
    """
    Make a scatter plot of x vs y, where x and y are sequence like objects of the same lengths.
    
    :param x: (*array_like*) Input x data.
    :param y: (*array_like*) Input y data.
    :param s: (*int*) Size of points.
    :param c: (*Color*) Color of the points.
    :param marker: (*string*) Marker of the points.
    :param label: (*string*) Label of the points series.
    
    :returns: Points legend break.
    """
    #Get dataset
    global gca
    if gca is None:
        dataset = XYListDataset()
    else:
        dataset = gca.getDataset()
        if dataset is None:
            dataset = XYListDataset()    
    
    #Add data series
    label = kwargs.pop('label', 'S_0')
    xdata = __getplotdata(x)
    ydata = __getplotdata(y)
    dataset.addSeries(label, xdata, ydata)
    
    #Create XY1DPlot
    if gca is None:
        plot = XY1DPlot(dataset)
    else:
        plot = gca
        plot.setDataset(dataset)
    
    #Set plot data styles
    pb, isunique = __getlegendbreak('point', kwargs)
    pb.setCaption(label)
    plot.setLegendBreak(dataset.getSeriesCount() - 1, pb)
    
    #Paint dataset
    if chartpanel is None:
        figure()
        
    chart = chartpanel.getChart()
    if gca is None:
        chart.clearPlots()
        chart.setPlot(plot)
    #chart.setAntiAlias(True)
    chartpanel.setChart(chart)
    gca = plot
    draw_if_interactive()
    return pb 
 
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
        
def show(newfig=True):
    if milapp == None:
        if not batchmode:            
            form = ChartForm(chartpanel)
            chartpanel.paintGraphics()
            form.setSize(600, 500)
            form.setLocationRelativeTo(None)
            form.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE)
            form.setVisible(True)     
    else:
        figureDock = milapp.getFigureDock()
        if newfig:
            figureDock.addFigure(chartpanel)
        else:
            if figureDock.getCurrentFigure() is None:
                figureDock.addFigure(chartpanel)
            else:
                figureDock.setCurrentFigure(chartpanel)
    
# Set figure background color
def bgcolor(color):
    chart = chartpanel.getChart()
    if color is None:
        chart.setDrawBackground(False)
    else:
        chart.setDrawBackground(True)
        chart.setBackground(__getcolor(color))
    draw_if_interactive()    
    
def subplot(nrows, ncols, plot_number):
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
    gca = chart.getPlot(plot_number)
    chart.setCurrentPlot(plot_number - 1)
    if gca is None:
        gca = XY1DPlot()
        gca.isSubPlot = True
        plot_number -= 1
        rowidx = plot_number / ncols
        colidx = plot_number % ncols
        gca.rowIndex = rowidx
        gca.columnIndex = colidx
        chart.addPlot(gca)
        chart.setCurrentPlot(chart.getPlots().size() - 1)
    #gca = plot
    
    return plot
    
def currentplot(plot_number):
    if chartpanel is None:
        figure()
        
    global gca
    chart = chartpanel.getChart()
    gca = chart.getPlot(plot_number)
    chart.setCurrentPlot(plot_number - 1)
    
    return plot
    
def axes(**kwargs):
    """
    Add an axes to the figure.
    
    :param position: (*list*) Optional, axes position specified by *position=* [left, bottom, width
        height] in normalized (0, 1) units. Default is [0.13, 0.11, 0.775, 0.815].
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
    if chartpanel is None:
        figure()
        
    position = kwargs.pop('position', [0.13, 0.11, 0.775, 0.815])
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
    xreverse = kwargs.pop('xreverse', False)
    yreverse = kwargs.pop('yreverse', False)
    xaxistype = kwargs.pop('xaxistype', 'normal')
    bgcobj = kwargs.pop('bgcolor', None)    
    plot = XY1DPlot()
    plot.setPosition(position[0], position[1], position[2], position[3])    
    if bottomaxis == False:
        plot.getAxis(Location.BOTTOM).setVisible(False)
    if leftaxis == False:
        plot.getAxis(Location.LEFT).setVisible(False)
    if topaxis == False:
        plot.getAxis(Location.TOP).setVisible(False)
    if rightaxis == False:
        plot.getAxis(Location.RIGHT).setVisible(False)
    if xreverse:
        plot.getXAxis().setInverse(True)
    if yreverse:
        plot.getYAxis().setInverse(True)
    if xaxistype == 'lon':
        plot.setXAxis(LonLatAxis('Longitude', True, True))
    elif xaxistype == 'lat':
        plot.setXAxis(LonLatAxis('Latitude', True, False))
    elif xaxistype == 'time':
        plot.setXAxis(TimeAxis('Time', True))
    if not bgcobj is None:
        bgcolor = __getcolor(bgcobj)
        plot.setDrawBackground(True)
        plot.setBackground(bgcolor)
    tickfontname = kwargs.pop('tickfontname', 'Arial')
    tickfontsize = kwargs.pop('tickfontsize', 14)
    tickbold = kwargs.pop('tickbold', False)
    if tickbold:
        font = Font(tickfontname, Font.BOLD, tickfontsize)
    else:
        font = Font(tickfontname, Font.PLAIN, tickfontsize)
    plot.setAxisLabelFont(font)
    chart = chartpanel.getChart()
    chart.setCurrentPlot(plot)
    global gca
    gca = plot
    return plot

def axesm(**kwargs):  
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
    :param frameon: (*boolean*) Optional, set frame visible or not. Default is ``True`` .
    :param tickfontname: (*string*) Optional, set axis tick labels font name. Default is ``Arial`` .
    :param tickfontsize: (*int*) Optional, set axis tick labels font size. Default is 14.
    :param tickbold: (*boolean*) Optional, set axis tick labels font bold or not. Default is ``False`` .
    
    :returns: The map axes.
    """
    if chartpanel is None:
        figure()
        
    position = kwargs.pop('position', [0.13, 0.11, 0.775, 0.815])
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
        
    gridlabel = kwargs.pop('gridlabel', True)
    gridline = kwargs.pop('gridline', False)
    griddx = kwargs.pop('griddx', 10)
    griddy = kwargs.pop('griddy', 10)
    frameon = kwargs.pop('frameon', True)
    axison = kwargs.pop('axison', None)
    bgcobj = kwargs.pop('bgcolor', None)
    xyscale = kwargs.pop('xyscale', 1)
    
    global gca
    mapview = MapView()
    mapview.setXYScaleFactor(xyscale)
    gca = MapPlot(mapview)    
    gca.setPosition(position[0], position[1], position[2], position[3])
    tickfontname = kwargs.pop('tickfontname', 'Arial')
    tickfontsize = kwargs.pop('tickfontsize', 14)
    tickbold = kwargs.pop('tickbold', False)
    if tickbold:
        font = Font(tickfontname, Font.BOLD, tickfontsize)
    else:
        font = Font(tickfontname, Font.PLAIN, tickfontsize)
    gca.setAxisLabelFont(font)
    if not axison is None:
        gca.setAxisOn(axison)
    else:
        if bottomaxis == False:
            gca.getAxis(Location.BOTTOM).setVisible(False)
        if leftaxis == False:
            gca.getAxis(Location.LEFT).setVisible(False)
        if topaxis == False:
            gca.getAxis(Location.TOP).setVisible(False)
        if rightaxis == False:
            gca.getAxis(Location.RIGHT).setVisible(False)
    mapframe = gca.getMapFrame()
    mapframe.setDrawGridLabel(gridlabel)
    mapframe.setDrawGridTickLine(gridlabel)
    mapframe.setDrawGridLine(gridline)
    mapframe.setGridXDelt(griddx)
    mapframe.setGridYDelt(griddy)
    gca.setDrawNeatLine(frameon)
    if not bgcobj is None:
        bgcolor = __getcolor(bgcobj)
        gca.setDrawBackground(True)
        gca.setBackground(bgcolor)
    gca.getMapView().projectLayers(projinfo)
    chart = chartpanel.getChart()
    if chart.getPlot() is None:
        chart.addPlot(gca)
    else:
        chart.setCurrentPlot(gca)
    return gca, projinfo
    
def twinx(ax):
    """
    Make a second axes that shares the x-axis. The new axes will overlay *ax*. The ticks 
    for *ax2* will be placed on the right, and the *ax2* instance is returned.
    
    :param ax: Existing axes.
    
    :returns: The second axes
    """
    ax.getAxis(Location.RIGHT).setVisible(False)
    ax.setSameShrink(True)
    plot = XY1DPlot()
    plot.setSameShrink(True)
    plot.setPosition(ax.getPosition())
    plot.getAxis(Location.BOTTOM).setVisible(False)
    plot.getAxis(Location.LEFT).setVisible(False)
    plot.getAxis(Location.TOP).setVisible(False)
    axis = plot.getAxis(Location.RIGHT)
    axis.setDrawTickLabel(True)
    axis.setDrawLabel(True)
    chartpanel.getChart().addPlot(plot)
    global gca
    gca = plot
    return plot

def xaxis(ax=None, **kwargs):
    """
    Set y axis of the axes.
    
    :param ax: The axes.
    :param color: (*Color*) Color of the y axis. Default is 'black'.
    :param shift: (*int) Y axis shif along x direction. Units is pixel. Default is 0.
    """
    if ax is None:
        ax = gca
    shift = kwargs.pop('shift', 0)
    color = kwargs.pop('color', 'black')
    c = __getcolor(color)
    minortick = kwargs.pop('minortick', False)
    locs = [Location.BOTTOM, Location.TOP]
    for loc in locs:
        axis = ax.getAxis(loc)
        axis.setShift(shift)
        axis.setColor_All(c)
        axis.setMinorTickVisible(minortick)
    draw_if_interactive
    
def yaxis(ax=None, **kwargs):
    """
    Set y axis of the axes.
    
    :param ax: The axes.
    :param color: (*Color*) Color of the y axis. Default is 'black'.
    :param shift: (*int) Y axis shif along x direction. Units is pixel. Default is 0.
    """
    if ax is None:
        ax = gca
    shift = kwargs.pop('shift', 0)
    color = kwargs.pop('color', 'black')
    c = __getcolor(color)
    minortick = kwargs.pop('minortick', False)
    locs = [Location.LEFT, Location.RIGHT]
    for loc in locs:
        axis = ax.getAxis(loc)
        axis.setShift(shift)
        axis.setColor_All(c)
        axis.setMinorTickVisible(minortick)
    draw_if_interactive
    
def antialias(b=True):
    """
    Set figure antialias or not.
    
    :param b: (*boolean*) Set figure antialias or not. Default is ``False`` .
    """
    if chartpanel is None:
        figure()
        
    chartpanel.getChart().setAntiAlias(b)
    draw_if_interactive()
    
def savefig(fname, width=None, height=None, dpi=None):
    """
    Save the current figure.
    
    :param fname: (*string*) A string containing a path to a filename. The output format
        is deduced from the extention of the filename. Supported format: 'png', 'bmp',
        'jpg', 'eps' and 'pdf'.
    :param width: (*int*) Optional, width of the output figure with pixel units. Default
        is None, the output figure size is same as *figures* window.
    :param height: (*int*) Optional, height of the output figure with pixel units. Default
        is None, the output figure size is same as *figures* window.
    """
    if (not width is None) and (not height is None):
        chartpanel.setSize(width, height)
    chartpanel.paintGraphics()
    if dpi != None:
        chartpanel.saveImage(fname, dpi)
    else:
        chartpanel.saveImage(fname)   
        
def savefig_jpeg(fname, width=None, height=None, dpi=None):
    if (not width is None) and (not height is None):
        chartpanel.setSize(width, height)
    chartpanel.paintGraphics()
    if not dpi is None:
        chartpanel.saveImage_Jpeg(fname, dpi)
    else:
        chartpanel.saveImage(fname)  

# Clear current axes
def cla():
    global gca
    if not gca is None:
        chartpanel.getChart().removePlot(gca)
        gca = None
        draw_if_interactive()

# Clear current figure    
def clf():
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
    if not gca is None:
        if isinstance(gca, XY1DPlot):
            gca.removeLastSeries()
        elif isinstance(gca, XY2DPlot):
            gca.removeLastLayer()
        draw_if_interactive()

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
        if lineStyle is None:           
            pb = PointBreak()
            pb.setCaption(caption)
            if '.' in style:
                pb.setSize(4)
                pb.setDrawOutline(False)
            else:
                pb.setSize(8)
            pb.setStyle(pointStyle)
            if not c is None:
                pb.setColor(c)
            return pb
        else:
            plb = PolylineBreak()
            plb.setCaption(caption)
            plb.setSize(linewidth)
            plb.setStyle(lineStyle)
            plb.setDrawSymbol(True)
            plb.setSymbolStyle(pointStyle)
            plb.setSymbolInterval(__getsymbolinterval(n))
            if not c is None:
                plb.setColor(c)
                plb.setSymbolColor(c)
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
    
def __getcolor(style):
    if style is None:
        return None
        
    if isinstance(style, Color):
        return style
        
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
    elif isinstance(style, tuple) or isinstance(style, list):
        if len(style) == 3:
            c = Color(style[0], style[1], style[2])
        else:
            c = Color(style[0], style[1], style[2], style[3])
               
    return c

def __getcolors(cs):
    colors = []
    for c in cs:
        colors.append(__getcolor(c))
    return colors
    
def __getsymbolinterval(n):
    i = 1
    v = 20
    if n < v:
        i = 1
    else:
        i = n / v
    
    return i
    
def __getfont(**kwargs):
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
    gca.setTitle(ctitile)
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
    axis = plot.getXAxis()
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
    axis = plot.getYAxis()
    axis.setLabel(label)
    axis.setDrawLabel(True)
    axis.setLabelFont(font)
    axis.setLabelColor(c)
    axis_r = plot.getAxis(Location.RIGHT)
    axis_r.setLabel(label)
    axis_r.setLabelFont(font)
    axis_r.setLabelColor(c)
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
    axis = gca.getXAxis()
    axis_t = gca.getAxis(Location.TOP)
    if len(args) > 0:
        locs = args[0]
        if isinstance(locs, (MIArray, DimArray)):
            locs = locs.aslist()
        axis.setTickLocations(locs)
        axis_t.setTickLocations(locs)
        args = args[1:]
    if len(args) > 0:
        labels = args[0]
        if isinstance(labels, (MIArray, DimArray)):
            labels = labels.aslist()
            axis.setTickLabels_Number(labels)
            axis_t.setTickLabels_Number(labels)
        else:
            axis.setTickLabels(labels)
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
    axis.setTickLabelFont(font)
    axis.setTickLabelColor(c)
    axis_t.setTickLabelFont(font)
    axis_t.setTickLabelColor(c)
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
    axis = gca.getYAxis()
    axis_r = gca.getAxis(Location.RIGHT)
    if len(args) > 0:
        locs = args[0]
        if isinstance(locs, MIArray):
            locs = locs.aslist()
        axis.setTickLocations(locs)
        axis_r.setTickLocations(locs)
        args = args[1:]
    if len(args) > 0:
        labels = args[0]
        if isinstance(labels, (MIArray, DimArray)):
            labels = labels.aslist()
            axis.setTickLabels_Number(labels)
            axis_r.setTickLabels_Number(labels)
        else:
            axis.setTickLabels(labels)
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
    axis_r.setTickLabelFont(font)
    axis_r.setTickLabelColor(c)
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
    coordinates = kwargs.pop('coordinates', 'data')
    text.setCoordinates(coordinates)
    if coordinates == 'figure':
        chartpanel.getChart().addText(text)
    else:
        gca.addText(text)
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
        gca.setDrawExtent(Extent(xmin, xmax, ymin, ymax))
        draw_if_interactive()
    else:
        print 'The limits parameter must be a list with 4 elements: xmin, xmax, ymin, ymax!'
        
def axism(limits=None):
    """
    Sets the min and max of the x and y map axes, with ``[xmin, xmax, ymin, ymax]`` .
    
    :param limits: (*list*) Min and max of the x and y map axes.
    """
    if limits is None:
        gca.setDrawExtent(gca.getMapView().getExtent())
        draw_if_interactive()
    else:
        if len(limits) == 4:
            xmin = limits[0]
            xmax = limits[1]
            ymin = limits[2]
            ymax = limits[3]
            gca.setLonLatExtent(Extent(xmin, xmax, ymin, ymax))
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
    gridline = plot.getGridLine()
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
    linewidth = kwargs.pop('linewidth', 1)
    gridline.setSize(linewidth)
    linestyle = kwargs.pop('linestyle', '--')
    linestyle = __getlinestyle(linestyle)
    gridline.setStyle(linestyle)
    draw_if_interactive()
    
def xlim(xmin, xmax):
    """
    Set the *x* limits of the current axes.
    
    :param xmin: (*float*) Minimum limit of the x axis.
    :param xmax: (*float*) Maximum limit of the x axis.
    """
    plot = gca
    extent = plot.getDrawExtent()
    extent.minX = xmin
    extent.maxX = xmax
    plot.setDrawExtent(extent)
    draw_if_interactive()
            
def ylim(ymin, ymax):
    """
    Set the *y* limits of the current axes.
    
    :param xmin: (*float*) Minimum limit of the y axis.
    :param xmax: (*float*) Maximum limit of the yaxis.
    """
    plot = gca
    extent = plot.getDrawExtent()
    extent.minY = ymin
    extent.maxY = ymax
    plot.setDrawExtent(extent)
    draw_if_interactive()   

def xreverse():
    gca.getXAxis().setInverse(True)
    draw_if_interactive()
    
def yreverse():
    gca.getYAxis().setInverse(True)
    draw_if_interactive()
            
def legend(*args, **kwargs):
    """
    Places a legend on the axes.
    
    :param breaks: (*ColorBreak*) Legend breaks (optional).
    :param labels: (*list of string*) Legend labels (optional).
    :param loc: (*string*) The location of the legend, including: 'upper right', upper left',
        'lower left', 'lower right', 'right', 'ceter left', 'center right', lower center',
        'upper center', 'center' and 'custom'. Default is 'upper right'.
    :param x: (*float*) Location x in normalized (0, 1) units when ``loc=custom`` .
    :param y: (*float*) Location y in normalized (0, 1) units when ``loc=custom`` .
    :param framon: (*boolean*) Control whether a frame should be drawn around the legend. Default
        is True.
    :param background: (*None or color*) Set draw background or not and/or background color.
        Default is None which set not draw background.
    :param fontname: (*string*) Font name. Default is ``Arial`` .
    :param fontsize: (*int*) Font size. Default is ``14`` .
    :param bold: (*boolean*) Is bold font or not. Default is ``False`` .
    :param labcolor: (*color*) Tick label string color. Default is ``black`` .
    """
    plot = gca
    plot.setDrawLegend(True)    
    clegend = plot.getLegend()   
    ls = kwargs.pop('legend', None)
    if ls is None:
        if len(args) > 0:
            lbs = args[0]
            if len(args) == 2:
                for i in range(0, len(lbs)):
                    labels = args[1]
                    lbs[i].setCaption(labels[i])
            ls = LegendScheme()
            ls.setLegendBreaks(lbs)
            if clegend is None:
                clegend = ChartLegend(ls)
                plot.setLegend(clegend)
            else:
                clegend.setLegendScheme(ls)
    else:
        if clegend is None:
            clegend = ChartLegend(ls)
            plot.setLegend(clegend)
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
        
def colorbar(layer, **kwargs):
    """
    Add a colorbar to a plot.
    
    :param layer: (*MapLayer*) The layer in plot.
    :param cmap: (*string*) Color map name. Default is None.
    :param shrink: (*float*) Fraction by which to shrink the colorbar. Default is 1.0.
    :param orientation: (*string*) Colorbar orientation: ``vertical`` or ``horizontal``.
    :param aspect: (*int*) Ratio of long to short dimensions.
    :param fontname: (*string*) Font name. Default is ``Arial`` .
    :param fontsize: (*int*) Font size. Default is ``14`` .
    :param bold: (*boolean*) Is bold font or not. Default is ``False`` .
    :param label: (*string*) Label. Default is ``None`` .
    :param extendrect: (*boolean*) If ``True`` the minimum and maximum colorbar extensions will be
        rectangular (the default). If ``False`` the extensions will be triangular.
    :param extendfrac: [None | 'auto' | length] If set to *None*, both the minimum and maximum triangular
        colorbar extensions with have a length of 5% of the interior colorbar length (the default). If
        set to 'auto', makes the triangular colorbar extensions the same lengths as the interior boxes
        . If a scalar, indicates the length of both the minimum and maximum triangle colorbar extensions
        as a fraction of the interior colorbar length.
    :param ticks: [None | list of ticks] If None, ticks are determined automatically from the input.
    """
    cmap = kwargs.pop('cmap', None)
    shrink = kwargs.pop('shrink', 1)
    orientation = kwargs.pop('orientation', 'vertical')
    aspect = kwargs.pop('aspect', 20)
    fontname = kwargs.pop('fontname', 'Arial')
    fontsize = kwargs.pop('fontsize', 14)
    bold = kwargs.pop('bold', False)
    if bold:
        font = Font(fontname, Font.BOLD, fontsize)
    else:
        font = Font(fontname, Font.PLAIN, fontsize)
    plot = gca
    ls = layer.legend()
    legend = plot.getLegend()
    if legend == None:
        legend = ChartLegend(ls)
        plot.setLegend(legend)
    else:
        legend.setLegendScheme(ls)
    legend.setColorbar(True)   
    legend.setShrink(shrink)
    legend.setAspect(aspect)
    legend.setLabelFont(font)
    label = kwargs.pop('label', None)
    if not label is None:
        legend.setLabel(label)
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
    plot.setDrawLegend(True)
    draw_if_interactive()

def set(obj, **kwargs):
    if isinstance(obj, Plot):
        xminortick = kwargs.pop('xminortick', None)
        if not xminortick is None:
            locs = [Location.BOTTOM, Location.TOP]
            for loc in locs:
                axis = obj.getAxis(loc)
                axis.setMinorTickVisible(xminortick)
        yminortick = kwargs.pop('yminortick', None)
        if not yminortick is None:
            locs = [Location.LEFT, Location.RIGHT]
            for loc in locs:
                axis = obj.getAxis(loc)
                axis.setMinorTickVisible(yminortick)
    draw_if_interactive()
    
def __getcolormap(**kwargs):
    colors = kwargs.pop('colors', None)
    if colors != None:
        if isinstance(colors, str):
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
        cmap = ColorUtil.getColorMap(cmapstr)
    reverse = kwargs.pop('cmapreverse', False)
    if reverse:
        cmap.reverse()
    return cmap
    
def __getlegendscheme(args, min, max, **kwargs):
    ls = kwargs.pop('symbolspec', None)
    if ls is None:
        cmap = __getcolormap(**kwargs)
        ecobj = kwargs.pop('edgecolor', None)
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
    size = kwargs.pop('size', None)
    marker = kwargs.pop('marker', None)
    if not marker is None:
        pstyle = __getpointstyle(marker)
    fcobj = kwargs.pop('facecolor', None)
    if not fcobj is None:
        facecolor = __getcolor(fcobj)
    ecobj = kwargs.pop('edgecolor', None)
    if not ecobj is None:
        edgecolor = __getcolor(ecobj)
    fill = kwargs.pop('fill', None)
    edge = kwargs.pop('edge', None)
    for lb in ls.getLegendBreaks():
        if not fcobj is None:
            lb.setColor(facecolor)
        if not marker is None:
            lb.setStyle(pstyle)
        if not size is None:
            lb.setSize(size)      
        if not ecobj is None:
            lb.setOutlineColor(edgecolor)  
        if not fill is None:
            lb.setDrawFill(fill)  
        if not edge is None:
            lb.setDrawOutline(edge)
    return ls
    
def __setlegendscheme_line(ls, **kwargs):
    ls = ls.convertTo(ShapeTypes.Polyline)
    size = kwargs.pop('size', 1)
    lsobj = kwargs.pop('linestyle', '-')
    linestyle = __getlinestyle(lsobj)
    cobj = kwargs.pop('color', 'k')
    color = __getcolor(cobj)    
    for lb in ls.getLegendBreaks():
        lb.setColor(facecolor)
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
        lb.setOutlineSize(size)        
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
    n = len(args)
    cmap = __getcolormap(**kwargs)
    fill_value = kwargs.pop('fill_value', -9999.0)
    if n <= 2:
        gdata = minum.asgridarray(args[0])
        args = args[1:]
    elif n <=4:
        x = args[0]
        y = args[1]
        a = args[2]
        gdata = minum.asgridarray(a, x, y, fill_value)
        args = args[3:]    
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
    layer = __plot_griddata(gdata, ls, 'imshow')
    return MILayer(layer)
      
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
    
    :returns: (*VectoryLayer*) Contour VectoryLayer created from array data.
    """
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
    layer = __plot_griddata(gdata, ls, 'contour', xaxistype=xaxistype)        
    
    return MILayer(layer)

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
    
    :returns: (*VectoryLayer*) Contour filled VectoryLayer created from array data.
    """
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
    layer = __plot_griddata(gdata, ls, 'contourf', xaxistype=xaxistype)
    return MILayer(layer)

def quiver(*args, **kwargs):
    """
    Plot a 2-D field of arrows.
    
    :param x: (*array_like*) Optional. X coordinate array.
    :param y: (*array_like*) Optional. Y coordinate array.
    :param u: (*array_like*) U component of the arrow vectors (wind field) or wind direction.
    :param v: (*array_like*) V component of the arrow vectors (wind field) or wind speed.
    :param z: (*array_like*) Optional, 2-D z value array.
    :param cmap: (*string*) Color map string.
    :param fill_value: (*float*) Fill_value. Default is ``-9999.0``.
    :param isuv: (*boolean*) Is U/V or direction/speed data array pairs. Default is True.
    :param size: (*float*) Base size of the arrows.
    :param order: (*int*) Z-order of created layer for display.
    
    :returns: (*VectoryLayer*) Created quiver VectoryLayer.
    """
    plot = gca
    cmap = __getcolormap(**kwargs)
    fill_value = kwargs.pop('fill_value', -9999.0)
    order = kwargs.pop('order', None)
    isuv = kwargs.pop('isuv', True)
    n = len(args) 
    iscolor = False
    cdata = None
    if n <= 4:
        udata = minum.asgriddata(args[0])
        vdata = minum.asgriddata(args[1])
        args = args[2:]
        if len(args) > 0:
            cdata = minum.asgriddata(args[0])
            iscolor = True
            args = args[1:]
    elif n <= 6:
        x = args[0]
        y = args[1]
        u = args[2]
        v = args[3]
        udata = minum.asgriddata(u, x, y, fill_value)
        vdata = minum.asgriddata(v, x, y, fill_value)
        args = args[4:]
        if len(args) > 0:
            cdata = minum.asgriddata(args[0], x, y, fill_value)
            iscolor = True
            args = args[1:]
    if iscolor:
        if len(args) > 0:
            level_arg = args[0]
            if isinstance(level_arg, int):
                cn = level_arg
                ls = LegendManage.createLegendScheme(cdata.min(), cdata.max(), cn, cmap)
            else:
                if isinstance(level_arg, MIArray):
                    level_arg = level_arg.aslist()
                ls = LegendManage.createLegendScheme(cdata.min(), cdata.max(), level_arg, cmap)
        else:
            ls = LegendManage.createLegendScheme(cdata.min(), cdata.max(), cmap)
    else:    
        if cmap.getColorCount() == 1:
            c = cmap.getColor(0)
        else:
            c = Color.black
        ls = LegendManage.createSingleSymbolLegendScheme(ShapeTypes.Point, c, 10)
    ls = __setlegendscheme_point(ls, **kwargs)
    layer = __plot_uvgriddata(udata, vdata, cdata, ls, 'quiver', isuv)
    udata = None
    vdata = None
    cdata = None
    return MILayer(layer)
    
def barbs(*args, **kwargs):
    """
    Plot a 2-D field of barbs.
    
    :param x: (*array_like*) Optional. X coordinate array.
    :param y: (*array_like*) Optional. Y coordinate array.
    :param u: (*array_like*) U component of the arrow vectors (wind field) or wind direction.
    :param v: (*array_like*) V component of the arrow vectors (wind field) or wind speed.
    :param z: (*array_like*) Optional, 2-D z value array.
    :param cmap: (*string*) Color map string.
    :param fill_value: (*float*) Fill_value. Default is ``-9999.0``.
    :param isuv: (*boolean*) Is U/V or direction/speed data array pairs. Default is True.
    :param size: (*float*) Base size of the arrows.
    :param order: (*int*) Z-order of created layer for display.
    
    :returns: (*VectoryLayer*) Created barbs VectoryLayer.
    """
    plot = gca
    cmap = __getcolormap(**kwargs)
    fill_value = kwargs.pop('fill_value', -9999.0)
    order = kwargs.pop('order', None)
    isuv = kwargs.pop('isuv', True)
    n = len(args) 
    iscolor = False
    cdata = None
    if n <= 4:
        udata = minum.asgriddata(args[0])
        vdata = minum.asgriddata(args[1])
        args = args[2:]
        if len(args) > 0:
            cdata = minum.asgriddata(args[0])
            iscolor = True
            args = args[1:]
    elif n <= 6:
        x = args[0]
        y = args[1]
        u = args[2]
        v = args[3]
        udata = minum.asgriddata(u, x, y, fill_value)
        vdata = minum.asgriddata(v, x, y, fill_value)
        args = args[4:]
        if len(args) > 0:
            cdata = minum.asgriddata(args[0], x, y, fill_value)
            iscolor = True
            args = args[1:]
    if iscolor:
        if len(args) > 0:
            level_arg = args[0]
            if isinstance(level_arg, int):
                cn = level_arg
                ls = LegendManage.createLegendScheme(cdata.min(), cdata.max(), cn, cmap)
            else:
                if isinstance(level_arg, MIArray):
                    level_arg = level_arg.aslist()
                ls = LegendManage.createLegendScheme(cdata.min(), cdata.max(), level_arg, cmap)
        else:
            ls = LegendManage.createLegendScheme(cdata.min(), cdata.max(), cmap)
    else:    
        if cmap.getColorCount() == 1:
            c = cmap.getColor(0)
        else:
            c = Color.black
        ls = LegendManage.createSingleSymbolLegendScheme(ShapeTypes.Point, c, 10)
    ls = __setlegendscheme_point(ls, **kwargs)
    layer = __plot_uvgriddata(udata, vdata, cdata, ls, 'barbs', isuv)
    udata = None
    vdata = None
    cdata = None
    return MILayer(layer)
    
def __plot_griddata(gdata, ls, type, xaxistype=None):
    #print 'GridData...'
    if type == 'contourf':
        layer = DrawMeteoData.createShadedLayer(gdata.data, ls, 'layer', 'data', True)
    elif type == 'contour':
        layer = DrawMeteoData.createContourLayer(gdata.data, ls, 'layer', 'data', True)
    elif type == 'imshow':
        layer = DrawMeteoData.createRasterLayer(gdata, 'layer', ls)
    
    #Create XY2DPlot
    global gca
    if gca is None:
        mapview = MapView()
        plot = XY2DPlot(mapview)
    else:
        if isinstance(gca, XY2DPlot):
            plot = gca
        else:
            mapview = MapView()
            plot = XY2DPlot(mapview)
    
    if xaxistype == 'lon':
        plot.setXAxis(LonLatAxis('Longitude', True, True))
    elif xaxistype == 'lat':
        plot.setXAxis(LonLatAxis('Latitude', True, False))
    elif xaxistype == 'time':
        plot.setXAxis(TimeAxis('Time', True))
    
    plot.addLayer(layer)
    plot.setDrawExtent(layer.getExtent().clone())
    
    if chartpanel is None:
        figure()
        
    chart = chartpanel.getChart()
    if gca is None or (not isinstance(gca, XY2DPlot)):
        chart.setCurrentPlot(plot)
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
    plot = XY2DPlot(mapview)
    plot.addLayer(layer)
    plot.setDrawExtent(layer.getExtent().clone())
    
    if chartpanel is None:
        figure()
    
    chart = Chart(plot)
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
        if a.rank == 1:
            gdata = minum.asstationdata(a, x, y, fill_value)
        else:
            if a.asarray().getSize() == x.asarray().getSize():
                gdata = minum.asstationdata(a, x, y, fill_value)                
            else:
                gdata = minum.asgriddata(a, x, y, fill_value)
        
    ls = __getlegendscheme(args, gdata.min(), gdata.max(), **kwargs)
    if 'symbolspec' in kwargs:
        __setlegendscheme(ls, **kwargs)
    else:
        ls = __setlegendscheme_point(ls, **kwargs)    
    if isinstance(gdata, PyGridData):
        layer = __plot_griddata_m(plot, gdata, ls, 'scatter', proj=proj, order=order)
    else:
        layer = __plot_stationdata_m(plot, gdata, ls, 'scatter', proj=proj, order=order)
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
 
    gca.addLayer(layer)
    gca.setDrawExtent(layer.getExtent())
    
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
 
    gca.addLayer(layer)
    gca.setDrawExtent(layer.getExtent())
    
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
    :param proj: (*ProjectionInfo*) Map projection of the data. Default is None.
    :param order: (*int*) Z-order of created layer for display.
    
    :returns: (*RasterLayer*) RasterLayer created from array data.
    """
    plot = gca
    cmap = __getcolormap(**kwargs)
    fill_value = kwargs.pop('fill_value', -9999.0)
    proj = kwargs.pop('proj', None)
    order = kwargs.pop('order', None)
    n = len(args) 
    if n <= 2:
        gdata = minum.asgridarray(args[0])
        args = args[1:]
    elif n <=4:
        x = args[0]
        y = args[1]
        a = args[2]
        gdata = minum.asgridarray(a, x, y, fill_value)
        args = args[3:]
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
        #ls = LegendManage.createLegendScheme(gdata.getminvalue(), gdata.getmaxvalue(), cmap)
        ls = LegendManage.createImageLegend(gdata, cmap)
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
        string, like ‘r’ or ‘red’, all levels will be plotted in this color. If a tuple of matplotlib 
        color args (string, float, rgb, etc), different levels will be plotted in different colors in 
        the order specified.
    :param fill_value: (*float*) Fill_value. Default is ``-9999.0``.
    :param proj: (*ProjectionInfo*) Map projection of the data. Default is None.
    :param isplot: (*boolean*) Plot layer or not. Default is ``True``.
    :param order: (*int*) Z-order of created layer for display.
    
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
    isplot = kwargs.pop('isplot', True)
    if isplot:
        plot = gca
    else:
        plot = None
    layer = __plot_griddata_m(plot, gdata, ls, 'contour', proj=proj, order=order)
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
    if isplot:
        plot = gca
    else:
        plot = None
    layer = __plot_griddata_m(plot, gdata, ls, 'contourf', proj=proj, order=order)
    gdata = None
    return MILayer(layer)
    
def gridfm(*args, **kwargs):
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
        if a.rank == 2 and a.asarray().getSize() != x.asarray().getSize():            
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

    gdata = None
    return MILayer(layer)
    
def surfacem(*args, **kwargs):
    plot = gca
    fill_value = kwargs.pop('fill_value', -9999.0)
    proj = kwargs.pop('proj', None)    
    order = kwargs.pop('order', None)
    n = len(args) 
    if n <= 2:
        a = args[0]
        y = minum.linspace(1, a.shape[1], 1)
        x = minum.linspace(1, a.shape[0], 1)
        args = args[1:]
    elif n <=4:
        x = args[0]
        y = args[1]
        a = args[2]
        if a.rank == 2 and a.asarray().getSize() != x.asarray().getSize():            
            x, y = minum.meshgrid(x, y)        
        args = args[3:]
    ls = __getlegendscheme(args, a.min(), a.max(), **kwargs)   
    
    if plot.getProjInfo().isLonLat():
        lonlim = 90
    else:
        lonlim = 0
        x, y = minum.project(x, y, toproj=plot.getProjInfo())
    layer = ArrayUtil.meshLayer(x.asarray(), y.asarray(), a.asarray(), ls, lonlim)
    layer.setProjInfo(plot.getProjInfo())
    shapetype = layer.getShapeType()
    if order is None:
        if shapetype == ShapeTypes.Polygon or shapetype == ShapeTypes.Image:
            plot.addLayer(0, layer)
        else:
            plot.addLayer(layer)
    else:
        plot.addLayer(order, layer)
    plot.setDrawExtent(layer.getExtent())
    
    if chartpanel is None:
        figure()
    
    chart = Chart(plot)
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
    :param cmap: (*string*) Color map string.
    :param fill_value: (*float*) Fill_value. Default is ``-9999.0``.
    :param isuv: (*boolean*) Is U/V or direction/speed data array pairs. Default is True.
    :param size: (*float*) Base size of the arrows.
    :param proj: (*ProjectionInfo*) Map projection of the data. Default is None.
    :param order: (*int*) Z-order of created layer for display.
    
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
            level_arg = args[0]
            if isinstance(level_arg, int):
                cn = level_arg
                ls = LegendManage.createLegendScheme(cdata.min(), cdata.max(), cn, cmap)
            else:
                if isinstance(level_arg, MIArray):
                    level_arg = level_arg.aslist()
                ls = LegendManage.createLegendScheme(cdata.min(), cdata.max(), level_arg, cmap)
        else:
            ls = LegendManage.createLegendScheme(cdata.min(), cdata.max(), cmap)
    else:    
        if cmap.getColorCount() == 1:
            c = cmap.getColor(0)
        else:
            c = Color.black
        ls = LegendManage.createSingleSymbolLegendScheme(ShapeTypes.Point, c, 10)
    ls = __setlegendscheme_point(ls, **kwargs)
    layer = __plot_uvdata_m(plot, x, y, u, v, cdata, ls, 'quiver', isuv, proj=proj)
    udata = None
    vdata = None
    cdata = None
    return MILayer(layer)
    
def quiverkey(*args, **kwargs):
    """
    Add a key to a quiver plot.
    
    :param Q: (*MILayer*) The quiver layer instance returned by a call to quiver/quiverm.
    :param X: (*float*) The location x of the key.
    :param Y: (*float*) The location y of the key.
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
    wa.setLayer(Q.layer)
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
    gca.setWindArrow(wa)
    draw_if_interactive()
    
def barbsm(*args, **kwargs):
    """
    Plot a 2-D field of barbs in a map.
    
    :param x: (*array_like*) Optional. X coordinate array.
    :param y: (*array_like*) Optional. Y coordinate array.
    :param u: (*array_like*) U component of the arrow vectors (wind field) or wind direction.
    :param v: (*array_like*) V component of the arrow vectors (wind field) or wind speed.
    :param z: (*array_like*) Optional, 2-D z value array.
    :param cmap: (*string*) Color map string.
    :param fill_value: (*float*) Fill_value. Default is ``-9999.0``.
    :param isuv: (*boolean*) Is U/V or direction/speed data array pairs. Default is True.
    :param size: (*float*) Base size of the arrows.
    :param proj: (*ProjectionInfo*) Map projection of the data. Default is None.
    :param order: (*int*) Z-order of created layer for display.
    
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
            level_arg = args[0]
            if isinstance(level_arg, int):
                cn = level_arg
                ls = LegendManage.createLegendScheme(cdata.min(), cdata.max(), cn, cmap)
            else:
                if isinstance(level_arg, MIArray):
                    level_arg = level_arg.aslist()
                ls = LegendManage.createLegendScheme(cdata.min(), cdata.max(), level_arg, cmap)
        else:
            ls = LegendManage.createLegendScheme(cdata.min(), cdata.max(), cmap)
    else:    
        if cmap.getColorCount() == 1:
            c = cmap.getColor(0)
        else:
            c = Color.black
        ls = LegendManage.createSingleSymbolLegendScheme(ShapeTypes.Point, c, 10)
    ls = __setlegendscheme_point(ls, **kwargs)
    layer = __plot_uvdata_m(plot, x, y, u, v, cdata, ls, 'barbs', isuv, proj=proj)
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
    if n <= 4:
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
    udata = None
    vdata = None
    return MILayer(layer)
        
def __plot_griddata_m(plot, gdata, ls, type, proj=None, order=None):
    #print 'GridData...'
    if type == 'contourf':
        layer = DrawMeteoData.createShadedLayer(gdata.data, ls, 'layer', 'data', True)
    elif type == 'contour':
        layer = DrawMeteoData.createContourLayer(gdata.data, ls, 'layer', 'data', True)
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
        
    if not plot is None:
        shapetype = layer.getShapeType()
        if order is None:
            if shapetype == ShapeTypes.Polygon or shapetype == ShapeTypes.Image:
                plot.addLayer(0, layer)
            else:
                plot.addLayer(layer)
        else:
            plot.addLayer(order, layer)
        plot.setDrawExtent(layer.getExtent().clone())
        
        if chartpanel is None:
            figure()
        
        #chart = Chart(plot)
        #chart.setAntiAlias(True)
        #chartpanel.setChart(chart)
        #global gca
        #gca = plot
        draw_if_interactive()
    return layer
    
def __plot_stationdata_m(plot, stdata, ls, type, proj=None, order=None):
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
 
    plot.addLayer(layer)
    plot.setDrawExtent(layer.getExtent().clone())
    
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
    #print 'GridData...'
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
    plot.addLayer(layer)
    plot.setDrawExtent(layer.getExtent().clone())
    
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
    plot.addLayer(layer)
    plot.setDrawExtent(layer.getExtent().clone())
    
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
    font = __getfont(**kwargs)
    cstr = kwargs.pop('color', 'black')
    color = __getcolor(cstr)
    labelset = layer.layer.getLabelSet()
    labelset.setLabelFont(font)
    labelset.setLabelColor(color)
    dynamic = kwargs.pop('dynamic', True)
    if dynamic:
        layer.layer.addLabelsContourDynamic(layer.layer.getExtent())
    else:
        layer.layer.addLabels()
    draw_if_interactive()
        
def worldmap():
    mapview = MapView()
    mapview.setXYScaleFactor(1.0)
    #print 'Is GeoMap: ' + str(mapview.isGeoMap())
    plot = MapPlot(mapview)
    chart = chartpanel.getChart()
    chart.clearPlots()
    chart.setPlot(plot)
    global gca
    gca = plot
    return plot    
        
def geoshow(*args, **kwargs):
    plot = gca
    if len(args) == 1:
        layer = args[0]
        layer = layer.layer   
        visible = kwargs.pop('visible', True)
        layer.setVisible(visible)
        if layer.getLayerType() == LayerTypes.ImageLayer:     
            plot.addLayer(layer)
        else:
            #LegendScheme
            ls = kwargs.pop('symbolspec', None)
            if ls is None:
                if 'facecolor' in kwargs or 'edgecolor' in kwargs or 'size' in kwargs:
                    fcobj = kwargs.pop('facecolor', None)
                    ecobj = kwargs.pop('edgecolor', None)
                    if fcobj is None:
                        facecolor = Color.lightGray
                        drawfill = False
                    else:
                        facecolor = __getcolor(fcobj)
                        drawfill = True
                    if ecobj is None:
                        drawline = False  
                        edgecolor = Color.black
                    else:
                        drawline = True
                        edgecolor = __getcolor(ecobj)            
                    size = kwargs.pop('size', None)
                    lb = layer.getLegendScheme().getLegendBreaks().get(0)
                    lb.setColor(facecolor)
                    btype = lb.getBreakType()
                    if btype == BreakTypes.PointBreak:
                        if size is None:
                            size = 6
                        lb.setSize(size)
                        lb.setDrawOutline(drawline)
                        lb.setOutlineColor(edgecolor)        
                    elif btype == BreakTypes.PolylineBreak:
                        if size is None:
                            size = 1
                        lb.setSize(size)
                    elif btype == BreakTypes.PolygonBreak:
                        lb.setDrawFill(drawfill)
                        lb.setDrawOutline(drawline)
                        lb.setOutlineColor(edgecolor)
                        if size is None:
                            size = 1
                        lb.setOutlineSize(size)
            else:
                layer.setLegendScheme(ls)
            plot.addLayer(layer)
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
                xoffset = kwargs.pop('xoffset', 0)
                labelset.setXOffset(xoffset)
                yoffset = kwargs.pop('yoffset', 0)
                labelset.setYOffset(yoffset)
                avoidcoll = kwargs.pop('avoidcoll', True)
                labelset.setAvoidCollision(avoidcoll)
                layer.addLabels()   
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

        lbreak, isunique = __getlegendbreak(displaytype, kwargs)
        if displaytype == 'point':
            plot.addPoint(lat, lon, lbreak)
        elif displaytype == 'polyline' or displaytype == 'line':
            plot.addPolyline(lat, lon, lbreak)
        elif displaytype == 'polygon':
            plot.addPolygon(lat, lon, lbreak)
    draw_if_interactive()

def makecolors(n, cmap='matlab_jet', reverse=False, alpha=None):
    ocmap = ColorUtil.getColorMap(cmap)
    if reverse:
        ocmap.reverse()
    if alpha is None:
        cols = ocmap.getColorList(n)    
    else:
        cols = ocmap.getColorList(n, alpha)
    colors = []
    for c in cols:
        colors.append(c)
    return colors

def makelegend(lbreaks):
    ls = LegendScheme(lbreaks)
    return ls
    
def makesymbolspec(geometry, *args, **kwargs):
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
        return ls
    
    ls = LegendScheme(shapetype)
    field = kwargs.pop('field', '')    
    ls.setFieldName(field)
    n = len(args)
    isunique = True
    for arg in args:
        lb, isu = __getlegendbreak(geometry, arg)
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
    if isinstance(weather, str):
        wlist = DrawMeteoData.getWeatherTypes(weather)
    else:
        wlist = weather
    c = __getcolor(color)
    return DrawMeteoData.createWeatherLegendScheme(wlist, size, c)

def __getlegendbreak(geometry, rule): 
    cobj = rule.pop('color', 'k')
    color = __getcolor(cobj)
    if geometry == 'point':
        lb = PointBreak()        
        marker = rule.pop('marker', 'o')
        pstyle = __getpointstyle(marker)
        lb.setStyle(pstyle)
        size = rule.pop('size', 6)
        lb.setSize(size)
        ecobj = rule.pop('edgecolor', 'k')
        edgecolor = __getcolor(ecobj)
        lb.setOutlineColor(edgecolor)
        fill = rule.pop('fill', True)
        lb.setDrawFill(fill)
        edge = rule.pop('edge', True)
        lb.setDrawOutline(edge)
    elif geometry == 'line':
        lb = PolylineBreak()
        size = rule.pop('size', 1)
        lb.setSize(size)
        lsobj = rule.pop('linestyle', '-')
        linestyle = __getlinestyle(lsobj)
        lb.setStyle(linestyle)
        marker = rule.pop('marker', None)
        if not marker is None:
            pstyle = __getpointstyle(marker)
            lb.setDrawSymbol(True)
            lb.setSymbolStyle(pstyle)
            markersize = rule.pop('markersize', 8)
            lb.setSymbolSize(markersize)
            markercolor = rule.pop('markercolor', None)
            if markercolor is None:
                makercolor = color
            else:
                makercolor = __getcolor(makercolor)
            lb.setSymbolColor(makercolor)
            fillcolor = rule.pop('makerfillcolor', None)
            if not fillcolor is None:
                lb.setFillSymbol(True)
                lb.setSymbolFillColor(__getcolor(fillcolor))
            else:
                lb.setSymbolFillColor(markercolor)
            interval = rule.pop('markerinterval', 1)
            lb.setSymbolInterval(interval)
    elif geometry == 'polygon':
        lb = PolygonBreak()
        ecobj = rule.pop('edgecolor', 'k')
        edgecolor = __getcolor(ecobj)
        lb.setOutlineColor(edgecolor)
        fill = rule.pop('fill', True)
        lb.setDrawFill(fill)
        edge = rule.pop('edge', True)
        lb.setDrawOutline(edge)
        size = rule.pop('size', 1)
        lb.setOutlineSize(size)
    else:
        lb = ColorBreak()
    caption = rule.pop('caption', None)
    if not caption is None:
        lb.setCaption(caption)    
    lb.setColor(color)
    value = rule.pop('value', None)
    isunique = True
    if not value is None:
        if isinstance(value, tuple):
            lb.setStartValue(value[0])
            lb.setEndValue(value[1])
            isunique = False
        else:
            lb.setStartValue(value)
            lb.setEndValue(value)
    return lb, isunique
    
def masklayer(mobj, layers):
    plot = gca
    mapview = plot.getMapView()
    mapview.getMaskOut().setMask(True)
    mapview.getMaskOut().setMaskLayer(mobj.layer.getLayerName())
    for layer in layers:
        layer.layer.setMaskout(True)
    draw_if_interactive()
    
def display(data):
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
        plot = XY2DPlot(mapview)
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
    """
    animation.finish()