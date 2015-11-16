#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2014-12-26
# Purpose: MeteoInfoLab plot module
# Note: Jython
#-----------------------------------------------------
import os
import inspect

from org.meteoinfo.chart import ChartPanel, Location
from org.meteoinfo.data import XYListDataset, GridData, ArrayUtil
from org.meteoinfo.data.mapdata import MapDataManage
from org.meteoinfo.data.meteodata import MeteoDataInfo, DrawMeteoData
from org.meteoinfo.chart.plot import XY1DPlot, BarPlot, XY2DPlot, MapPlot, ChartPlotMethod, PlotOrientation
from org.meteoinfo.chart import Chart, ChartText, ChartLegend, LegendPosition
from org.meteoinfo.chart.axis import LonLatAxis, TimeAxis
from org.meteoinfo.script import ChartForm, MapForm
from org.meteoinfo.legend import MapFrame, LineStyles, BreakTypes, ColorBreak, PointBreak, PolylineBreak, PolygonBreak, LegendManage, LegendScheme, LegendType
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
import midata
import milayer
from milayer import MILayer, MIXYListData

## Global ##
milapp = None
batchmode = False
isinteractive = False
maplayout = MapLayout()
chartpanel = None
isholdon = True
c_plot = None
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
    elif isinstance(data, list):
        return data
    else:
        return [data]

def draw_if_interactive():
    if isinteractive:
		chartpanel.paintGraphics()
        
def plot(*args, **kwargs):
    #if ismap:
    #    map(False)

    #Parse args
    global c_plot
    if isholdon:
        if c_plot == None:
            dataset = XYListDataset()
        else:
            if not isinstance(c_plot, XY1DPlot):
                dataset = XYListDataset()
            else:
                dataset = c_plot.getDataset()
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
    if c_plot is None:
        plot = XY1DPlot()
    else:
        if isinstance(c_plot, XY1DPlot):
            plot = c_plot
        else:
            plot = XY1DPlot()
    
    if xaxistype == 'lon':
        plot.setXAxis(LonLatAxis('Longitude', True, True))
    elif xaxistype == 'lat':
        plot.setXAxis(LonLatAxis('Latitude', True, False))
    elif xaxistype == 'time':
        plot.setXAxis(TimeAxis('Time', True))
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
    if c_plot is None or (not isinstance(c_plot, XY1DPlot)):
        chart.clearPlots()
        chart.setPlot(plot)
    c_plot = plot
    #chart.setAntiAlias(True)
    chartpanel.setChart(chart)
    draw_if_interactive()
    if len(lines) > 1:
        return lines
    else:
        return lines[0]

def bar(*args, **kwargs):
    #Get dataset
    global c_plot
    if c_plot is None:
        dataset = XYListDataset()
    else:
        dataset = c_plot.getDataset()
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
    dataset.addSeries(label, xdata, ydata)   

    #Create bar plot
    if c_plot is None:
        plot = BarPlot()
    else:
        if isinstance(c_plot, BarPlot):
            plot = c_plot
        else:
            plot = BarPlot()
    plot.setDataset(dataset)
    if not autowidth:
        plot.setAutoWidth(autowidth)
        plot.setBarWidth(width)
    
    #Set plot data styles
    fcobj = kwargs.pop('color', None)
    if fcobj is None:
        fcobj = kwargs.pop('facecolor', 'b')
    color = __getcolor(fcobj)
    lb = PolygonBreak()
    lb.setCaption(label)
    lb.setColor(color)
    ecobj = kwargs.pop('edgecolor', 'k')
    edgecolor = __getcolor(ecobj)
    lb.setOutlineColor(edgecolor)
    linewidth = kwargs.pop('linewidth', 1.0)
    lb.setOutlineSize(linewidth)
    plot.setLegendBreak(dataset.getSeriesCount() - 1, lb)
    
    #Create figure
    if chartpanel is None:
        figure()
    
    #Set chart
    chart = chartpanel.getChart()
    if c_plot is None:
        chart.clearPlots()
        chart.setPlot(plot)
    #chart.setAntiAlias(True)
    chartpanel.setChart(chart)
    c_plot = plot
    draw_if_interactive()
    return lb
        
def hist(x, bins=10, range=None, normed=False, cumulative=False,
    bottom=None, histtype='bar', align='mid',
    orientation='vertical', rwidth=None, log=False, **kwargs):
    
    return None
    
