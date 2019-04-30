$(function(){
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

    $(document).ready(function() {
        $('#datum').change(function(){
            update_chart(scatterChart);
        });

        $('#pv_modul').change(function(){
            update_chart(scatterChart);
        });

        $('#mess_reihe').change(function(){
            update_chart(scatterChart);
        });
    });
});

function update_chart(chart) {
    chosen_values = getArgumentsFromSelectFields();
    console.log(chosen_values);

    $.getJSON('/_query_results',
        {
        date: chosen_values.date,
        measurement_series: chosen_values.meas_series,
        pv_module_id: chosen_values.model_id
        },
            function(json){
                console.log(json);
                let data_U_P = json[0]['data_u_p']
                let data_U_I = json[0]['data_u_i']

                let chart_data = {'datasets':   [{'label':   'U',
                                                'xAxisID': 'ax_U',
                                                'yAxisID': 'ax_I',
                                                'data':    data_U_I,
                                                'borderColor': 'rgba(75, 192, 192, 1)',},
                                               {'type': 'line',
                                                'label':   'P',
                                                'xAxisID': 'ax_U',
                                                'yAxisID': 'ax_P',
                                                'data':    data_U_P,
                                                'borderColor': 'rgba(153, 102, 255, 1)'}]
                                 };
                chart.data = chart_data;
                chart.update();
        })
        .fail(function() {
            console.log('error');
        });
};
function getArgumentsFromSelectFields(){
    let a = document.getElementById('mess_reihe')
    let chosen_meas_series = a.options[a.selectedIndex].text

    let b = document.getElementById('datum')
    let chosen_date = b.options[b.selectedIndex].text

    let c = document.getElementById('pv_modul')
    let chosen_model_id = c.options[c.selectedIndex].value

    return {
        meas_series : chosen_meas_series,
        date : chosen_date,
        model_id : chosen_model_id,
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

function test_chart(chart)
{
    chart.title = 'Awesome change';
    chart.update();
}