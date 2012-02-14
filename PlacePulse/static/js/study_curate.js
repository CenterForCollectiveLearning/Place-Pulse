var map; //Google Map
var randomPoint; //Random Lat/Long Point
var isWithinCity;
var studyArea = new Object();
var studyPolygon = [];
var polygon;
var gLat;
var gLng;
var gHeading;
var gPitch;
var gId;
var green;
var shadow;
var shape;

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
        strokeColor: '#4aea39',
        fillColor: '#4aea39'
    });
    green = new google.maps.MarkerImage(
      '/static/img/marker-images/green.png',
      new google.maps.Size(16,26),
      new google.maps.Point(0,0),
      new google.maps.Point(8,26)
    );

    shadow = new google.maps.MarkerImage(
      '/static/img/marker-images/shadow.png',
      new google.maps.Size(32,26),
      new google.maps.Point(0,0),
      new google.maps.Point(8,26)
    );

    shape = {
      coord: [11,0,13,1,14,2,15,3,15,4,15,5,15,6,15,7,15,8,15,9,15,10,15,11,15,12,14,13,14,14,13,15,13,16,12,17,12,18,11,19,11,20,10,21,10,22,9,23,9,24,8,25,7,25,6,24,6,23,5,22,5,21,4,20,4,19,3,18,3,17,2,16,2,15,1,14,1,13,0,12,0,11,0,10,0,9,0,8,0,7,0,6,0,5,0,4,0,3,1,2,2,1,4,0,11,0],
      type: 'poly'
    };
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
function save_changes(id,lat,lng,heading,pitch)
{
    $.ajax({
            url:'/study/curate/location/update/' + id,
            // Expect JSON to be returned. This is also enforced on the server via mimetype.
            dataType: 'json',
            data: {
                id: id,
                lat: lat,
                lng: lng,
                heading: heading,
                pitch: pitch
            },
            type: 'POST',
            success: function(data) {
                if (data.success === "True")
                {
                    $("#close_modal").trigger('click');
                    $('#'+ id).replaceWith('<a id="' + id + '" class="thumbnail cursor" data-toggle="modal" onMouseover="center_map(' + lat + ',' + lng + ')" onclick="editsv(\'' + id + '\',' + lat + ',' + lng + ',' + heading + ',' + pitch +')"><img id="img' + id + '" src="http://maps.googleapis.com/maps/api/streetview?size=160x120&location=' + lat + ',%20' + lng + '&fov=90&heading=' + heading + '&pitch=' + pitch +'&sensor=false" /></a>');
                }
            }
        });
}
function delete_image(id)
{
    $.ajax({
            url:'/study/curate/location/delete/' + id,
            // Expect JSON to be returned. This is also enforced on the server via mimetype.
            dataType: 'json',
            data: {
                id: id
            },
            type: 'POST',
            success: function(data) {
                if (data.success === "True")
                {
                    $("#close_modal").trigger('click');
                    $('#li'+ id).remove()
                }
            }
        });
}
function editsv(id, lat, lng, heading, pitch) {
    $('#edit_street_view').modal();
    var location = new google.maps.LatLng(lat,lng);
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
    gId = id;
    gLat = lat;
    gLng = lng;
    gHeading = heading;
    gPitch = pitch;
    var panorama = new google.maps.StreetViewPanorama(document.getElementById("edit_pano"), panoramaOptions);
    panorama.setVisible(true);
    $('#edit_street_view').on('shown', function () 
    {
        google.maps.event.trigger(panorama, 'resize');
        google.maps.event.addListener(panorama, 'position_changed', function() {
            gLat = panorama.getPosition().lat();
            gLng = panorama.getPosition().lng();
        });

        google.maps.event.addListener(panorama, 'pov_changed', function() {
            gHeading = panorama.getPov().heading;
            gPitch = panorama.getPov().pitch;
        });
    });
}
    
function center_map(lat,lng){
    var location = new google.maps.LatLng(lat,lng);
    var mapOptions = {
      center: location,
      zoom: 14,
      mapTypeId: google.maps.MapTypeId.HYBRID
    };
    var map = new google.maps.Map(document.getElementById("map4"), mapOptions);
    marker = new google.maps.Marker({
      draggable: true,
      raiseOnDrag: false,
      icon: green,
      shadow: shadow,
      shape: shape,
      animation: google.maps.Animation.DROP,
      map: map,
      position: location
    });

        //google.maps.event.addListener(marker, 'click', toggleBounce);     
}
// Array max/min monkeypatching
// JavaScript Document
Array.max = function( array ){
    return Math.max.apply( Math, array );
};
Array.min = function( array ){
    return Math.min.apply( Math, array );
};