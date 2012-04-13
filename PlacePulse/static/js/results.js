var map = null;
var marker = null;

var gmaps_green;
var gmaps_shadow;
var gmaps_shape;

var gmaps_icons = [];

$(document).ready(function() {
    function loadScript() {
      var script = document.createElement("script");
      script.type = "text/javascript";
      script.src = "http://maps.google.com/maps/api/js?sensor=false&callback=initGmaps";
      document.body.appendChild(script);
    }
	loadScript();
	// If we're rendering the city view, we need to wait for initGmaps first
	if (typeof CITY_NAME == 'undefined') {
		$.ajax({
			'type': 'GET',
			'url': '/top_results_data/' + STUDY_NAME,
			'dataType': 'json',
			'success': renderStudyResults
		});
	}
});

function prepGmapsIcons() {
	var canvas = document.createElement('canvas');
	canvas.width = 16;
	canvas.height = 16;
	var ctx = canvas.getContext('2d');
	
	const numIconDegrees = 10;
	// 10 degrees of icons
	for (var iconX = 0; iconX < numIconDegrees; iconX++) {
		// Clear canvas
		ctx.fillStyle = "rgba(0,0,0,0)";
		ctx.fillRect(0,0,16,16);
		ctx.fill();
		
		ctx.strokeStyle = "rgba(0,0,0,1.0)";
		// Draw circle
		var grayscaleVal = iconX/numIconDegrees*255;
		ctx.fillStyle = "rgba(" + grayscaleVal + ',' + grayscaleVal + ',' + grayscaleVal + ',1.0)';
		ctx.fillRect(0,0,12,12);
		ctx.strokeRect(0,0,12,12);
		ctx.fill();
		ctx.stroke();
		
		gmaps_icons.push(new google.maps.MarkerImage(
		      canvas.toDataURL(),
		      new google.maps.Size(16,16),
		      new google.maps.Point(0,0),
		      new google.maps.Point(8,26)));
	}
}

function initGmaps() {
	const loc = new google.maps.LatLng(-34.397, 150.644);
    gmaps_green = new google.maps.MarkerImage(
      '/static/img/marker-images/green.png',
      new google.maps.Size(16,26),
      new google.maps.Point(0,0),
      new google.maps.Point(8,26)
    );
    gmaps_shape = {
      coord: [11,0,13,1,14,2,15,3,15,4,15,5,15,6,15,7,15,8,15,9,15,10,15,11,15,12,14,13,14,14,13,15,13,16,12,17,12,18,11,19,11,20,10,21,10,22,9,23,9,24,8,25,7,25,6,24,6,23,5,22,5,21,4,20,4,19,3,18,3,17,2,16,2,15,1,14,1,13,0,12,0,11,0,10,0,9,0,8,0,7,0,6,0,5,0,4,0,3,1,2,2,1,4,0,11,0],
      type: 'poly'
    };
    gmaps_shadow = new google.maps.MarkerImage(
      '/static/img/marker-images/shadow.png',
      new google.maps.Size(32,26),
      new google.maps.Point(0,0),
      new google.maps.Point(8,26)
    );
    var mapOptions = {
      center: loc,
      zoom: 15,
      mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    map = new google.maps.Map($('#results_map').get()[0],mapOptions);
	marker = new google.maps.Marker({
      draggable: false,
      raiseOnDrag: false,
      icon: gmaps_green,
      shadow: gmaps_shadow,
      shape: gmaps_shape,
      animation: google.maps.Animation.DROP,
      map: map,
      position: loc
    });
	prepGmapsIcons();
	if (typeof CITY_NAME != 'undefined')
		fetchCityResults();
}

function fetchCityResults() {
	$.ajax({
		'type': 'GET',
		'url': '/city_results_data/' + STUDY_NAME + '/' + CITY_NAME,
		'dataType': 'json',
		'success': renderCityResults
	});	
}

function renderCityResults(resultsData) {
	var markerParams = {
      draggable: true,
      raiseOnDrag: false,
      icon: gmaps_green,
      // shadow: gmaps_green,
      // shape: gmaps_green,
      animation: google.maps.Animation.DROP,
      map: map
    };
	
	var upperLeft = [9999,9999];
	var lowerRight = [-9999,-9999];
	
	var imageTemplate = _.template($('#appearRankedImageTemplate').html());
	for (var imgIdx in resultsData.ranking[0].places) {
		var place = resultsData.ranking[0].places[imgIdx];
		var newImg = $(imageTemplate(place));
		newImg.addClass('rankedImageUnappeared');
		newImg.get()[0].placeData = place;
		$('.resultsImgs').append(newImg);
		
		var newMarkerParams = markerParams;
		newMarkerParams['icon'] = gmaps_icons[parseInt(Math.random()*gmaps_icons.length)];
		newMarkerParams['position'] = new google.maps.LatLng(place.coords[0], place.coords[1]);
		var marker = new google.maps.Marker(newMarkerParams);
		
		upperLeft[0] = Math.min(upperLeft[0],place.coords[0]);
		upperLeft[1] = Math.min(upperLeft[1],place.coords[1]);
		
		lowerRight[0] = Math.max(lowerRight[0],place.coords[0]);
		lowerRight[1] = Math.max(lowerRight[1],place.coords[1]);		
	}
	$('.rankedImageUnappeared').appear(function() {
		console.log(this);
		$(this).removeClass('rankedImageUnappeared');
		$(this).css('background-image','url(' + getSVURL(this.placeData.coords[0],this.placeData.coords[1],230,137) + ')');
		$(this).show();
		
	});
	map.fitBounds(new google.maps.LatLngBounds(new google.maps.LatLng(upperLeft[0],upperLeft[1]),new google.maps.LatLng(lowerRight[0],lowerRight[1])));
}

function renderStudyResults(resultsData) {
	$('.questionName').html(resultsData.question);
	
	var resultTemplate = _.template($('#rankItemTemplate').html());
	var imageTemplate = _.template($('#rankedImageTemplate').html());
	
	for (var city in resultsData.ranking) {
		var cityItem = $(resultTemplate(resultsData.ranking[city]));
		$('.rankItems').append(cityItem);
		
		var cityRanking = resultsData.ranking[city];

		function renderImgList(appendTo,coordsList) {
			for (var item in coordsList) {
				var imgCoords = coordsList[item].coords;
				var newImg = $(imageTemplate(coordsList[item]));
				$(appendTo).append(newImg);
				newImg.get()[0].mapCoords = imgCoords;
			}
		}
		renderImgList(cityItem.find('.topRanked'),cityRanking.top);
		renderImgList(cityItem.find('.bottomRanked'),cityRanking.bottom);
	}
	
	$('.rankItems').on('click','.rankedImage',null,function() {
		var gmapsCoords = new google.maps.LatLng(this.mapCoords[0],this.mapCoords[1]);
		map.panTo(gmapsCoords);
		marker.setPosition(gmapsCoords);
		marker.setAnimation(google.maps.Animation.BOUNCE);
	});
}

function getSVURL(lat,lng,imageWidth,imageHeight) {
	if (!imageWidth)
		imageWidth = $('.rankItems').width()/3 - 50;
	if (!imageHeight)
		imageHeight = Math.round(imageWidth*0.75);
    return "http://maps.googleapis.com/maps/api/streetview?size=" + imageWidth + "x" + imageHeight + "&location=" + lat + "," + lng + "&sensor=false";
}