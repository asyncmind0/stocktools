                   var seriesData = [];
                   var random = new Rickshaw.Fixtures.RandomData(150);
                   var colors = ["#c05020", "#6060c0"];
                   for(var sym in quotes){
                       var data = []
                       var symData = quotes[sym];
                       for (var i = 0; i < symData.length; i++) {
	                   data.push(
                               {x: d3.time.format("%Y%m%d")
                                .parse(symData[i][1].toString()).getTime(),
                                y: symData[i][3]});
                       }
                       seriesData.push({
                           color: colors.pop(),
                           name: sym,
                           data: data});
                   }

                   // instantiate our graph!

                   var graph = new Rickshaw.Graph( {
	               element: document.getElementById("chart"),
	               width: 960,
	               height: 500,
	               renderer: 'line',
	               series: seriesData
                   } );

                   graph.render();

                   var hoverDetail = new Rickshaw.Graph.HoverDetail( {
	               graph: graph
                   } );

                   var legend = new Rickshaw.Graph.Legend( {
	               graph: graph,
	               element: document.getElementById('legend')

                   } );

                   var shelving = new Rickshaw.Graph.Behavior.Series.Toggle( {
	               graph: graph,
	               legend: legend
                   } );

                   var axes = new Rickshaw.Graph.Axis.Time( {
	               graph: graph,
                   } );
                   axes.render();
