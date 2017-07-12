# coding=utf-8
#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2017-3-25
# Purpose: MeteoInfoLab axes module
# Note: Jython
#-----------------------------------------------------

from org.meteoinfo.chart.plot import Plot2D, MapPlot, PolarPlot, PiePlot, Plot3D

from java.awt import Font

from mipylib.numeric.dimarray import DimArray
from mipylib.numeric.miarray import MIArray

class Axes():
    '''
    Axes with Cartesian coordinate.
    '''

    def __init__(self, axes=None):
        if axes is None:
            self.axes = Plot2D()
        else:
            self.axes = axes
            
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
        
    def set_title(self, title):
        '''
        Set title
        
        :param title: (*string*) Title
        '''
        self.axes.setTitle(title)
    
    def add_graphic(self, graphic):
        '''
        Add a graphic
        
        :param graphic: (*Graphic*) The graphic to be added.
        '''
        self.axes.addGraphic(graphic)
        
##############################################
class PieAxes(Axes):
    '''
    Axes for pie plot.       
    '''
    
    def __init__(self, axes=None):
        if axes is None:        
            self.axes = PiePlot()
        else:
            self.axes = axes

##############################################        
class MapAxes(Axes):
    '''
    Axes with geological map coordinate.
    '''
    
    def __init__(self, axes=None, mapview=None):
        if axes is None:        
            if mapview is None:
                self.axes = MapPlot()
            else:
                self.axes = MapPlot(mapview)
        else:
            self.axes = axes
            
    def add_layer(self, layer, zorder=None):
        '''
        Add a map layer
        
        :param layer: (*MapLayer*) The map layer.
        :param zorder: (*int*) Layer z order.
        '''
        if zorder is None:
            self.axes.addLayer(layer)
        else:
            self.axes.addLayer(zorder, layer)
            
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
        
#########################################################
class Axes3D(Axes):
    '''
    Axes with 3 dimensional.
    '''
    
    def __init__(self, axes=None, panel=None):
        if axes is None:        
            self.axes = Plot3D(panel)
        else:
            self.axes = axes