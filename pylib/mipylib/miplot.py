#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2014-12-26
# Purpose: MeteoInfo plot module
# Note: Jython
#-----------------------------------------------------
import os
import inspect

from org.meteoinfo.chart import ChartPanel
from org.meteoinfo.data import XYListDataset, GridData
from org.meteoinfo.data.mapdata import MapDataManage
from org.meteoinfo.data.meteodata import MeteoDataInfo, DrawMeteoData
from org.meteoinfo.chart.plot import XY1DPlot, XY2DPlot, MapPlot, ChartPlotMethod
from org.meteoinfo.chart import Chart, ChartText, ChartLegend, LegendPosition
from org.meteoinfo.script import ChartForm, MapForm
from org.meteoinfo.legend import MapFrame, LineStyles, BreakTypes, PointBreak, PolylineBreak, LegendManage, LegendScheme
from org.meteoinfo.drawing import PointStyle
from org.meteoinfo.global import Extent
from org.meteoinfo.global.colors import ColorUtil, ColorMap
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

## Global ##
milapp = None
isinteractive = False
maplayout = MapLayout()
chartpanel = ChartPanel(Chart())
isholdon = False
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
    global c_plot
    if ishold:
        c_plot = chartpanel.getChart().getPlot()
    else:
        c_plot = None
 
def __getplotdata(data):
    if isinstance(data, MIArray):
        return data.array
    elif isinstance(data, DimArray):
        return data.array.array
    elif isinstance(data, list):
        return data
    else:
        return data
 
def plot(*args, **kwargs):
    if ismap:
        map(False)

    #Parse args
    if c_plot is None:
        dataset = XYListDataset()
    else:
        if not isinstance(c_plot, XY1DPlot):
            dataset = XYListDataset()
        else:
            dataset = c_plot.getDataset()
            if dataset is None:
                dataset = XYListDataset()
    xdatalist = []
    ydatalist = []    
    styles = []
    if len(args) == 1:
        ydata = __getplotdata(args[0])
        xdata = []
        for i in range(0, len(args[0])):
            xdata.append(i)
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
    
    #Add data series
    for i in range(0, len(xdatalist)):
        label = kwargs.pop('label', 'S_' + str(i + 1))
        xdata = __getplotdata(xdatalist[i])
        ydata = __getplotdata(ydatalist[i])
        dataset.addSeries(label, xdata, ydata)
    
    #Create XY1DPlot
    if c_plot is None:
        plot = XY1DPlot(dataset)
    else:
        if isinstance(c_plot, XY1DPlot):
            plot = c_plot
            plot.setDataset(dataset)
        else:
            plot = XY1DPlot(dataset)
    
    #Set plot data styles
    if styles != None:
        for i in range(0, len(styles)):
            idx = dataset.getSeriesCount() - len(styles) + i
            print 'Series index: ' + str(idx)
            __setplotstyle(plot, idx, styles[i], len(xdatalist[i]), **kwargs)
    
    #Paint dataset
    chart = chartpanel.getChart()
    if c_plot is None or (not isinstance(c_plot, XY1DPlot)):
        chart.clearPlots()
        chart.setPlot(plot)
    #chart.setAntiAlias(True)
    chartpanel.setChart(chart)
    if isinteractive:
		chartpanel.paintGraphics()
    return plot    
 
def hist(x, bins=10, range=None, normed=False, cumulative=False,
    bottom=None, histtype='bar', align='mid',
    orientation='vertical', rwidth=None, log=False, **kwargs):
    
    return None
    
def scatter(x, y, s=8, c='b', marker='o', cmap=None, norm=None, vmin=None, vmax=None,
            alpha=None, linewidths=None, verts=None, hold=None, **kwargs):
    #Get dataset
    if c_plot is None:
        dataset = XYListDataset()
    else:
        dataset = c_plot.getDataset()
        if dataset is None:
            dataset = XYListDataset()    
    
    #Add data series
    label = kwargs.pop('label', 'S_0')
    dataset.addSeries(label, x, y)
    
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
    pb.setSize(s)
    pb.setStyle(pointStyle)
    pb.setColor(color)
    plot.setLegendBreak(0, pb)
    
    #Paint dataset
    chart = chartpanel.getChart()
    if c_plot is None:
        chart.clearPlots()
        chart.setPlot(plot)
    #chart.setAntiAlias(True)
    chartpanel.setChart(chart)
    if isinteractive:
		chartpanel.paintGraphics()
    return plot 
 
