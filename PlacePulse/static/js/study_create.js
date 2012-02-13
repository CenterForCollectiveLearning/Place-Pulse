var poly, map;
var markers;
var path;
var markerIcon;
var area=0;
var cityList;
var mapReady = false;

$(document).ready(function() {

    setupUI();
    
    // Hide entire map interface
    $('#mapInterface').hide();
    $('#selectionarea').hide();

    // Load the GMaps API, callback on load to initialize()
    function loadScript() {
      var script = document.createElement("script");
      script.type = "text/javascript";
      script.src = "http://maps.google.com/maps/api/js?sensor=false&callback=initialize&libraries=geometry";
      document.body.appendChild(script);
    }
    
    loadScript();
});

/***************************/
//@Author: Adrian "yEnS" Mato Gondelle & Ivan Guardado Castro
//@website: www.yensdesign.com
//@email: yensamg@gmail.com
//@license: Feel free to use it, but keep this credits please!                    
/***************************/

    //global vars
    var study_name = $("#study_name");
    var study_name_cg = $('#study_name_cg');
    var study_name_error = $('#study_name_error');

    var study_question = $("#study_question");
    var study_question_cg = $('#study_question_cg');
    var study_question_error = $('#study_question_error');
    
    //On blur
    study_name.blur(validate_study_name);
    study_question.blur(validate_study_question);

    
    //validation functions
    function validate_study_name(){
        //testing regular expression
        var a = $("#study_name").val();
        var filter = /^(?:\b\w+\b[\s\r\n]*){3,10}$/;
        //if it's valid email
        if(filter.test(a)){
            study_name_cg.removeClass("error");
            study_name_error.addClass("hidden");
            study_name_cg.addClass("success");
            return true;
        }
        //if it's NOT valid
        else{
            study_name_cg.addClass("error");
            study_name_cg.removeClass("success");
            study_name_error.removeClass("hidden");
            return false;
        }
    }
    function validate_study_question(){
        //if it's NOT valid
            var a = $("#study_question").val();
            var filter = /^(?:\b\w+\b[\s\r\n]*){1,3}$/;
            //if it's valid email
            if(filter.test(a)){
                study_question_cg.removeClass("error");
                study_question_error.addClass("hidden");
                study_question_cg.addClass("success");
                return true;
            }
            //if it's NOT valid
            else{
                study_question_cg.addClass("error");
                study_question_cg.removeClass("success");
                study_question_error.removeClass("hidden");
                return false;
            }
        }

        function validateStudyForm() {
            if(validate_study_name() & validate_study_question())
                return true
            else
                return false;
        }

function setupQuestions(qString) {
	var list = qString.split(",");
	var newStr = "[";
	for(var i =0;i<list.length;i++) {
		newStr+='"'+list[i]+'"';
		if(i<list.length-1)
			newStr+=',';
		else
			newStr+=']';
	}
	var questions = document.getElementById("study_question");
	alert(questions.placeholder);
	questions.data-source = newStr;
	//questions.data-items=""+list.length;
	alert("done");
/*
	document.getElementById("study_question").data-source = newStr;
	alert(document.getElementById("study_question").value);
	//document.getElementById("#study_question").data-source = newStr;
	document.getElementById("study_question").data-items = ""+list.length;
*/
}
function setupUI() {

    $('#clearCurrentSelection').click(clearOverlays);
    
    $('#finishStudyForm').click(function() {
        if (!mapReady) {
            alert("ERROR: Couldn't initialize Google Maps!");
            return;
        }
        
        if (validateStudyForm()) {
            $('#mapInterface').show();
            $('#createStudyForm').hide();
            $('#info-alert').html('<strong>Step 2 of 5:</strong><br />Now, select an area you want to study by drawing polygon on the map. To start, click any three places on the map.');
            $('#info').replaceWith('<li id="info"><a href="/admin/studies/"><i class="icon-book"></i> Study Information</a></li>');
            $('#define').replaceWith('<li id="define" class="active"><a href="/admin/studies/"><i class="icon-book icon-white"></i> Define Area</a></li>');
            //Replace Selected menu
            startMap();
        }
    });
    
    $('#submitPolygon').click(function() {
    if(area<500.0) {
        // Create a comma-separated list of numbers representing the polygon.
        // List is flattened, so (x1,y1),(x2,y2) becomes x1,y1,x2,y2 etc...
        var polyPath = poly.getPath().getArray();
        var polyArray = [];
        for (var polygonIdx = 0; polygonIdx < polyPath.length; polygonIdx++) {
            //replaced .Qa .Pa
            polyArray.push(polyPath[polygonIdx].lng());
            polyArray.push(polyPath[polygonIdx].lat());
        }
        updateDB();
    }
    else {
        alert("Please limit your polygon to less than 500 square miles in area.");
    }
    });
}