def scatter(x, y, s=8, c='b', marker='o', cmap=None, norm=None, vmin=None, vmax=None,
            alpha=None, linewidths=None, verts=None, hold=None, **kwargs):
    #Get dataset
    global c_plot
    if c_plot is None:
        dataset = XYListDataset()
    else:
        dataset = c_plot.getDataset()
        if dataset is None:
            dataset = XYListDataset()    
    
    #Add data series
    label = kwargs.pop('label', 'S_0')
    xdata = __getplotdata(x)
    ydata = __getplotdata(y)
    dataset.addSeries(label, xdata, ydata)
    
    #Create XY1DPlot
    if c_plot is None:
        plot = XY1DPlot(dataset)
    else:
        plot = c_plot
        plot.setDataset(dataset)
    
    #Set plot data styles
    pointStyle = __getpointstyle(marker)
    c = kwargs.pop('color', c)
    color = __getcolor(c)
    pb = PointBreak()
    pb.setCaption(label)
    pb.setSize(s)
    pb.setStyle(pointStyle)
    pb.setColor(color)
    plot.setLegendBreak(dataset.getSeriesCount() - 1, pb)
    
    #Paint dataset
    if chartpanel is None:
        figure()
        
    chart = chartpanel.getChart()
    if c_plot is None:
        chart.clearPlots()
        chart.setPlot(plot)
    #chart.setAntiAlias(True)
    chartpanel.setChart(chart)
    c_plot = plot
    draw_if_interactive()
    return pb 
 
def figure(bgcolor=None, figsize=None, newfig=True):
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
    if chartpanel is None:
        figure()
        
    global c_plot
    chart = chartpanel.getChart()
    chart.setRowNum(nrows)
    chart.setColumnNum(ncols)
    c_plot = chart.getPlot(plot_number)
    chart.setCurrentPlot(plot_number - 1)
    if c_plot is None:
        c_plot = XY1DPlot()
        c_plot.isSubPlot = True
        plot_number -= 1
        rowidx = plot_number / ncols
        colidx = plot_number % ncols
        c_plot.rowIndex = rowidx
        c_plot.columnIndex = colidx
        chart.addPlot(c_plot)
        chart.setCurrentPlot(chart.getPlots().size() - 1)
    #c_plot = plot
    
    return plot
    
def axes(**kwargs):
    if chartpanel is None:
        figure()
        
    position = kwargs.pop('position', [0.13, 0.11, 0.775, 0.815])
    bottomaxis = kwargs.pop('bottomaxis', True)
    leftaxis = kwargs.pop('leftaxis', True)
    topaxis = kwargs.pop('topaxis', True)
    rightaxis = kwargs.pop('rightaxis', True)
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
    if xaxistype == 'lonlat':
        plot.setXAxis(LonLatAxis('Longitude', True))
    elif xaxistype == 'time':
        plot.setXAxis(TimeAxis('Time', True))
    if not bgcobj is None:
        bgcolor = __getcolor(bgcobj)
        plot.setDrawBackground(True)
        plot.setBackground(bgcolor)
    chart = chartpanel.getChart()
    chart.setCurrentPlot(plot)
    global c_plot
    c_plot = plot
    return plot

