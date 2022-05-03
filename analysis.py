#!/usr/local/bin/python3.8
# FLASK_APP=app.py
# FLASK_ENV=development
# flask run
import sqlite3
import datetime as dt
import numpy as np
#import matplotlib
#matplotlib.use('Tkagg')
#import matplotlib.pyplot as plt
from flask import Flask, Response, render_template, request, session, jsonify
import json

import time

import subprocess
power_list =[]
reset = 0
old_date = ""
path="ac_telemetry.db"
db_backup = "ac_telemetry_backup.db"
cmd = "cp -a ac_telemetry.db ac_telemetry_backup.db"
returned_value = subprocess.call(cmd, shell=True)  # returns the exit code in unix
print("databased backed")
time.sleep(1)
conn = sqlite3.connect(path, check_same_thread=False)
cur = conn.cursor()

app = Flask(__name__)


sql_lastrow = "SELECT * FROM ac_parameters ORDER BY id DESC LIMIT 1;"
sql_dayrecords =" select * from ac_parameters where date > '2022/04/29' and time > '00:00:00' and time < '00:59:00' and voltage > 200 ;"
#sql_avg_minute ="select avg(power) from ac_parameters where date >= '2022/04/25' and time >= '?' and time <= '?' and voltage > 200;"




def getPower():
    global db_backup,power_list
    power_list = []
    date_find ='2022-04-29'

    conn = sqlite3.connect(db_backup, check_same_thread=False)
    db = conn.cursor()
    print("getting list")
    for hour in range(24):
        for min in range(59):
            t1 = dt.datetime.strptime(str(hour)+":"+str(min)+":00", '%H:%M:%S').time()
            t2 = dt.datetime.strptime(str(hour)+":"+str(min+1)+":00", '%H:%M:%S').time()
            sql_avg_minute ="select avg(power) from ac_parameters where date >= ? and time >= ? and time <= ? and voltage > 200;"
            #print(t2,end=" ")
            #print(t1,end=" ")
            
            db.execute(sql_avg_minute,(date_find,str(t1),str(t2)))

            rows= db.fetchall()#average power
            #print(rows)
            #print(f"total records {rows[0]} time {t2}")
            print(".", end="")
            power_raw=[round(sl[0],2) for sl in rows]
            

            
            power_list.append((date_find+" "+str(t2),power_raw[0]))

    print("done with list")

    return power_list

@app.route('/')
def index():
    return render_template('index.html', title='Sensor1', max=30)



@app.route('/_sensor1', methods=['GET'])
def sensorLive():
    
    def generate_random_data():
        with app.app_context(): 
            global path,sql_dayrecords,cur,reset,power_list
            newdate =[]
            newCurrent = []

            if(reset==0):
                
                
                #date=[s1[1]+" "+s1[2] for s1 in rows]
                #time_clock=[sl[2] for sl in rows]
                #power=[sl[5] for sl in rows]
                #power_float=[float(sl[5]) for sl in rows]
                newdate = [date[0] for date in power_list]
                newCurrent = [power[1] for power in power_list]
                
                #newdate=power_list[0][:]
                #newCurrent = power_list[1][:]
                print(f"total records {len(newdate)-1}")
                reset = 1
                
            else:
                cur.execute(sql_lastrow)
                rows = cur.fetchall()
                rows = list(rows)
                print(f"else: {rows[0][1]}",end=" ")
                print(rows[0][5])

                newCurrent = rows[0][5]
                newdate = rows[0][1]+" "+rows[0][2]
                #print(newdate)
                #print(newCurrent)
            json_data = json.dumps({'date': newdate, 'current': newCurrent, 'reset':reset}, default=str)
            yield f"data:{json_data}\n\n"
            
            time.sleep(1)

    return Response(generate_random_data(), mimetype='text/event-stream')

if __name__ == '__main__':
    reset = 0
    power_list =getPower()
    app.run(debug=True, threaded=True, host='0.0.0.0', port=5000)
    #getPower()
