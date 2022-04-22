#!/usr/local/bin/python3.8
# FLASK_APP=app.py
# FLASK_ENV=development
# flask run
from ast import While
import json
from threading import Thread
import time
import datetime
from datetime import date,datetime
from flask import Flask, Response, render_template, request, session, jsonify


from cv2 import sqrt
import smbus2
import time
import datetime
import signal

import sqlite3

import socket
import random

is_shutdown = False
realvolt = 4.59
# DECLARATIONS
var_current_ac= ""
var_volt_ac = ""
d1 = ""
d2 = ""
POWER = ""
reset = 0
index_data = int(0)
path="/home/nano/projects/electrical_datalogger_jetsonnano_arduino/ac_telemetry.db"


print(f"START at {datetime.datetime.now()}")

app = Flask(__name__)



#print(f"FIRST ROW: {string_tmp}  {ac_value}")

bus = smbus2.SMBus(0)

conn = sqlite3.connect(path, check_same_thread=False)
print ("Opened database successfully")
conn.execute('''CREATE TABLE IF NOT EXISTS ac_parameters
            (ID INTEGER PRIMARY KEY AUTOINCREMENT,
            DATE           TEXT    NOT NULL,
            TIME            TEXT     NOT NULL,
            VOLTAGE        REAL,
            CURRENT         REAL,
            POWER          REAL);''')



def gather_data():
    global var_volt_ac, var_current_ac,bus,POWER,d1,d2
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
        volt_ac = 9999
        ac_curr = 9999
        POWER = 0
        #seconds_delay = random.randint(0, 3)
        #time.sleep(seconds_delay)
    d1 = ""
    d2 = ""
    m_volt_ac = ""
    m_current_ac= ""
    if(volt_ac < 300):

        var_volt_ac = str(round(volt_ac,2))
        m_volt_ac = var_volt_ac
        
        var_current_ac = str(round(ac_curr,2))
        m_current_ac = var_current_ac
        today = date.today()
        d1 = today.strftime("%Y/%m/%d")
        from datetime import datetime
        now = datetime.now()
        d2 = now.strftime("%H:%M:%S")
        POWER = str(round(volt_ac*ac_curr,2))

    return [d1,d2,m_volt_ac,m_current_ac,POWER]

def gather_loop():

    while not is_shutdown:
        [d1,d2,var_volt_ac,var_current_ac,POWER] = gather_data()
        if(d1!=""):
            conn.execute("INSERT INTO ac_parameters (DATE,TIME,VOLTAGE,CURRENT,POWER) \
            VALUES ( ?, ?, ?, ?, ? )",(d1,d2,var_volt_ac,var_current_ac,POWER))
            conn.commit()
            time.sleep(0.5)
    conn.close()
    

def socket_loop():
    global var_volt_ac,var_current_ac,d1,d2,POWER
    while not is_shutdown:
        s = socket.socket()
        port = 12345
        s.bind(('0.0.0.0', port))
        s.listen(5)
        c, addr = s.accept()
        print (f"Socket Up and running with a connection from {addr}")
        while not is_shutdown:
                rcvdData = c.recv(4096)
                print(f"S: {rcvdData}")
                str_sendData = str([d1,d2,var_volt_ac,var_current_ac,POWER])
                try:
                    c.send(str_sendData.encode())
                except:
                    print("Broken pipe error on display.py")
                    break
        s.close()
    


gather_thread = Thread(target=gather_loop)
socket_thread = Thread(target=socket_loop)


#signal handling service

def stop(sig, frame):
  print(f"SIGTERM at {datetime.datetime.now()}")
  global is_shutdown
  is_shutdown = True
  conn.close()
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
    socket_thread.start()
    #gather_loop()
    #app.run(debug=True, threaded=True, host='0.0.0.0', port=5000)
    

    print(f"END at {datetime.datetime.now()}")

    
    


