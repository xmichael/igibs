/* editable properties grid for Metadata */// Read/Write-able properties for each cell?
// single grid (rows=layers, headers=properties ) or many cells = layes with 2x2 arrays property value (no headers)

/** Global metadata hash/object to enable fast in-memory processing instead of relying on stupid Ext CRUD Object model  */
var metadata = { "layers": [ { id: 1, name: "myName" , projection: "epsg:4326" } ] };

/** editable properties for metadata.layers */
var editable = [ "name", "projection", "opacity", "fillColour", "width", "outlineColour" ]

/** update object by copying only overlapping fields in records leaving the other ones untouched */
function updateObject(src, dst){
    for ( k in src ){
        if ( k in dst){dst[k] = src[k]};
    }
}

/** save global metadata */
function save_wms(uuid,redirect) {
    var metadata_js = Ext.util.JSON.encode(metadata);
    Ext.Ajax.request({
        url: "/wsgi/saveMetadata/" + uuid,
        success: function(e) {
            var wmsurl = e.responseText;
            var mapclient ;
            if ( metadata.wmsdata.protected == true ){
                mapclient = 'https://' + redirect + '/wsgi/mapclient/' + uuid;
            }
            else /* not using shibboleth ergo use existing host */
            {
                mapclient = 'http://' + window.location.host + '/wsgi/mapclient/' + uuid;
            }
            Ext.Msg.show({
                title:'View Service URL',
                width:'800',
                msg: "<pre>The Url of the generated service is:\n\n" + 
                    wmsurl + 
                    "\n\nPlease press <b>OK</b> to view the use the IGIBS mapping client or " +  
                    "<b>CANCEL</b>\nin case you just want to access the service from a desktop GIS client.</pre>",
                buttons: Ext.Msg.OKCANCEL,
                fn: function (btnId, text, opt){ 
                        if (btnId == 'ok') 
                        { 
                             window.location.href= mapclient; 
                        } 
                },
                animEl: 'createWMS',
                icon: Ext.MessageBox.INFO
            });
        },
        failure: function(e) {
            Ext.MessageBox.alert("Failure", "Unable to update the metadata on the server!");
        },
        params: {
            uuid: uuid,
            metadata: metadata_js
        }
    });
}

