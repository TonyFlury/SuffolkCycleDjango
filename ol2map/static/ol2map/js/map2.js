var map;

function init() {
    var bounds = new OpenLayers.Bounds();
    bounds.extend( new OpenLayers.LonLat(0.2, 52.55).transform('EPSG:4326', 'EPSG:3857'));
    bounds.extend( new OpenLayers.LonLat(1.95, 51.5).transform('EPSG:4326', 'EPSG:3857'));

    map = new OpenLayers.Map('map', {
        zoomDuration: 10,
        animationEnabled: true,
        projection: new OpenLayers.Projection("EPSG:3857"),
        displayProjection: new OpenLayers.Projection("EPSG:4326"),
        layers: [
            new OpenLayers.Layer.Google(
                "Google Streets", // the default
                {
                  sphericalMercator:true,
                  numZoomLevels: 20, minZoomLevel: 1, maxZoomLevel: 16 }
            ),
        ],
        controls: [ /* new OpenLayers.Control.Graticule(), */
                    new OpenLayers.Control.Navigation(),
                    new OpenLayers.Control.PanZoomBar(),
        ],
       center: new OpenLayers.LonLat( 1.0, 52.1)
            // Google.v3 uses web mercator as projection, so we have to
            // transform our coordinates
            .transform('EPSG:4326', 'EPSG:3857'),
//        restrictedExtent: bounds,
        zoom: 9
    });

    var layer = new OpenLayers.Layer.Vector("vector", {
           animationEnabled: true,
           projection: map.displayProjection,
           strategies: [new OpenLayers.Strategy.Fixed()],
           opacity: 0.5,
           protocol: new OpenLayers.Protocol.HTTP({
                url: "/static/OL3Example/kml/day1.kml",
                format: new OpenLayers.Format.KML({
                    extractStyles: true,
                    extractAttributes: true,
                })
            })
        }) ;
    map.addLayer(layer);

   map.addControl(new OpenLayers.Control.LayerSwitcher());

}