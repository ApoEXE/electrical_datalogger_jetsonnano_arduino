$(document).ready(function() {


    setInterval(viewChart, 50);



    
    function viewChart(){
    fetch('/_sensor').then((response) => {
        return response.json();
    })
        .then((data) => {

            //console.log(data.temp);
            var barData = {
                labels: data.date,

                datasets: [{
                    fillColor: "rgba(151,187,205,0.2)",
                    strokeColor: "rgba(151,187,205,1)",
                    pointColor: "rgba(151,187,205,1)",
                    pointStrokeColor: "#fff",
                    pointHighlightFill: "#fff",
                    pointHighlightStroke: "rgba(151,187,205,1)",
                    bezierCurve: false,
                    data: data.temp
                }]
            }

            Chart.defaults.global.animationSteps = 50;
            Chart.defaults.global.tooltipYPadding = 16;
            Chart.defaults.global.tooltipCornerRadius = 0;
            Chart.defaults.global.tooltipTitleFontStyle = "normal";
            Chart.defaults.global.tooltipFillColor = "rgba(0,0,0,0.8)";
            Chart.defaults.global.animationEasing = "easeOutBounce";
            Chart.defaults.global.responsive = false;
            Chart.defaults.global.scaleLineColor = "black";
            Chart.defaults.global.scaleFontSize = 16;

            // get bar chart canvas
            var mychart = document.getElementById("chart1").getContext("2d");

            steps = 10

            // draw bar chart
            var LineChartDemo = new Chart(mychart).Line(barData, {
                scaleOverride: true,
                scaleSteps: steps,
                scaleStepWidth: Math.ceil(max / steps),
                scaleStartValue: 0,
                scaleShowVerticalLines: true,
                scaleShowGridLines: true,
                barShowStroke: true,
                scaleShowLabels: true,
                bezierCurve: false,
            });
        });
    }
});