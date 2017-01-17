#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2014-12-27
# Purpose: MeteoInfo data module
# Note: Jython
#-----------------------------------------------------

import os

from org.meteoinfo.data.meteodata import MeteoDataInfo, Dimension, DimensionType

from  mipylib.numeric.dimarray import PyGridData, DimArray, PyStationData
import dimdatafile
from dimdatafile import DimDataFile, DimDataFiles

currentfolder = None

__all__ = [
    'addfile','addfiles','addfile_arl','addfile_ascii_grid','addfile_awx','addfile_geotiff',
    'addfile_grads','addfile_hyconc','addfile_hytraj','addfile_lonlat','addfile_micaps',
    'addfile_mm5','addfile_nc','addfile_surfer',
    'getgriddata','getstationdata'
    ]

def isgriddata(gdata):
    return isinstance(gdata, PyGridData)
    
def isstationdata(sdata):
    return isinstance(sdata, PyStationData)
    
def __getfilename(fname):
    s5 = fname[0:5]
    isweb = False
    if s5 == 'http:' or s5 == 'https' or s5 == 'dods:' or s5 == 'dap4:':
        isweb = True
        return fname, isweb
    if os.path.exists(fname):
        if os.path.isabs(fname):
            return fname, isweb
        else:
            return os.path.join(currentfolder, fname), isweb
    else:
        if currentfolder != None:
            fname = os.path.join(currentfolder, fname)
            if os.path.isfile(fname):
                return fname, isweb
            else:
                print 'File not exist: ' + fname
                return None, isweb
        else:
            print 'File not exist: ' + fname
            return None, isweb
            
def addfiles(fnames):
    '''
    Open multiple data files.
    
    :param fnames: (*list of string*) Data file names to be opened.
    
    :returns: (*DimDataFiles*) DimDataFiles object.
    '''
    dfs = []
    for fname in fnames:
        dfs.append(addfile(fname))
    return DimDataFiles(dfs)
          
def addfile(fname, access='r', dtype='netcdf', keepopen=False, **kwargs):
    """
    Opens a data file that is written in a supported file format.
    
    :param fname: (*string*) The full or relative path of the data file to load.
    :param access: (*string*) The access right setting to the data file. Default is ``r``.
    :param dtype: (*string*) The data type of the data file. Default is ``netcdf``.
    :param keepopen: (*boolean*) If the file keep open after this function. Default is ``False``. The
        file need to be closed later if ``keepopen`` is ``True``.
    
    :returns: (*DimDataFile*) Opened file object.
    """
    if access == 'r':
        fname = fname.strip()
        fname, isweb = __getfilename(fname)
        if fname is None:
            return None

        if isweb:
            return addfile_nc(fname, False)
        
        if not os.path.exists(fname):
            print 'File not exist: ' + fname
            return None
        
        fsufix = os.path.splitext(fname)[1].lower()
        if fsufix == '.ctl':
            return addfile_grads(fname, False)
        elif fsufix == '.tif':
            return addfile_geotiff(fname, False)
        elif fsufix == '.awx':
            return addfile_awx(fname, False)
        
        meteodata = MeteoDataInfo()
        meteodata.openData(fname, keepopen)
        datafile = DimDataFile(meteodata)
        return datafile
    elif access == 'c':
        if dtype == 'arl':
            arldata = ARLDataInfo()
            arldata.createDataFile(fname)
            datafile = DimDataFile(arldata=arldata)
        elif dtype == 'bufr':
            bufrdata = BufrDataInfo()
            if os.path.exists(fname):
                try:
                    os.remove(fname)
                except:   
                    info=sys.exc_info()   
                    print info[0],":",info[1]
            bufrdata.createDataFile(fname)
            datafile = DimDataFile(bufrdata=bufrdata)
        else:
            version = kwargs.pop('version', 'netcdf3')
            if version == 'netcdf3':
                version = NetcdfFileWriter.Version.netcdf3
            else:
                version = NetcdfFileWriter.Version.netcdf4
            ncfile = NetcdfFileWriter.createNew(version, fname)
            datafile = DimDataFile(ncfile=ncfile)
        return datafile
    else:
        return None
    
def addfile_grads(fname, getfn=True):
    '''
    Add a GrADS data file.
    
    :param fname: (*string*) GrADS control file name.
    :param getfn: (*string*) If run ``__getfilename`` function or not. Default is ``True``.
    
    :returns: (*DimDataFile*) Opened file object.
    '''
    if getfn:
        fname, isweb = __getfilename(fname)
    meteodata = MeteoDataInfo()
    meteodata.openGrADSData(fname)
    datafile = DimDataFile(meteodata)
    return datafile
    
def addfile_nc(fname, getfn=True):
    '''
    Add a netCDF data file.
    
    :param fname: (*string*) The netCDF file name.
    :param getfn: (*string*) If run ``__getfilename`` function or not. Default is ``True``.
    
    :returns: (*DimDataFile*) Opened file object.
    '''
    if getfn:
        fname, isweb = __getfilename(fname)
    meteodata = MeteoDataInfo()
    meteodata.openNetCDFData(fname)
    datafile = DimDataFile(meteodata)
    return datafile
    
