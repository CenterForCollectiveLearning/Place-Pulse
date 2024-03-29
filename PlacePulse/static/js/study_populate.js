var map; //Google Map
var randomPoint; //Random Lat/Long Point
var sv = null;
var isWithinCity;
var placeArea = new Object();
var placePolygon = [];
var polygon;
var completed = 0;
var virgin = 0;
var pointsToAdd = 100;
var placeID = '';
var totalPoints=0;
var goodHits=0;
var waitingForFinish = false;
var green;
var shadow;
var shape;
var dataRes;
var locDist;
var maxHitsPerBox=5;
var maxRows;
var maxCols;
var colDiff;
var rowDiff;
var counter=0;
var hitsInGrid=0;
var countCalls=0;
var countReturns=0;
var progressBarMax=0;
function startPopulatingPlace(_placeID, polygonStr, dataResolution, locDistribution) {

    placeID = _placeID;

    pointsToAdd = 100; //TODO: Michael X
    progressBarMax=pointsToAdd; //TODO: Michael X
    extendGmaps();
    dataRes = parseInt(dataResolution);
    locDist = locDistribution;
    placePolygon = [];
    var polyArray = polygonStr.split(',');
    // polygonStr is formatted like x1,y1,x2,y2, etc...
    for (var polyArrayIdx = 0; polyArrayIdx < polyArray.length; polyArrayIdx+=2) {
        placePolygon.push(new google.maps.LatLng(polyArray[polyArrayIdx+1],polyArray[polyArrayIdx],true));
    }

    // TODO: comment this out once populating is working again.
    console.log(placePolygon);

    sv = new google.maps.StreetViewService(); //Google Street View Service

  placeArea = {name: "placeArea", polygon: placePolygon, TLLat: null, TLLng: null, BRLat: null, BRLng: null};
  //Calculate Bounding box for fetched city
    calcBoundingBox();
    pickPoints();
}
function calcBoundingBox()
{
  var arrayLat = [];
  var arrayLng = [];
  for (var i=0; i<placeArea.polygon.length; i++)
  {
    arrayLat[i] = placeArea.polygon[i].lat();
    arrayLng[i] = placeArea.polygon[i].lng();
  }
  placeArea.TLLat = Math.max.apply(Math, arrayLat);
  placeArea.TLLng = Math.min.apply(Math, arrayLng);
  placeArea.BRLat = Math.min.apply(Math, arrayLat);
  placeArea.BRLng = Math.max.apply(Math, arrayLng);
  if(locDist=='randomly') {
    maxRows=0;
    maxCols=0;
    colDiff=placeArea.BRLng-placeArea.TLLng;
    rowDiff=placeArea.TLLat-placeArea.BRLat;
  }
  else {
    var boundingBox =[]
    boundingBox.push(new google.maps.LatLng(placeArea.TLLat,placeArea.TLLng));
    boundingBox.push(new google.maps.LatLng(placeArea.TLLat,placeArea.BRLng));
    boundingBox.push(new google.maps.LatLng(placeArea.BRLat,placeArea.BRLng));
    boundingBox.push(new google.maps.LatLng(placeArea.BRLat,placeArea.TLLng));
    var area = google.maps.geometry.spherical.computeArea(boundingBox);
    var h = placeArea.TLLat-placeArea.BRLat;
    var l = placeArea.BRLng-placeArea.TLLng;
    var c = Math.pow(area/(h*l),.5);
    maxRows = Math.round(c*h/dataRes/2.0);
    maxCols = Math.round(c*l/dataRes/2.0);
    rowDiff = h/maxRows;
    colDiff = l/maxCols;
  }

  polygon = new google.maps.Polygon({
    paths: placeArea.polygon,
    strokeWeight: 2,
        strokeOpacity: 1,
        strokeColor: '#4aea39',
        fillColor: '#4aea39'
        });
        pointsToAdd = Math.round(google.maps.geometry.spherical.computeArea(placeArea.polygon)/Math.pow(dataRes*2,2));
}


function pickPoints() {
    if(locDist=='randomly') {
  for(var i=0;i<pointsToAdd*5;i++)
    newPoint(0,0);
    }
    else {
      for(var r=0;r<maxRows;r++) {
      for(var c=0;c<maxCols;c++) {
          newPoint(r,c);
      }
      }
      progressBarMax=countCalls;
    }
}

