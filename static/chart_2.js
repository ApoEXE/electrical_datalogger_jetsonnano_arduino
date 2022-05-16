
$(document).ready(function () {
        const config = {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: "Power Panel W",
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
                    text: 'Power Panel (W) real time Plotting'
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
        


        reset_value_2 = 0;
        source.onmessage = function (event) {
            const data = JSON.parse(event.data);


        
          if(reset_value_2==0){
            for (let index = 0; index < data.date_panel.length; index++) {
                
                config.data.labels.push(data.date_panel[index]);
                config.data.datasets[0].data.push(data.var_panel[index]);
                console.log(data.date_panel[index]);
                lineChart.update();
                if(data.date_panel.length>1){
                    reset_value_2=1;
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