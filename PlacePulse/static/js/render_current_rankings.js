$.ajax({
    url:'/getstudies/',
    type: 'GET',
    success: function(data) {
      var studies = [];
      for(var i=0; i<data.length; i++) {
        var abbr_q = data[i].study_question.split(" ");
        if(abbr_q.length > 1)
          studies[data[i]._id] = abbr_q[1];
        else
          studies[data[i]._id] = abbr_q[0];
      }
      getallstats(studies);
    }
  });

function getallstats(_studies) {
  var results = [];

  for(var key in _studies) {
    $.ajax({
      url:'/study/'+key+'/getcityrank',
      type:'GET',
      success: function(data) {
        results.push({'study': data[0].study_id, 'data': data});
        if(results.length == 5)
          consolidate_results(results, _studies);
      }
    });
  }
}

function consolidate_results(_results, _studies) {
  var rows = {};

  for(var i=0;i<_results.length;i++) {
    var len = _results[i].data.length;
    var min = _results[i].data[len-1]['trueskill']['score'];
    var max = _results[i].data[0]['trueskill']['score'];
    for(var j=0;j<len;j++) {
      if(i==0) {
        rows[_results[i].data[j].place_name] = {};
      }
      var this_study = _studies[_results[i].study];
      rows[_results[i].data[j].place_name][this_study] = {};
      var stdev_l = _results[i].data[j]['trueskill']['stds'].length;
      if(max!=min) {
        // normalizing scores between 1-10
        rows[_results[i].data[j].place_name][this_study]['score'] = (((_results[i].data[j]['trueskill']['score'] - min) / (max-min))*9)+1;
        var new_stdev = _results[i].data[j]['trueskill']['stds'][stdev_l-1]*rows[_results[i].data[j].place_name][this_study]['score']/_results[i].data[j]['trueskill']['score'];
        rows[_results[i].data[j].place_name][this_study]['stdev'] = parseFloat(new_stdev).toFixed(3);
        rows[_results[i].data[j].place_name][this_study]['score'] = parseFloat(rows[_results[i].data[j].place_name][this_study]['score']).toFixed(3);
      }
      else {
        rows[_results[i].data[j].place_name][this_study]['score'] = 1;
        var new_stdev = _results[i].data[j]['trueskill']['stds'][stdev_l-1]/_results[i].data[j]['trueskill']['score'];
        rows[_results[i].data[j].place_name][this_study]['stdev'] = parseFloat(new_stdev).toFixed(3);
      }
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