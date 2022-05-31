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
                date1=data.date1;
                precio=data.precio;

                avg_pv_power2=data.avg_pv_power2;
                avg_pv_current2=data.avg_pv_current2;
                avg_pv_voltage2=data.avg_pv_voltage2;
                avg_pv_power_load2=data.avg_pv_power_load2;
                avg_pv_power_ac2=data.avg_pv_power_ac2;
                avg_pv_current_ac2=data.avg_pv_current_ac2;
                avg_pv_voltage_ac2=data.avg_pv_voltage_ac2;
                date2=data.date2;
                precio2=data.precio2;

                avg_pv_power3=data.avg_pv_power3;
                avg_pv_current3=data.avg_pv_current3;
                avg_pv_voltage3=data.avg_pv_voltage3;
                avg_pv_power_load3=data.avg_pv_power_load3;
                avg_pv_power_ac3=data.avg_pv_power_ac3;
                avg_pv_current_ac3=data.avg_pv_current_ac3;
                avg_pv_voltage_ac3=data.avg_pv_voltage_ac3;
                date3=data.date3;
                precio3=data.precio3;

                avg_pv_power4=data.avg_pv_power4;
                avg_pv_current4=data.avg_pv_current4;
                avg_pv_voltage4=data.avg_pv_voltage4;
                avg_pv_power_load4=data.avg_pv_power_load4;
                avg_pv_power_ac4=data.avg_pv_power_ac4;
                avg_pv_current_ac4=data.avg_pv_current_ac4;
                avg_pv_voltage_ac4=data.avg_pv_voltage_ac4;
                date4=data.date4;
                precio4=data.precio4;

                avg_pv_power5=data.avg_pv_power5;
                avg_pv_current5=data.avg_pv_current5;
                avg_pv_voltage5=data.avg_pv_voltage5;
                avg_pv_power_load5=data.avg_pv_power_load5;
                avg_pv_power_ac5=data.avg_pv_power_ac5;
                avg_pv_current_ac5=data.avg_pv_current_ac5;
                avg_pv_voltage_ac5=data.avg_pv_voltage_ac5;
                date5=data.date5;
                precio5=data.precio5;

                viewData();
            });
    }

    function viewData() {

        document.getElementById("sensor1").innerHTML =
            "<td>"+  date1   +"</td>" +
            "<td>"+  precio    +"</td>" +
            "<td>" + avg_pv_power_ac + "</td>" +
            "<td>" + avg_pv_current_ac + "</td>" +
            "<td>" + avg_pv_power_load + "</td>" +
            "<td>" + avg_pv_current + "</td>";
            document.getElementById("sensor2").innerHTML =
            "<td>"+  date2   +"</td>" +
            "<td>"+  precio2    +"</td>" +
            "<td>" + avg_pv_power_ac2 + "</td>" +
            "<td>" + avg_pv_current_ac2 + "</td>" +
            "<td>" + avg_pv_power_load2 + "</td>" +
            "<td>" + avg_pv_current2 + "</td>";
            document.getElementById("sensor3").innerHTML =
            "<td>"+  date3   +"</td>" +
            "<td>"+  precio3    +"</td>" +
            "<td>" + avg_pv_power_ac3 + "</td>" +
            "<td>" + avg_pv_current_ac3 + "</td>" +
            "<td>" + avg_pv_power_load3 + "</td>" +
            "<td>" + avg_pv_current3 + "</td>";
            document.getElementById("sensor4").innerHTML =
            "<td>"+  date4  +"</td>" +
            "<td>"+  precio4    +"</td>" +
            "<td>" + avg_pv_power_ac4 + "</td>" +
            "<td>" + avg_pv_current_ac4 + "</td>" +
            "<td>" + avg_pv_power_load4 + "</td>" +
            "<td>" + avg_pv_current4 + "</td>";
            document.getElementById("sensor5").innerHTML =
            "<td>"+  date5   +"</td>" +
            "<td>"+  precio5    +"</td>" +
            "<td>" + avg_pv_power_ac5 + "</td>" +
            "<td>" + avg_pv_current_ac5 + "</td>" +
            "<td>" + avg_pv_power_load5 + "</td>" +
            "<td>" + avg_pv_current5 + "</td>";

       
     
    }
  setInterval(extractCsv, 1000);


 });
