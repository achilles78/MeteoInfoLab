# coding=utf-8
#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2018-4-4
# Purpose: MeteoInfoLab figure module
# Note: Jython
#-----------------------------------------------------

from org.meteoinfo.chart import ChartPanel, Chart, Location, MouseMode
import plotutil
from axes import Axes, PolarAxes, Axes3D
from mapaxes import MapAxes
from java.awt import Font

class Figure(ChartPanel):
    '''
    top level container for all plot elements
    '''
    
    def __init__(self, figsize=None, dpi=None, bgcolor='w'):
        '''
        Constructor
        
        :param figsize: (*list*) Optional, width and height of the figure such as ``[600, 400]``.
        :param bgcolor: (*Color*) Optional, background color of the figure. Default is ``w`` (white).
        :param dpi: (*int*) Dots per inch.
        '''
        chart = Chart()
        chart.setBackground(plotutil.getcolor(bgcolor))
        if figsize is None:
            super(Figure, self).__init__(chart)
        else:
            super(Figure, self).__init__(chart, figsize[0], figsize[1])
            
    def get_size(self):
        '''
        Get figure size.
        
        :returns: Figure width and height
        '''
        return self.getFigureWidth(), self.getFigureHeight()
     
    def __create_axes(self, *args, **kwargs):
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
        
    def __set_axes_common(self, ax, *args, **kwargs):
        if len(args) > 0:
            position = args[0]
        else:
            position = kwargs.pop('position', None)    
        outerposition = kwargs.pop('outerposition', None)
        if position is None:
            if ax.axestype == '3d':
                position = [0.13, 0.11, 0.71, 0.815]
            else:
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
        
    def __set_axes(self, ax, **kwargs):
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
        bgcolor = plotutil.getcolor(bgcobj)
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
        
    def __create_axesm(self, *args, **kwargs):  
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
        
    def __set_axesm(self, ax, **kwargs):  
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
        aspect = kwargs.pop('aspect', 'equal')
        if aspect == 'equal':
            ax.axes.setAutoAspect(False)
        elif aspect == 'auto':
            ax.axes.setAutoAspect(True)
        else:
            if isinstance(aspect, (int, float)):
                ax.axes.setAspect(aspect)
                ax.axes.setAutoAspect(False)
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
        ax.axes.setAspect(xyscale)
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
        mapframe.setGridFont(font)
        mapframe.setDrawGridLabel(gridlabel)
        mapframe.setDrawGridTickLine(gridlabel)
        mapframe.setDrawGridLine(gridline)
        mapframe.setGridXDelt(griddx)
        mapframe.setGridYDelt(griddy)
        ax.axes.setDrawNeatLine(frameon)
        bgcolor = plotutil.getcolor(bgcobj)
        ax.axes.setBackground(bgcolor)
     
        return ax

    def __create_axes3d(self, *args, **kwargs):
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
        
    def __set_axes3d(self, ax, **kwargs):
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
        tickfontname = kwargs.pop('tickfontname', 'Arial')
        tickfontsize = kwargs.pop('tickfontsize', 14)
        tickbold = kwargs.pop('tickbold', False)
        if tickbold:
            font = Font(tickfontname, Font.BOLD, tickfontsize)
        else:
            font = Font(tickfontname, Font.PLAIN, tickfontsize)
        ax.axes.setAxisTickFont(font)
        return ax
        
    def new_axes(self, *args, **kwargs):
        '''
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
        '''
        axestype = kwargs.pop('axestype', 'cartesian')
        polar = kwargs.pop('polar', False)
        if polar:
            axestype = 'polar'
        if axestype == 'polar':
            ax = PolarAxes(figure=self)
            self.__set_axes(ax, **kwargs)
        elif axestype == 'map':
            ax = MapAxes(figure=self, **kwargs)
            self.__set_axesm(ax, **kwargs)
        elif axestype == '3d':
            ax = Axes3D(figure = self, **kwargs)
            self.__set_axes3d(ax, **kwargs)
        else:
            ax = Axes(figure=self)
            self.__set_axes(ax, **kwargs)
        self.__set_axes_common(ax, *args, **kwargs)   

        return ax
     
    def add_axes(self, *args, **kwargs):
        '''
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
        '''
        ax = self.new_axes(*args, **kwargs)
        newaxes = kwargs.pop('newaxes', True)
        chart = self.getChart()
        if newaxes:
            chart.addPlot(ax.axes)
        else:
            plot = chart.getCurrentPlot()
            if plot.isSubPlot:
                ax.axes.isSubPlot = True
                position = kwargs.pop('position', None)
                if position is None:
                    ax.set_position(plot.getPosition())  
            chart.setCurrentPlot(ax.axes)

        return ax
        
    def draw(self):
        '''
        Re-paint the figure.
        '''
        self.paintGraphics()
        
    def set_mousemode(self, mm):
        '''
        Set MouseMode.
        
        :param mm: (*string*) MouseMode string [zoom_in | zoom_out | pan | identifer
            | rotate | select].
        '''
        mm = MouseMode.valueOf(mm.upper())
        self.setMouseMode(mm)
