
$(document).ready(function () {
        const config = {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: "Power AC W",
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
                    text: 'Power (W) real time Plotting'
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

        const context = document.getElementById('canvas1').getContext('2d');

        const lineChart = new Chart(context, config);

        const source = new EventSource("/_sensor1");

     

        reset_value = 0;
        source.onmessage = function (event) {
            const data = JSON.parse(event.data);
            
          if(reset_value==0){
            for (let index = 0; index < data.date.length; index++) {
                
                config.data.labels.push(data.date[index]);
                config.data.datasets[0].data.push(data.current[index]);
                //console.log(data.date[index]);
                lineChart.update();
                if(data.date.length>1){
                reset_value=1;
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