Ext.onReady(function() {
    /* remove loading indicator */
    setTimeout(function(){
            Ext.get('loading').remove();
            Ext.get('loading-mask').fadeOut({remove:true});
        }, 250);

    Ext.QuickTips.init();
    var wms_id = document.getElementById("wms_id").innerHTML;
    
    /* metadata Store */
    
    var metadataStore = new Ext.data.JsonStore( {
        storeId: "metadataStore",
        fields: [ "id", "name", "type", { name: "projection", type: "string" }, "extent",  "opacity", "fillColour", "properties" ],
        idProperty: 'id',
        root: 'layers',
        listeners: {
            update: function(store, record, operation){
                /* conmmiting to store */
                for ( k in record.modified ) {
                    metadata.layers[record.id][k] = record.data[k];
                }
            }
        }
    });
        
    var wmsGrid = new Ext.grid.PropertyGrid( {
        title: "<b>WMS Metadata (Double-click to edit)</b>",
        //columnWidth: 1 / 3,
        height: 100,
        clicksToEdit: 2,
        autoHeight: true,
        renderTo: "wmsProps",
        stripeRows: true,
        propertyNames: {
            "title" : "Title",
            "name": "Name",
            "projection": "Target Projection",
            "protected" : "Shibboleth Protected"
        },
        source: { name : "WMSName" },
        viewConfig: {
                forceFit: true
        }
    });
  
    
    ////////////////////////////////////////////////////////////////

    /** get symbol store object per layer id */
    function getSymbolById (id){
        l = metadata.layers[id];
        s = {};
        //if it doesn't exist it won't show up (e.g. rasters only have opacity)
        for (idx in editable) {
            s[editable[idx]] = l[editable[idx]]
        }
        return s;
    }
    
    function saveSymbolById (id, symbol){
        updateObject ( symbol, metadata.layers[id] );
    }
   
    
    /* Create a new popup instance of a properties Grid. Call .show() to display */
    function styleGridFactory(id) {
        var dataSource = getSymbolById(id);
        var pg = new Ext.grid.PropertyGrid( {
            title: "<b>Layer " + id + "</b>",
            height: 100,
            clicksToEdit: 1,
            autoHeight: true,
            stripeRows: true,
            propertyNames: {
                "name" : "Layer Name",
                "projection" : "Projection",
                "fillColour" : "Fill Colour",
                "outlineColour": "Outline Colour",
                "opacity": "Opacity %"                
            },
            source: dataSource,
            viewConfig: {
                forceFit: true
            },
            customEditors: {
                'projection' : new Ext.grid.GridEditor( new Ext.form.ComboBox({
                                                typeAhead: true,
                                                triggerAction: 'all',
                                                lazyRender:true,
                                                mode: 'local',
                                                store: new Ext.data.ArrayStore({
                                                id: 0,
                                                fields: ['key','value'],
                                                    data: [ ['epsg:27700', 'epsg:27700'], ['epsg:4326', 'epsg:4326'],['epsg:900112', 'epsg:900112'] ]
                                                }),
                                                valueField: 'key',
                                                displayField: 'value'
                                            }) ),
                'date' : new Ext.grid.GridEditor(new Ext.form.DateField({selectOnFocus:true})),
                'fillColour' : new Ext.grid.GridEditor(new Ext.ux.ColorField({ 
                                fallback: true , 
                                listeners: {
                                    select: function(field, colour){
                                        dataSource["fillColour"] = colour;
                                        pg.setSource(dataSource); 
                                    }
                                }
                            })),
                'outlineColour' : new Ext.grid.GridEditor(new Ext.ux.ColorField({ 
                                fallback: true , 
                                listeners: {
                                    select: function(field, colour){
                                        dataSource["outlineColour"] = colour;
                                        pg.setSource(dataSource); 
                                    }
                                }
                            })),
                'opacity' : new Ext.grid.GridEditor( new Ext.form.NumberField({
                                allowBlank: false,
                                allowDecimals: false,
                                allowNegative: false,
                                minValue: 0,
                                maxValue: 100
                             }))
            },
            customRenderers: {
                'fillColour' : function (value, md, record, rowIndex, colIndex,store)
                {  
                    md.style +="background-color: " + value + ";"
                    return value;
                },
                'outlineColour' : function (value, md, record, rowIndex, colIndex,store)
                {  
                    md.style +="background-color: " + value + ";"
                    return value;
                }

            },
            viewConfig: {
                forceFit: true
            }
        });
        return pg;
    }

    function popupFactory(id, stylegrid) {
        var winid = "style-" + id
        var popwin = new Ext.Window({
                        id: winid,
                        title: '<b>Editable properties</b>',
                        pageX: 400 + id*20,
                        pageY: 200 + id*20,
                        width: 500,
                        height: 300,
                        plain: true,
                        items: [ stylegrid ],
                        buttons: [{
                            id: 'btn-' + id,
                            text: 'Close',
                            handler: function() {
                                        /* save styles */
                                        saveSymbolById( id, stylegrid.getSource() );
                                        stylegrid.destroy();
                                        popwin.destroy();
                                    }
                                 }]
            });
        return popwin;
    }

    /////////////////////////////////////////////////////////////////
    
    
    
    var layerGrid = new Ext.grid.EditorGridPanel( {
        title: "<b>Layer Metadata (Double-click to access Symbology)</b>",
        renderTo: "layerProps",
        height: 200,
        autoHeight: true,
        //width: 800,
        stripeRows: true,
        clicksToEdit: 1,
        store: Ext.StoreMgr.lookup("metadataStore"),
        columns: [{
                    header: "Layer Name",
                    dataIndex: "name"
                }, {
                    header: "Type",
                    dataIndex: "type",
                    renderer: function (v, md, record, rowIndex, colIndex,store){                         
                          return v + " - "  + metadata.layers[record.id]["geometry_type"];
                        }
                }, {
                    header: "Projection",
                    dataIndex: "projection"
                }, {
                    header: "Extent",
                    dataIndex: "extent"
                }, {
                    header: "Properties",
                    dataIndex: "properties",
                    renderer: function (v, md, record, rowIndex, colIndex,store){                         
                         return v.slice(1,-1);
                    }
                }] ,
        viewConfig: {
                forceFit: true
        },
        sm: new Ext.grid.RowSelectionModel({singleSelect:true}),
        listeners: {
            celldblclick: function(grid, rowIndex, columnIndex, e) {
                        var record = grid.getStore().getAt(rowIndex);  // Get the Record
                        var fieldName = grid.getColumnModel().getDataIndex(columnIndex); // Get field name
                        var data = record.get(fieldName);
                        var popup = popupFactory( record.id,  styleGridFactory(record.id) );
                        popup.show();

                     }
                 }
    });
  
    /** Load global var metadata */
    Ext.Ajax.request({
        url: "/wsgi/loadMetadata/" + wms_id,
        success: function(e) {
            res = e.responseText;
            jres = Ext.util.JSON.decode(res);
            metadata = jres;
            wmsGrid.setSource(metadata.wmsdata);
            metadataStore.loadData(metadata);            
        },
        failure: function(e) {
            Ext.MessageBox.alert("Failure", "Unable to retrieve metadata from server!");
        }
    });
    
    Ext.fly("logo").setVisible(true);
    Ext.fly("createWMS").setVisible(true);
});