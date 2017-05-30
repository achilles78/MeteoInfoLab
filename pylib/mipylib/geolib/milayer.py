#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2015-9-20
# Purpose: MeteoInfoLab layer module
# Note: Jython
#-----------------------------------------------------
from org.meteoinfo.data import TableUtil, XYListDataset
from org.meteoinfo.layer import LayerTypes, VectorLayer
from org.meteoinfo.projection import ProjectionManage, KnownCoordinateSystems
from org.meteoinfo.shape import PolygonShape, ShapeTypes, PointShape, ShapeUtil
from java.util import Date, Calendar
from java.awt import Font
from datetime import datetime
import mipylib.miutil as miutil
import mipylib.numeric.minum as minum

class MILayer():
    '''
    Map layer
    
    :param layer: (*MapLayer*) MapLayer object.
    :param shapetype: (*ShapeTypes*) Shape type ['point' | 'line' | 'polygon']
    '''
    def __init__(self, layer=None, shapetype=None):
        if layer is None:
            if shapetype is None:
                print 'shapetype must be specified!'
            else:                
                type = ShapeTypes.Point
                if shapetype == 'line':
                    type = ShapeTypes.Polyline
                elif shapetype == 'polygon':
                    type = ShapeTypes.Polygon
                self.layer = VectorLayer(type)
                self.shapetype = type
                self.proj = KnownCoordinateSystems.geographic.world.WGS1984
        else:
            self.layer = layer
            self.shapetype = layer.getShapeType()
            self.proj = layer.getProjInfo()
    
    def __repr__(self):
        return self.layer.getLayerInfo()
    
    def isvectorlayer(self):
        return self.layer.getLayerType() == LayerTypes.VectorLayer
    
    def cellvalue(self, fieldname, shapeindex):
        '''
        Get attribute table cell value.
        
        :param fieldname: (*string*) Field name.
        :param shapeindex: (*int*) Shape index.
        
        :returns: The value in attribute table identified by field name and shape index.
        '''
        v = self.layer.getCellValue(fieldname, shapeindex)
        if isinstance(v, Date):
            cal = Calendar.getInstance()
            cal.setTime(v)
            year = cal.get(Calendar.YEAR)
            month = cal.get(Calendar.MONTH) + 1
            day = cal.get(Calendar.DAY_OF_MONTH)
            hour = cal.get(Calendar.HOUR_OF_DAY)
            minute = cal.get(Calendar.MINUTE)
            second = cal.get(Calendar.SECOND)
            dt = datetime(year, month, day, hour, minute, second)
            return dt
        else:
            return v
            
    def setcellvalue(self, fieldname, shapeindex, value):
        '''
        Set cell value in attribute table.
        
        :param fieldname: (*string*) Field name.
        :param shapeindex: (*int*) Shape index.
        :param value: (*object*) Cell value to be asigned.
        '''
        self.layer.editCellValue(fieldname, shapeindex, value)
            
    def shapes(self):
        return self.layer.getShapes()
        
    def shapenum(self):
        return self.layer.getShapeNum()
        
    def legend(self):
        return self.layer.getLegendScheme()
        
    def setlegend(self, legend):
        self.layer.setLegendScheme(legend)
    
    def addfield(self, fieldname, dtype, values=None):
        dt = TableUtil.toDataTypes(dtype)
        self.layer.editAddField(fieldname, dt)
        if not values is None:
            n = self.shapenum()
            for i in range(n):
                if i < len(values):
                    self.layer.editCellValue(fieldname, i, values[i])
                    
    def delfield(self, fieldname):
        self.layer.editRemoveField(fieldname)
        
    def renamefield(self, fieldname, newfieldname):
        self.layer.editRenameField(fieldname, newfieldname)
        
    def addshape(self, x, y, fields=None):
        type = 'point'
        if self.shapetype == ShapeTypes.Polyline:
            type = 'line'
        elif self.shapetype == ShapeTypes.Polygon:
            type = 'polygon'
        shapes = makeshapes(x, y, type)
        if len(shapes) == 1:
            self.layer.editAddShape(shapes[0], fields)
        else:
            for shape, field in zip(shapes, fields):
                self.layer.editAddShape(shape, field)
                    
    def addlabels(self, fieldname, **kwargs):
        labelset = self.layer.getLabelSet()
        labelset.setFieldName(fieldname)
        fontname = kwargs.pop('fontname', 'Arial')
        fontsize = kwargs.pop('fontsize', 14)
        bold = kwargs.pop('bold', False)
        if bold:
            font = Font(fontname, Font.BOLD, fontsize)
        else:
            font = Font(fontname, Font.PLAIN, fontsize)
        labelset.setLabelFont(font)
        color = kwargs.pop('color', None)
        if not color is None:
            color = miutil.getcolor(color)
            labelset.setLabelColor(color)
        xoffset = kwargs.pop('xoffset', 0)
        labelset.setXOffset(xoffset)
        yoffset = kwargs.pop('yoffset', 0)
        labelset.setYOffset(yoffset)
        avoidcoll = kwargs.pop('avoidcoll', True)
        labelset.setAvoidCollision(avoidcoll)
        self.layer.addLabels()
        
    def getlabel(self, text):
        return self.layer.getLabel(text)
        
    def movelabel(self, label, x=0, y=0):
        self.layer.moveLabel(label, x, y)
        
    def project(self, toproj):
        r = ProjectionManage.projectLayer(self.layer, toproj)
        return MILayer(r)
        
    def buffer(self, dist=0, merge=False):
        r = self.layer.buffer(dist, False, merge)
        return MILayer(r)
        
    def clip(self, clipobj):
        if isinstance(clipobj, PolygonShape):
            clipobj = [clipobj]
        elif isinstance(clipobj, MILayer):
            clipobj = clipobj.layer
        r = self.layer.clip(clipobj)
        return MILayer(r)
        
    def clone(self):
        return MILayer(self.layer.clone())
    
    def save(self, fn=None):
        """
        Save layer as shape file.
        
        :param fn: (*string*) Shape file name (.shp).
        """
        if fn is None:
            if self.layer.getFileName().strip() == '':
                print 'File name is needed to save the layer!'
            else:
                self.layer.saveFile()    
        else:
            self.layer.saveFile(fn)
    
    def savekml(self, fn):
        """
        Save layer as KML file.
        
        :param fn: (*string*) KML file name.
        """
        self.layer.saveAsKMLFile(fn)