def axesm(projinfo=None, proj='longlat', **kwargs):    
    if chartpanel is None:
        figure()
        
    position = kwargs.pop('position', [0.13, 0.11, 0.775, 0.815])
    bottomaxis = kwargs.pop('bottomaxis', True)
    leftaxis = kwargs.pop('leftaxis', True)
    topaxis = kwargs.pop('topaxis', True)
    rightaxis = kwargs.pop('rightaxis', True)
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
    if projinfo == None:
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
    
    global c_plot
    mapview = MapView()
    mapview.setXYScaleFactor(xyscale)
    c_plot = MapPlot(mapview)    
    c_plot.setPosition(position[0], position[1], position[2], position[3])
    tickfontname = kwargs.pop('tickfontname', 'Arial')
    tickfontsize = kwargs.pop('tickfontsize', 14)
    tickbold = kwargs.pop('tickbold', False)
    if tickbold:
        font = Font(tickfontname, Font.BOLD, tickfontsize)
    else:
        font = Font(tickfontname, Font.PLAIN, tickfontsize)
    c_plot.setAxisLabelFont(font)
    if not axison is None:
        c_plot.setAxisOn(axison)
    else:
        if bottomaxis == False:
            c_plot.getAxis(Location.BOTTOM).setVisible(False)
        if leftaxis == False:
            c_plot.getAxis(Location.LEFT).setVisible(False)
        if topaxis == False:
            c_plot.getAxis(Location.TOP).setVisible(False)
        if rightaxis == False:
            c_plot.getAxis(Location.RIGHT).setVisible(False)
    mapframe = c_plot.getMapFrame()
    mapframe.setDrawGridLabel(gridlabel)
    mapframe.setDrawGridTickLine(gridlabel)
    mapframe.setDrawGridLine(gridline)
    mapframe.setGridXDelt(griddx)
    mapframe.setGridYDelt(griddy)
    c_plot.setDrawNeatLine(frameon)
    if not bgcobj is None:
        bgcolor = __getcolor(bgcobj)
        c_plot.setDrawBackground(True)
        c_plot.setBackground(bgcolor)
    c_plot.getMapView().projectLayers(projinfo)
    chart = chartpanel.getChart()
    if chart.getPlot() is None:
        chart.addPlot(c_plot)
    else:
        chart.setCurrentPlot(c_plot)
    return c_plot, projinfo
    
def twinx(ax):
    ax.getAxis(Location.RIGHT).setVisible(False)
    plot = XY1DPlot()
    plot.setPosition(ax.getPosition())
    plot.getAxis(Location.BOTTOM).setVisible(False)
    plot.getAxis(Location.LEFT).setVisible(False)
    plot.getAxis(Location.TOP).setVisible(False)
    axis = plot.getAxis(Location.RIGHT)
    axis.setDrawTickLabel(True)
    axis.setDrawLabel(True)
    chartpanel.getChart().addPlot(plot)
    global c_plot
    c_plot = plot
    return plot
    
def yaxis(ax, **kwargs):
    shift = kwargs.pop('shift', 0)
    color = kwargs.pop('color', 'black')
    c = __getcolor(color)
    axis_l = ax.getAxis(Location.LEFT)
    axis_l.setShift(shift)
    axis_l.setColor_All(c)   
    axis_r = ax.getAxis(Location.RIGHT)
    axis_r.setShift(shift)
    axis_r.setColor_All(c)    
    draw_if_interactive
    
def antialias(b=True):
    if chartpanel is None:
        figure()
        
    chartpanel.getChart().setAntiAlias(b)
    draw_if_interactive()
    
def savefig(fname, width=None, height=None, dpi=None):
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
    global c_plot
    if not c_plot is None:
        chartpanel.getChart().removePlot(c_plot)
        c_plot = None
        draw_if_interactive()

# Clear current figure    
def clf():
    if chartpanel is None:
        return
    
    if chartpanel.getChart() is None:
        return
        
    chartpanel.getChart().clearPlots()
    global c_plot
    c_plot = None
    draw_if_interactive()

# Clear last layer    
def cll():
    if not c_plot is None:
        if isinstance(c_plot, XY1DPlot):
            c_plot.removeLastSeries()
        elif isinstance(c_plot, XY2DPlot):
            c_plot.removeLastLayer()
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
            if not c is None:
                plb.setColor(c)
                plb.setSymbolColor(c)
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

def title(title, fontname='Arial', fontsize=14, bold=True, color='black'):
    if bold:
        font = Font(fontname, Font.BOLD, fontsize)
    else:
        font = Font(fontname, Font.PLAIN, fontsize)
    c = __getcolor(color)
    ctitile = ChartText(title, font)
    ctitile.setColor(c)
    c_plot.setTitle(ctitile)
    draw_if_interactive()

def xlabel(label, fontname='Arial', fontsize=14, bold=False, color='black'):
    if bold:
        font = Font(fontname, Font.BOLD, fontsize)
    else:
        font = Font(fontname, Font.PLAIN, fontsize)
    c = __getcolor(color)
    plot = c_plot
    axis = plot.getXAxis()
    axis.setLabel(label)
    axis.setDrawLabel(True)
    axis.setLabelFont(font)
    axis.setLabelColor(c)
    draw_if_interactive()
    
