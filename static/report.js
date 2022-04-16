/**
 * Created by jav on 3/8/20.
 */
 $(document).ready(function(){
    var sensor =0;
    function extractCsv() {
                req = $.ajax({
                url : '/extract_data',
                type : 'POST',
            });

            req.done(function(data) {
                sensor=data.sensor;
                difftimeSensor=data.difftimeSensor;
                totalpointsSensor=data.totalpointsSensor;
                biggestTimeSensor=data.biggestTimeSensor;
                smallestTimeSensor=data.smallestTimeSensor;
                totalpointsDead=data.totalpointsDead;
                totalpointsClean=data.totalpointsClean;
                totalpointsTxFail=data.totalpointsTxFail;
                viewData();
            });
    }

    function viewData() {
        if(sensor==1){
        document.getElementById("sensor1").innerHTML =
            "<td>"+  sensor    +"</td>" +
            "<td>" + difftimeSensor + "</td>" +
            "<td>" + totalpointsSensor + "</td>" +
            "<td>" + biggestTimeSensor + "</td>" +
            "<td>" + smallestTimeSensor + "</td>" +
            "<td>" + totalpointsDead + "</td>" +
            "<td>" + totalpointsClean + "</td>" +
            "<td>" + totalpointsTxFail + "</td>";
        }
        if(sensor==2){
        document.getElementById("sensor2").innerHTML =
            "<td>"+  sensor    +"</td>" +
            "<td>" + difftimeSensor + "</td>" +
            "<td>" + totalpointsSensor + "</td>" +
            "<td>" + biggestTimeSensor + "</td>" +
            "<td>" + smallestTimeSensor + "</td>" +
            "<td>" + totalpointsDead + "</td>" +
            "<td>" + totalpointsClean + "</td>" +
            "<td>" + totalpointsTxFail + "</td>";
        }
        if(sensor==3){
            document.getElementById("sensor3").innerHTML =
            "<td>"+  sensor    +"</td>" +
            "<td>" + difftimeSensor + "</td>" +
            "<td>" + totalpointsSensor + "</td>" +
            "<td>" + biggestTimeSensor + "</td>" +
            "<td>" + smallestTimeSensor + "</td>" +
            "<td>" + totalpointsDead + "</td>" +
            "<td>" + totalpointsClean + "</td>" +
            "<td>" + totalpointsTxFail + "</td>";
        }
        if(sensor==4){
            document.getElementById("sensor4").innerHTML =
            "<td>"+  sensor    +"</td>" +
            "<td>" + difftimeSensor + "</td>" +
            "<td>" + totalpointsSensor + "</td>" +
            "<td>" + biggestTimeSensor + "</td>" +
            "<td>" + smallestTimeSensor + "</td>" +
            "<td>" + totalpointsDead + "</td>" +
            "<td>" + totalpointsClean + "</td>" +
            "<td>" + totalpointsTxFail + "</td>";
        }

        if(sensor==5){
            document.getElementById("sensor5").innerHTML =
            "<td>"+  sensor    +"</td>" +
            "<td>" + difftimeSensor + "</td>" +
            "<td>" + totalpointsSensor + "</td>" +
            "<td>" + biggestTimeSensor + "</td>" +
            "<td>" + smallestTimeSensor + "</td>" +
            "<td>" + totalpointsDead + "</td>" +
            "<td>" + totalpointsClean + "</td>" +
            "<td>" + totalpointsTxFail + "</td>";
        }
        if(sensor==6){
             document.getElementById("sensor6").innerHTML =
            "<td>"+  sensor    +"</td>" +
            "<td>" + difftimeSensor + "</td>" +
            "<td>" + totalpointsSensor + "</td>" +
            "<td>" + biggestTimeSensor + "</td>" +
            "<td>" + smallestTimeSensor + "</td>" +
            "<td>" + totalpointsDead + "</td>" +
            "<td>" + totalpointsClean + "</td>" +
            "<td>" + totalpointsTxFail + "</td>";
        }
    }
  setInterval(extractCsv, 1000);


 });
