
$(document).ready(function () {
    const config = {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: "AC Watt Real Time",
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
                text: 'Watt real time Plotting'
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

    const context = document.getElementById('canvas4').getContext('2d');

    const lineChart = new Chart(context, config);

    const source = new EventSource("/_sensor4");

    source.onmessage = function (event) {
        const data = JSON.parse(event.data);

        config.data.labels.push(data.date_ac_power);
        config.data.datasets[0].data.push(data.ac_power);
        lineChart.update();
    }


});