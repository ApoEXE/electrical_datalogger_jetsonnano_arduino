#!/usr/bin/python3
# FLASK_APP=app.py
# FLASK_ENV=development
# flask run
import json
from threading import Thread
import time
import os
import datetime
from datetime import date,datetime
from flask import Flask, Response, render_template, request, session, jsonify


from cv2 import sqrt
import smbus
import time
import datetime
import signal

import csv

import pathlib

is_shutdown = False
realvolt = 4.59
# DECLARATIONS
var_current_ac= 0
var_volt_ac = 0

reset = 0
index_data = int(0)
path="/home/nano/projects/electrical_datalogger_jetsonnano_arduino/ac_telemetry.csv"


print(f"START at {datetime.datetime.now()}")
file = pathlib.Path(path)
if(file.exists()==False):
    file = open(path,"x")

file =  open(path,"r+")
ac_writer = csv.writer(file,delimiter=',',quoting=csv.QUOTE_MINIMAL)
reader = csv.reader(file)
data = list(reader)
n_lines= len(data)
print(f"number of lines: {n_lines}  ")

app = Flask(__name__)



#print(f"FIRST ROW: {string_tmp}  {ac_value}")

bus = smbus.SMBus(0)


def gather_data():
    global var_volt_ac, var_current_ac,bus
    address = 0x20
    try:

        bus.write_byte_data(address, 0, 0x0A)
        read = bus.read_i2c_block_data(address,0,4)

        #VOLTAGE-----------
        ac_volt_dig = read[2]<<8 | read[3]
        #print(ac_volt_dig)
        anaVolt = ac_volt_dig*(realvolt / 1023.0)
        volt_in = anaVolt*(1000+880000)/1000
        volt_ac = (volt_in/1.4142135623730950488016887242097)+21
        print('AC Voltage in ',end="")

        print(str(round(volt_ac,2)),end="")

        print(' Vac',end="")


        #current-----------
        ac_curr = read[0]<<8 | read[1]
        print(' AC Current in ',end="")
        ac_curr = ac_curr/1000.0
        print(str(round(ac_curr,2)),end="")
  
        print(' A  ')


    except:
        print(f"ERROR gather 0x20 i2c disconnection")

    if(volt_ac<300):
        var_volt_ac = str(round(volt_ac,2))
        var_current_ac = str(round(ac_curr,2))
        today = date.today()
        d1 = today.strftime("%Y/%m/%d")
        from datetime import datetime
        now = datetime.now()
        d2 = now.strftime("%H:%M:%S")
        ac_writer.writerow([d1,d2,volt_ac*ac_curr,var_volt_ac,var_current_ac])
        file.flush()
        #time.sleep(0.1)
        
        #oled_disp()
        #time.sleep(0.1)
    return [volt_ac,ac_curr]

def gather_loop():
    global var_volt_ac,var_current_ac
    while not is_shutdown:
        [ac_voltage, ac_current] = gather_data()
       # var_volt_ac = ac_voltage
       # var_current_ac = ac_current
        time.sleep(0.5)



gather_thread = Thread(target=gather_loop)



#signal handling service

def stop(sig, frame):
  print(f"SIGTERM at {datetime.datetime.now()}")
  global is_shutdown
  is_shutdown = True
  file.close()
  exit(1)

signal.signal(signal.SIGINT, stop)

@app.route('/')
def index():
    return render_template('index.html', title='Sensor1', max=30)



@app.route('/_sensor1', methods=['GET'])
def sensorLive():
    
    def generate_random_data():
        with app.app_context(): 
            global data,index_data, var_current_ac
            #[newVolt,newCurrent]=gather_data()
            #newdate = ""
            #newCurrent = 0.0
            newCurrent = var_current_ac
            newdate = datetime.datetime.now()
            #newCurrent = var_current_ac
            #print(var_current_ac)
            #if(index_data < n_lines):
            #    newdate =  data[int(index_data)][0] + " " + data[int(index_data)][1]
            #    newCurrent = data[int(index_data)][4]
            #if(index_data >= n_lines):
            #    newdate = datetime.datetime.now()
            #    newCurrent = var_current_ac

            index_data=int(index_data)+1
            json_data = json.dumps({'date': newdate, 'current': newCurrent, 'reset':reset}, default=str)
            yield f"data:{json_data}\n\n"
            time.sleep(1)

    return Response(generate_random_data(), mimetype='text/event-stream')


if __name__ == '__main__':
   
    gather_thread.start()

    app.run(debug=True, threaded=True, host='0.0.0.0', port=5000)

    print(f"END at {datetime.datetime.now()}")

    
    


