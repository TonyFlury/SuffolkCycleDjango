
$(document).ready(function(){

    var map, select;

    $.each( $('div.ol2mapElement'), function(){

        var id = $(this).attr('id');
        var url = $(this).attr('data-ol2map-instance');
        var extent = JSON.parse($(this).attr('data-ol2map-extent'));
        var center = JSON.parse($(this).attr('data-ol2map-center'));
        var kmlLayers = JSON.parse($(this).attr('data-ol2map-kmlLayers'));
        var zoom = JSON.parse($(this).attr('data-ol2map-zoom'));
        var switcher = JSON.parse($(this).attr('data-ol2map-switcher'));

        if (extent != null)
        {
            var bounds = new OpenLayers.Bounds();
            bounds.extend( new OpenLayers.LonLat(extent[0][0], extent[0][1]).transform('EPSG:4326', 'EPSG:3857'));
            bounds.extend( new OpenLayers.LonLat(extent[1][0], extent[1][1]).transform('EPSG:4326', 'EPSG:3857'));
        }
        else
            var bounds = null;

        if (center != null)
            var center_pos = new OpenLayers.LonLat( center[0], center[1]).transform('EPSG:4326', 'EPSG:3857');
        else
            var center_pos = null;


        map = new OpenLayers.Map(id, {
            zoomDuration: 10,
            animationEnabled: true,
            projection: new OpenLayers.Projection("EPSG:3857"),
            displayProjection: new OpenLayers.Projection("EPSG:4326"),
            layers: [
                new OpenLayers.Layer.Google(
                    "Google Streets", // the default
                    {
                      sphericalMercator:true,
                      numZoomLevels: 20, minZoomLevel: 1, maxZoomLevel: 16,
                      displayInLayerSwitcher: false }
                ),
            ],

            controls: [ new OpenLayers.Control.Navigation(),
                        new OpenLayers.Control.PanZoomBar() ],

            zoom: (zoom != null)?zoom:9
        });

        if (bounds)
            map.restrictedExtent = bounds

        if (center_pos)
            map.setCenter(center_pos, (zoom != null)?zoom:9);

        if (kmlLayers != null)
        {
            var layers = [];

            for (var i=0,  tot=kmlLayers.length; i < tot; i++) {
                var layer = new OpenLayers.Layer.Vector(kmlLayers[i][0], {
                   animationEnabled: true,
                   projection: map.displayProjection,
                   strategies: [new OpenLayers.Strategy.Fixed()],
                   opacity: kmlLayers[i][2],
                   protocol: new OpenLayers.Protocol.HTTP({
                        url: kmlLayers[i][1],
                        format: new OpenLayers.Format.KML({
                            extractStyles: true,
                            extractAttributes: true,
                        })
                    })
                }) ;
                map.addLayer(layer);
                layers[i] = layer;

                layer.events.on({
                        "featureselected": onFeatureSelect,
                        "featureunselected": onFeatureUnselect
                });
            }
            if (switcher)
                map.addControl(new OpenLayers.Control.LayerSwitcher());

            select = new OpenLayers.Control.SelectFeature(layers);
            map.addControl(select);
            select.activate();

        }
    })

    function onPopupClose(evt) {
//        var layer = evt.feature.layer;
//        var map = layer.map;
//        var select = null;
//        for (var i=0,  tot=map.controls.length; i < tot; i++) {
//            if (map.controls[i] instanceof OpenLayers.Control.SelectFeature)
//                select = map.controls[i]
//        }
//        if (select)
            select.unselectAll();
    }

    function onFeatureSelect(event) {
        var feature = event.feature;
        var selectedFeature = feature;
        var layer = feature.layer;
        var map = layer.map;
        var popup = new OpenLayers.Popup.FramedCloud("chicken",
            feature.geometry.getBounds().getCenterLonLat(),
            new OpenLayers.Size(100,100),
            "<h2>"+feature.attributes.name + "</h2>" + feature.attributes.description,
            null, true, onPopupClose
        );
        feature.popup = popup;
        map.addPopup(popup);
    }
    function onFeatureUnselect(event) {
        var feature = event.feature;
        var map = feature.layer.map;
        if(feature.popup) {
            map.removePopup(feature.popup);
            feature.popup.destroy();
            delete feature.popup;
        }
    }

});