def ylabel(label, fontname='Arial', fontsize=14, bold=False, color='black'):
    if bold:
        font = Font(fontname, Font.BOLD, fontsize)
    else:
        font = Font(fontname, Font.PLAIN, fontsize)
    c = __getcolor(color)
    plot = c_plot
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
    axis = c_plot.getXAxis()
    axis_t = c_plot.getAxis(Location.TOP)
    if len(args) > 0:
        locs = args[0]
        if isinstance(locs, MIArray):
            locs = locs.aslist()
        axis.setTickLocations(locs)
        axis_t.setTickLocations(locs)
        args = args[1:]
    if len(args) > 0:
        labels = args[0]
        if isinstance(labels, MIArray):
            labels = labels.aslist()
        axis.setTickLabels(labels)
        axis_t.setTickLabels(labels)
    draw_if_interactive()
    
def yticks(*args, **kwargs):
    axis = c_plot.getYAxis()
    axis_r = c_plot.getAxis(Location.RIGHT)
    if len(args) > 0:
        locs = args[0]
        if isinstance(locs, MIArray):
            locs = locs.aslist()
        axis.setTickLocations(locs)
        axis_r.setTickLocations(locs)
        args = args[1:]
    if len(args) > 0:
        labels = args[0]
        if isinstance(labels, MIArray):
            labels = labels.aslist()
        axis.setTickLabels(labels)
        axis_r.setTickLabels(labels)
    draw_if_interactive()
    
def text(x, y, s, **kwargs):
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
    c_plot.addText(text)
    draw_if_interactive()
    
def axis(limits):
    if len(limits) == 4:
        xmin = limits[0]
        xmax = limits[1]
        ymin = limits[2]
        ymax = limits[3]
        c_plot.setDrawExtent(Extent(xmin, xmax, ymin, ymax))
        draw_if_interactive()
        
def axism(limits=None):
    if limits is None:
        c_plot.setDrawExtent(c_plot.getMapView().getExtent())
        draw_if_interactive()
    else:
        if len(limits) == 4:
            xmin = limits[0]
            xmax = limits[1]
            ymin = limits[2]
            ymax = limits[3]
            c_plot.setLonLatExtent(Extent(xmin, xmax, ymin, ymax))
            draw_if_interactive()
        else:
            print 'The limits parameter must be a list with 4 elements: xmin, xmax, ymin, ymax!'

def grid(b=None, which='major', axis='both', **kwargs):
    plot = c_plot
    gridline = plot.getGridLine()
    isDraw = gridline.isDrawXLine()
    if b is None:
        isDraw = not gridline.isDrawXLine()
    elif b == True or b == 'on':
        isDraw = True
    elif b == False or b == 'on':
        isDraw = False
    gridline.setDrawXLine(isDraw)
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
    plot = c_plot
    extent = plot.getDrawExtent()
    extent.minX = xmin
    extent.maxX = xmax
    plot.setDrawExtent(extent)
    draw_if_interactive()
            
def ylim(ymin, ymax):
    plot = c_plot
    extent = plot.getDrawExtent()
    extent.minY = ymin
    extent.maxY = ymax
    plot.setDrawExtent(extent)
    draw_if_interactive()   

def xreverse():
    c_plot.getXAxis().setInverse(True)
    draw_if_interactive()
    
def yreverse():
    c_plot.getYAxis().setInverse(True)
    draw_if_interactive()
            
def legend(*args, **kwargs):
    plot = c_plot
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
    shadow = kwargs.pop('shadow', False)
    clegend.setDrawBackground(shadow)
    bcobj = kwargs.pop('background', 'w')
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
    if os.path.exists(fn):
        ls = LegendScheme()
        ls.importFromXMLFile(fn, False)
        return ls
    else:
        print 'File not exists: ' + fn
        return None
        
