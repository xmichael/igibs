<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html 
	  PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
	  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
  <head>
    <title>IGIBS Demonstrator</title>
    <!-- STYLSHEETS -->
    <link rel="stylesheet" href="/igibs/styles/igibs.css" type="text/css" />
    <link rel="stylesheet" href="/igibs/styles/loading.css" type="text/css" />
    <link rel="stylesheet" href="http://extjs.cachefly.net/ext-3.4.0/resources/css/ext-all.css" type="text/css">
    <style type="text/css">
            .x-panel-mc {
                font-size: 12px;
                line-height: 18px;
            }
            .hidden { 
                display: none; 
            }
            #props{
                position: relative;
            }
            #wmsProps {
            }
            #layerProps {
                margin-top: 25px;
            }
            #createWMS {
                margin-top: 25px;
            }
    </style>
  </head>
  <body>
  <div id="loading-mask"></div>
  <div id="loading">
    <div class="loading-indicator">
        Loading...
        </div>
    </div>
    <div id="logo" class="hidden">  
      <img src="/igibs/images/IGIBS-finallogo-outlines717x240.jpg" alt="EDINA" />
    </div>
    <div id="content">
        <div id="props">
            <div id="wmsProps"></div>
            <div id="layerProps"></div>
        </div>
        <div id="createWMS" class="hidden">
           <input type="button" value="Create WMS Server" onClick="save_wms('{{uuid}}','{{redirect}}');"></input>
        </div>
        <div id="wms_id" class="hidden">{{uuid}}</div>
    </div>
    <!-- SCRIPTS -->
    <script src="http://extjs.cachefly.net/ext-3.4.0/adapter/ext/ext-base.js" type="text/javascript"></script>
    <script src="http://extjs.cachefly.net/ext-3.4.0/ext-all.js" type="text/javascript"></script> 
    <script src="/lib/ext-ux/ColorField/Ext.ux.ColorField.js" type="text/javascript"></script> 
    <script src="/igibs/scripts/metadata.js" type="text/javascript"></script>
  </body>
</html>
