<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
  <head>
    <title>IGIBS Demonstrator</title>
    <!-- STYLSHEETS -->
    <link rel="stylesheet" href="/igibs/styles/igibs.css" type="text/css" />
    <!-- SCRIPTS -->
    <link rel="stylesheet" href="http://extjs.cachefly.net/ext-3.4.0/resources/css/ext-all.css" type="text/css">
    <link rel="stylesheet" type="text/css" href="http://api.geoext.org/1.0/resources/css/geoext-all-debug.css"></link>
    <link rel="stylesheet" href="/igibs/styles/loading.css" type="text/css" />
    <style type="text/css">
            .x-panel-mc {
                font-size: 12px;
                line-height: 18px;
            }
            .hidden { 
                display: none; 
            }
            #logo img {
                margin-bottom: 0;
                margin-left: 35%;
                margin-top: 0;
                padding: 0;
                position: relative;
                width: 20%;
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
        <div id="wmsResult" class="hidden">
            <div id="wms_url">{{wms_url}}</div>
            <div id="protected">{{protected}}</div>
            <div id="wag_url">{{wag_url}}</div>
        </div>
         <div id="map"></div> 
    <script src="http://extjs.cachefly.net/ext-3.4.0/adapter/ext/ext-base.js" type="text/javascript"></script>
    <script src="http://extjs.cachefly.net/ext-3.4.0/ext-all.js" type="text/javascript"></script> 
    <script src="/lib/overrides/ext-base-ajax.js" type="text/javascript"></script> 
    <script src="http://www.openlayers.org/api/2.10/OpenLayers.js"" type="text/javascript"></script>
    <script src="http://api.geoext.org/1.0/script/GeoExt.js" type="text/javascript"></script>
    <script src="/igibs/scripts/mapclient.js" type="text/javascript"></script>
  </body>
</html>
