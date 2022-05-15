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
                avg_pv_power=data.avg_pv_power;
                avg_pv_current=data.avg_pv_current;
                avg_pv_voltage=data.avg_pv_voltage;
                avg_pv_power_load=data.avg_pv_power_load;
                avg_pv_power_ac=data.avg_pv_power_ac;
                avg_pv_current_ac=data.avg_pv_current_ac;
                avg_pv_voltage_ac=data.avg_pv_voltage_ac;

                viewData();
            });
    }

    function viewData() {

        document.getElementById("sensor1").innerHTML =
            "<td>"+  avg_pv_power    +"</td>" +
            "<td>" + avg_pv_current + "</td>" +
            "<td>" + avg_pv_voltage + "</td>" +
            "<td>" + avg_pv_power_load + "</td>" +
            "<td>" + avg_pv_power_ac + "</td>" +
            "<td>" + avg_pv_current_ac + "</td>" +
            "<td>" + avg_pv_voltage_ac + "</td>";

       
     
    }
  setInterval(extractCsv, 1000);


 });
