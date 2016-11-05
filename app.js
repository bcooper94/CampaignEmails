'use strict';

var graph = function (serverData) {
    Highcharts.chart('container', {
        chart: {
            type: 'bubble',
            plotBorderWidth: 1,
            zoomType: 'xy'
        },
        legend: {
            enabled: false // IDK what this does
        },
        title: {
            text: 'Polling Percentage vs Volume of Emails Over Time'
        },
        subtitle: {
            text: ''
        },
        xAxis: {
            gridLineWidth: 1,
            title: {
                text: 'Month'
            },
            plotLines: [{
                color: 'red',
                dashStyle: 'solid',
                width: 1,
                value: 5,
                label: {
                    rotation: 0,
                    text: 'Republican Primary'
                },
                zIndex: 3
            }, {
                color: 'blue',
                dashStyle: 'solid',
                width: 1,
                value: 6,
                label: {
                    rotation: 0,
                    text: 'Democratic Primary'
                },
                zIndex: 3
            }],
            // Options added by us
            categories: [
               'Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct'
            ]
        },
        yAxis: {
            title: {
                text: 'Polling Percentage'
            },
            labels: {
                format: '{value}%'
            }
        },
        tooltip: {
            useHTML: true,
            headerFormat: '<div>',
            pointFormatter: function () {
               return `
                  <h2> ${this.candidate} </h2>
                  <p> Month: ${this.x + 1} </p>
                  <p> Polling: ${this.y + 1}% </p>
                  <p> Email Count: ${this.z + 1} </p>
               `
            },
            footerFormat: '</div>',
            followPointer: true
        },
        plotOptions: {
            series: {
                dataLabels: {
                    enabled: true,
                    format: '{point.candidate}'
                }
            }
        },
        series: [{
            data: serverData 
        }]
    });
};

var main = function () {
   var request = new XMLHttpRequest();
   request.addEventListener('load', function (evt) {
      console.log(JSON.parse(request.responseText));
      graph(JSON.parse(request.responseText));
   });
   request.open('GET', './data.json', true);
   request.send();
};

window.addEventListener('load', main);
