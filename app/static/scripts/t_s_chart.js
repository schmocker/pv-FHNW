$.getJSON("/eos/data", function (data) {
    new Chart(document.getElementById("t-s-chart"), {
        type: 'scatter',
        data: {
            datasets: [{
                data: data,
                borderWidth: 1,
                showLine: true,
                radius: 0,
                label: "Isobaric ",
                fill: false
            }
            ]
        },
        options: {
            title: {
                display: true,
                text: 'T-s Diagram of H20'
            },
            scales: {
                yAxes: [{
                    scaleLabel: {
                        display: true,
                        labelString: "Temperatur T [K]"
                    }
                }],
                xAxes: [{
                    scaleLabel: {
                        display: true,
                        labelString: "Entropy S [kJ/(kg*K)]"
                    }
                }]
            }
        },

    });
});

