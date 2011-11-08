/* Utility functions: */

// reimplements $.extend(obj1 obj2...)
Object.extend = function(destination, source) {
    for (var property in source) {
        if (source.hasOwnProperty(property)) {
            destination[property] = source[property];
        }
    }
    return destination;
};
    
    ////////// OL Declarations /////////////
    var lon = -1.40000; 
    var lat = 54.00000;
    var zoom = 7;
    var extent = new OpenLayers.Bounds(-9.49714,49.7668,3.63202,61.581);
    // 0 0 70k 130k : new OpenLayers.Bounds(-7.55645, 49.76688, 5.49638, 61.375625);

    var base;

    var map_options = {
          controls: [ 
                        new OpenLayers.Control.PanZoomBar(),
                        //new OpenLayers.Control.ScaleLine(),
                        //new OpenLayers.Control.Scale(),
                        new OpenLayers.Control.Navigation(),
                        //new OpenLayers.Control.KeyboardDefaults(),
                        //new OpenLayers.Control.LayerSwitcher(), 
                        //new OpenLayers.Control.maximizeControl()
                        new OpenLayers.Control.MousePosition(),
                        new OpenLayers.Control.OverviewMap(),
                        new OpenLayers.Control.Permalink(),
                        new OpenLayers.Control.Attribution()
                    ],
          format: "image/jpeg",
          maxResolution: "auto",
          maxExtent: extent,
          units: "degrees"
    };

   /************************* BASE LAYERS **********************************/

        /** Demis World Map */
/*
    base = new OpenLayers.Layer.WMS( "Demis World Map", "http://www2.demis.nl/wms/wms.asp?wms=WorldMap&",
                                      {layers: "Bathymetry,Countries,Topography", format: "image/jpeg", transparent: false}, 
                                      {singleTile: true,  visibility: true }
                                      ); */

    /** OS Free:  OSOpenData {Streetview,VMD_Raster,Raster_250k,Miniscale_100,GB}  */

    var blank = new OpenLayers.Layer("Blank Basemap", {isBaseLayer: true,
                    'displayInLayerSwitcher': true }, {visibility: false});
    
    /** OS Free:  OSOpenData {Streetview,VMD_Raster,Raster_250k,Miniscale_100,GB}  THROUGH GWC WMS emulation */
    var osattr = "Contains Ordnance Survey data. (c) Crown copyright and database right 20XX. Data provided by Digimap OpenStream, an EDINA, University of Edinburgh Service."
    var base = new OpenLayers.Layer.WMS( "OS Free", "http://dlib-mumra.ucs.ed.ac.uk/geowebcache/service/wms?",
                                      {layers: "OSOpenData", format: "image/jpeg", isBaseLayer: true, cache: false}, 
                                      {visibility: true, attribution: osattr}
                                      );

   /************************ OVERLAYS *********************************/
/////////////////////////////
/** Statically defined Wales datasets 
 * GetCapabilities: https://ec2-46-137-92-186.eu-west-1.compute.amazonaws.com/geoserver/ows?service=wms&version=1.1.1&request=GetCapabilities
 * Sample GetMap:
 * 
 * https://ec2-46-137-92-186.eu-west-1.compute.amazonaws.com/geoserver/wms?service=WMS&version=1.1.0&request=GetMap&layers=wagdata:tan15&styles=&
 * bbox=171236.08,162687.001,381403.421,395433.218&width=462&height=512&srs=EPSG:900913&format=image/png
 */


imagetrick = function ( requestUrl , successCb ) {
   cb = successCb || function () { return; };
   image = new Image();
   image.onerror = successCb;
   image.src = requestUrl;
}

