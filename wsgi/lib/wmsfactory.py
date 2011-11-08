import uuid, os, time, json
import configuration, helper, geozip

class WMSFactory:
    """ Class to reponsible for the generation, tracking, saving, loading of View Services/WMSs """
    #########################
    ### WEB related stuff ###
    #########################
    # IP
    ip = ""
    # File Object containing uploaded data
    zfiledata = "" 
    # uuid corresponding to request (for sharing). This is permanent and unique
    uuid = ""
    # filename (main file e.g. foo.shp in the filepath to open)
    zfilename = ""
    # file pointer
    zfiledata = ""
    # Full path pointing to the saved data directory
    filedir = ""
    # time of request (object)
    time = None    
    ######################
    ### WMS Metatadata ###
    ######################
    #calculated dataset name without funny chars:
    datasetname = ""
    # full path pointing of the generated mapfile
    mapfile = ""
    # Shibboleth Protected
    protected = False
    ######################
    ### LAYER Metadata ###
    ######################
    # rasters
    rasters = None
    # vectors
    vectors = None
    # layers = rasters + vectors
    layers = None

    ################
    ### metadata ###
    ################
    # General attirbutes for WMS including metadata for wms 1.3.0, global extent envelope, default target projection, protected etc.
    wms_md = {}
    
    def __init__(self):
        """ Use one of the loadXXX methods to initialise the class as python does not have multiple constructors """
        pass

    def loadFromWeb(self, ip, uploadFilename, uploadFile):
        """
        Create a wms based on a uploaded zip file.
        
        ip: remote address
        uploadFilename: upload user name of file (string)
        uploadFile: uploaded user file (file pointer made available by WSGI server)
        """
        helper.dbg("Filename was: " + uploadFilename )
        self.ip = ip
        self.uuid =  uuid.uuid4().hex
        self.zfilename = uploadFilename
        self.zfiledata = uploadFile
        self.extractdir = os.path.join (configuration.getDataDir(), self.uuid)
        self.zfilepath = os.path.join (self.extractdir, self.zfilename)
        self.time = time.strftime('%d%m%y-%H:%M:%S')
        self._savefile()
        self.rasters = [] # list of probe results for rasters
        self.vectors = [] # list of probe results for vectors
        f = geozip.GeoZip(self.zfilepath)
        if f.check_integrity() == False:
            raise IOError("Checksum error: zipfile is corrupted")
        #extract all files under extractdir
        f.extract(self.extractdir)
        #group by name
        f.group_files()
        #probe all the properties of geotiffs
        self.rasters = [ helper.probedata(x) for x in f.getGeoTiffFiles() ]
        self.vectors = [ helper.probedata(x) for x in f.getShapeFiles() ]
        helper.dbg("Extracted RASTERS: " + `self.rasters`)
        helper.dbg("Extracted VECTORS: " + `self.vectors`)
        self.datasetname = helper.getBaseName(self.zfilename)
        self.layers = self.rasters + self.vectors
        self._addlayersid()
        self.wms_md = { "title": self.datasetname , "Language" : "ENG", "Keywords":"IGIBS, View Service", "Fees": "N/A", "protected": self.protected, "extent": [ -7.55645, 49.76688, 3.6342, 61.465701 ], "projection" : "epsg:4326" }
        helper.dbg("DatasetName: " + `self.datasetname`)
        helper.dbg("zfilename: " + `self.zfilename`)
        
    def loadFromFile(self, uuid):
        """
        Create a wms based on saved configuration.
        
        uuid: the uuid corresponding to the saved wms instance
        @exceptions: file does not exist, parse error
        """
        self.uuid = uuid
        self.extractdir = os.path.join (configuration.getDataDir(), self.uuid)
        
        helper.dbg("loading saved uuid: " + self.uuid)
        metadata_file = open(os.path.join ( self.extractdir, 'metadata.json' ), 'r')
        metadata = json.load( metadata_file )
        metadata_file.close()
        if metadata == None:
            raise ValueError("Cannot parse metadata.json for uuid: " + uuid)
        self.rasters = metadata["rasters"]
        self.vectors = metadata["vectors"]
        self.layers = self.rasters + self.vectors
        self._addlayersid()
        self.ip = metadata["ip"]
        self.datasetname = metadata["datasetname"]
        self.zfilename = metadata["zfilename"]
        self.zfilepath = os.path.join (self.extractdir, self.zfilename)
        self.time = metadata["time"]
        self.protected = metadata["protected"]
        self.wms_md = metadata["wms_md"]
        helper.dbg("Loaded RASTERS: " + `self.rasters`)
        helper.dbg("Loaded VECTORS: " + `self.vectors`)        

    def saveconf( self ):
        if ( (self.rasters == None) and (self.vectors == None) ):
            raise IOError("Trying to save null data!")
        metadata_file = open(os.path.join ( self.extractdir, 'metadata.json' ), 'w')
        metadata={}
        metadata["rasters"] = self.rasters
        metadata["vectors"] = self.vectors
        metadata["ip"] = self.ip
        metadata["datasetname"] = self.datasetname
        metadata["zfilename"] = self.zfilename
        metadata["time"] = self.time
        metadata["protected"] = self.protected
        metadata["wms_md"] = self.wms_md
        json.dump(metadata, metadata_file)
        metadata_file.close()
        helper.dbg("saved metadata")


    def updateconf( self, md_json ):
        """
          Updates the existing configuration using externally provided json metadata
          
        """
        metadata = json.loads(md_json)
        
        ## Global (WMS-wide) metadata
        self.wms_md = metadata["wmsdata"]
        
        ## Layer medata (array of dicts)
        layers = metadata["layers"]
        # TODO: rasters, vectors should be processed separately in javascript (client-side) to avoid this filtering
        self.rasters = [ l for l in layers if (l["type"] == "Raster") ]
        self.vectors = [ l for l in layers if (l["type"] == "Vector") ]
        self.layers = self.rasters + self.vectors
        #don't _addlayersid() as it is added on loading metadata and not on saving them

    def savemap( self, wms_url ):
        """
        Generate a mapfile based on user data. The mapfile's name is based on the uuid associated to the request
        pdata: list of dictionaries returned from from ogrprobe
        returns: path to mapfile relative to mapfile_base_dir in config.ini
        """        
        
        mapfileStr = helper.createMapfile( wmsname = self.zfilename, wmsurl = wms_url, extent= self.wms_md["extent"], units = 'METERS', wms = self)
        self.mapfile = os.path.join(configuration.getMapfileDir() , self.uuid + ".map")
        f = open(self.mapfile, "w")
        f.write(mapfileStr)
        f.close()
        helper.dbg("Wrote Mapfile: " + self.mapfile)

    def generate_wms_url(self):
        """ OBSOLETE: just use the pseudo "/VS/uuid" path to create an INSPIRE compliant view service
            Returns the URL of the backend CGI mapserv resuable from a desktop client. Make sure you call savemap() afterwards to generate the actual mapfile 
        """
        if ( self.wms_md["protected"] == True ):
            wms_url = configuration.getSecureMapserverURL() + "/" + self.uuid
        else:
            wms_url = configuration.getMapserverURL() + "/" + self.uuid
        return wms_url

    def _savefile( self ):
        """
        save the user supplied file under the data directory
        """
        # create uuid-based directory
        helper.dbg("Creating dir: " + self.extractdir)
        os.mkdir(self.extractdir, 0770)
        # save zipfile under that dir
        f = open ( self.zfilepath, "w" )
        f.write(self.zfiledata.read())
        f.close()

    def _addlayersid( self ):
        """
        add unique identifiers for on self.layers
        """
        i = 0
        for k in self.layers:
            k["id"] = i
            i=i+1
        
if __name__ == "__main__":
    ip = '127.0.0.1'
    uploadFile = open ( configuration.getMarineShape() )
    wms = WMSFactory()
    wms.loadFromWeb(ip, "myOsm.zip" , uploadFile)
    wms.saveconf()
    wms.savemap("http://127.0.0.1/igibs/cgi-mapserv/mapserv?")
    for i in wms.rasters + wms.vectors:
        print `i`


