MAP
  NAME "{{wmsname}}"

  WEB
    METADATA
      "wms_title" "{{wms.wms_md["title"]}}"
      "wms_srs" "{{wms.wms_md["projection"]}} EPSG:27700"
      "wms_onlineresource" "{{wmsurl}}"
    END    
  END

  # This is *OUTPUT* Projection.
  
  #Britain: 
  #EXTENT  -7.55645 49.76688 3.6342 61.465701
  #resolutions: 1000,200,100,50,25,12.5,5,2.5,1
  #World
  #EXTENT  -90 0 90 180
  EXTENT {{extent[0]}} {{extent[1]}} {{extent[2]}} {{extent[3]}}
  UNITS {{units}}
  PROJECTION
      "init={{wms.wms_md["projection"]}}"
  END

  SYMBOL
      NAME "circle"
      TYPE ellipse
      FILLED true
      POINTS
      10 10
      END # POINTS
  END # SYMBOL

%for l in wms.layers:
%if l["type"] == "Raster":
  LAYER
    METADATA
      "wms_title" "{{l['name']}}"
      "wms_srs" "{{wms.wms_md["projection"]}} EPSG:27700 EPSG:900913"
    END
    PROJECTION
       "init={{l["projection"]}}"
    END
    NAME "{{l['name']}}"
    DATA "{{l['filepath']}}"
    TYPE RASTER
    STATUS ON
    #GROUP "ALL"
  END
%end
%if l["type"] == "Vector":
  LAYER
    NAME "{{l['name']}}"
    TYPE {{l['geometry_type']}}
    METADATA
      "wms_title" "{{l['name']}}"
      "wms_srs" "{{wms.wms_md["projection"]}} EPSG:27700 EPSG:900913"
      #"wms_group_title" "ALL"
    END    
    PROJECTION
       "init={{l["projection"]}}"
    END
    DATA "{{l['filepath']}}"
    STATUS ON
    #GROUP "ALL"
    CLASS
        NAME "{{l['name']}}"
%if l["geometry_type"] == "Polygon" or l["geometry_type"] == "Line":
        STYLE
            OUTLINECOLOR {{int(l['outlineColour'][1:3],16)}} {{int(l['outlineColour'][3:5],16)}} {{int(l['outlineColour'][5:7],16)}}
            WIDTH {{l['width']}}
            ANTIALIAS TRUE
        END
        STYLE
            OPACITY {{l['opacity']}}
            COLOR {{int(l['fillColour'][1:3],16)}} {{int(l['fillColour'][3:5],16)}} {{int(l['fillColour'][5:7],16)}}
        END
%end
%if l["geometry_type"] == "Point":
        STYLE
            SYMBOL 'circle'
            OPACITY {{l['opacity']}}
            COLOR {{int(l['fillColour'][1:3],16)}} {{int(l['fillColour'][3:5],16)}} {{int(l['fillColour'][5:7],16)}}
            SIZE {{l['width']}}
            WIDTH {{l['width']}}
        END
%end
    END
  END
%end
%end

    # Set output formats. Mapserver doesn't even transmit alpha by defautl
    OUTPUTFORMAT
        NAME "aggpng"
        DRIVER AGG/PNG
        MIMETYPE "image/png"
        IMAGEMODE RGBA
        EXTENSION "png"
    END
END
