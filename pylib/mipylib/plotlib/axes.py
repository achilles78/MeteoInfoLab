# coding=utf-8
#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2017-3-25
# Purpose: MeteoInfoLab axes module
# Note: Jython
#-----------------------------------------------------

from org.meteoinfo.chart.plot import PolarPlot

class PolarAxes(PolarPlot):
    '''
    Axes with polar coordinate.
    '''
    
    def set_rmax(self, rmax):
        '''
        Set radius max circle.
        
        :param rmax: (*float*) radius max value.
        '''
        self.setRadius(rmax)