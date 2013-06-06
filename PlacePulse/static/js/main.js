//var locs_buffer;
var locs;
//var buffer_left;
//var buffer_right;
//var numVotes = 0;
var left_done = false;
var right_done = false;

$('#pano_right').hover(function() {$('#right_arrow').toggleClass('choice_button_hover')}, function() {$('#right_arrow').toggleClass('choice_button_hover')});

$('#pano_left').hover(function() {$('#left_arrow').toggleClass('choice_button_hover')}, function() {$('#left_arrow').toggleClass('choice_button_hover')});

$('#right_arrow').hover(function() {$('#pano_right').toggleClass('streetViewChoice_hover')}, function() {$('#pano_right').toggleClass('streetViewChoice_hover')});

$('#left_arrow').hover(function() {$('#pano_left').toggleClass('streetViewChoice_hover')}, function() {$('#pano_left').toggleClass('streetViewChoice_hover')});

$('#equal').hover(function() {$('#pano_left, #pano_right').toggleClass('streetViewChoice_hover')}, function() {$('#pano_left, #pano_right').toggleClass('streetViewChoice_hover')});

function onStreetViewChoice(choice) {
    left_done = false;
    right_done = false;
    $("img.place").unbind('click').on("click", function() {void(0); });
    $("#left_arrow").unbind('click').on("click", function() {void(0); });
    $("#right_arrow").unbind('click').on("click", function() {void(0); });
    $("#equal").unbind('click').on("click", function() {void(0); });
    $('.loadingmsg').css("display","block");
    $("ul.thumbnails").css("opacity", 0.2);
    $(".equalbutton").css("opacity", 0.2);
    console.log("on street view " + choice)
    var dataObj = {
            study_id: study_id,
            left: locs[0].id,
            right: locs[1].id,
            choice: choice
        };
    $.ajax({
        type: 'POST',
        url: '/study/vote/' + study_id + '/',
        data: dataObj,
        success: function(data) {
            //getImagesFromBuffer();
            //loadImagesToBuffer();
            getImagePair();
        }
    });
}
function getImagesFromBuffer() {
    locs = locs_buffer;
    $('#pano_left img.place').attr('src', getSVURL(locs[0].loc[0],locs[0].loc[1]));
    $('#pano_right img.place').attr('src', getSVURL(locs[1].loc[0],locs[1].loc[1]));
    //console.log("obtained image pair from buffer");
}
function loadImagesToBuffer() {
    $.ajax({
        url: '/study/getpair/' + study_id,
        type: 'GET',
        success: function(data) {
            locs_buffer = data.locs;
            if(locs_buffer === undefined || locs_buffer[0] === undefined || locs_buffer[0].loc === undefined) {
                console.log("null locations returned from the server")
                console.log(locs_buffer);
                console.log(study_id);
            }
            $('#pano_left_buffer img.place').attr('src',getSVURL(locs_buffer[0].loc[0],locs_buffer[0].loc[1]));
            $('#pano_right_buffer img.place').attr('src',getSVURL(locs_buffer[1].loc[0],locs_buffer[1].loc[1]));
            console.log("obtained buffer image pair")
            console.log("------------------------------")
        }
    });
}

function getImagePair() {
    $.ajax({
        url: '/study/getpair/' + study_id,
        type: 'GET',
        success: function(data) {
            locs = data.locs;
            if(locs === undefined || locs[0] === undefined || locs[0].loc === undefined) {
                console.log("null locations returned from the server")
                console.log(locs);
                console.log(study_id);
            }
            imagesLoaded( $('ul.thumbnails'), function(){
                $("img.place").unbind('click');
                $('#pano_left img.place').on("click", function() { onStreetViewChoice('left'); });
                $('#left_arrow').on("click", function() { onStreetViewChoice('left'); });
                $('#pano_right img.place').on("click", function() { onStreetViewChoice('right'); });
                $('#right_arrow').on("click", function() { onStreetViewChoice('right'); });
                $('#equal').on("click", function() { onStreetViewChoice('equal'); });

                $('.loadingmsg').css("display","none");
                $("ul.thumbnails").css("opacity", 1.0);
                $(".equalbutton").css("opacity", 1.0);
            });
            $('#pano_left img.place').attr('src', getSVURL(locs[0].loc[0],locs[0].loc[1]));
            $('#pano_right img.place').attr('src', getSVURL(locs[1].loc[0],locs[1].loc[1]));


        }
    });
}

function getSVURL(lat, lng) {
    // TODO: re-add this SV-specific data: &fov=90&heading=235&pitch=10
    //return "http://maps.googleapis.com/maps/api/streetview?size=470x306&location=" + lat + "," + lng + "&sensor=false&key=AIzaSyABK8O6uR0xcb_GQDSum__7gVkJXsMKZWU";
    return "http://maps.googleapis.com/maps/api/streetview?size=470x306&location=" + lat + "," + lng + "&sensor=false";
}

$(document).ready(function() {
    getImagePair();
});
