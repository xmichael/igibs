## This is a Singleton class to return values stored under resources/config.ini. 
## Read that file for documentation.
## note to java coders: Singletons in python are just modules with plain functions.

import ConfigParser

config = ConfigParser.SafeConfigParser()
config.read(['resources/config.ini'])

# e.g. ./mapfiles
def getMapfileDir():
    return config.get('DEFAULT','mapfile_dir')

def getDataDir():
    return config.get('DEFAULT','data_dir')

def getMarineTiff():
    return config.get('TEST','marine_tiff') 

def getOSMMTiff():
    return config.get('TEST','osmm_tiff') 

def getMarineShape():
    return config.get('TEST','marine_shape') 

def getLandsatTiff():
    return config.get('TEST','landsat_tif')

def getWalesShape():
    return config.get('TEST','wales_shape')

def getMapserverURL():
    return config.get('DEFAULT','wms_url')

def getSecureMapserverURL():
    return config.get('DEFAULT','shib_wms_url')

def getWAGURL():
    return config.get('DEFAULT','wag_url')

def getRedirect():
    return config.get('DEFAULT','redirect')


if __name__ == "__main__":
    print "OSMMTiff: " + getOSMMTiff()
    print "MarineTiff: " + getMarineTiff()
    print "Shib wms url (with expansion): " + getSecureMapserverURL()

