#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2017-7-27
# Purpose: MeteoInfo plotutil module in plotlib package
# Note: Jython
#-----------------------------------------------------

import datetime

from org.meteoinfo.legend import LineStyles, HatchStyle, BreakTypes, ColorBreak, PointBreak, PolylineBreak, PolygonBreak, BarBreak, LegendManage, LegendScheme, LegendType
from org.meteoinfo.drawing import PointStyle, MarkerType
from org.meteoinfo.global.colors import ColorUtil, ColorMap
from org.meteoinfo.shape import ShapeTypes
from java.awt import Color, Font

from mipylib.numeric.dimarray import DimArray
from mipylib.numeric.miarray import MIArray
import mipylib.numeric.minum as minum
import mipylib.miutil as miutil

def getplotdata(data):
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

def getcolor(style, alpha=None):
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
    
def getcolormap(**kwargs):
    colors = kwargs.pop('colors', None)
    issingle = False
    if colors is None:
        colors = kwargs.pop('color', None)
        issingle = True
    if not colors is None:
        if issingle or isinstance(colors, str):
            c = getcolor(colors)
            cmap = ColorMap(c)
        else:
            cs = []
            for cc in colors:
                c = getcolor(cc)
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
    
def getpointstyle(style):
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
    
def getlinestyle(style):
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
    
def getplotstyle(style, caption, **kwargs):    
    linewidth = kwargs.pop('linewidth', 1.0)
    if style is None:
        color = kwargs.pop('color', 'red')
        c = getcolor(color)
    else:
        c = getcolor(style)
    pointStyle = getpointstyle(style)
    lineStyle = getlinestyle(style)
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
            edgecolor = getcolor(edgecolor)
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
            makercolor = getcolor(makercolor)
            plb.setSymbolColor(c)
            makerfillcolor = kwargs.pop('makerfillcolor', makercolor)
            makerfillcolor = getcolor(makerfillcolor)
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
        
def getlegendbreak(geometry, **kwargs): 
    cobj = kwargs.pop('color', None)
    if cobj is None:
        cobj = kwargs.pop('facecolor', None)
    color = None
    if not cobj is None:
        color = getcolor(cobj)
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
            pstyle = getpointstyle(marker)
            lb.setStyle(pstyle)
        size = kwargs.pop('size', 6)
        lb.setSize(size)
        ecobj = kwargs.pop('edgecolor', 'k')
        edgecolor = getcolor(ecobj)
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
        linestyle = getlinestyle(lsobj)
        lb.setStyle(linestyle)
        marker = kwargs.pop('marker', None)
        if not marker is None:
            pstyle = getpointstyle(marker)
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
        edgecolor = getcolor(ecobj)
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
        lb.setColor(getcolor(lb.getColor(), alpha))
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
    
def getlegendscheme(args, min, max, **kwargs):
    ls = kwargs.pop('symbolspec', None)
    if ls is None:
        cmap = getcolormap(**kwargs)        
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
            edgecolor = getcolor(ecobj)
            ls = ls.convertTo(ShapeTypes.Polygon)
            for lb in ls.getLegendBreaks():
                lb.setDrawOutline(True)
                lb.setOutlineColor(edgecolor)
    return ls
    
def setlegendscheme(ls, **kwargs):
    st = ls.getShapeType()
    if st == ShapeTypes.Point:
        setlegendscheme_point(ls, **kwargs)
    elif st == ShapeTypes.Polyline:
        setlegendscheme_line(ls, **kwargs)
    elif st == ShapeTypes.Polygon:
        setlegendscheme_polygon(ls, **kwargs)
    else:
        setlegendscheme_image(ls, **kwargs)

def setlegendscheme_image(ls, **kwargs):
    cobj = kwargs.pop('color', None)
    if not cobj is None:
        color = getcolor(cobj)    
        for lb in ls.getLegendBreaks():
            lb.setColor(color)
    return ls
        
def setlegendscheme_point(ls, **kwargs):
    ls = ls.convertTo(ShapeTypes.Point)    
    for lb in ls.getLegendBreaks():
        setpointlegendbreak(lb, **kwargs)
    return ls
    
def setlegendscheme_line(ls, **kwargs):
    ls = ls.convertTo(ShapeTypes.Polyline)
    size = kwargs.pop('size', 1)
    lsobj = kwargs.pop('linestyle', '-')
    linestyle = getlinestyle(lsobj)
    cobj = kwargs.pop('color', None)
    if cobj is None:
        color = None
    else:
        color = getcolor(cobj)    
    for lb in ls.getLegendBreaks():
        if not color is None:
            lb.setColor(color)
        lb.setStyle(linestyle)
        lb.setSize(size)
    return ls
    
def setlegendscheme_polygon(ls, **kwargs):
    ls = ls.convertTo(ShapeTypes.Polygon)
    fcobj = kwargs.pop('facecolor', None)
    if fcobj is None:
        facecolor = None
    else:
        facecolor = getcolor(fcobj)
    ecobj = kwargs.pop('edgecolor', 'k')
    edgecolor = getcolor(ecobj)
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
    
def setpointlegendbreak(lb, **kwargs):       
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
        pstyle = getpointstyle(marker)
        lb.setStyle(pstyle)
    size = kwargs.pop('size', 6)
    lb.setSize(size)
    ecobj = kwargs.pop('edgecolor', 'k')
    edgecolor = getcolor(ecobj)
    lb.setOutlineColor(edgecolor)
    fill = kwargs.pop('fill', True)
    lb.setDrawFill(fill)
    edge = kwargs.pop('edge', True)
    lb.setDrawOutline(edge)