def colorbar(layer, **kwargs):
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
    plot = c_plot
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
    ticklabel = kwargs.pop('ticklabel', None)
    if not ticklabel is None:
        legend.setTickLabels(ticklabel)
    plot.setDrawLegend(True)
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
    size = kwargs.pop('size', 6)
    marker = kwargs.pop('marker', 'o')
    pstyle = __getpointstyle(marker)
    fcobj = kwargs.pop('facecolor', None)
    if fcobj is None:
        facecolor = None
    else:
        facecolor = __getcolor(fcobj)
    ecobj = kwargs.pop('edgecolor', 'k')
    edgecolor = __getcolor(ecobj)
    fill = kwargs.pop('fill', True)
    edge = kwargs.pop('edge', True)
    for lb in ls.getLegendBreaks():
        if not facecolor is None:
            lb.setColor(facecolor)
        lb.setStyle(pstyle)
        lb.setSize(size)        
        lb.setOutlineColor(edgecolor)        
        lb.setDrawFill(fill)        
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
    n = len(args)
    cmap = __getcolormap(**kwargs)
    fill_value = kwargs.pop('fill_value', -9999.0)
    if n <= 2:
        gdata = midata.asgriddata(args[0])
        args = args[1:]
    elif n <=4:
        x = args[0]
        y = args[1]
        a = args[2]
        gdata = midata.asgriddata(a, x, y, fill_value)
        args = args[3:]
    ls = __getlegendscheme(args, gdata.min(), gdata.max(), **kwargs)
    layer = __plot_griddata(gdata, ls, 'imshow')
    return MILayer(layer)
      
def contour(*args, **kwargs):
    n = len(args)
    cmap = __getcolormap(**kwargs)
    fill_value = kwargs.pop('fill_value', -9999.0)
    xaxistype = None
    if n <= 2:
        gdata = midata.asgriddata(args[0])
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
        gdata = midata.asgriddata(a, x, y, fill_value)
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
    n = len(args)    
    cmap = __getcolormap(**kwargs)
    fill_value = kwargs.pop('fill_value', -9999.0)
    xaxistype = None
    if n <= 2:
        gdata = midata.asgriddata(args[0])
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
        gdata = midata.asgriddata(a, x, y, fill_value)
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
    plot = c_plot
    cmap = __getcolormap(**kwargs)
    fill_value = kwargs.pop('fill_value', -9999.0)
    order = kwargs.pop('order', None)
    isuv = kwargs.pop('isuv', True)
    size = kwargs.pop('size', 10)
    n = len(args) 
    iscolor = False
    cdata = None
    if n <= 4:
        udata = midata.asgriddata(args[0])
        vdata = midata.asgriddata(args[1])
        args = args[2:]
        if len(args) > 0:
            cdata = midata.asgriddata(args[0])
            iscolor = True
            args = args[1:]
    elif n <= 6:
        x = args[0]
        y = args[1]
        u = args[2]
        v = args[3]
        udata = midata.asgriddata(u, x, y, fill_value)
        vdata = midata.asgriddata(v, x, y, fill_value)
        args = args[4:]
        if len(args) > 0:
            cdata = midata.asgriddata(args[0], x, y, fill_value)
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
        ls = LegendManage.createSingleSymbolLegendScheme(ShapeTypes.Point, c, size)
    layer = __plot_uvgriddata(udata, vdata, cdata, ls, 'quiver', isuv)
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
        layer = DrawMeteoData.createRasterLayer(gdata.data, 'layer', ls)
    
    #Create XY1DPlot
    global c_plot
    if c_plot is None:
        mapview = MapView()
        plot = XY2DPlot(mapview)
    else:
        if isinstance(c_plot, XY2DPlot):
            plot = c_plot
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
    if c_plot is None or (not isinstance(c_plot, XY2DPlot)):
        chart.setCurrentPlot(plot)
    c_plot = plot
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
    global c_plot
    c_plot = plot
    draw_if_interactive()
    return layer
    
