var citydata = [
["Amsterdam",92.15,637],
["Atlanta",554.69,4059],
["Bangkok",217.96,1617],
["Barcelona",223.35,1443],
["Belo Horizonte",235.52,1969],
["Berlin",523.4,3987],
["Boston",188.95,1333],
["Bratislava",98.16,640],
["Bucharest",328.95,2169],
["Cape Town",393.64,2515],
["Chicago",444.81,3223],
["Copenhagen",69.85,506],
["Denver",328.89,2409],
["Dublin",228.15,1573],
["Gaborone",104.04,715],
["Glasgow",133.14,951],
["Guadalajara",215.87,1552],
["Helsinki",99.33,688],
["Hong Kong",78,633],
["Houston",414.43,3086],
["Johannesburg",270.26,1871],
["Kiev",124,891],
["Kyoto",65.14,729],
["Lisbon",260.97,1890],
["London",368.38,2688],
["Los Angeles",178.09,1294],
["Madrid",315,2158],
["Melbourne",379.7,2726],
["Mexico City",305.15,2103],
["Milan",249.96,1723],
["Minneapolis",118.93,844],
["Montreal",373.04,2625],
["Moscow",452.61,2893],
["Munich",347.05,2238],
["New York",470.26,3411],
["Paris",331.49,2484],
["Philadelphia",387.87,2790],
["Portland",247.65,1937],
["Prague",237.29,1743],
["Rio De Janeiro",513.05,3684],
["Rome",336.3,2182],
["San Francisco",137.13,1027],
["Santiago",484.46,3500],
["Sao Paulo",426.3,2982],
["Seattle",209.02,1510],
["Singapore",382.45,2616],
["Stockholm",162.34,1179],
["Sydney",442.34,3371],
["Taipei",189.37,1387],
["Tel Aviv",69.6,640],
["Tokyo",450.42,3795],
["Toronto",417.12,3308],
["Valparaiso",42.73,428],
["Warsaw",392.47,3002],
["Washington DC",115.97,954],
["Zagreb",142.21,1082]
]

for(var i=0; i<citydata.length; i++) {
  var htmlstr = '<div class="row" style="padding-bottom:30px; border-bottom: 1px dashed black; padding-top:30px;">'
      +'<div class="span6" style="width:100%;"><div class="cityinfo"><p class="cityname">'+citydata[i][0]+'</p>'
      +'<br><br><p><b>Area: '+citydata[i][1]+' sq km</b></p><br><p><b>Images: 1617</b></p><br>'
      +'<p><b>Images per sq km: '+citydata[i][2]+'</b></p></div><img class="citypic" src="/static/img/map_bounds/'+
      citydata[i][0].replace(/ /g,'')+'.png"/></div></div>';
    $('#newcities').append(htmlstr);
}