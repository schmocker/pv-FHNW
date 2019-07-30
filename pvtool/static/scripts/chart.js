$(function(){
    let ctx = document.getElementById('myChart').getContext('2d');

    let scatterChart = new Chart(ctx, {
                    type: 'line',
                    data: chart_data,
                    options: {
                        legend: {position: 'right'},
                        scales: {
                            xAxes: [{
                                type: 'linear',
                                position: 'bottom',
                                id: 'ax_U',
                                scaleLabel: {
                                    display: true,
                                    labelString: "Spannung U [V]",
                                },
                                ticks: {
                                    beginAtZero: true
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
                            },
                            {
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
                        },
//                        tooltips: {
//                            callbacks: {
//                                title: function (tooltipItem, data) {
//                                    return data['datasets'][tooltipItem[0].datasetIndex]['label'];
//                                },
//                                label: function (tooltipItem, data) {
//                                    let y_unit = 'A';
//                                    if (data['datasets'][tooltipItem.datasetIndex].yAxisID == 'ax_P'){
//                                        y_unit = 'W';
//                                    }
//                                    return data['datasets'][0].data[tooltipItem['index']].x + ' V / ' +
//                                        data['datasets'][0].data[tooltipItem['index']].y + ' ' + y_unit;
//                                },
//                                afterLabel: function (tooltipItem, data) {
//                                    return null
//                                }
//                            },
//                        }
                    },
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

    $.getJSON('/_query_results',
        {
        date: chosen_values.date,
        measurement_series: chosen_values.meas_series,
        pv_module_id: chosen_values.model_id,
        stc_temp : chosen_values.stc_temp,
        stc_rad : chosen_values.stc_rad
        },
            function(json){
                console.log(json);
                let data_U_P = json['data_u_p']
                let data_U_I = json['data_u_i']

                let data_U_P_STC = json['data_u_p_stc']
                let data_U_I_STC = json['data_u_i_stc']

                let chart_data = {datasets: [{label:   'Messung U-I',
                                                xAxisID: 'ax_U',
                                                yAxisID: 'ax_I',
                                                data:    data_U_I,
                                                borderColor: 'rgba(75, 192, 192, 1)',
                                                options: '{elements: {point:{radius: 3}},}',
                                                type: 'bubble',
                                                },
                                               {
                                                label:   'Messung U-P',
                                                xAxisID: 'ax_U',
                                                yAxisID: 'ax_P',
                                                data:    data_U_P,
                                                borderColor: 'rgba(153, 102, 255, 1)',
                                                type: 'bubble',
                                                },
                                                {label:   'Messung U-I in STC',
                                                xAxisID: 'ax_U',
                                                yAxisID: 'ax_I',
                                                data:    data_U_I_STC,
                                                borderColor: 'rgba(7, 19, 192, 1)',
                                                options: '{elements: {point:{radius: 3}},}',
                                                type: 'bubble',
                                                },
                                               {
                                                label:   'Messung U-P in STC',
                                                xAxisID: 'ax_U',
                                                yAxisID: 'ax_P',
                                                data:    data_U_P_STC,
                                                borderColor: 'rgba(15, 12, 25, 1)',
                                                type: 'bubble',
                                                },

                                               {label: "Hersteller U-I",
                                                function: function(x){ return voltage_current_function_manufacturer(x,json)},
                                                borderColor: "rgba(20, 12, 192, 1)",
                                                data: [],
                                                xAxisID: 'ax_U',
                                                yAxisID: 'ax_I',
                                                type: 'line',
                                                radius: '0',
                                                fill: 'false',
                                                },

                                                {label: "Hersteller U-P",
                                                function: function(x){ return voltage_power_function_manufacturer(x,json)},
                                                borderColor: "rgba(1, 1, 1, 1)",
                                                data: [],
                                                xAxisID: 'ax_U',
                                                yAxisID: 'ax_P',
                                                type: 'line',
                                                radius: '0'  ,
                                                fill: 'false',
                                                },
                                                {label: "Flasher U-I",
                                                function: function(x){ return voltage_current_function_flasher(x,json)},
                                                borderColor: "rgba(191, 63, 74, 1)",
                                                data: [],
                                                xAxisID: 'ax_U',
                                                yAxisID: 'ax_I',
                                                type: 'line',
                                                radius: '0',
                                                fill: 'false',
                                                },

                                                {label: "Flasher U-P",
                                                function: function(x){ return voltage_power_function_flasher(x,json)},
                                                borderColor: "rgba(251, 255, 15, 1)",
                                                data: [],
                                                xAxisID: 'ax_U',
                                                yAxisID: 'ax_P',
                                                type: 'line',
                                                radius: '0'  ,
                                                fill: 'false',
                                                },
                                                {label: "Flasher U-I in STC",
                                                function: function(x){ return voltage_current_function_flasher_stc(x,json)},
                                                borderColor: "rgba(50, 53, 20, 1)",
                                                data: [],
                                                xAxisID: 'ax_U',
                                                yAxisID: 'ax_I',
                                                type: 'line',
                                                radius: '0',
                                                fill: 'false',
                                                },

                                                {label: "Flasher U-P in STC",
                                                function: function(x){ return voltage_power_function_flasher_stc(x,json)},
                                                borderColor: "rgba(21, 255, 255, 1)",
                                                data: [],
                                                xAxisID: 'ax_U',
                                                yAxisID: 'ax_P',
                                                type: 'line',
                                                radius: '0'  ,
                                                fill: 'false',
                                                },
                                                ]
                                 };
                Chart.pluginService.register({
                    beforeUpdate: function(chart) {
                        var data = chart.config.data;
                        var volt_vector = [];

                        for (var i = 0; i < data_U_I.length; i++)
                        {
                            volt_vector.push(data_U_I[i]['x']);
                        }
                        var min_volt = 0;//Math.min.apply(null,volt_vector);
                        var max_volt = get_intersection_with_x_axis(json);//Math.max.apply(null,volt_vector);

                        var increment = (max_volt-min_volt)/100;

                        for(var i = 4; i <= 9; i++)
                        {
                            var result = [];
                            for( var j = 0; j<100; j++)
                            {
                                var fct = data.datasets[i].function,
                                x = (min_volt + j*increment),
                                y = fct(x);
                                result.push({'x':x,'y':y});
                            }
                            data.datasets[i].data = result;
                        }
                    }
                });
                chart.data = chart_data;
                chart.update();
        })
        .fail(function() {
            console.log('query to obtain measurement values failed');
        });
};

function getArgumentsFromSelectFields(){
    let a = document.getElementById('mess_reihe')
    let chosen_meas_series = a.options[a.selectedIndex].text

    let b = document.getElementById('datum')
    let chosen_date = b.options[b.selectedIndex].text

    let c = document.getElementById('pv_modul')
    let chosen_model_id = c.options[c.selectedIndex].value
//    let stc_temp = document.getElementById('stc_temp').value
//
//    let stc_rad = document.getElementById('stc_rad').value

    return {
        meas_series : chosen_meas_series,
        date : chosen_date,
        model_id : chosen_model_id,
//        stc_temp : stc_temp,
//        stc_rad : stc_rad
    }
}

function voltage_current_function_manufacturer(x,json)
{
    let i_sc = json['manufacturer_data']['_I_sc_m'];
    let i_mpp = json['manufacturer_data']['_I_mpp_m'];
    let u_oc = json['manufacturer_data']['_U_oc_m'];
    let u_mpp = json['manufacturer_data']['_U_mpp_m'];

    let c_2 = Math.log(1-(i_mpp/i_sc)) / (u_mpp-u_oc);
    let c_1 =i_sc * Math.exp(-c_2*u_oc);
    return i_sc - c_1 * Math.exp(c_2 * x);
}

function voltage_power_function_manufacturer(x, json)
{
    return x * voltage_current_function_manufacturer(x, json);
}

function voltage_current_function_flasher(x,json)
{
    let i_sc = json['flasher_data']['_I_sc_f'];
    let i_mpp = json['flasher_data']['_I_mpp_f'];
    let u_oc = json['flasher_data']['_U_oc_f'];
    let u_mpp = json['flasher_data']['_U_mpp_f'];

    let c_2 = Math.log(1-(i_mpp/i_sc)) / (u_mpp-u_oc);
    let c_1 =i_sc * Math.exp(-c_2*u_oc);
    return i_sc - c_1 * Math.exp(c_2 * x);
}

function voltage_power_function_flasher(x, json)
{
    return x * voltage_current_function_flasher(x, json);
}

function voltage_current_function_flasher_stc(x,json)
{
    let i_sc = json['flasher_data_stc']['_I_sc_f'];
    let i_mpp = json['flasher_data_stc']['_I_mpp_f'];
    let u_oc = json['flasher_data_stc']['_U_oc_f'];
    let u_mpp = json['flasher_data_stc']['_U_mpp_f'];

    let c_2 = Math.log(1-(i_mpp/i_sc)) / (u_mpp-u_oc);
    let c_1 =i_sc * Math.exp(-c_2*u_oc);
    return i_sc - c_1 * Math.exp(c_2 * x);
}

function voltage_power_function_flasher_stc(x, json)
{
    return x * voltage_current_function_flasher_stc(x, json);
}

function get_intersection_with_x_axis(json)
{
    let i_sc = json['manufacturer_data']['_I_sc_m'];
    let i_mpp = json['manufacturer_data']['_I_mpp_m'];
    let u_oc = json['manufacturer_data']['_U_oc_m'];
    let u_mpp = json['manufacturer_data']['_U_mpp_m'];

    let c_2 = Math.log(1-(i_mpp/i_sc)) / (u_mpp-u_oc);
    let c_1 =i_sc * Math.exp(-c_2*u_oc);
    console.log("the interseciton", Math.log(i_sc/c_1)/c_2);
    return Math.log(i_sc/c_1)/c_2;
}