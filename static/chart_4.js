
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
    reset_value_4 = 0;
    
    source.onmessage = function (event) {
        const pythondata = JSON.parse(event.data);
        console.log(pythondata.ac_power);
        console.log(pythondata.date_ac_power.length);
        if (reset_value_4 == 0 && pythondata.date_ac_power.length > 1) {
            for (let index = 0; index < pythondata.date_ac_power.length; index++) {
                config.data.labels.push(pythondata.date_ac_power[index]);
                config.data.datasets[0].data.push(pythondata.ac_power[index]);
                console.log(pythondata.ac_power);
                reset_value_4 = 1;

            }
            lineChart.update();

        } 
        if(reset_value_4 == 1){
            config.data.labels.push(pythondata.date_ac_power_sec);
            config.data.datasets[0].data.push(pythondata.ac_power_sec);
            console.log("on realtime");
            console.log(pythondata.date_ac_power_sec);
            console.log(pythondata.ac_power_sec);
            lineChart.update();

        }
        const dict_values = { reset_value_4 }
        const s = JSON.stringify(dict_values); // Stringify converts a JavaScript object or value to a JSON string
        
        console.log(reset_value_4);
        //console.log(s);
        //window.alert(s)
        $.ajax({
            url: "/reset4",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify(s)
        });
        
    }


});