def figure():
    show()
    
def show():
    #print ismap
    if ismap:
        frame = MapForm(maplayout)
        frame.setSize(750, 540)
        frame.setLocationRelativeTo(None)
        frame.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE)
        frame.setVisible(True)
        maplayout.paintGraphics()
    else:
        if milapp == None:
            form = ChartForm(chartpanel)
            chartpanel.paintGraphics()
            form.setSize(600, 500)
            form.setLocationRelativeTo(None)
            form.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE)
            form.setVisible(True)     
        else:
            figureDock = milapp.getFigureDock()
            figureDock.addNewFigure('Figure 1', chartpanel)
    
def subplot(nrows, ncols, plot_number):
    global c_plot
    chart = chartpanel.getChart()
    chart.setRowNum(nrows)
    chart.setColumnNum(ncols)
    plot = chart.getPlot(plot_number)
    if plot is None:
        plot = XY1DPlot()
        plot_number -= 1
        rowidx = plot_number / ncols
        colidx = plot_number % ncols
        plot.rowIndex = rowidx
        plot.columnIndex = colidx
        chart.addPlot(plot)
    c_plot = plot
    return plot
    
def savefig(fname, width=None, height=None):
    if (not width is None) and (not height is None):
        chartpanel.setSize(width, height)
    chartpanel.paintGraphics()
    chartpanel.exportToPicture(fname)    
 	
def __setplotstyle(plot, idx, style, n, **kwargs):
    c = __getcolor(style)
    linewidth = kwargs.pop('linewidth', 1.0)
    #print 'Line width: ' + str(linewidth)
    caption = plot.getLegendBreak(idx).getCaption()
    pointStyle = __getpointstyle(style)
    lineStyle = __getlinestyle(style)
    if not pointStyle is None:
        if lineStyle is None:
            #plot.setChartPlotMethod(ChartPlotMethod.POINT)            
            pb = PointBreak()
            pb.setCaption(caption)
            pb.setSize(8)
            pb.setStyle(pointStyle)
            if not c is None:
                pb.setColor(c)
            plot.setLegendBreak(idx, pb)
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
    
def __getlinestyle(style):
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
    pointStyle = None
    if 'o' in style:
        pointStyle = PointStyle.Circle
    elif 'D' in style:
        pointStyle = PointStyle.Diamond
    elif '+' in style:
        pointStyle = PointStyle.Plus
    elif 's' in style:
        pointStyle = PointStyle.Square
    elif '*' in style:
        pointStyle = PointStyle.StarLines
    elif '^' in style:
        pointStyle = PointStyle.UpTriangle
    elif 'x' in style:
        pointStyle = PointStyle.XCross
    
    return pointStyle
    
def __getcolor(style):
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
    elif isinstance(style, tuple):
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
    chartpanel.getChart().getPlot().setTitle(ctitile)
    if isinteractive:
        chartpanel.paintGraphics()

def xlabel(label, fontname='Arial', fontsize=14, bold=False, color='black'):
    if bold:
        font = Font(fontname, Font.BOLD, fontsize)
    else:
        font = Font(fontname, Font.PLAIN, fontsize)
    c = __getcolor(color)
    plot = chartpanel.getChart().getPlot()
    axis = plot.getXAxis()
    axis.setLabel(label)
    axis.setDrawLabel(True)
    axis.setLabelFont(font)
    axis.setLabelColor(c)
    if isinteractive:
        chartpanel.paintGraphics()
    
def ylabel(label, fontname='Arial', fontsize=14, bold=False, color='black'):
    if bold:
        font = Font(fontname, Font.BOLD, fontsize)
    else:
        font = Font(fontname, Font.PLAIN, fontsize)
    c = __getcolor(color)
    plot = chartpanel.getChart().getPlot()
    axis = plot.getYAxis()
    axis.setLabel(label)
    axis.setDrawLabel(True)
    axis.setLabelFont(font)
    axis.setLabelColor(c)
    if isinteractive:
        chartpanel.paintGraphics()
    
def axis(limits):
    if len(limits) == 4:
        xmin = limits[0]
        xmax = limits[1]
        ymin = limits[2]
        ymax = limits[3]
        plot = chartpanel.getChart().getPlot()
        plot.setDrawExtent(Extent(xmin, xmax, ymin, ymax))
        if isinteractive:
            chartpanel.paintGraphics()
            
