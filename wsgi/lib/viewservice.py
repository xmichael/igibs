#!/usr/local/edina/bin/python2.6
# -*- coding: utf-8 -*-
#################################################################################
# WMS wrapper using mapscript to enforce INSPIRE View Services compliance       #
#                                                                               #
# 2010, Michael Koutroumpas   -- under the public domain                        #
#                                                                               #
# Many thanks to Bart van den Eijnden for posting the initial code              #
# to support the LANGUAGE extension: http://pastebin.com/f4cb916ce              #
#################################################################################

import mapscript
from xml.dom.minidom import parseString

import helper

#IDEAS: could use internal caching to save time reparsing mapfile BUT will have to restart app every time a mapfile is handedited

####### Global Vars ########
language = "ENG"
# I got these URLs from the INSPIRE VS TG. Not sure if they are permanent.
namespace = 'http://inspire.europa.eu/networkservice/view/1.0'
prefix = 'inspire_vs'
schemaLocation = 'http://gditestbed.agiv.be/XSD/networkservice/view/1.0/INSPIRE_ExtendedCapabilities_WMS_130.xsd'
default_style = "INSPIRE:DEFAULT"
gmd_ns = 'http://www.isotc211.org/2005/gmd'
gmd_pre = 'gmd'
gco_ns = 'http://www.isotc211.org/2005/gco'
gco_pre = 'gco'

def altercapabilities(content, namespace, prefix, schemaLocation,  language):
    """ Patches the nominal GetCapabilities to add the INSPIRE VS extras"""
    dom = parseString(content)
    
    ###SCHEMAS##
    root = dom.getElementsByTagName('WMS_Capabilities')[0];
    schema = root.getAttributeNS("http://www.w3.org/2001/XMLSchema-instance", "schemaLocation")
    ## add inspire schema extension to xsi:schemaLocation
    schema += " " + namespace + " " + schemaLocation
    root.setAttribute("xsi:schemaLocation", schema)
    ###ATTRIBUTES###
    root_layer = dom.getElementsByTagName("Layer")[0]
    ## create wms:WMS_Capabilities/wms:Capability/inspire_vs:ExtendedCapabilities
    view_caps = dom.createElementNS(namespace, prefix+":ExtendedCapabilities")
    # add inspire_vs, gmd etc.
    view_caps.setAttributeNS(namespace, "xmlns:"+prefix, namespace)
    view_caps.setAttributeNS(gmd_ns, "xmlns:"+gmd_pre, gmd_ns)
    view_caps.setAttributeNS(gco_ns, "xmlns:"+gco_pre, gco_ns)
    ## create ResourceType
    rt = dom.createElementNS(namespace, prefix+":ResourceType")
    scoped_code = dom.createElementNS(gmd_ns, gmd_pre + ":MD_ScopeCode")
    scoped_code.appendChild(dom.createTextNode("service"))
    scoped_code.setAttribute("codeList","http://standards.iso.org/ittf/PubliclyAvailableStandards/ISO_19139_Schemas/resources/Codelist/gmxCodelists.xml#MD_ScopeCode")
    scoped_code.setAttribute("codeListValue","dataset")
    rt.appendChild(scoped_code)
    view_caps.appendChild(rt)
    ## create TemporalReference
    # unimplemented for conformance testing
    ## create Conformity
    # unimplemented for conformance testing
    ## create MetadataPointOfContact
    md_poc = dom.createElementNS(namespace, prefix+":MetadataPointOfContact")
    role = dom.createElementNS(gmd_ns, gmd_pre + ":role")
    rolecode = dom.createElementNS(gmd_ns, gmd_pre + ":CI_RoleCode")
    rolecode.appendChild(dom.createTextNode("PointOfContact"))
    rolecode.setAttribute("codeList","http://standards.iso.org/ittf/PubliclyAvailableStandards/ISO_19139_Schemas/resources/Codelist/gmxCodelists.xml#MD_RoleCode")
    rolecode.setAttribute("codeListValue","pointOfContact")
    role.appendChild(rolecode)
    md_poc.appendChild(role)
    view_caps.appendChild(md_poc)
    ## create MetadataDate
    date = dom.createElementNS(namespace, prefix+":MetadataDate")
    date.appendChild(dom.createTextNode("20060520"))
    view_caps.appendChild(date)
    ## create SpatialDataServiceType
    ds_type = dom.createElementNS(namespace, prefix+":SpatialDataServiceType")
    lname = dom.createElementNS(gco_ns, gco_pre + ":LocalName")
    lname.appendChild(dom.createTextNode("view"))
    ds_type.appendChild(lname)
    view_caps.appendChild(ds_type)
    ## create Languages/Language
    langs = dom.createElementNS(namespace, prefix+":Languages")
    # We only support one language for now
    lang = dom.createElementNS(namespace, prefix+":Language")
    lang.appendChild(dom.createTextNode(language))
    lang.setAttribute("default", "true")
    langs.appendChild(lang)
    view_caps.appendChild(langs)
    ## create currentLanguage
    cur_lang = dom.createElementNS(namespace, prefix+":CurrentLanguage")
    cur_lang.appendChild(dom.createTextNode(language))
    view_caps.appendChild(cur_lang)
    root_layer.parentNode.insertBefore(view_caps, root_layer);
    
    return dom.toxml()

########## MAIN function  ############
def mapserver(params,mapfile):
    """ Function implementing mapserver functionality.
    
    params: dictionary of query string of a mapserver GET request
    mapfile: path to mapfile
    
    returns: tuple with content type and response body
    """
    helper.dbg("creating map for: " + mapfile)
    request = mapscript.OWSRequest()
    #request.loadParams()
    for k in params:
        #helper.dbg( "%s : %s" % (k,params[k]))
        request.setParameter(k,params[k])
    # change the style INSPIRE:DEFAULT back to an empty string otherwise Mapserver will complain
    styles = request.getValueByName('STYLES')
    if (styles is not None and styles.count(default_style) > 0):
        styles = styles.replace(default_style, "")
        request.setParameter("STYLES", styles)
    style = request.getValueByName('STYLE')
    if style == default_style:
        request.setParameter("STYLE", "") 
            
    map = mapscript.mapObj( mapfile )
    mapscript.msIO_installStdoutToBuffer()
    map.OWSDispatch( request )
    content_type = mapscript.msIO_stripStdoutBufferContentType()
    content = mapscript.msIO_getStdoutBufferBytes()
    operation = request.getValueByName('REQUEST')
    version = request.getValueByName('VERSION')
    if (version == '1.3.0' or version is None) and operation.upper() == 'GETCAPABILITIES':
        content = altercapabilities(content, namespace, prefix, schemaLocation, language)
    #response = 'Content-type: %s\n%s' % (content_type,content)    
    return [content_type, content]
