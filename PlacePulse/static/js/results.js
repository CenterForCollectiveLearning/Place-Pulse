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
	// If we're rendering the city or study view, we need to wait for initGmaps first
	if (typeof STUDY_ID != 'undefined') {
		$.ajax({
			'type': 'GET',
			'url': '/study/results_data/' + STUDY_ID + '/',
			'dataType': 'json',
			'success': renderStudyResults
		});
	}
	$('.lockedLink').popover();
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
	// FIXME: Have the coordinate set to a point within the dataset? For now, it's preset to bldg E-14.
	const loc = new google.maps.LatLng(42.36050, -71.08737);
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
	      map: map
	    });
	prepGmapsIcons();
	if (typeof PLACE_NAME_SLUG != 'undefined')
		fetchPlaceResults();
	// else if (typeof STUDY_ID != 'undefined')
	// 	fetchStudyResults();
}

// function fetchStudyResults() {
// 	$.ajax({
// 		'type': 'GET',
// 		'url': '/study_results_data/' + STUDY_ID,
// 		'dataType': 'json',
// 		'success': renderStudyResults
// 	});	
// }

function fetchPlaceResults() {
	$.ajax({
		'type': 'GET',
		'url': '/study/results_data/' + STUDY_ID + '/' + PLACE_NAME_SLUG + '/',
		'dataType': 'json',
		'success': renderPlaceResults
	});	
}

function renderPlaceResults(resultsData) {
	var markerParams = {
      draggable: false,
      raiseOnDrag: false,
      icon: gmaps_green,
      // shadow: gmaps_green,
      // shape: gmaps_green,
      animation: google.maps.Animation.DROP,
      map: map
    };
	
	console.log(resultsData);
	
	var upperLeft = [9999,9999];
	var lowerRight = [-9999,-9999];
	
	var imageTemplate = _.template($('#appearRankedImageTemplate').html());
	
	for (var imgIdx in resultsData.ranking[0].rankings) {
		var location = resultsData.ranking[0].rankings[imgIdx];
		var newImg = $(imageTemplate(location));
		newImg.addClass('rankedImageUnappeared');
		newImg.get()[0].locationData = location;
		$('.resultsImgs').append(newImg);
		
		var newMarkerParams = markerParams;
		var rank = parseFloat(imgIdx)/resultsData.ranking[0].rankings.length;
		newMarkerParams['icon'] = gmaps_icons[parseInt(rank*gmaps_icons.length)];
		newMarkerParams['position'] = new google.maps.LatLng(location.loc[0], location.loc[1]);
		var marker = new google.maps.Marker(newMarkerParams);
		newImg.get()[0].marker = marker;
		
		function attachMarkerEvent(marker_, img_) {
			google.maps.event.addListener(marker_, 'click', function() {
				$('.mapSelected').removeClass('mapSelected');
				img_.addClass('mapSelected');
                // Thanks, http://oncemade.com/animated-page-scroll-with-jquery/
				// Make the destination 30px above the top of the image
                var scrollDestination = img_.offset().top - 30;
                $("html,body").stop();
                $("html,body").animate({ scrollTop: scrollDestination-20}, 250);
			});
		}
		
		attachMarkerEvent(marker,newImg);
		
		// Keep updating bounding rect coords
		upperLeft[0] = Math.min(upperLeft[0],location.loc[0]);
		upperLeft[1] = Math.min(upperLeft[1],location.loc[1]);
		lowerRight[0] = Math.max(lowerRight[0],location.loc[0]);
		lowerRight[1] = Math.max(lowerRight[1],location.loc[1]);		
	}
	$('.rankedImage').click(function() {
		map.setCenter(new google.maps.LatLng(this.locationData.loc[0],this.locationData.loc[1]));
		map.setZoom(15);
		this.marker.setAnimation(google.maps.Animation.DROP);
	});
	$('.rankedImageUnappeared').appear(function() {
		console.log(this);
		$(this).removeClass('rankedImageUnappeared');
		$(this).css('background-image','url(' + getSVURL(this.locationData.loc[0],this.locationData.loc[1],230,137) + ')');
		$(this).show();
	});
	// Keep all points in bounding rect
	map.fitBounds(new google.maps.LatLngBounds(new google.maps.LatLng(upperLeft[0],upperLeft[1]),new google.maps.LatLng(lowerRight[0],lowerRight[1])));
}

function renderStudyResults(resultsData) {
	var resultTemplate = _.template($('#rankItemTemplate').html());
	var imageTemplate = _.template($('#rankedImageTemplate').html());
	
	for (var place in resultsData.ranking) {
		var placeItem = $(resultTemplate(resultsData.ranking[place]));
		placeItem.addClass('rankedItems');
		$('.rankItems').append(placeItem);
		
		var placeRanking = resultsData.ranking[place];

		function renderImgList(appendTo,coordsList) {
			for (var item in coordsList) {
				var imgCoords = coordsList[item].loc;
				var newImg = $(imageTemplate(coordsList[item]));
				$(appendTo).append(newImg);
				newImg.get()[0].mapCoords = imgCoords;
			}
		}
		renderImgList(placeItem.find('.topRanked'),placeRanking.top);
		renderImgList(placeItem.find('.bottomRanked'),placeRanking.bottom);
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