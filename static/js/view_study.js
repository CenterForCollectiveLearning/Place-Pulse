function onStreetViewChoice() {
		$.ajax({
			url: '/study/update',
			type: 'POST',
			data: {
				option_left: $('#sv1').attr('place'),
				option_right: $('#sv2').attr('place'),
				choice: $(this).attr('place')
			}
		});
	$('.streetViewChoice').unbind(onStreetViewChoice);		
}

function newPrompt() {
	$.ajax({
		url: '/study/get_prompt',
		type: 'GET',
		data: {
			'studyID': studyID
		},
		success: function(data) {
			var leftPlace = {
			  position: new google.maps.LatLng(data.place[0].loc[0],data.place[0].loc[1])
			};
			
			var rightPlace = {
			  position: new google.maps.LatLng(data.place[1].loc[0],data.place[1].loc[1])
			};
			
			var panorama = new  google.maps.StreetViewPanorama(document.getElementById("pano"), panoramaOptions);
			map.setStreetView(panorama);
		}
	});
	
	$('.streetViewChoice').click(onStreetViewChoice);

}


function init() {
	newPrompt();
}