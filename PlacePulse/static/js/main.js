var locs_buffer;
var locs;
var buffer_left;
var buffer_right;
var uiLocked = true;
var numVotes = 0;

function onStreetViewChoice(choice) {
    if (uiLocked) return;
    uiLocked = true;
    $.ajax({
        type: 'POST',
        url: '/study/vote/' + study_id + '/',
        data: {
            study_id: study_id,
            left: locs[0].id,
            right: locs[1].id,
            choice: choice
        },
        success: function(data) {
            getImagesFromBuffer();
            loadImagesToBuffer();
			numVotes += 1;
			$('.progress .bar').css('width',(numVotes/20*100).toString() + '%');
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
}
function getSVURL(lat,lng) {
    // TODO: re-add this SV-specific data: &fov=90&heading=235&pitch=10
    return "http://maps.googleapis.com/maps/api/streetview?size=470x306&location=" + lat + "," + lng + "&sensor=false";
}
