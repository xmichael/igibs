#-*- mode: python; -*-
## CHECKLIST ##
################# INIT ###################
import os, sys, json
## Change working directory so relative paths (and template lookup) work
pwd = os.path.dirname(__file__)
os.chdir(pwd)
## Also add library to the python path
sys.path.append(os.path.join(pwd,'lib'))

import bottle
from bottle import route, get, post, request, response, view, template
# igibs helper functions
import helper, wmsfactory, configuration, viewservice
from OGRException import OGRException

## TODO: Remove that from production environment:
bottle.debug(True)

################ ROUTES ####################

# ... build or import the bottle app here ...
# Do NOT use bottle.run() with mod_wsgi
application = bottle.default_app()
@route('/upload', method='POST')
def do_upload():
    response = []
    #max file size (pass from form)
    max_file_size = request.forms.get('MAX_FILE_SIZE')
    #client_ip
    ip = request.environ.get('REMOTE_ADDR')
    #data pointer
    data = request.files.get('fileInput')
    if data != None:
        try:
            wms = wmsfactory.WMSFactory()
            wms.loadFromWeb( ip, data.filename, data.file )
        except IOError:
            return template('probe_response_error', msg = "File %s is not a valid ZIP file. Please try again." %  data.filename )
        except OGRException:
            return template('probe_response_error', msg = "Could not find any usable file insize the %s. Please be reminded that each shape file requires an associated shx and dbf file (and optionally a prj file). Geotiff files require both a tif and a tfw file for each dataset." % data.filename )
        probed_data = wms.layers
        helper.pp(probed_data)
        if probed_data != []:
            wms.saveconf()
            return template('probe_response_js', uuid=wms.uuid, redirect=configuration.getRedirect())
        else:
            return template('probe_response_error', msg = "Could not find any supported format inside %s." % data.filename )
    else:
        response.append("File was NOT uploaded!")
    return response

@route('/template')
@view('upload_response')
def test_response(results = "Test Successful <br/> second line"):
    return dict(results=results)

@route('/probe_test')
def probeTest():
    """ 
    Test a pre-uploaded file. It tests the probing and mapgeneration phase of the webapp
    using an existing geo file to avoid having to upload the file manually
    """
    ### see configuratio.py for list of available testing files
    samplefile = configuration.getWalesShape()
    ### mock POST request
    filename = samplefile.split('/')[-1]
    data = open(samplefile)
    ###
    wms = wmsfactory.WMSFactory()
    wms.loadFromWeb( '127.0.0.1', filename , data )
    # save file , keep track based on uuid
    wms.saveconf()
    return template('probe_response_js', uuid=wms.uuid, redirect=configuration.getRedirect())

@route('/mapclient/:uuid')
def mapclient( uuid ):
    wms = wmsfactory.WMSFactory()
    wms.loadFromFile(uuid)
    # now create mapfile:
    wms_url = wms.generate_wms_url()
    helper.dbg( "mapclient accessing WMS at: " + wms_url)
    return template('mapclient', wms_url=wms_url, protected = wms.wms_md["protected"], wag_url = configuration.getWAGURL() )

# Pure mapscript ViewService. Use this for INSPIRE VS & WMS 1.3.0 or plain WMS 1.1.1 depending on VERSION parameter. Doesn't need a mapfile in the request.
@route ('/VS/:uuid')
def createVS( uuid ):
    wms = wmsfactory.WMSFactory()
    params = request.GET
    [ctype, cbody] = viewservice.mapserver( params, os.path.join(configuration.getMapfileDir(), uuid+'.map' ) )
    response.content_type = ctype
    return cbody

######################
### AJAX Callbacks ###
######################

### Load Metadata ###
@route('/loadMetadata/:uuid')
def getMetadata( uuid ):
    helper.dbg('Got AJAX LOAD metadata request for: ' + uuid)
    wms = wmsfactory.WMSFactory()
    wms.loadFromFile(uuid)
    # build response tree:
    metadata = { "wmsdata": wms.wms_md , "layers" : wms.layers }
    helper.dbg("metadata: ")
    helper.pp(metadata)
    return metadata

### Save Metadata ###
@route('/saveMetadata/:uuid', method='POST')
def saveMetadata( uuid ):
    helper.dbg('Got AJAX SAVE metadata request for: ' + uuid)
    wms = wmsfactory.WMSFactory()
    wms.loadFromFile(uuid)
    metadata = request.forms.get('metadata')
    wms.updateconf( metadata )
    wms.saveconf()
    helper.dbg("parsed new metadata: ")
    helper.pp(metadata)
    ## now create mapfile:
    wms_url = wms.generate_wms_url()  # pure mapserver CGI
    wms.savemap( wms_url )
    helper.dbg( "wms URL is: " + wms_url)    
    return [ wms_url,]
