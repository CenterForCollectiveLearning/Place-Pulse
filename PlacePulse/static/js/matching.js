$(document).ready(function() {
	var matchingGameScores = [];

	getMatchingPrompt();
	
	// Allow user to drop image back in original box if they choose
	$('#matchFrom').droppable({
		accept: ".draggableImage",
		drop: function(e,ui) {
			$('#matchFrom').append(ui.draggable);
			unsetImgFromMatchTo(ui.draggable);
		}
	 });
	
	$('.resetButton').click(function() {
		unsetImgFromMatchTo('.draggableImage');
		$('#matchFrom').append($('.draggableImage').get());
	});
	
	function submitMatching() {
		function avg(list){
			var sum = 0;
			for (var x = 0; x < list.length; x++)
				sum += list[x];
			return sum/list.length;
		}
		var matchResults = $('.dragPlace').map(function(idx,el){
			return {
				place_name: $(el).attr('data-placename'),
				locid: $(el).children('li').attr('data-locid')
			};
		});
		$.ajax({
			url: '/matching/eval_solution/',
			type: 'POST',
			success: function(data) {
				matchingGameScores.push(data.num_correct/4);
				// Only calculate the average based on last 10 scores
				matchingGameScores = matchingGameScores.slice(0,10);
				
				var statusDiv = $('<div>');
				statusDiv.append($("<div>You got " + data.num_correct + " out of 4 right!</div>"));
				statusDiv.append($("<div><strong>Moving avg.</strong>  " + parseInt(avg(matchingGameScores)*100) + "% </div>"));
				statusDiv.addClass('alert');
				statusDiv.addClass('alert-info');
				$('#winStatus').html(statusDiv);
				
				displayPrompt(data.next_prompt);
			}
		});
	};
	
	
	function unsetImgFromMatchTo(elemSelector) {
		// Dropping an image sets position:absolute and left/top:0, unset them so it fits inside of #matchFrom
		$(elemSelector).css('position','relative');
		$(elemSelector).css('left','');
		$(elemSelector).css('top','');
	}
	
	function checkIfDone() {
		// Have we matched all of the images?
		if ($('#matchTo img').length == 4)
			submitMatching();
	}
	
	function makeDraggable(elem) {
		elem.draggable({
			revert: "invalid"
		});
	}
	
	function makeDroppable(elem) {
		elem.droppable({
			accept: '.draggableImage',
			hoverClass: 'dropZoneHover',
			drop: function(e,ui) {
				// If there's already an image dragged here, move it back to #matchFrom
				if ($(this).children('.draggableImage')) {
					unsetImgFromMatchTo($(this).children('.draggableImage').get());
					$('#matchFrom').append($(this).children('.draggableImage'));
				}
				
				// Snap the dropped image into the drop zone
				$(ui.draggable).css('position','absolute');
				$(ui.draggable).css('left',0);
				$(ui.draggable).css('top',0);
				
				$(this).append($(ui.draggable));
				
				console.log($(ui.draggable).parent());
				
				checkIfDone();
			}
		});
	}
	
	function getMatchingPrompt() {
		$.ajax({
			type: 'GET',
			url: "/matching/get_prompt/",
			dataType: 'json',
			success: displayPrompt
		});
	}
	
	function displayPrompt(data) {
		// Clear out old li elements that may exist from previous round
		$('#matchFrom li').remove();
		$('#matchTo li').remove();
		for (var loc in data.locs) {
			var newImgLi = $('<li>').addClass('draggableImage');
			var newImg = $("<img>");
			newImg.attr('src',getSVURL(data.locs[loc].coords));
			newImgLi.append(newImg);
			$('#matchFrom').append(newImgLi);
			makeDraggable(newImgLi);
			newImgLi.attr('data-locid',data.locs[loc].id);
		}
		for (var place in data.place_names) {
			var newPlaceLi = $("<li>").addClass('dragPlace');
			newPlaceLi.append($('<span>' + data.place_names[place].name + '</span>').addClass("placeName"));
			$('#matchTo').append(newPlaceLi);
			makeDroppable(newPlaceLi);
			newPlaceLi.attr('data-placename',data.place_names[place].name);
		}
	}
});

function getSVURL(coords) {
    return "http://maps.googleapis.com/maps/api/streetview?size=235x153&location=" + coords[0] + "," + coords[1] + "&sensor=false";
}