function newPoint(r,c)
{
  var point = guessPoint(r,c);
  point = checkPoly(point,r,c);
  if(point!=false){
    ++countCalls;
    sv.getPanoramaByLocation(point, 50, processSVData);
  }


}
function guessPoint(row,col)
{
  if(locDist=='evenly') {
    var lat = rowDiff*.5+placeArea.TLLat-rowDiff*(row+1.0);
    var lng = colDiff*.5+placeArea.TLLng+colDiff*(col);
  }
  else {
    var lat = Math.random()*rowDiff+placeArea.TLLat-rowDiff*(row+1.0);
    var lng = Math.random()*colDiff+placeArea.TLLng+colDiff*(col);
  }
  return new google.maps.LatLng(lat, lng);

}
function checkPoly(point,r,c)
{
  var p = new google.maps.LatLng(point.lat(),point.lng());
  var count=0;
  while(!polygon.containsLatLng(p) && count<2)
  {
    p = guessPoint(r,c);
    ++count;
  }
  if(count>=2)
    return false
  return p;
}
function plot()
{
  var mapOptions =
  {
    center: randomPoint,
    zoom: 10,
    mapTypeId: google.maps.MapTypeId.HYBRID,
    streetViewControl: false
  };
  map = new google.maps.Map($('#map').get()[0], mapOptions);
  polygon.setMap(map);
  var swpoint = new google.maps.LatLng(placeArea.BRLat, placeArea.TLLng);
    var nepoint = new google.maps.LatLng(placeArea.TLLat, placeArea.BRLng);
    var bounds = new google.maps.LatLngBounds(swpoint, nepoint);
    map.fitBounds(bounds);
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
}
function processSVData(data, status)
{
  ++countReturns;
  if((goodHits+1)*12.5<totalPoints && locDist=='randomly') {
    //alert("Bad Polygon");
  }
  ++totalPoints;
  if (status == google.maps.StreetViewStatus.OK)
  {

    ++goodHits;
    if(virgin==0)
    {
      plot();
      virgin = 1;
    }
    if(completed < pointsToAdd)
    {
      var lat = data.location.latLng.lat();
      var lng = data.location.latLng.lng();
      refreshMap(lat,lng);
      updateDB(lat,lng);
    }

  }
  if(countReturns==countCalls) {
    endplacePopulation();
  }
}

function endplacePopulation() {
        $.ajax({
            dataType: 'json',
            url: "/place/finish_populate/" + placeID + '/',
            type: "POST",
            data: {
                'place_id': placeID
            },
            success: function(e) {
                window.location = "/place/curate/" + placeID;
            }
        });
}

function updateDB(lat,lng)
{
  console.log('updateDB: ' + completed)
  $.ajax({
    type: "POST",
    url: window.location.href,
    data: {
      'lat': lat,
      'lng': lng
       },
    success: function(result) {
      if(result.success)
      {

          console.log(completed + ' places sent.');
        completed++;
        if(completed<=pointsToAdd)
        {
          refreshMap(lat,lng);
        }
        else {
          endplacePopulation();
        }

      }
    },
    error: function(data){
      //alert(data.responseText);
    },
    complete: function(data){
    }
  });

}

function findGridBox(lat,lng) {
  return [Math.floor((placeArea.TLLat-lat)/rowDiff),Math.floor((lng-placeArea.TLLng)/colDiff)]
}

function refreshMap(lat,lng)
{
  var marker = new google.maps.Marker({
      draggable: true,
      raiseOnDrag: false,
      icon: green,
      shadow: shadow,
      shape: shape,
      animation: google.maps.Animation.DROP,
      map: map,
      position: new google.maps.LatLng(lat, lng)
    });
  $("#progress_bar").css("width",countReturns/progressBarMax*100 + "%");
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

function generateGrid() {

}
// Array max/min monkeypatching
// JavaScript Document
Array.max = function( array ){
    return Math.max.apply( Math, array );
};
Array.min = function( array ){
    return Math.min.apply( Math, array );
};