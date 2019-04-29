$(function(){
    update_chart();
});
function update_chart() {
    let ctx = document.getElementById('myChart').getContext('2d');

    chosen_values = getArgumentsFromDropdown();

    $.getJSON($SCRIPT_ROOT + '/_query_results',
        {
        date: chosen_values.date,
        measurement_series: chosen_values.meas_series
        },
            function(json){
                let data_U_P = json[0]['data_u_p']
                let data_U_I = json[0]['data_u_i']

                let chart_data = {'datasets': [{'label':   'U',
                                'xAxisID': 'ax_U',
                                'yAxisID': 'ax_I',
                                'data':    data_U_I,
                                'borderColor':  '[rgba(8,8,251,1)]'},
                               {'type': 'line',
                                'label':   'P',
                                'xAxisID': 'ax_U',
                                'yAxisID': 'ax_P',
                                'data':    data_U_P,
                                'borderColor': '[rgba(255,99,132,0.2)]'}
                               ]};

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
};
function getArgumentsFromDropdown(){
    let a = document.getElementById('mess_reihe')
    let chosen_meas_series = a.options[a.selectedIndex].text

    let b = document.getElementById('datum')
    let chosen_date = b.options[b.selectedIndex].text

    let c = document.getElementById('pv_modul')
    let chosen_model = c.options[c.selectedIndex].text

    return {
        meas_series : chosen_meas_series,
        date : chosen_date,
        model : chosen_model,
    }
}
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