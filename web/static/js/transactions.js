function on_ready(){
    chart = new Highcharts.Chart({
        chart: {
            renderTo: 'container',
            type: 'bar'
        },
        title: {
            text: 'Expenses '+startdate+ ' - '+ enddate
        },
        subtitle: {
            text: 'Source: Commbank statements'
        },
        xAxis: {
            categories: categories,
            title: {
                text: null
            }
        },
        yAxis: {
            min: 0,
            title: {
                text: 'Dollars (AUD)',
                align: 'high'
            }
        },
        tooltip: {
            formatter: function() {
                return ''+
                    this.series.name +': '+ this.y +' AUD';
            }
        },
        plotOptions: {
            bar: {
                dataLabels: {
                    enabled: true
                }
            }
        },
        legend: {
            layout: 'vertical',
            align: 'right',
            verticalAlign: 'top',
            x: -100,
            y: 100,
            floating: true,
            borderWidth: 1,
            backgroundColor: '#FFFFFF',
            shadow: true
        },
        credits: {
            enabled: false
        },
        series: [{
            name: 'Transactions',
            data: series_data
        }]
    });
}
var chart;
$(document).ready(on_ready);