def scatterm(*args, **kwargs):
    plot = c_plot
    fill_value = kwargs.pop('fill_value', -9999.0)
    proj = kwargs.pop('proj', None)    
    order = kwargs.pop('order', None)
    n = len(args) 
    if n == 1:
        if isinstance(args[0], PyStationData):
            gdata = args[0]
        else:
            gdata = midata.asgriddata(args[0])
        args = []
    elif n <=4:
        x = args[0]
        y = args[1]
        if not isinstance(x, (DimArray, MIArray)):
            x = midata.array(x)
        if not isinstance(y, (DimArray, MIArray)):
            y = midata.array(y)
        if n == 2:
            a = x
            args = []
        else:
            a = args[2]
            if not isinstance(a, (DimArray, MIArray)):
                a = midata.array(a)
            args = args[3:]                
        if a.rank == 1:
            gdata = midata.asstationdata(a, x, y, fill_value)
        else:
            if a.asarray().getSize() == x.asarray().getSize():
                gdata = midata.asstationdata(a, x, y, fill_value)                
            else:
                gdata = midata.asgriddata(a, x, y, fill_value)
        
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
    plot = c_plot
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
            xdatalist.append(midata.asarray(xdata))
            ydatalist.append(midata.asarray(ydata))
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
        xdatalist.append(midata.asarray(xdata))
        ydatalist.append(midata.asarray(ydata))
    else:
        c = 'x'
        for arg in args: 
            if c == 'x':    
                xdatalist.append(midata.asarray(arg))
                c = 'y'
            elif c == 'y':
                ydatalist.append(midata.asarray(arg))
                c = 's'
            elif c == 's':
                if isinstance(arg, basestring):
                    styles.append(arg)
                    c = 'x'
                else:
                    styles.append('-')
                    xdatalist.append(midata.asarray(arg))
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
 
    c_plot.addLayer(layer)
    c_plot.setDrawExtent(layer.getExtent())
    
    if chartpanel is None:
        figure()

    draw_if_interactive()
    return MILayer(layer)
    
def stationmodel(*args, **kwargs):
    smdata = args[0]
    proj = kwargs.pop('proj', None)
    size = kwargs.pop('size', 12)
    surface = kwargs.pop('surface', True)
    ls = LegendManage.createSingleSymbolLegendScheme(ShapeTypes.Point, Color.blue, size)
    layer = DrawMeteoData.createStationModelLayer(smdata, ls, 'stationmodel', surface)
    if (proj != None):
        layer.setProjInfo(proj)
 
    c_plot.addLayer(layer)
    c_plot.setDrawExtent(layer.getExtent())
    
    if chartpanel is None:
        figure()

    draw_if_interactive()
    return MILayer(layer)
        
def imshowm(*args, **kwargs):
    plot = c_plot
    cmap = __getcolormap(**kwargs)
    fill_value = kwargs.pop('fill_value', -9999.0)
    proj = kwargs.pop('proj', None)
    order = kwargs.pop('order', None)
    n = len(args) 
    if n <= 2:
        gdata = midata.asgriddata(args[0])
        args = args[1:]
    elif n <=4:
        x = args[0]
        y = args[1]
        a = args[2]
        gdata = midata.asgriddata(a, x, y, fill_value)
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
        #ls = LegendManage.createLegendScheme(gdata.getminvalue(), gdata.getmaxvalue(), cmap)
        ls = LegendManage.createImageLegend(gdata.data, cmap)
    layer = __plot_griddata_m(plot, gdata, ls, 'imshow', proj=proj, order=order)
    gdata = None
    return MILayer(layer)
    
def contourm(*args, **kwargs):  
    plot = c_plot
    fill_value = kwargs.pop('fill_value', -9999.0)      
    proj = kwargs.pop('proj', None)
    order = kwargs.pop('order', None)
    n = len(args) 
    if n <= 2:
        gdata = midata.asgriddata(args[0])
        args = args[1:]
    elif n <=4:
        x = args[0]
        y = args[1]
        a = args[2]
        gdata = midata.asgriddata(a, x, y, fill_value)
        args = args[3:]
    ls = __getlegendscheme(args, gdata.min(), gdata.max(), **kwargs)
    layer = __plot_griddata_m(plot, gdata, ls, 'contour', proj=proj, order=order)
    gdata = None
    return MILayer(layer)
        
def contourfm(*args, **kwargs):
    plot = c_plot
    fill_value = kwargs.pop('fill_value', -9999.0)
    interpolate = kwargs.pop('interpolate', False)
    proj = kwargs.pop('proj', None)
    order = kwargs.pop('order', None)
    n = len(args) 
    if n <= 2:
        gdata = midata.asgriddata(args[0])
        args = args[1:]
    elif n <=4:
        x = args[0]
        y = args[1]
        a = args[2]
        gdata = midata.asgriddata(a, x, y, fill_value)
        args = args[3:]
    ls = __getlegendscheme(args, gdata.min(), gdata.max(), **kwargs)
    if interpolate:
        gdata = gdata.interpolate()
    layer = __plot_griddata_m(plot, gdata, ls, 'contourf', proj=proj, order=order)
    gdata = None
    return MILayer(layer)
    
