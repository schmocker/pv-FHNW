$(function () {
    let ctx = document.getElementById('myChart').getContext('2d');
    let scatterChart = new Chart(ctx, {
        type: 'bubble',
        data: chart_data,
        options: {
            scales: {
                xAxes: [{
                    type: 'linear',
                    position: 'bottom',
                    id: 'ax_U',
                    scaleLabel: {
                        display: true,
                        labelString: "Spannung U [V]",
                    }
                }],
                yAxes: [{
                    type: 'linear',
                    position: 'left',
                    id: 'ax_I',
                    scaleLabel: {
                        display: true,
                        labelString: 'Strom I [A]'
                    }
                }, {
                    type: 'linear',
                    display: true,
                    id: 'ax_P',
                    position: 'right',
                    reverse: true,
                    scaleLabel: {
                        display: true,
                        labelString: "Leistung P [W]",
                    },

                    // grid line settings
                    gridLines: {
                        drawOnChartArea: false, // only want the grid lines for one axis to show up
                    },
                }]
            }, tooltips: {
                callbacks: {
                    title: function (tooltipItem, data) {
                        return data['datasets'][tooltipItem[0].datasetIndex]['label'];
                    },
                    label: function (tooltipItem, data) {
                        let y_unit = 'A';
                        if (data['datasets'][tooltipItem.datasetIndex].yAxisID == 'ax_P'){
                            y_unit = 'W';
                        }
                        return data['datasets'][0].data[tooltipItem['index']].x + ' V / ' +
                            data['datasets'][0].data[tooltipItem['index']].y + ' ' + y_unit;
                    },
                    afterLabel: function (tooltipItem, data) {
                        return null
                    }
                },
                // backgroundColor: '#FFF',
                // titleFontSize: 16,
                // titleFontColor: '#0066ff',
                // bodyFontColor: '#000',
                // bodyFontSize: 14,
                // displayColors: false
            }
        },
        showLine: true
    });
});
function test_change(word){
    console.log(word);
    let select_word = document.getElementById(word)

    $.getJSON($SCRIPT_ROOT + '/_query_results',
    {
    date:"test",
    meas_series:"testy"
    },
        function(json){
            console.log("Success");
            console.log(json[1]);
    });

}