def makeshapes(x, y, type=None, z=None, m=None):
    """
    Make shapes by x and y coordinates.
    
    :param x: (*array_like*) X coordinates.
    :param y: (*array_like*) Y coordinates.    
    :param type: (*string*) Shape type [point | line | polygon].
    :param z: (*array_like*) Z coordinates.
    :param m: (*array_like*) M coordinates.
    
    :returns: Shapes
    """
    shapes = []   
    if isinstance(x, (int, float)):
        shape = PointShape()
        shape.setPoint(PointD(x, y))
        shapes.append(shape)    
    else:
        x = minum.asarray(x)
        y = minum.asarray(y)
        if not z is None:
            z = minum.asarray(z)
            if m is None:
                m = minum.zeros(len(z)).array
            else:
                m = minum.asarray(m)
        if type == 'point':
            if z is None:
                shapes = ShapeUtil.createPointShapes(x, y)
            else:
                shapes = ShapeUtil.createPointShapes(x, y, z, m)
        elif type == 'line':
            if z is None:
                shapes = ShapeUtil.createPolylineShapes(x, y)
            else:
                shapes = ShapeUtil.createPolylineShapes(x, y, z, m)
        elif type == 'polygon':
            if z is None:
                shapes = ShapeUtil.createPolygonShapes(x, y)
            else:
                shapes = ShapeUtil.createPolygonShape(x, y, z, m)
    return shapes   
        
class MIXYListData():
    def __init__(self, data=None):
        if data is None:
            self.data = XYListDataset()
        else:
            self.data = data
        
    def __getitem__(self, indices):
        if not isinstance(indices, tuple):
            inds = []
            inds.append(indices)
            indices = inds
            
        if isinstance(indices[0], int):
            if isinstance(indices[1], int):
                x = self.data.getX(indices[0], indices[1])
                y = self.data.getY(indices[0], indices[1])
                return x, y
            else:
                return self.data.getXValues(indices[0]), self.data.getXValues(indices[0])           
        
    def size(self, series=None):
        if series is None:
            return self.data.getSeriesCount()
        else:
            return self.data.getItemCount(series)
            
    def addseries(self, xdata, ydata, key=None):
        if key is None:
            key = 'Series_' + str(self.size())
        if isinstance(xdata, list):
            self.data.addSeries(key, xdata, ydata)
        else:
            self.data.addSeries(key, xdata.asarray(), ydata.asarray())   
            