def gridfm(*args, **kwargs):
    plot = c_plot
    fill_value = kwargs.pop('fill_value', -9999.0)
    interpolate = kwargs.pop('interpolate', False)
    proj = kwargs.pop('proj', None)
    order = kwargs.pop('order', None)
    n = len(args) 
    if n <= 2:
        gdata = midata.asgriddata(args[0])
        args = args[1:]
    elif n <=4:
        x = args[0]
        y = args[1]
        a = args[2]
        gdata = midata.asgriddata(a, x, y, fill_value)
        args = args[3:]
    ls = __getlegendscheme(args, gdata.min(), gdata.max(), **kwargs)
    if interpolate:
        gdata = gdata.interpolate()
    layer = __plot_griddata_m(plot, gdata, ls, 'gridf', proj=proj, order=order)
    gdata = None
    return MILayer(layer)
    
def surfacem_1(*args, **kwargs):
    plot = c_plot
    fill_value = kwargs.pop('fill_value', -9999.0)
    proj = kwargs.pop('proj', None)    
    order = kwargs.pop('order', None)
    n = len(args) 
    if n <= 2:
        if isinstance(args[0], PyStationData):
            gdata = args[0]
        else:
            gdata = midata.asgriddata(args[0])
        args = args[1:]
    elif n <=4:
        x = args[0]
        y = args[1]
        a = args[2]
        if a.rank == 2 and a.asarray().getSize() != x.asarray().getSize():            
            gdata = midata.asgriddata(a, x, y, fill_value)
        else:
            if not plot.getProjInfo().isLonLat():
                x, y = midata.project(x, y, plot.getProjInfo())
            a, x_g, y_g = midata.griddata([x, y], a, method='surface')
            gdata = midata.asgriddata(a, x_g, y_g, fill_value)
        
        args = args[3:]
    ls = __getlegendscheme(args, gdata.min(), gdata.max(), **kwargs)
    symbolspec = kwargs.pop('symbolspec', None)
    if symbolspec is None:
        ls = __setlegendscheme_point(ls, **kwargs)    
          
    layer = __plot_griddata_m(plot, gdata, ls, 'imshow', proj=plot.getProjInfo(), order=order)

    gdata = None
    return MILayer(layer)
    
def surfacem(*args, **kwargs):
    plot = c_plot
    fill_value = kwargs.pop('fill_value', -9999.0)
    proj = kwargs.pop('proj', None)    
    order = kwargs.pop('order', None)
    n = len(args) 
    if n <= 2:
        a = args[0]
        y = midata.linspace(1, a.shape[1], 1)
        x = midata.linspace(1, a.shape[0], 1)
        args = args[1:]
    elif n <=4:
        x = args[0]
        y = args[1]
        a = args[2]
        if a.rank == 2 and a.asarray().getSize() != x.asarray().getSize():            
            x, y = midata.meshgrid(x, y)        
        args = args[3:]
    ls = __getlegendscheme(args, a.min(), a.max(), **kwargs)   
    
    if plot.getProjInfo().isLonLat():
        lonlim = 90
    else:
        lonlim = 0
        x, y = midata.project(x, y, toproj=plot.getProjInfo())
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
    plot = c_plot
    cmap = __getcolormap(**kwargs)
    fill_value = kwargs.pop('fill_value', -9999.0)
    proj = kwargs.pop('proj', None)
    order = kwargs.pop('order', None)
    isuv = kwargs.pop('isuv', True)
    size = kwargs.pop('size', 10)
    n = len(args) 
    iscolor = False
    cdata = None
    if n <= 4:
        udata = midata.asgriddata(args[0])
        vdata = midata.asgriddata(args[1])
        args = args[2:]
        if len(args) > 0:
            cdata = midata.asgriddata(args[0])
            iscolor = True
            args = args[1:]
    elif n <= 6:
        x = args[0]
        y = args[1]
        u = args[2]
        v = args[3]
        udata = midata.asgriddata(u, x, y, fill_value)
        vdata = midata.asgriddata(v, x, y, fill_value)
        args = args[4:]
        if len(args) > 0:
            cdata = midata.asgriddata(args[0], x, y, fill_value)
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
        ls = LegendManage.createSingleSymbolLegendScheme(ShapeTypes.Point, c, size)
    layer = __plot_uvgriddata_m(plot, udata, vdata, cdata, ls, 'quiver', isuv, proj=proj)
    udata = None
    vdata = None
    cdata = None
    return MILayer(layer)
    
