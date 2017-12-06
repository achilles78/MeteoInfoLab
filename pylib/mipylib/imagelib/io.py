# coding=utf-8
#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2017-5-25
# Purpose: MeteoInfoLab io in image package
# Note: Jython
#-----------------------------------------------------

from org.meteoinfo.shape import Graphic
from org.meteoinfo.image import ImageUtil
from org.meteoinfo.global.image import GifDecoder
from mipylib.geolib.milayer import MILayer
from mipylib.numeric.miarray import MIArray
from org.meteoinfo.image.filter import ContrastFilter, SharpenFilter, RGBAdjustFilter, ChannelMixFilter, \
    GainFilter, GammaFilter, GrayFilter, GrayscaleFilter, HSBAdjustFilter, InvertAlphaFilter, \
    InvertFilter, LevelsFilter, MaskFilter, PosterizeFilter, RescaleFilter, SolarizeFilter, \
    ThresholdFilter, FlipFilter, RotateFilter, EmbossFilter, TritoneFilter, LightFilter, OpacityFilter
from java.awt.image import BufferedImage
import math
import os

__all__ = [
    'imread','imload','imwrite','gifopen','gifread','gifload'
    ]

def imread(fname):
    '''
    Read RGB(A) data array from image file.
    
    :param fname: (*String*) Image file name.
    
    :returns: (*array*) RGB(A) data array.
    '''
    if not os.path.exists(fname):
        raise IOError(fname)
    r = ImageUtil.imageRead(fname)
    return MIArray(r)
    
def imload(fname):
    '''
    Load image from image file.
    
    :param fname: (*String*) Image file name.
    
    :returns: (*BufferedImage*) Loadded image.
    '''
    if not os.path.exists(fname):
        raise IOError(fname)
    r = ImageUtil.imageLoad(fname)
    return r
 
def imwrite(a, fname):
    '''
    Write RGB(A) data array or image into an image file.
    
    :param a: (*array or BufferedImage*) RGB(A) data array or image.
    :param fname: (*String*) Image file name.
    '''
    ImageUtil.imageSave(a, fname)
        
def gifopen(fname):
    '''
    Open a gif image file.
    
    :param fname: (*string*) Gif image file name.
    
    :returns: (*GifDecoder*) Gif decoder object.
    '''
    if not os.path.exists(fname):
        raise IOError(fname)
    decoder = GifDecoder()
    decoder.read(fname)
    return decoder
    
def gifread(gif, frame=0):
    '''
    Read RGB(A) data array from a gif image file or a gif decoder object.
    
    :param gif: (*string or GifDecoder*) Gif image file or gif decoder object.
    :param frame: (*int*) Image frame index.
    
    :returns: (*array*) RGB(A) data array.
    '''
    if isinstance(gif, basestring):
        gif = gifopen(gif)
    im = gif.getFrame(frame)
    r = ImageUtil.imageRead(im)
    return MIArray(r)
    
def gifload(gif, frame=0):
    '''
    Load image from a gif image file or a gif decoder object.
    
    :param gif: (*string or GifDecoder*) Gif image file or gif decoder object.
    :param frame: (*int*) Image frame index.
    
    :returns: (*BufferedImage*) Loadded image.
    '''
    if isinstance(gif, basestring):
        gif = gifopen(gif)
    im = gif.getFrame(frame)
    return im