def legend(*args, **kwargs):
    plot = chartpanel.getChart().getPlot()
    plot.updateLegendScheme()
    legend = plot.getLegend()
    loc = kwargs.pop('loc', 'upper right')    
    lp = LegendPosition.fromString(loc)
    legend.setPosition(lp)
    if lp == LegendPosition.CUSTOM:
        x = kwargs.pop('x', 0)
        y = kwargs.pop('y', 0)
        legend.setX(x)
        legend.setY(y)
    plot.setDrawLegend(True)
    if isinteractive:
        chartpanel.paintGraphics()
        
def colorbar(layer, **kwargs):
    cmap = kwargs.pop('cmap', None)
    shrink = kwargs.pop('shrink', 1)
    plot = chartpanel.getChart().getPlot()
    ls = layer.getLegendScheme()
    legend = plot.getLegend()
    if legend == None:
        legend = ChartLegend(ls)
        plot.setLegend(legend)
    else:
        legend.setLegendScheme(ls)
    legend.setColorbar(True)    
    legend.setPosition(LegendPosition.RIGHT_OUTSIDE)
    legend.setDrawNeatLine(False)
    plot.setDrawLegend(True)
    if isinteractive:
        chartpanel.paintGraphics()

def __getcolormap(**kwargs):
    colors = kwargs.pop('colors', None)
    if colors != None:
        if isinstance(colors, str):
            c = __getcolor(colors)
            cmap = ColorMap(c)
        elif isinstance(colors, tuple):
            cs = []
            for cc in colors:
                cs.append(__getcolor(cc))
            cmap = ColorMap(cs)
    else:
        cmapstr = kwargs.pop('cmap', 'matlab_jet')
        cmap = ColorUtil.getColorMap(cmapstr)
    return cmap
      
def imshow(*args, **kwargs):
    n = len(args)
    cmap = __getcolormap(**kwargs)
    missingv = kwargs.pop('missingv', -9999.0)
    if n <= 2:
        gdata = midata.asgriddata(args[0])
        args = args[1:]
    elif n <=4:
        x = args[0]
        y = args[1]
        a = args[2]
        gdata = midata.asgriddata(a, x, y, missingv)
        args = args[3:]
    if len(args) > 0:
        level_arg = args[0]
        if isinstance(level_arg, int):
            cn = level_arg
            ls = LegendManage.createLegendScheme(gdata.getminvalue(), gdata.getmaxvalue(), cn, cmap)
        else:
            ls = LegendManage.createLegendScheme(gdata.getminvalue(), gdata.getmaxvalue(), level_arg, cmap)
    else:    
        ls = LegendManage.createLegendScheme(gdata.getminvalue(), gdata.getmaxvalue(), cmap)
    layer = __plot_griddata(gdata, ls, 'imshow')
    return layer
      
def contour(*args, **kwargs):
    n = len(args)
    cmap = __getcolormap(**kwargs)
    missingv = kwargs.pop('missingv', -9999.0)
    if n <= 2:
        gdata = midata.asgriddata(args[0])
        args = args[1:]
    elif n <=4:
        x = args[0]
        y = args[1]
        a = args[2]
        gdata = midata.asgriddata(a, x, y, missingv)
        args = args[3:]
    if len(args) > 0:
        level_arg = args[0]
        if isinstance(level_arg, int):
            cn = level_arg
            ls = LegendManage.createLegendScheme(gdata.getminvalue(), gdata.getmaxvalue(), cn, cmap)
        else:
            ls = LegendManage.createLegendScheme(gdata.getminvalue(), gdata.getmaxvalue(), level_arg, cmap)
    else:    
        ls = LegendManage.createLegendScheme(gdata.getminvalue(), gdata.getmaxvalue(), cmap)
    layer = __plot_griddata(gdata, ls, 'contour')
    return layer

def contourf(*args, **kwargs):
    n = len(args)    
    cmap = __getcolormap(**kwargs)
    missingv = kwargs.pop('missingv', -9999.0)
    if n <= 2:
        gdata = midata.asgriddata(args[0])
        args = args[1:]
    elif n <=4:
        x = args[0]
        y = args[1]
        a = args[2]
        gdata = midata.asgriddata(a, x, y, missingv)
        args = args[3:]
    if len(args) > 0:
        level_arg = args[0]
        if isinstance(level_arg, int):
            cn = level_arg
            ls = LegendManage.createLegendScheme(gdata.getminvalue(), gdata.getmaxvalue(), cn, cmap)
        else:
            if isinstance(level_arg, MIArray):
                level_arg = level_arg.aslist()
            ls = LegendManage.createLegendScheme(gdata.getminvalue(), gdata.getmaxvalue(), level_arg, cmap)
    else:    
        ls = LegendManage.createLegendScheme(gdata.getminvalue(), gdata.getmaxvalue(), cmap)
    layer = __plot_griddata(gdata, ls, 'contourf')
    return layer

