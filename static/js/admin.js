var map; //Google Map
var panorama; //Google Street View Panorama
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
var cityList;
var markerIcon = '/static/images/yellow.png';



function displayCityOptions(_studyID, polygonStr, cities) {
    studyID = _studyID;
    cityList=cities;
    studyPolygon = [];
	//initialize saveCity
	$('#saveCity').click(saveCity);
    var polyArray = polygonStr.split(',');
    // polygonStr is formatted like x1,y1,x2,y2, etc...
    for (var polyArrayIdx = 0; polyArrayIdx < polyArray.length; polyArrayIdx+=2) {
        studyPolygon.push(new google.maps.LatLng(polyArray[polyArrayIdx+1],polyArray[polyArrayIdx],true));
    }

    // TODO: comment this out once populating is working again.
    console.log(studyPolygon);
    //console.log(numVotes);

	studyArea = {name: "studyArea", polygon: studyPolygon, TLLat: null, TLLng: null, BRLat: null, BRLng: null};
	//Calculate Bounding box for fetched city
	calcBoundingBoxAndPolygon();
	plot();
}
function calcBoundingBoxAndPolygon() 
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
    polygon = new google.maps.Polygon({
		paths: studyArea.polygon,        
		strokeWeight: 2,
        strokeOpacity: 1,
        strokeColor: '#eeb44b',
        fillColor: '#eeb44b'
    });
}

function plot()
{
    var newLoc = new google.maps.LatLng(42.37, -71.13);
	var mapOptions =
	{
		center: newLoc,
		zoom: 10,
		mapTypeId: google.maps.MapTypeId.HYBRID,
		streetViewControl: false
	};
	map = new google.maps.Map($('#map_canvas').get()[0], mapOptions);
	polygon.setMap(map);
	var swpoint = new google.maps.LatLng(studyArea.BRLat, studyArea.TLLng);
    var nepoint = new google.maps.LatLng(studyArea.TLLat, studyArea.BRLng);
    var bounds = new google.maps.LatLngBounds(swpoint, nepoint);
    map.fitBounds(bounds);
}

function populateDropDownMenu(cityList)
{
	for(var i = 0;i<cityList.length;i++)
	{
			var opt = document.createElement('option');
			document.getElementById('dropDownList').options.add(opt);
			opt.text=""+cityList[i];
			opt.value=""+cityList[i];
	}
}

function saveCity()
{
	var index = document.getElementById('dropDownList').selectedIndex;
	if(index==0)
	{
		var city_name = prompt("What is the name of the city?");
		if(city_name!=null && city_name!="")
		{
			updateCity(city_name);
		}
		else
		{
			alert("Please enter a name or choose one from the list.");
		}
	}
	else
	{
		updateCity(cityList[index-1]);
	}
}

function updateCity(cityname)
{
	$.ajax({
		type: "POST",
		url: window.location.href,
		data: { 'city': cityname }
	});
	window.location = '/success/'+ studyID;
}
// Array max/min monkeypatching
// JavaScript Document
Array.max = function( array ){
    return Math.max.apply( Math, array );
};
Array.min = function( array ){
    return Math.min.apply( Math, array );
};
