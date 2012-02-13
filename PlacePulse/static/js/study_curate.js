function editsv(id, lat, lng, heading, pitch) {
    $('#edit_street_view').modal();
    var location = new google.maps.LatLng(lat,lng);
    var mapOptions = {
      center: location,
      zoom: 14,
      mapTypeId: google.maps.MapTypeId.HYBRID
    };
    var map = new google.maps.Map(document.getElementById("map4"), mapOptions);
    var panoramaOptions = {
      position: location,
      pov: {
        heading: heading,
        pitch: pitch,
        zoom: 1
      },
      	addressControl: false,
  		linksControl: false,
  		disableDoubleClickZoom: true,
  		zoomControl: false,
  		navigationControl: false,
  		enableCloseButton: false
    };
    var panorama = new  google.maps.StreetViewPanorama(document.getElementById("edit_pano"), panoramaOptions);
    map.setStreetView(panorama);
    panorama.setVisible(true);
}
var map; //Google Map
var randomPoint; //Random Lat/Long Point
var isWithinCity;
var studyArea = new Object();
var studyPolygon = [];
var polygon;
var markerIcon = '/static/images/yellow.png';


function initialize(_studyID, polygonStr) {
    studyID = _studyID;
    extendGmaps();
    
    studyPolygon = [];
    var polyArray = polygonStr.split(',');
    // polygonStr is formatted like x1,y1,x2,y2, etc...
    for (var polyArrayIdx = 0; polyArrayIdx < polyArray.length; polyArrayIdx+=2) {
        studyPolygon.push(new google.maps.LatLng(polyArray[polyArrayIdx+1],polyArray[polyArrayIdx],true));
    }

    // TODO: comment this out once populating is working again.
    //console.log(studyPolygon);
    
    //sv = new google.maps.StreetViewService(); //Google Street View Service
	studyArea = {name: "studyArea", polygon: studyPolygon, TLLat: null, TLLng: null, BRLat: null, BRLng: null};
	//Calculate Bounding box for fetched city
	polygon = new google.maps.Polygon({
		paths: studyArea.polygon,        
		strokeWeight: 2,
        strokeOpacity: 1,
        strokeColor: '#eeb44b',
        fillColor: '#eeb44b'
    });
	calcBoundingBox();
	plot();
}
function calcBoundingBox() 
{
	var arrayLat = [];
	var arrayLng = [];
	for (var i=0; i<studyArea.polygon.length; i++)
	{
		arrayLat[i] = studyArea.polygon[i].lat();
		arrayLng[i] = studyArea.polygon[i].lng();
	}
	studyArea.TLLat = Math.max.apply(Math, arrayLat);
	studyArea.TLLng = Math.min.apply(Math, arrayLng);
	studyArea.BRLat = Math.min.apply(Math, arrayLat);
	studyArea.BRLng = Math.max.apply(Math, arrayLng);
}
function plot()
{
	var mapOptions =
	{
		zoom: 10,
		mapTypeId: google.maps.MapTypeId.HYBRID,
		streetViewControl: false
	};
	map = new google.maps.Map($('#map4').get()[0], mapOptions);
	polygon.setMap(map);
	var swpoint = new google.maps.LatLng(studyArea.BRLat, studyArea.TLLng);
    var nepoint = new google.maps.LatLng(studyArea.TLLat, studyArea.BRLng);
    var bounds = new google.maps.LatLngBounds(swpoint, nepoint);
    map.fitBounds(bounds);
}
// Gmaps API extension

// Polygon getBounds extension - google-maps-extensions
// http://code.google.com/p/google-maps-extensions/source/browse/google.maps.Polygon.getBounds.js
function extendGmaps() {

    if (!google.maps.Polygon.prototype.getBounds) {
      google.maps.Polygon.prototype.getBounds = function(latLng) {
        var bounds = new google.maps.LatLngBounds();
        var paths = this.getPaths();
        var path;
    
        for (var p = 0; p < paths.getLength(); p++) {
          path = paths.getAt(p);
          for (var i = 0; i < path.getLength(); i++) {
            bounds.extend(path.getAt(i));
          }
        }

        return bounds;
      }
    }

    // Polygon containsLatLng - method to determine if a latLng is within a polygon
    google.maps.Polygon.prototype.containsLatLng = function(latLng) {
      // Exclude points outside of bounds as there is no way they are in the poly
      var bounds = this.getBounds();

      if(bounds != null && !bounds.contains(latLng)) {
        return false;
      }

      // Raycast point in polygon method
      var inPoly = false;

      var numPaths = this.getPaths().getLength();
      for(var p = 0; p < numPaths; p++) {
        var path = this.getPaths().getAt(p);
        var numPoints = path.getLength();
        var j = numPoints-1;

        for(var i=0; i < numPoints; i++) { 
          var vertex1 = path.getAt(i);
          var vertex2 = path.getAt(j);

          if (vertex1.lng() < latLng.lng() && vertex2.lng() >= latLng.lng() || vertex2.lng() < latLng.lng() && vertex1.lng() >= latLng.lng())  {
            if (vertex1.lat() + (latLng.lng() - vertex1.lng()) / (vertex2.lng() - vertex1.lng()) * (vertex2.lat() - vertex1.lat()) < latLng.lat()) {
              inPoly = !inPoly;
            }
          }

          j = i;
        }
      }

      return inPoly;
    }
}

// Array max/min monkeypatching
// JavaScript Document
Array.max = function( array ){
    return Math.max.apply( Math, array );
};
Array.min = function( array ){
    return Math.min.apply( Math, array );
};