def quiver(*args, **kwargs):
    n = len(args)    
    cmap = __getcolormap(**kwargs)
    missingv = kwargs.pop('missingv', -9999.0)
    if n <= 2:
        gdata = midata.asgriddata(args[0])
        args = args[1:]
    elif n <=4:
        x = args[0]
        y = args[1]
        a = args[2]
        gdata = midata.asgriddata(a, x, y, missingv)
        args = args[3:]
    if len(args) > 0:
        level_arg = args[0]
        if isinstance(level_arg, int):
            cn = level_arg
            ls = LegendManage.createLegendScheme(gdata.getminvalue(), gdata.getmaxvalue(), cn, cmap)
        else:
            if isinstance(level_arg, MIArray):
                level_arg = level_arg.aslist()
            ls = LegendManage.createLegendScheme(gdata.getminvalue(), gdata.getmaxvalue(), level_arg, cmap)
    else:    
        ls = LegendManage.createLegendScheme(gdata.getminvalue(), gdata.getmaxvalue(), cmap)
    layer = __plot_griddata(gdata, ls, 'contourf')
    return layer
    
def __plot_griddata(gdata, ls, type):
    #print 'GridData...'
    if type == 'contourf':
        layer = DrawMeteoData.createShadedLayer(gdata.data, ls, 'layer', 'data', True)
    elif type == 'contour':
        layer = DrawMeteoData.createContourLayer(gdata.data, ls, 'layer', 'data', True)
    elif type == 'imshow':
        layer = DrawMeteoData.createRasterLayer(gdata.data, 'layer', ls)
    mapview = MapView()
    plot = XY2DPlot(mapview)
    plot.addLayer(layer)
    chart = Chart(plot)
    #chart.setAntiAlias(True)
    chartpanel.setChart(chart)
    if isinteractive:
        chartpanel.paintGraphics()
    return layer
    
def scatterm(*args, **kwargs):
    cmap = __getcolormap(**kwargs)
    missingv = kwargs.pop('missingv', -9999.0)
    proj = kwargs.pop('proj', None)
    plot = args[0]
    args = args[1:]
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
        if a.rank == 1:
            gdata = midata.asstationdata(a, x, y, missingv)
        else:
            gdata = midata.asgriddata(a, x, y, missingv)
        args = args[3:]
    if len(args) > 0:
        level_arg = args[0]
        if isinstance(level_arg, int):
            cn = level_arg
            ls = LegendManage.createLegendScheme(gdata.getminvalue(), gdata.getmaxvalue(), cn, cmap)
        else:
            ls = LegendManage.createLegendScheme(gdata.getminvalue(), gdata.getmaxvalue(), level_arg, cmap)
    else:    
        ls = LegendManage.createLegendScheme(gdata.getminvalue(), gdata.getmaxvalue(), cmap)
    if isinstance(gdata, PyGridData):
        layer = __plot_griddata_m(plot, gdata, ls, 'scatter', proj=proj)
    else:
        layer = __plot_stationdata_m(plot, gdata, ls, 'scatter', proj=proj)
    gdata = None
    return layer
        
def imshowm(*args, **kwargs):
    cmap = __getcolormap(**kwargs)
    missingv = kwargs.pop('missingv', -9999.0)
    proj = kwargs.pop('proj', None)
    plot = args[0]
    args = args[1:]
    n = len(args) 
    if n <= 2:
        gdata = midata.asgriddata(args[0])
        args = args[1:]
    elif n <=4:
        x = args[0]
        y = args[1]
        a = args[2]
        gdata = midata.asgriddata(a, x, y, missingv)
        args = args[3:]
    if len(args) > 0:
        level_arg = args[0]
        if isinstance(level_arg, int):
            cn = level_arg
            ls = LegendManage.createLegendScheme(gdata.getminvalue(), gdata.getmaxvalue(), cn, cmap)
        else:
            ls = LegendManage.createLegendScheme(gdata.getminvalue(), gdata.getmaxvalue(), level_arg, cmap)
    else:    
        #ls = LegendManage.createLegendScheme(gdata.getminvalue(), gdata.getmaxvalue(), cmap)
        ls = LegendManage.createImageLegend(gdata.data, cmap)
    layer = __plot_griddata_m(plot, gdata, ls, 'imshow', proj=proj)
    gdata = None
    return layer
    
