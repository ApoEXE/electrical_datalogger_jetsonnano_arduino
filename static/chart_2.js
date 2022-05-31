
$(document).ready(function () {
    const config = {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: "PV W",
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
                text: 'Power Produced Panel (W) real time Plotting'
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

    const context = document.getElementById('canvas2').getContext('2d');

    const lineChart = new Chart(context, config);

    const source = new EventSource("/_sensor2");

    source.onmessage = function (event) {
        const data = JSON.parse(event.data);

        config.data.labels.push(data.pv_date);
        config.data.datasets[0].data.push(data.pv_power);

        lineChart.update();

    }

});