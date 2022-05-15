
$(document).ready(function () {
    const config = {

        data: {

            labels: [],
            datasets: [{
                type: 'line',
                label: "PV Voltage",
                backgroundColor: 'rgb(255, 99, 132)',
                borderColor: 'rgb(255, 99, 132)',
                data: [],
                fill: false,
            }, {
                type: 'line',
                label: "PV Current",
                backgroundColor: 'rgb(255, 99, 132)',
                borderColor: 'rgb(255, 99, 132)',
                data: [],
                fill: false,
            }],
        },
        options: {
            responsive: true,
            animation: {
                duration: 0 // general animation time
            },
            title: {
                display: true,
                text: 'Voltage (V) And Ampere'
            },
            tooltips: {
                mode: 'index',
                intersect: false,
            },
            hover: {
                mode: 'nearest',
                intersect: true
            },
            scales: {
                xAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Time'
                    }
                }],
                yAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Value'
                    }
                }]
            }
        }
    };

    const context = document.getElementById('canvas3').getContext('2d');

    const lineChart = new Chart(context, config);

    const source = new EventSource("/_sensor3");



    reset_value_3 = 0;
    source.onmessage = function (event) {
        const python_data = JSON.parse(event.data);

        if (reset_value_3 == 0) {
            for (let index = 0; index < python_data.date_panel.length; index++) {

                config.data.labels.push(python_data.date_panel[index]);
                config.data.datasets[0].data.push(python_data.var_panel_volt[index]);
                config.data.datasets[1].data.push(python_data.var_panel_current[index]);

                console.log(python_data.var_panel_current[index]);
                console.log(python_data.var_panel_volt[index]);
                lineChart.update();
                if (python_data.date_panel.length > 1) {
                    reset_value_3 = 1;
                }

            }
        }
        //else{ //to push one by one real time
        //config.data.labels.push(data.date);
        //config.data.datasets[0].data.push(data.current);
        //}
        lineChart.update();
    }


});