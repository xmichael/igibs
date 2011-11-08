#!/usr/bin/python
# -*- coding: utf-8 -*-

######### Probe as much info as possible from a gdal or ogr file #######
import sys, random
import osgeo.ogr as ogr
import osgeo.gdal as gdal
from osgeo.gdalconst import *

######## CONSTS ##########
# Example Datasets:
marine_tiff = '../data/Marine_Shape/nw25400040_szCE_PROTECTED_AREAS_region.shp'
osmm_tiff = '../data/OSMM_tiff/nt2176.tfw'
marine_shape = '../data/Marine_Tiff/0245-0_w.tif'

geom = [ "Point", "Line", "Polygon" ]

def get_random_colour():
    samples = ['#8FBC8F','#7CFC00','#FFFFFF','#4169E1','#708090','#8B8B83','#CDC9C9','#CDB79E']
    return random.choice(samples)

def detected_raster(ds):
    """ Returns a dictionary with probed values for rasters { format, driver, size, projection, origin, pixel_size } """
    res  = {}
    res['type'] = 'Raster'
    res['format'] =  ds.GetDriver().LongName
    width = ds.RasterXSize
    height = ds.RasterYSize
    res['size'] = `height` + 'x' + `width` + 'x' + `ds.RasterCount`
    #Values below are fsck'ed in OS datasets that lack Projection metadata.
    #might be an easier way to get proj4 format:
    #res['projection'] = ds.GetProjection()
    srs = ogr.osr.SpatialReference()
    srs.ImportFromWkt(ds.GetProjection())
    srs.AutoIdentifyEPSG()
    if srs != None and ( srs.AutoIdentifyEPSG() != 7 ):
        res['projection'] = "%s:%s" % ( srs.GetAuthorityName('GEOGCS').lower(), srs.GetAuthorityCode('GEOGCS') )
    else:
        res["projection"] = 'epsg:27700'    
    ####
    gt = ds.GetGeoTransform()
    if not gt is None:
        minx = gt[0]
        miny = gt[3] + width*gt[4] + height*gt[5]
        maxx = gt[0] + width*gt[1] + height*gt[2]
        maxy = gt[3] 
        res[ 'extent' ] = [ minx, miny, maxx, maxy ]
        res[ 'origin' ] = '(' + `gt[0]` + ',' + `gt[3]` + ')'
        res[ 'pixel_size' ] = '(' + `gt[1]` + ',' + `gt[5]` + ')'
    res["transparency"] = "50"
    return res


def detected_vector(ds):
    """ Returns a list of dictionary with probed values for vectors { format, layers, name, geometry_type, properties...  }.
    Properties are taken from the first layer (Assuming the properties don't change from layer to layer)."""
    res = {}
    res['type'] = 'Vector'
    layers = ds.GetLayerCount()
    res['layernum'] = layers
    #get first layer
    lr = ds.GetLayerByIndex(0)
    feature_defn = lr.GetLayerDefn()
    res["name"] = feature_defn.GetName()
    res["geometry_type"] = geom[feature_defn.GetGeomType() - 1]
    #this is the tricky bit as many datasets have really strange values
    srs = lr.GetSpatialRef()
    if srs != None and ( srs.AutoIdentifyEPSG() != 7 ):
        res["projection"] = "%s:%s" % ( srs.GetAuthorityName('GEOGCS').lower(), srs.GetAuthorityCode('GEOGCS') )
    else:
        res["projection"] = 'epsg:27700'
    # GetExtent returns minx maxx miny may 
    tmp = lr.GetExtent()
    # convert to minx miny miny maxy
    res["extent"] = [ tmp[0], tmp[2], tmp[1], tmp[3] ]
    props = [ feature_defn.GetFieldDefn(i).GetName() for i in xrange(feature_defn.GetFieldCount()) ]
    res["properties"] = `props`
    # default fill colour (white)
    res["fillColour"] = '#FFFFFF'
    # default line width
    res["width"] = '2'
    # default outline colours
    res["outlineColour"] = get_random_colour()
    # suffle: random.shuffle(colours)
    res["opacity"] = '50'
    # Add default properties
    lr.ResetReading()
    return res
        
#Should be Raster, Vector or None if filetype not supported by libogr

def find_format(filepath):
    ds = ogr.Open( filepath )
    #See if it's a vector
    if ds is None:
        #Not an Vector file."
        #perhaps it's a raster?
        ds = gdal.Open( filepath, GA_ReadOnly )
        if ds is None:
            # "Not a Raster file either."
            return None
        else:
            res =  detected_raster(ds)
            res['filepath'] = filepath
            res['name'] = filepath[filepath.rfind('/')+1:]
            return res
    else:
        res = detected_vector(ds)
        res['filepath'] = filepath
        return res

if __name__ == "__main__":
    filepath = sys.argv[1]
    res = find_format(filepath)
    if res is None:
        print "Could not detect file format"
        sys.exit(1)
    print `res`

