var map = null;
var marker = null;

$(document).ready(function() {
    function loadScript() {
      var script = document.createElement("script");
      script.type = "text/javascript";
      script.src = "http://maps.google.com/maps/api/js?sensor=false&callback=initGmaps";
      document.body.appendChild(script);
    }
	loadScript();
	$.ajax({
		'type': 'GET',
		'url': '/top_results_data/' + STUDY_NAME,
		'dataType': 'json',
		'success': renderResults
	});
});

function initGmaps() {
	const loc = new google.maps.LatLng(-34.397, 150.644);
    green = new google.maps.MarkerImage(
      '/static/img/marker-images/green.png',
      new google.maps.Size(16,26),
      new google.maps.Point(0,0),
      new google.maps.Point(8,26)
    );
    shape = {
      coord: [11,0,13,1,14,2,15,3,15,4,15,5,15,6,15,7,15,8,15,9,15,10,15,11,15,12,14,13,14,14,13,15,13,16,12,17,12,18,11,19,11,20,10,21,10,22,9,23,9,24,8,25,7,25,6,24,6,23,5,22,5,21,4,20,4,19,3,18,3,17,2,16,2,15,1,14,1,13,0,12,0,11,0,10,0,9,0,8,0,7,0,6,0,5,0,4,0,3,1,2,2,1,4,0,11,0],
      type: 'poly'
    };
    shadow = new google.maps.MarkerImage(
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
      icon: green,
      shadow: shadow,
      shape: shape,
      animation: google.maps.Animation.DROP,
      map: map,
      position: loc
    });
}

function renderResults(resultsData) {
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