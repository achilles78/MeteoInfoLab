# coding=utf-8
#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2017-5-25
# Purpose: MeteoInfoLab io in image package
# Note: Jython
#-----------------------------------------------------

from org.meteoinfo.shape import Graphic
from org.meteoinfo.image import ImageUtil
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
    'imread','imwrite'    
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
 
def imwrite(a, fname):
    '''
    Write RGB(A) data array into an image file.
    
    :param a: (*array*) RGB(A) data array.
    :param fname: (*String*) Image file name.
    '''
    ImageUtil.imageSave(a, fname)
        