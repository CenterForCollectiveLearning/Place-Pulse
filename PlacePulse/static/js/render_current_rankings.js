var studyid2question = {
  "50a68a51fdc9f05596000002": ["Less safe", "More safe", 1],
  "50f62c41a84ea7c5fdd2e454": ["Less lively", "More lively", 1],
  "50f62c68a84ea7c5fdd2e456": ["More boring", "Less boring", -1],
  "50f62cb7a84ea7c5fdd2e458": ["Less wealthy", "More wealthy", 1],
  "50f62ccfa84ea7c5fdd2e459": ["More depressing", "Less depressing", -1]
}

$.ajax({
    url:'/getstudies/',
    type: 'GET',
    success: function(data) {
      var studies = [];
      for(var i=0; i<data.length; i++) {
        if(studyid2question[data[i]['_id']] === undefined) {
          continue;
        }
        var abbr_q = data[i].study_question.split(" ");
        if(abbr_q.length > 1)
          studies[data[i]._id] = abbr_q[1];
        else
          studies[data[i]._id] = abbr_q[0];
      }
      getallstats(studies);
    }
  });

var studyid2data = {};
function getallstats(_studies) {
  var results = [];

  for(var key in _studies) {
    $.ajax({
      url:'/study/'+key+'/getcityrank',
      type:'GET',
      success: function(data) {
        results.push({'study': data[0].study_id, 'data': data});
        studyid2data[data[0].study_id] = data;
        if(results.length == 5) {
          consolidate_results(results, _studies);
          render();
        }
      }
    });
  }
}

function consolidate_results(_results, _studies) {
  var rows = {};
  for(var i=0;i <_results.length; i++) {
    var len = _results[i].data.length;
    for(var j=0;j<len;j++) {
      if (rows[_results[i].data[j].place_name] === undefined) { rows[_results[i].data[j].place_name] = {};}
      var this_study = _studies[_results[i].study];
      if (rows[_results[i].data[j].place_name][this_study] === undefined) { rows[_results[i].data[j].place_name][this_study] = {}; }
      var stdev_l = _results[i].data[j]['trueskill']['stds'].length;
      rows[_results[i].data[j].place_name][this_study]['score'] = _results[i].data[j]['trueskill']['mean'].toFixed(2)
      rows[_results[i].data[j].place_name][this_study]['stdev'] = _results[i].data[j]['trueskill']['std'].toFixed(2)
    }
  }
  var k=1;
  for(var key in rows) {
    //construct a row
    var newrow = '<tr class="rankingrow"><td class="citycell">'+key+
      '</td><td class="scorecell">'+rows[key]["boring"]["score"]+'</td>'+
      '<td class="scorecell">'+rows[key]["boring"]["stdev"]+'</td>'+
      '<td class="scorecell">'+rows[key]["depressing"]["score"]+'</td>'+
      '<td class="scorecell">'+rows[key]["depressing"]["stdev"]+'</td>'+
      '<td class="scorecell">'+rows[key]["livelier"]["score"]+'</td>'+
      '<td class="scorecell">'+rows[key]["livelier"]["stdev"]+'</td>'+
      '<td class="scorecell">'+rows[key]["safer"]["score"]+'</td>'+
      '<td class="scorecell">'+rows[key]["safer"]["stdev"]+'</td>'+
      '<td class="scorecell">'+rows[key]["wealthier"]["score"]+'</td>'+
      '<td class="scorecell">'+rows[key]["wealthier"]["stdev"]+'</td>'+'</tr>';
    $('#rankings_table > tbody:last').append(newrow);

    var newserial = '<tr><td class="numcell">'+k+'. </td></tr>';
    $('#serialnum_table > tbody:last').append(newserial);
    k++;
  }

  $('#rankings_table').tablesorter({ sortList: [[5,1]] });
}

function hoverOverCity(d) {
  console.log(d.place_name)
}

function plotLine(container, width, height, data, question) {
  data.forEach(function (d) {
    d.x = d.trueskill.mean;
  });  

  data.sort(function(d1,d2){return d1.trueskill.mean - d2.trueskill.mean});
  var svg = container.append("svg")
    .attr("width", width)
    .attr("height", height)
  

  //first add the labels on the side
  //left label
  var sidelabel = svg.append("text");
  sidelabel.text(question[0]).attr("class", "sidelabel")
  var bBox = sidelabel[0][0].getBBox();
  var leftMargin = bBox.width + 30;
  sidelabel.attr("x", 0).attr("y", height/2 + bBox.height/4.0);
  
  // right label
  sidelabel = svg.append("text");
  sidelabel.text(question[1]).attr("class", "sidelabel")
  var bBox = sidelabel[0][0].getBBox();
  var rightMargin = bBox.width + 30;
  sidelabel.attr("x", width-bBox.width).attr("y", height/2 + bBox.height/4.0);
  

  var xExtent = d3.extent(data, function(d){ return d.x;});
  //var color = d3.scale.linear().domain([1, 5.5, 10]).range(["blue", "white", "red"]);
  var xscale = d3.scale.linear().domain(xExtent);
  if(question[2] === -1) {
    xscale.range([width-rightMargin, leftMargin]);
  } else {
    xscale.range([leftMargin, width-rightMargin]);
  }

  var stdevExtent = d3.extent(data, function (d) { return d.trueskill.std; });
  var radius = d3.scale.linear().domain(stdevExtent).range([2, 10]);
  svg.append("line")
    .attr("x1",leftMargin)
    .attr("x2",width - rightMargin)
    .attr("y1",height/2)
    .attr("y2",height/2)

  var g = svg.append("g")
  var yshift = function(d, i, isText) {
    var tmp = height/2 + Math.pow(-1,i%2)*((i%9)+1)*13;
    if(isText) {
      if(i%2) { tmp += 3; }
      else { tmp-=10; }
    }
    return tmp;
  };

  g.selectAll("circle")
   .data(data)
   .enter()
   .append("circle")
   .attr("fill", function(d) {return "#ea4839"})
   .attr("stroke", '#999')
   .attr("opacity", "0.5")
   .attr("cx", function(d) {return xscale(d.x)})
   .attr("cy", height/2)
   .attr("r", function (d) {return radius(d.trueskill.std);})
   .on("mouseover", hoverOverCity);

  g.selectAll("text")
   .data(data)
   .enter()
   .append("text")
   .text(function(d) { return d.place_name; })
   .attr("x", function(d) { return xscale(d.x) })
   .attr("y", function(d,i) { return yshift(d,i, false)})
   .attr("text-anchor", "middle")
   .attr("class", "citylabel")

  g.selectAll("line")
   .data(data)
   .enter()
   .append("line")
   .attr("x1",function(d) { return xscale(d.x)})
   .attr("x2",function(d) { return xscale(d.x)})
   .attr("y1",function(d,i) { return yshift(d, i, true)})
   .attr("y2",function(d,i) { return height/2 + Math.pow(-1,i%2)*radius(d.trueskill.std)})
}


var width = 940;
var height = 280;

function render() {
  for (var studyid in studyid2question) {
    plotLine(d3.select("#ongoing_stats"), width, height, studyid2data[studyid], studyid2question[studyid]);
  }
}