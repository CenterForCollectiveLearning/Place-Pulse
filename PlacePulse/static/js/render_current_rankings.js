function plotLine(container, width, height, data, question) {
  data.forEach(function (d) {
    d.x = d.trueskill.mean;
  });  

  data.sort(function(d1,d2){return d1.trueskill.mean - d2.trueskill.mean});
  var svg = container.append("svg")
    .attr("width", width)
    .attr("height", height)
  

  //first add the labels on the side
  
  // right label
  var sidelabel = svg.append("text");
  sidelabel.text("More " + question).attr("class", "sidelabel")
  var bBox = sidelabel[0][0].getBBox();
  var rightMargin = bBox.width;
  sidelabel.attr("x", width-bBox.width).attr("y", height/2).attr("dy", "-15px");
  //left label
  sidelabel = svg.append("text");
  sidelabel.text("Less " + question).attr("class", "sidelabel")
  var bBox = sidelabel[0][0].getBBox();
  var leftMargin = bBox.width;
  sidelabel.attr("x", 0).attr("y", height/2).attr("dy", "-15px");


  // add the middle line
  //var g = svg.append("g").attr("transform", "translate(" + marginLeft + "," + margin.top + ")");

  var xExtent = d3.extent(data, function(d){ return d.x;});
  //var color = d3.scale.linear().domain([1, 5.5, 10]).range(["blue", "white", "red"]);
  var xscale = d3.scale.linear().domain(xExtent).range([leftMargin+25, width-rightMargin-25]);

  svg.append("line")
    .attr("x1",0)
    .attr("x2",width)
    .attr("y1",height/2)
    .attr("y2",height/2)

  var g = svg.append("g")
  var yshift = function(d, i, isText) {
    var tmp = height/2 + Math.pow(-1,i%2)*((i%7)+1)*15;
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
   .attr("cx", function(d) {return xscale(d.x)})
   .attr("cy", height/2)
   .attr("r", 5);

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
   .attr("y1",function(d,i) { return yshift(d,i, true)})
   .attr("y2",function(d,i) { return height/2 + Math.pow(-1,i%2)*5})
}


var width = 940;
var height = 270;

var studyid2question = {
  "50a68a51fdc9f05596000002": "safe",
  "50f62c41a84ea7c5fdd2e454": "lively",
  "50f62c68a84ea7c5fdd2e456": "boring",
  "50f62cb7a84ea7c5fdd2e458": "wealthy",
  "50f62ccfa84ea7c5fdd2e459": "depressing"
}
var studyid2data = {};
var loaded = 0;

//load all the data
for (var studyid in studyid2question) {
  (function(studyid) {
    d3.json("/study/" + studyid + "/getcityrank/", function(error, data) {
      studyid2data[studyid] = data;
      loaded+=1;
      if (loaded == 5) {
        render();
      }
    });
  })(studyid);
}

function render() {
  for (var studyid in studyid2question) {
    plotLine(d3.select("#ongoing_stats"), width, height, studyid2data[studyid], studyid2question[studyid]);
  }
}