def streamplotm(*args, **kwargs):
    plot = c_plot
    cmap = __getcolormap(**kwargs)
    fill_value = kwargs.pop('fill_value', -9999.0)
    proj = kwargs.pop('proj', None)
    cobj = kwargs.pop('color', 'b')
    color = __getcolor(cobj)
    isuv = kwargs.pop('isuv', True)
    density = kwargs.pop('density', 4)
    n = len(args)
    if n <= 4:
        udata = midata.asgriddata(args[0])
        vdata = midata.asgriddata(args[1])
        args = args[2:]
    elif n <= 6:
        x = args[0]
        y = args[1]
        u = args[2]
        v = args[3]
        udata = midata.asgriddata(u, x, y, fill_value)
        vdata = midata.asgriddata(v, x, y, fill_value)
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
        layer = DrawMeteoData.createRasterLayer(gdata.data, 'layer', ls)      
    elif type == 'scatter':
        layer = DrawMeteoData.createGridPointLayer(gdata.data, ls, 'layer', 'data')
    elif type == 'gridf':
        layer = DrawMeteoData.createGridFillLayer(gdata.data, ls, 'layer', 'data')
    else:
        layer = None
        return layer
    
    if (proj != None):
        layer.setProjInfo(proj)
        
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
    #global c_plot
    #c_plot = plot
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
    #global c_plot
    #c_plot = plot
    draw_if_interactive()
    return layer
    
def __plot_uvgriddata_m(plot, udata, vdata, cdata, ls, type, isuv, proj=None, density=4):
    #print 'GridData...'
    if type == 'quiver':
        if cdata == None:
            layer = DrawMeteoData.createGridVectorLayer(udata.data, vdata.data, ls, 'layer', isuv)
        else:
            layer = DrawMeteoData.createGridVectorLayer(udata.data, vdata.data, cdata.data, ls, 'layer', isuv)
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
    #global c_plot
    #c_plot = plot
    draw_if_interactive()
    return layer
    
def clabel(layer, **kwargs):
    font = __getfont(**kwargs)
    cstr = kwargs.pop('color', 'black')
    color = __getcolor(cstr)
    labelset = layer.layer.getLabelSet()
    labelset.setLabelFont(font)
    labelset.setLabelColor(color)
    layer.layer.addLabelsContourDynamic(layer.layer.getExtent())
    draw_if_interactive()
        
def worldmap():
    mapview = MapView()
    mapview.setXYScaleFactor(1.0)
    #print 'Is GeoMap: ' + str(mapview.isGeoMap())
    plot = MapPlot(mapview)
    chart = chartpanel.getChart()
    chart.clearPlots()
    chart.setPlot(plot)
    global c_plot
    c_plot = plot
    return plot    
        
def geoshow(layer, **kwargs):
    plot = c_plot
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
                size = kwargs.pop('size', 1)
                lb = layer.getLegendScheme().getLegendBreaks().get(0)
                lb.setColor(facecolor)
                btype = lb.getBreakType()
                if btype == BreakTypes.PointBreak:        
                    lb.setDrawOutline(drawline)
                    lb.setOutlineColor(edgecolor)        
                elif btype == BreakTypes.PolylineBreak:
                    lb.setSize(size)
                elif btype == BreakTypes.PolygonBreak:
                    lb.setDrawFill(drawfill)
                    lb.setDrawOutline(drawline)
                    lb.setOutlineColor(edgecolor)
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
    elif geometry == 'polygon':
        lb = PolygonBreak()
        ecobj = rule.pop('edgecolor', 'k')
        edgecolor = __getcolor(ecobj)
        lb.setOutlineColor(edgecolor)
        fill = rule.pop('fill', True)
        lb.setDrawFill(fill)
        edge = rule.pop('edge', True)
        lb.setDrawOutline(edge)
    else:
        lb = ColorBreak()
    caption = rule.pop('caption', None)
    if not caption is None:
        lb.setCaption(caption)
    cobj = rule.pop('color', 'k')
    color = __getcolor(cobj)
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
    plot = c_plot
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