/* Main */
Ext.onReady(function() {
    /* remove loading indicator */
    setTimeout(function(){
            Ext.get('loading').remove();
            Ext.get('loading-mask').fadeOut({remove:true});
        }, 250);

    Ext.QuickTips.init();
    
    var map = new OpenLayers.Map( 'map', map_options ); //implied "EPSG:4326"

        
    /** Parse some global variables passed synchronously from HTML (AJAX is error-prone) */
    /* do we want shibb protection + wag datasets? */
    var protected = document.getElementById('protected').innerHTML == "True" ? true : false;
    /* url of secure wag datasets */
    var wag_url = document.getElementById('wag_url').innerHTML;
    // var wag_getcap_url = wag_url + '?service=wms&version=1.1.1&request=GetCapabilities';
    /* url of our just generated wms */
    var wms_url = document.getElementById('wms_url').innerHTML;

    
    
    if ( protected ) {
        /**sample wag url for testing */
        var waglayer_names = [ "wagdata:LA Region", "wagdata:PA Region", "wagdata:Wales Region", "wagdata:assemblyoffices_pnt", "wagdata:firestations_pnt",
        "wagdata:hospitals_pnt", "wagdata:lifeboatstations_pnt", "wagdata:policepremises_pnt", "wagdata:schools_pnt" ];
        
        //     var wag_tan15 = new OpenLayers.Layer.WMS ( "WAG Tan 15" ,  wag_url,  {layers: 'wagdata:tan15' , transparent: 'true', format: 'image/png'},
        //                                        {singleTile: false, visibility: false, transparent: true});
        
        var waglayers = []
        for ( i = 0; i < waglayer_names.length; i++ ) {
            ln = waglayer_names[i];
            layer = new OpenLayers.Layer.WMS ( ln ,  wag_url,  {layers: ln , transparent: 'true', format: 'image/png'},
                                            {singleTile: false, visibility: false, transparent: true});
            waglayers.push(layer);
            map.addLayer(layer);
        }    
                // create WAG store
        var wagstore = new GeoExt.data.WMSCapabilitiesStore({
                url: wag_url + '?service=wms&version=1.1.1&request=GetCapabilities'
        });

     }
        
    // create a new WMS capabilities store
    var store = new GeoExt.data.WMSCapabilitiesStore({
        url: wms_url + '?REQUEST=GetCapabilities&VERSION=1.1.1&SERVICE=WMS'
    });
        
    // load the store with records derived from the doc at the above url
    if (protected){
        imagetrick( wag_url , function () { wagstore.load() } );    
        imagetrick( wms_url , function () { store.load() } );
    }
    else {
        store.load();
    }

    // create a grid to display records from the store
    var wmscaps = new Ext.grid.GridPanel({
        id: 'wmscaps',
        title: "<b>WMS Capabilities</b>",
        store: store,
        autoHeight: true,
        autoWidth: true,
        collapsible: true,
        animCollapse: true,
        stripeRows: true,
        collapsed: true,
        columns: [
            {header: "Title", dataIndex: "title", sortable: true},
            {header: "Name", dataIndex: "name", sortable: true},
            {header: "Queryable", dataIndex: "queryable", sortable: true, width: 70},
            {header: "BBOX Lon/Lat", dataIndex: "llbbox", sortable: false, width: 70},
            {id: "description", header: "Description", dataIndex: "abstract"}
        ],
        listeners: {
              cellclick: function(grid, rowIndex, columnIndex, e){ 
                  var record = grid.getStore().getAt(rowIndex);
                  var ext = record.get('llbbox');
                  var layer = record.getLayer().clone();
                  map.addLayer(layer);
                  bbox = new OpenLayers.Bounds(ext[0], ext[1], ext[2], ext[3]);
                  map.zoomToExtent(bbox);
              }
        }
    });
    
    // Main mapPanel
    var mapPanel = new GeoExt.MapPanel({
        id: "mapPanel",
        border: true,
        region: "center",
        map: map,
        contentEl:              "map",
        extent:                 extent,
        split:                  true,
        layers: [ base, blank ]
    });
 
    // layerControl@controlPanel
    var layerControl = new Ext.tree.TreePanel({
        title: "<b>Layers</b>",
        plugins: [{
            ptype: "gx_treenodecomponent"
        }],
        loader: {
            applyLoader: false
        },
        root: {
            nodeType: "gx_layercontainer",
            loader: {
                createNode: function(attr) {
                    attr.component = {
                        xtype: "gx_wmslegend",
                        layerRecord: mapPanel.layers.getByLayer(attr.layer),
                                                showTitle: false,
                                                cls: "legend"
                    }
                    return GeoExt.tree.LayerLoader.prototype.createNode.call(this, attr);
                }
            }
        },
        rootVisible: false,
        lines: false,
        collapsed: false
    });

    // controlPanel@Viewport
    var controlPanel = new Ext.Panel({
        region:'west',
        margins:'5 0 5 5',
        split:true,
        width: 510,
        collapsible: true,
        layout:'accordion',
        layoutConfig:{
            animate:true
        },
        items: [wmscaps, layerControl]
    });

    
    // Viewport    
    var viewport = new Ext.Viewport({
        id:     'viewport',
        layout: 'border',
        border: false,
        items:  [controlPanel, mapPanel]
    });

    map.zoomToMaxExtent()
});
