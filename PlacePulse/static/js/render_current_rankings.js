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
    for(var j=0;j<_results[i].data.length;j++) {
      if(i==0)
        rows[_results[i].data[j].place_name] = {};
      var this_study = _studies[_results[i].study];
      rows[_results[i].data[j].place_name][this_study] = _results[i].data[j]['trueskill']['score'];
    }
  }
  for(var key in rows) {
    //construct a row
    var newrow = '<tr class="rankingrow"><td class="citycell">'+key+'</td><td class="scorecell">'+parseFloat((rows[key]["boring"]).toFixed(3))+'</td><'+
      'td class="scorecell">'+parseFloat((rows[key]["depressing"]).toFixed(3))+'</td><td class="scorecell">'+parseFloat((rows[key]["livelier"]).toFixed(3))+'</td><'+
      '<td class="scorecell">'+parseFloat((rows[key]["safer"]).toFixed(3))+'</td><td class="scorecell">'+parseFloat((rows[key]["wealthier"]).toFixed(3))+'</td></tr>';
    $('#rankings_table > tbody:last').append(newrow);
  }

  $('#rankings_table').tablesorter({sortList: [[5,1]]});
}