def contourm(*args, **kwargs):      
    cmap = __getcolormap(**kwargs)
    missingv = kwargs.pop('missingv', -9999.0)    
    plot = args[0]
    args = args[1:]
    n = len(args) 
    if n <= 2:
        gdata = midata.asgriddata(args[0])
        args = args[1:]
    elif n <=4:
        x = args[0]
        y = args[1]
        a = args[2]
        gdata = midata.asgriddata(a, x, y, missingv)
        args = args[3:]
    if len(args) > 0:
        level_arg = args[0]
        if isinstance(level_arg, int):
            cn = level_arg
            ls = LegendManage.createLegendScheme(gdata.getminvalue(), gdata.getmaxvalue(), cn, cmap)
        else:
            ls = LegendManage.createLegendScheme(gdata.getminvalue(), gdata.getmaxvalue(), level_arg, cmap)
    else:    
        ls = LegendManage.createLegendScheme(gdata.getminvalue(), gdata.getmaxvalue(), cmap)
    layer = __contour_griddata_m(plot, gdata, ls, 'contour')
    gdata = None
    return layer
        
def contourfm(*args, **kwargs):
    cmap = __getcolormap(**kwargs)
    missingv = kwargs.pop('missingv', -9999.0)
    plot = args[0]
    args = args[1:]
    n = len(args) 
    if n <= 2:
        gdata = midata.asgriddata(args[0])
        args = args[1:]
    elif n <=4:
        x = args[0]
        y = args[1]
        a = args[2]
        gdata = midata.asgriddata(a, x, y, missingv)
        args = args[3:]
    if len(args) > 0:
        level_arg = args[0]
        if isinstance(level_arg, int):
            cn = level_arg
            ls = LegendManage.createLegendScheme(gdata.getminvalue(), gdata.getmaxvalue(), cn, cmap)
        else:
            ls = LegendManage.createLegendScheme(gdata.getminvalue(), gdata.getmaxvalue(), level_arg, cmap)
    else:    
        ls = LegendManage.createLegendScheme(gdata.getminvalue(), gdata.getmaxvalue(), cmap)
    layer = __plot_griddata_m(plot, gdata, ls, 'contourf')
    gdata = None
    return layer
    
def quiverm(*args, **kwargs):
    cmap = __getcolormap(**kwargs)
    missingv = kwargs.pop('missingv', -9999.0)
    isuv = kwargs.pop('isuv', True)
    size = kwargs.pop('size', 10)
    plot = args[0]
    args = args[1:]
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
        udata = midata.asgriddata(u, x, y, missingv)
        vdata = midata.asgriddata(v, x, y, missingv)
        args = args[4:]
        if len(args) > 0:
            cdata = midata.asgriddata(args[0], x, y, missingv)
            iscolor = True
            args = args[1:]
    if iscolor:
        if len(args) > 0:
            level_arg = args[0]
            if isinstance(level_arg, int):
                cn = level_arg
                ls = LegendManage.createLegendScheme(cdata.getminvalue(), cdata.getmaxvalue(), cn, cmap)
            else:
                ls = LegendManage.createLegendScheme(cdata.getminvalue(), cdata.getmaxvalue(), level_arg, cmap)
        else:
            ls = LegendManage.createLegendScheme(cdata.getminvalue(), cdata.getmaxvalue(), cmap)
    else:    
        if cmap.getColorCount() == 1:
            c = cmap.getColor(0)
        else:
            c = Color.black
        ls = LegendManage.createSingleSymbolLegendScheme(ShapeTypes.Point, c, size)
    layer = __plot_uvgriddata_m(plot, udata, vdata, cdata, ls, 'quiver', isuv)
    udata = None
    vdata = None
    cdata = None
    return layer
        
