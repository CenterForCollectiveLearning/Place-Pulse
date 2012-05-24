var locs_buffer;
var locs;
var buffer_left;
var buffer_right;
var uiLocked = true;
var numVotes = 0;

function onStreetViewChoice(choice) {
    if (uiLocked) return;
    uiLocked = true;
	var dataObj = {
            study_id: study_id,
            left: locs[0].id,
            right: locs[1].id,
            choice: choice
        };
	GAMIFICATION_STATUS.numVotes += 1;
	if (typeof(GAMIFICATION_STATUS) != 'undefined') {
		// If we just unlocked a new study, request an update for the GAMIFICATION_STATUS obj from the server
		// and display the success box.
		if (GAMIFICATION_STATUS.numVotes == GAMIFICATION_STATUS.nextStudy.votesToUnlock) {
			dataObj['gamification_status'] = true;
			updateNextStudy(GAMIFICATION_STATUS,'#voteSuccessLink');
			$('#voteSuccess').show();
		}
		else {
			updateVoteCount(GAMIFICATION_STATUS);
			$('#voteSuccess').hide();
		}
	}
    $.ajax({
        type: 'POST',
        url: '/study/vote/' + study_id + '/',
        data: dataObj,
        success: function(data) {
            getImagesFromBuffer();
            loadImagesToBuffer();
			if (data['gamificationStatus']) {
				GAMIFICATION_STATUS = data['gamificationStatus'];
				updateNextStudy(GAMIFICATION_STATUS);
				updateVoteCount(GAMIFICATION_STATUS);
			}
        }
    });
}
function getImagesFromBuffer() {
    var buffer_left = $('#pano_left_buffer img.place').attr('src');
    var buffer_right = $('#pano_right_buffer img.place').attr('src');
    
    $('#pano_left img.place').attr('src', buffer_left);
    $('#pano_right img.place').attr('src', buffer_right);
    locs = locs_buffer;
}
function loadImagesToBuffer() {
    $.ajax({
        url: '/study/getpair/' + study_id,
        type: 'GET',
        success: function(data) {
            locs_buffer = data.locs;
            $('#pano_left_buffer img.place').attr('src',getSVURL(locs_buffer[0].loc[0],locs_buffer[0].loc[1]));
            $('#pano_right_buffer img.place').attr('src',getSVURL(locs_buffer[1].loc[0],locs_buffer[1].loc[1]));
            uiLocked = false;
        }
    });
}
function init() {
    $.ajax({
        url: '/study/getpair/' + study_id,
        type: 'GET',
        success: function(data) {
            locs = data.locs;
            $('#pano_left img.place').attr('src', getSVURL(locs[0].loc[0],locs[0].loc[1]));
            $('#pano_right img.place').attr('src', getSVURL(locs[1].loc[0],locs[1].loc[1]));
            loadImagesToBuffer();
        }
    });
	// Progress for gamification stuff
	if (typeof(GAMIFICATION_STATUS) == 'undefined'){
		$('#voteProgress').hide();
	} else {
		updateVoteCount(GAMIFICATION_STATUS);
		updateNextStudy(GAMIFICATION_STATUS);
	}
}

function updateVoteCount(gamificationStatus) {
	var numVotes = gamificationStatus.numVotes - gamificationStatus.lastUnlockedAt;
	var votesToUnlock = gamificationStatus.nextStudy.votesToUnlock - gamificationStatus.lastUnlockedAt;
	$('#votesRemaining').html(votesToUnlock - numVotes);
	$('.progress .bar').css('width',(numVotes/votesToUnlock*100).toString() + '%');
}

function updateNextStudy(gamificationStatus,updateDiv) {
	if (!updateDiv)
		updateDiv = "#nextStudyToUnlock";
	var studyLink = $('<a href=""></a>');
	studyLink.attr('_target','_blank');
	studyLink.attr('href','/study/results/' + gamificationStatus.nextStudy.studyID);
	studyLink.text(gamificationStatus.nextStudy.studyQuestion);
	$(updateDiv).html(studyLink);
}

function getSVURL(lat,lng) {
    // TODO: re-add this SV-specific data: &fov=90&heading=235&pitch=10
    return "http://maps.googleapis.com/maps/api/streetview?size=470x306&location=" + lat + "," + lng + "&sensor=false";
}
