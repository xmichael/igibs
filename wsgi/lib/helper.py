## Just some utility functions that didn't justify the creation of a class. Pretty-print, log etc...

import sys, pprint
import probe
from bottle import template
from OGRException import OGRException

### Constants ###
geom = { "1" : "Point", "2": "Line", "3": "Polygon" }
#################

## Can only log in stderr (or environ['wsgi.errors']) when using WSGI:
def dbg(msg):
    print >> sys.stderr, msg


def strfilter(text , remove):
    """
    remove chars in remove from text
    """
    return ''.join([c for c in text if c not in remove])

def pp(obj):
    """
    shortcut for pretty printing python object on the debug channel
    """
    pprinter = pprint.PrettyPrinter(indent=4)
    dbg(pprinter.pformat(obj))

def getBaseName(filename):
    """ Converts uploaded filename from something like "C\foo\windows\name.zip to name """
    #remove suffix
    tmp = filename
    tmp = tmp[ :tmp.rfind('.')]
    #remove funny chars
    return strfilter(tmp , "\\/")

def probedata(filepath):
    """
    filepath: File object of the main data file (e.g. foo.shp)
    """
    res = probe.find_format( filepath)
    if res == None:
        raise OGRException( "Could not recognise file format")
    return res

def createMapfile( wmsname, wmsurl, extent, units, wms ):
    """ wms: includes list of data results taken from ogrprobe for every geofile
        returns: mapfile as a string
    """
    mapfileStr = template('mapfile_js', wmsname = wmsname, wmsurl = wmsurl, extent = extent, units = units, wms = wms )
    return mapfileStr