def __plot_griddata_m(plot, gdata, ls, type, proj=None):
    #print 'GridData...'
    if type == 'contourf':
        layer = DrawMeteoData.createShadedLayer(gdata.data, ls, 'layer', 'data', True)
    elif type == 'contour':
        layer = DrawMeteoData.createContourLayer(gdata.data, ls, 'layer', 'data', True)
    elif type == 'imshow':
        layer = DrawMeteoData.createRasterLayer(gdata.data, 'layer', ls)
    elif type == 'scatter':
        layer = DrawMeteoData.createGridPointLayer(gdata.data, ls, 'layer', 'data')
    else:
        layer = None
        return layer
    
    if (proj != None):
        layer.setProjInfo(proj)
        
    shapetype = layer.getShapeType()
    if shapetype == ShapeTypes.Polygon or shapetype == ShapeTypes.Image:
        plot.addLayer(0, layer)
    else:
        plot.addLayer(layer)
    plot.setDrawExtent(layer.getExtent())
    chart = Chart(plot)
    #chart.setAntiAlias(True)
    chartpanel.setChart(chart)
    if isinteractive:
        chartpanel.paintGraphics()
    return layer
    
def __plot_stationdata_m(plot, stdata, ls, type, proj=None):
    #print 'GridData...'
    if type == 'scatter':
        layer = DrawMeteoData.createSTPointLayer(stdata.data, ls, 'layer', 'data')
    else:
        layer = None
        return layer
    
    if (proj != None):
        layer.setProjInfo(proj)
 
    plot.addLayer(layer)
    plot.setDrawExtent(layer.getExtent())
    chart = Chart(plot)
    #chart.setAntiAlias(True)
    chartpanel.setChart(chart)
    if isinteractive:
        chartpanel.paintGraphics()
    return layer
    
def __plot_uvgriddata_m(plot, udata, vdata, cdata, ls, type, isuv):
    #print 'GridData...'
    if type == 'quiver':
        if cdata == None:
            layer = DrawMeteoData.createGridVectorLayer(udata.data, vdata.data, ls, 'layer', isuv)
        else:
            layer = DrawMeteoData.createGridVectorLayer(udata.data, vdata.data, cdata.data, ls, 'layer', isuv)
    shapetype = layer.getShapeType()
    plot.addLayer(layer)
    plot.setDrawExtent(layer.getExtent())
    chart = Chart(plot)
    #chart.setAntiAlias(True)
    chartpanel.setChart(chart)
    if isinteractive:
        chartpanel.paintGraphics()
    return layer


    
def clabel(layer, **kwargs):
    font = __getfont(**kwargs)
    cstr = kwargs.pop('color', 'black')
    color = __getcolor(cstr)
    labelset = layer.getLabelSet()
    labelset.setLabelFont(font)
    labelset.setLabelColor(color)
    layer.addLabelsContourDynamic(layer.getExtent())
    if isinteractive:
        chartpanel.paintGraphics()
        
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
    
def axesm(projinfo=None, proj='longlat', **kwargs):
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
    c_plot.getMapFrame().setDrawGridLabel(gridlabel)
    c_plot.getMapFrame().setDrawGridTickLine(gridlabel)
    c_plot.getMapView().projectLayers(projinfo)
    return projinfo
        
def geoshow(plot, layer, **kwargs):
    visible = kwargs.pop('visible', True)
    layer.setVisible(visible)
    drawfill = kwargs.pop('drawfill', False)
    fcobj = kwargs.pop('facecolor', None)
    if fcobj == None:
        facecolor = Color.lightGray
    else:
        facecolor = __getcolor(fcobj)
    lcobj = kwargs.pop('linecolor', None)
    if lcobj == None:
        linecolor = Color.black
    else:
        if isinstance(lcobj, str):
            linecolor = __getcolor(lcobj)
        else:
            if len(lcobj) == 3:                
                linecolor = Color(lcobj[0], lcobj[1], lcobj[2])
            else:
                linecolor = Color(lcobj[0], lcobj[1], lcobj[2], lcobj[3])
    size = kwargs.pop('size', 1)
    lb = layer.getLegendScheme().getLegendBreaks().get(0)
    lb.setColor(facecolor)
    btype = lb.getBreakType()
    if btype == BreakTypes.PointBreak:
        lb.setOutlineColor(linecolor)
    elif btype == BreakTypes.PolylineBreak:
        lb.setSize(size)
    elif btype == BreakTypes.PolygonBreak:
        lb.setDrawFill(drawfill)
        lb.setOutlineColor(linecolor)
        lb.setOutlineSize(size)
    plot.addLayer(layer)
    if isinteractive:
        chartpanel.paintGraphics()
    
def figmask(plot, dlayer, mlayer):
    mapview = plot.getMapView()
    mapview.getMaskOut().setMask(True)
    mapview.getMaskOut().setMaskLayer(mlayer.getLayerName())
    dlayer.setMaskout(True)
    if isinteractive:
        chartpanel.paintGraphics()
    
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