def addfile_arl(fname, getfn=True):
    '''
    Add a ARL data file.
    
    :param fname: (*string*) The ARL file name.
    :param getfn: (*string*) If run ``__getfilename`` function or not. Default is ``True``.
    
    :returns: (*DimDataFile*) Opened file object.
    '''
    if getfn:
        fname, isweb = __getfilename(fname)
    meteodata = MeteoDataInfo()
    meteodata.openARLData(fname)
    datafile = DimDataFile(meteodata)
    return datafile
    
def addfile_surfer(fname, getfn=True):
    '''
    Add a Surfer ASCII grid data file.
    
    :param fname: (*string*) The Surfer ASCII grid file name.
    :param getfn: (*string*) If run ``__getfilename`` function or not. Default is ``True``.
    
    :returns: (*DimDataFile*) Opened file object.
    '''
    if getfn:
        fname, isweb = __getfilename(fname)
    meteodata = MeteoDataInfo()
    meteodata.openSurferGridData(fname)
    datafile = DimDataFile(meteodata)
    return datafile
    
def addfile_mm5(fname, getfn=True):
    '''
    Add a MM5 data file.
    
    :param fname: (*string*) The MM5 file name.
    :param getfn: (*string*) If run ``__getfilename`` function or not. Default is ``True``.
    
    :returns: (*DimDataFile*) Opened file object.
    '''
    if getfn:
        fname, isweb = __getfilename(fname)
    meteodata = MeteoDataInfo()
    meteodata.openMM5Data(fname)
    datafile = DimDataFile(meteodata)
    return datafile
    
def addfile_lonlat(fname, getfn=True, missingv=-9999.0):
    '''
    Add a Lon/Lat ASCII data file.
    
    :param fname: (*string*) The Lon/Lat ASCII file name.
    :param getfn: (*string*) If run ``__getfilename`` function or not. Default is ``True``.
    
    :returns: (*DimDataFile*) Opened file object.
    '''
    if getfn:
        fname, isweb = __getfilename(fname)
    meteodata = MeteoDataInfo()
    meteodata.openLonLatData(fname)
    meteodata.getDataInfo().setMissingValue(missingv)
    datafile = DimDataFile(meteodata)
    return datafile
    
def addfile_micaps(fname, getfn=True):
    '''
    Add a MICAPS data file.
    
    :param fname: (*string*) The MICAPS file name.
    :param getfn: (*string*) If run ``__getfilename`` function or not. Default is ``True``.
    
    :returns: (*DimDataFile*) Opened file object.
    '''
    if getfn:
        fname, isweb = __getfilename(fname)
    meteodata = MeteoDataInfo()
    meteodata.openMICAPSData(fname)
    datafile = DimDataFile(meteodata)
    return datafile

def addfile_hytraj(fname, getfn=True):
    '''
    Add a HYSPLIT trajectory endpoint data file.
    
    :param fname: (*string*) The HYSPLIT trajectory endpoint file name.
    :param getfn: (*string*) If run ``__getfilename`` function or not. Default is ``True``.
    
    :returns: (*DimDataFile*) Opened file object.
    '''
    if isinstance(fname, basestring):
        if getfn:
            fname, isweb = __getfilename(fname)
    meteodata = MeteoDataInfo()
    meteodata.openHYSPLITTrajData(fname)
    datafile = DimDataFile(meteodata)
    return datafile
    
def addfile_hyconc(fname, getfn=True):
    '''
    Add a HYSPLIT concentration data file.
    
    :param fname: (*string*) The HYSPLIT concentration file name.
    :param getfn: (*string*) If run ``__getfilename`` function or not. Default is ``True``.
    
    :returns: (*DimDataFile*) Opened file object.
    '''
    if getfn:
        fname, isweb = __getfilename(fname)
    meteodata = MeteoDataInfo()
    meteodata.openHYSPLITConcData(fname)
    datafile = DimDataFile(meteodata)
    return datafile
    
def addfile_geotiff(fname, getfn=True):
    '''
    Add a GeoTiff data file.
    
    :param fname: (*string*) The GeoTiff file name.
    :param getfn: (*string*) If run ``__getfilename`` function or not. Default is ``True``.
    
    :returns: (*DimDataFile*) Opened file object.
    '''
    if getfn:
        fname, isweb = __getfilename(fname)
    meteodata = MeteoDataInfo()
    meteodata.openGeoTiffData(fname)
    datafile = DimDataFile(meteodata)
    return datafile
    
def addfile_awx(fname, getfn=True):
    '''
    Add a AWX data file (Satellite data file format from CMA).
    
    :param fname: (*string*) The AWX file name.
    :param getfn: (*string*) If run ``__getfilename`` function or not. Default is ``True``.
    
    :returns: (*DimDataFile*) Opened file object.
    '''
    if getfn:
        fname, isweb = __getfilename(fname)
    meteodata = MeteoDataInfo()
    meteodata.openAWXData(fname)
    datafile = DimDataFile(meteodata)
    return datafile
    
def addfile_ascii_grid(fname, getfn=True):
    '''
    Add a ESRI ASCII grid data file.
    
    :param fname: (*string*) The ESRI ASCII grid file name.
    :param getfn: (*string*) If run ``__getfilename`` function or not. Default is ``True``.
    
    :returns: (*DimDataFile*) Opened file object.
    '''
    if getfn:
        fname, isweb = __getfilename(fname)
    if not os.path.exists(fname):
        print 'File not exist: ' + fname
        return None
    meteodata = MeteoDataInfo()
    meteodata.openASCIIGridData(fname)
    datafile = DimDataFile(meteodata)
    return datafile       