/*
    Map polygon chooser.
*/

function initialize() {
    // Gmaps callback happened.
    mapReady = true;
}

function startMap() {
    // Initialize map interface
    markers = [];
    path = new google.maps.MVCArray;
    markerIcon = '/static/images/blue.png';
    var varzoom = 10;
    panMap(varzoom);
}

function panMap(varzoom)
 {
    // var newLoc = new google.maps.LatLng(start);

    map = new google.maps.Map($('#map').get()[0], {
        zoom: varzoom,
        // center: newLoc,
        draggableCursor: 'crosshair',
        mapTypeId: google.maps.MapTypeId.HYBRID
    });

    poly = new google.maps.Polygon({
        strokeWeight: 2,
        strokeOpacity: 1,
        strokeColor: '#eeb44b',
        fillColor: '#eeb44b'
    });

    // var swpoint = new google.maps.LatLng(point.swlat, point.swlng); //Google adds lat then lng, even though lat is Y coord and Lng is X
    //     var nepoint = new google.maps.LatLng(point.nelat, point.nelng);
    //     var bounds = new google.maps.LatLngBounds(swpoint, nepoint);
    
    map.fitBounds(new google.maps.LatLngBounds(new google.maps.LatLng(7.188100871179058,-129.39241035029778),new google.maps.LatLng(55.07836723201517,-50.64241035029778) ));
    // map.fitBounds(bounds);

    // addPointLatLng(swpoint.lat(), swpoint.lng());
    // addPointLatLng(nepoint.lat(), swpoint.lng());
    // addPointLatLng(nepoint.lat(), nepoint.lng());
    // addPointLatLng(swpoint.lat(), nepoint.lng());

    poly.setMap(map);
    poly.setPaths(new google.maps.MVCArray([path]));

    google.maps.event.addListener(map, 'click', addPoint);
    google.maps.event.addListener(poly, 'click', addPoint);
}
/*
    Overlay stuff.
*/

