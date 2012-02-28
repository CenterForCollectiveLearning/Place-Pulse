var map; //Google Map
var randomPoint; //Random Lat/Long Point
var sv = null;
var isWithinCity;
var studyArea = new Object();
var studyPolygon = [];
var polygon;
var completed = 0;
var virgin = 0;
var pointsToAdd = 100;
var studyID = ''
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
var row=0;
var col=-1;
var colDiff;
var rowDiff;
var counter=0;
var hitsInGrid=0;
var canFinish=false;

function startPopulatingStudy(_studyID, polygonStr, dataResolution, locDistribution) {
    studyID = _studyID;
    pointsToAdd = 100;
    extendGmaps();
    dataRes = parseInt(dataResolution);
    locDist = locDistribution;
    studyPolygon = [];
    var polyArray = polygonStr.split(',');
    // polygonStr is formatted like x1,y1,x2,y2, etc...
    for (var polyArrayIdx = 0; polyArrayIdx < polyArray.length; polyArrayIdx+=2) {
        studyPolygon.push(new google.maps.LatLng(polyArray[polyArrayIdx+1],polyArray[polyArrayIdx],true));
    }

    // TODO: comment this out once populating is working again.
    console.log(studyPolygon);
    
    sv = new google.maps.StreetViewService(); //Google Street View Service

	studyArea = {name: "studyArea", polygon: studyPolygon, TLLat: null, TLLng: null, BRLat: null, BRLng: null};
	//Calculate Bounding box for fetched city
	calcBoundingBox();
	newPoint();
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
	if(locDist=='randomly') {
		maxRows=0;
		maxCols=0;
		colDiff=studyArea.BRLng-studyArea.TLLng;
		rowDiff=studyArea.TLLat-studyArea.BRLat;
	}
	else {
		var boundingBox =[]
		boundingBox.push(new google.maps.LatLng(studyArea.TLLat,studyArea.TLLng));
		boundingBox.push(new google.maps.LatLng(studyArea.TLLat,studyArea.BRLng));
		boundingBox.push(new google.maps.LatLng(studyArea.BRLat,studyArea.BRLng));
		boundingBox.push(new google.maps.LatLng(studyArea.BRLat,studyArea.TLLng));
		var area = google.maps.geometry.spherical.computeArea(boundingBox);
		var h = studyArea.TLLat-studyArea.BRLat;
		var l = studyArea.BRLng-studyArea.TLLng;
		var c = Math.pow(area/(h*l),.5);
		maxRows = Math.round(c*h/dataRes/2.0);
		maxCols = Math.round(c*l/dataRes/2.0);
		rowDiff = h/maxRows;
		colDiff = l/maxCols;
	}

	polygon = new google.maps.Polygon({
		paths: studyArea.polygon,        
		strokeWeight: 2,
        strokeOpacity: 1,
        strokeColor: '#4aea39',
        fillColor: '#4aea39'
        });
        pointsToAdd = Math.round(google.maps.geometry.spherical.computeArea(studyArea.polygon)/Math.pow(dataRes*2,2));
}
function nextGridBox() {
	if(locDist=='randomly') {
		col=0;
		row=0;
	}
	else if(row<maxRows) {
		if(col>=maxCols-1) {
			col= -1;
			row++;
		}
	col++;
	}
}
function newPoint()
{
	nextGridBox();
	if(locDist=='randomly') {
		col=0;
		row=0;
		hitsInGrid=4;//arbitrary very negative number
	}
	else if(locDist=='evenly') {
		hitsInGrid=4;
	}
	else if(locDist=='gridrandom') {
		hitsInGrid=4;
	}
	guessPoint();
	checkPoly();
	sv.getPanoramaByLocation(randomPoint, 50, processSVData);
	

}
function guessPoint() 
{
	var lat;
	var lng;
	if(locDist=='evenly') {
		lat = rowDiff*.5+studyArea.TLLat-rowDiff*(row+1);
		lng = colDiff*.5+studyArea.TLLng+colDiff*(col);
	}
	else {
		lat = Math.random()*rowDiff+studyArea.TLLat-rowDiff*(row+1);
		lng = Math.random()*colDiff+studyArea.TLLng+colDiff*(col);
	}
	randomPoint = new google.maps.LatLng(lat, lng);

}
function checkPoly()
{
	while(!polygon.containsLatLng(randomPoint) && (row<maxRows || locDist=='randomly'))
	{	
		++hitsInGrid;
		if(hitsInGrid>4) {
			nextGridBox();
		}
			
		guessPoint();
	}
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
	var swpoint = new google.maps.LatLng(studyArea.BRLat, studyArea.TLLng);
    var nepoint = new google.maps.LatLng(studyArea.TLLat, studyArea.BRLng);
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
		if(completed < pointsToAdd && (locDist=='randomly' || row<maxRows))
		{

			updateDB(data.location.latLng.lat(),data.location.latLng.lng());
		}
		else
		{
			
		    // Only call /study/finish_populate once
		    if (waitingForFinish) return;
		    $.ajax({
		        dataType: 'json',
		        url: "/study/finish_populate/" + studyID + '/',
		        type: "POST",
		        data: {
		            'study_id': studyID
		        },
		        success: function(e) {
		            window.location = "/study/curate/" + studyID;
		        }
		    });
		    
		    waitingForFinish = true;

		}
	}
	newPoint();
}


function updateDB(lat1,lng1)
{
	var lat = lat1;
	var lng = lng1;
	console.log('updateDB: ' + completed)
	$.ajax({
		type: "POST",
		url: window.location.href,
		data: { 
			'lat': lat,
			'lng': lng,
			'study_id': studyID },
		success: function(result) {
			if(result.success)
			{

			    console.log(completed + ' places sent.');
				completed++;
				if(completed<=pointsToAdd)
				{
					refreshMap(lat,lng);
				}
			

			}
		},
		error: function(data){
			//alert(data.responseText);
		},
		complete: function(data){
			newPoint();
		}
	});
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
	$("#progress_bar").css("width",completed/pointsToAdd*100 + "%");
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