function addPointLatLng(lat, lng) {
    var point = new google.maps.LatLng(lat, lng);
    // path.insertAt(path.length, point);
    var marker = new google.maps.Marker({
        position: point,
        map: map,
        draggable: true,
        icon: markerIcon
    });
    markers.push(marker);

    google.maps.event.addListener(marker, 'click',
    function() {
        marker.setMap(null);
        for (var i = 0, I = markers.length; i < I && markers[i] != marker; ++i);
        markers.splice(i, 1);
        path.removeAt(i);
    updateArea();
    }
    );

    google.maps.event.addListener(marker, 'dragend',
    function() {
        for (var i = 0, I = markers.length; i < I && markers[i] != marker; ++i);
        path.setAt(i, marker.getPosition());
    updateArea();
    }

    );
}
function clearOverlays() {
    for (var m = 0; m < markers.length; m) {
        google.maps.event.trigger(markers[0], 'click');
    }
    poly.setOptions({
    strokeWeight: 2,
        strokeOpacity: 1,
        strokeColor: '#eeb44b',
        fillColor: '#eeb44b'
    });
    

}
function removeMarker(index) {
    if (markers.length > 0) {
        //clicked marker has already been deleted
        if (index != markers.length) {
            markers[index].setMap(null);
            markers.splice(index, 1);
        } else {
            markers[index - 1].setMap(null);
            markers.splice(index - 1, 1);
        }
    }
    index = null;
};
function addPoint(event) {
    var minDist = 0;
    var minPlace;
    var midPt = [];

    for (var i = 0, I = markers.length; i < I; ++i) {
        currPos = markers[i].getPosition();
        nextPt = (i + 1 < I) ? i + 1: 0;
        nextPos = markers[nextPt].getPosition();
        midPt[i] = new google.maps.LatLng((currPos.lat() + nextPos.lat()) / 2, (currPos.lng() + nextPos.lng()) / 2);

        var currDistance = getDistance(event.latLng, midPt[i]);
        if (minDist == 0 || currDistance < minDist) {
            minDist = currDistance;
            minPlace = i;
        }
    }

    var marker = new google.maps.Marker({
        position: event.latLng,
        map: map,
        draggable: true,
        icon: markerIcon
    });
    var next = minPlace + 1;
    markers.splice(next, 0, marker);
    path.insertAt(next, event.latLng);
    updateArea();    

    google.maps.event.addListener(marker, 'click',
    function() {
        marker.setMap(null);
        for (var i = 0, I = markers.length; i < I && markers[i] != marker; ++i);
        markers.splice(i, 1);
        path.removeAt(i);
    updateArea();
    }
    );

    google.maps.event.addListener(marker, 'dragend',
    function() {
        for (var i = 0, I = markers.length; i < I && markers[i] != marker; ++i);
        path.setAt(i, marker.getPosition());
    updateArea();
    }
    );
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

function saveCity() {
    var index = document.getElementById('dropDownList').selectedIndex;
    if(index==0)
    {
        var city_name = prompt("What is the name of the city?");
        if(city_name!=null && city_name!="")
        {
            updateDB(city_name);
        }
        else
        {
            alert("Please enter a name or choose one from the list.");
        }
    }
    else
    {
        updateDB(cityList[index-1]);
    }

}

function updateDB() {
        var polyPath = poly.getPath().getArray();
        var polyArray = [];
        for (var polygonIdx = 0; polygonIdx < polyPath.length; polygonIdx++) {
            polyArray.push(polyPath[polygonIdx].lng());
            polyArray.push(polyPath[polygonIdx].lat());
        }
    $.ajax({
            url:'/study/create/',
            // Expect JSON to be returned. This is also enforced on the server via mimetype.
            dataType: 'json',
            data: {
                polygon: polyArray.toString(),
                study_name: $('#study_name').val(),
                study_question: $('#study_question').val(),
                study_public: $('input:radio[name=study_public]:checked').val(),
                data_resolution: $('#data_resolution').val(),
                location_distribution: $('#location_distribution').val()
            },
            type: 'POST',
            success: function(data) {
                window.location.replace(window.location.protocol + '//' + window.location.host + "/study/populate/" + data.studyID);
            }
        });
}

function updateArea() {
    if(poly.getPath().length>2) {
        var numMetersInSquareMile = Math.pow(5280.0*12*2.54/100,2);
        area =  google.maps.geometry.spherical.computeArea(poly.getPath())/numMetersInSquareMile;
        if(area>500.0) {
            $('#area').html(area.toFixed(3)+" square miles is above the limit of 500 ");
            poly.setOptions({strokeColor: '#d70f37',fillColor:'#d70f37'});
            toggleMarkers('/static/images/red.png');
            $('#selectionarea').html('<strong>Selection Too Large</strong><br />Your current selection area is ' + area.toFixed(0) + ' square miles. Please reduce the area of your selection to under 500 square miles.')
            $('#selectionarea').show();
        }
        else { 
            poly.setOptions({strokeColor: '#9fe732',fillColor:'#9fe732'});
            toggleMarkers('/static/images/blue.png');
            $('#selectionarea').hide();
        }
    }
    else {
    area=0.0;
    $('#area').html(area);
    }
}

function toggleMarkers(markerIcon) {
    for(var i=0;i<markers.length;i++)
        markers[i].setIcon(markerIcon);
}
/*
    Distance math.
*/
function rad(x) {
    return x * Math.PI / 180;
}
function getDistance(start, end) {
    //3959mi 6371km
    return 6731 * 2 * Math.asin(Math.sqrt(Math.pow(Math.sin((start.lat() - end.lat()) * Math.PI / 180 / 2), 2) + Math.cos(start.lat() * Math.PI / 180) * Math.cos(end.lat() * Math.PI / 180) * Math.pow(Math.sin((start.lng() - end.lng()) * Math.PI / 180 / 2), 2)));
}
