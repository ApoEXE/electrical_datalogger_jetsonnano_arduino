#!/usr/local/bin/python3.8
# FLASK_APP=app.py
# FLASK_ENV=development
# flask run
from cgitb import enable
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


from threading import Thread

enable_server = 0
power_list =[]
power_list_panel=[]
voltage_list_panel=[]
current_list_panel=[]
reset = 0
reset2 = 0
old_date = ""
date_to_find = "2022-05-16"
db_backup = "ac_telemetry_backup.db"
avg_pv_power = 0.0
avg_pv_current = 0.0
avg_pv_voltage = 0.0
avg_pv_power_load = 0.0
avg_pv_power_ac = 0.0
avg_pv_current_ac = 0.0
avg_pv_voltage_ac = 0.0

up_to_hour = 24
up_to_min = 59

cmd = "cp -a ac_telemetry.db ac_telemetry_backup.db"
returned_value = subprocess.call(cmd, shell=True)  # returns the exit code in unix
print("databased backed")
time.sleep(1)





conn = sqlite3.connect(db_backup, check_same_thread=False)
cur = conn.cursor()

app = Flask(__name__)

from datetime import datetime, timedelta
from tzlocal import get_localzone # pip install tzlocal

DAY = timedelta(1)
local_tz = get_localzone()   # get local timezone
now = datetime.now(local_tz) # get timezone-aware datetime object
day_ago = local_tz.normalize(now - DAY) # exactly 24 hours ago, time may differ
naive = now.replace(tzinfo=None) - DAY # same time
yesterday = local_tz.localize(naive, is_dst=None) # but elapsed hours may differ
date_yesterday,hour = str(yesterday).split(" ")
print(date_yesterday)


named_tuple = time.localtime() # get struct_time
date_today,time_str=time.strftime("%Y-%m-%d %H:%M:%S", named_tuple).split(" ")

sql_lastrow = "SELECT * FROM parameters ORDER BY id DESC LIMIT 1;"
sql_dayrecords =f" select * from parameters where date > '{date_yesterday}' and time > '00:00:00' and time < '00:59:00' and voltage > 200 ;"
#sql_avg_minute ="select avg(power) from ac_parameters where date >= '2022/04/25' and time >= '?' and time <= '?' and voltage > 200;"

def getPanelPower():
    global db_backup,power_list_panel,enable_server,date_to_find,up_to_hour,up_to_min
    power_list_panel = []
    date_find =date_to_find

    conn = sqlite3.connect(db_backup, check_same_thread=False)
    db = conn.cursor()
    print("getting Panel Power list")
    for hour in range(up_to_hour):
        for min in range(up_to_min):
            t1 = dt.datetime.strptime(str(hour)+":"+str(min)+":00", '%H:%M:%S').time()
            t2 = dt.datetime.strptime(str(hour)+":"+str(min+1)+":00", '%H:%M:%S').time()
            sql_avg_minute ="select avg(PANEL_POWER) from parameters where date >= ? and time >= ? and time <= ?;"
            db.execute(sql_avg_minute,(date_find,str(t1),str(t2)))
            rows= db.fetchall()#average power
            #print(f"total Panel records {rows[0]} time {t2}")
            for sl in rows:
                if(sl[0]!=None):
                    power_raw=[round(sl[0],2)]
                    power_list_panel.append((date_find+" "+str(t2),power_raw[0]))
            

    print("done with Panel list")
    enable_server +=1 
    return power_list_panel

def getPanel_voltage():
    global db_backup,voltage_list_panel,enable_server,date_to_find,up_to_hour,up_to_min
    voltage_list_panel = []
    date_find =date_to_find

    conn = sqlite3.connect(db_backup, check_same_thread=False)
    db = conn.cursor()
    print("getting PV Volt list")
    for hour in range(up_to_hour):
        for min in range(up_to_min):
            t1 = dt.datetime.strptime(str(hour)+":"+str(min)+":00", '%H:%M:%S').time()
            t2 = dt.datetime.strptime(str(hour)+":"+str(min+1)+":00", '%H:%M:%S').time()
            sql_avg_minute ="select avg(PANEL_VOLTAGE) from parameters where date >= ? and time >= ? and time <= ?;"
            db.execute(sql_avg_minute,(date_find,str(t1),str(t2)))
            rows= db.fetchall()#average power
            for sl in rows:
                if(sl[0]!=None):
                    power_raw=[round(sl[0],2)]
                    voltage_list_panel.append((date_find+" "+str(t2),power_raw[0]))
            

    print("done with PV Volt list")
    enable_server +=1 
    return voltage_list_panel



def getPanel_current():
    global db_backup,current_list_panel,enable_server,date_to_find,up_to_hour,up_to_min
    current_list_panel = []
    date_find =date_to_find

    conn = sqlite3.connect(db_backup, check_same_thread=False)
    db = conn.cursor()
    print("getting PanelCurrent list")
    for hour in range(up_to_hour):
        for min in range(up_to_min):
            t1 = dt.datetime.strptime(str(hour)+":"+str(min)+":00", '%H:%M:%S').time()
            t2 = dt.datetime.strptime(str(hour)+":"+str(min+1)+":00", '%H:%M:%S').time()
            sql_avg_minute ="select avg(PANEL_CURRENT) from parameters where date >= ? and time >= ? and time <= ?;"
            db.execute(sql_avg_minute,(date_find,str(t1),str(t2)))
            rows= db.fetchall()#average power
            for sl in rows:
                if(sl[0]!=None):
                    power_raw=[round(sl[0],2)]
                    current_list_panel.append((date_find+" "+str(t2),power_raw[0]))
            

    print("done with PV current list")
    enable_server +=1 
    return current_list_panel

#************************************** AC Power
def getPower():
    global db_backup,power_list,enable_server,date_to_find,up_to_hour,up_to_min
    power_list = []
    date_find =date_to_find

    conn = sqlite3.connect(db_backup, check_same_thread=False)
    db = conn.cursor()
    print("getting AC list")
    for hour in range(up_to_hour):
        for min in range(up_to_min):
            t1 = dt.datetime.strptime(str(hour)+":"+str(min)+":00", '%H:%M:%S').time()
            t2 = dt.datetime.strptime(str(hour)+":"+str(min+1)+":00", '%H:%M:%S').time()
            sql_avg_minute ="select avg(power) from parameters where date >= ? and time >= ? and time <= ? and voltage > 200;"           
            db.execute(sql_avg_minute,(date_find,str(t1),str(t2)))
          
            rows= db.fetchall()#average power
        
            start = time.time()
            for sl in rows:
                if(sl[0]!=None):
                    power_raw=[round(sl[0],2)]
                    power_list.append((date_find+" "+str(t2),power_raw[0]))
            

    print("done with AC Power list")
    enable_server +=1 
    return power_list


#******************THREADSA
power_ac_thread = Thread(target=getPower)
power_pv__thread = Thread(target=getPanelPower)
current_pv__thread = Thread(target=getPanel_current)
voltage_pv__thread = Thread(target=getPanel_voltage)



@app.route('/')
def index():
    global date_to_find,power_ac_thread,power_pv__thread,current_pv__thread,voltage_pv__thread,enable_server,power_list
    print("index")
    start = time.time()
    try:
        power_ac_thread.start()
        power_pv__thread.start()
        current_pv__thread.start()
        voltage_pv__thread.start()
        power_ac_thread.join()
        power_pv__thread.join()
        current_pv__thread.join()
        voltage_pv__thread.join()
        newdate = [date[0] for date in power_list]
        print(newdate[0])
    except Exception as e:
        print("Cannot restart thread")
        print(e)
    print(enable_server)
    delta_time = round((time.time()-start)/60,2)
    print(f"delta time: {delta_time}")
    return render_template('index.html', title='Sensor1',date_t=date_to_find,date_y=date_to_find, max=30)


#*********************************************************************************AC POWER
@app.route('/_sensor1', methods=['GET'])
def sensorAC():
    
    def generate_random_data():
        with app.app_context(): 
            global path,sql_dayrecords,cur,reset,power_list,date_today,date_yesterday,enable_server
            print(f"enable server: {enable_server}")
            if enable_server >=4:
                m_date = date_today
                newdate =[]
                newCurrent = []
                print("calling _sensor1")
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
                    #reset = 1

                json_data = json.dumps({'date': newdate, 'current': newCurrent, 'reset':reset, 'date_analisys':m_date}, default=str)
                yield f"data:{json_data}\n\n"
            
            time.sleep(1)

    return Response(generate_random_data(), mimetype='text/event-stream')
#*********************************************************************************PANEL VOLTAGE
@app.route('/_sensor2', methods=['GET'])
def sensorPowerPV():
    
    def generate_random_data():
        with app.app_context(): 
            global path,sql_dayrecords,cur,reset,power_list_panel,reset2,date_today,enable_server
            if enable_server >=4:
                m_date = date_today
                newdate =[]
                newCurrent = []
                print("calling _sensor2")
                if(reset2==0):
                    
                    newdate = [date[0] for date in power_list_panel]
                    newCurrent = [power[1] for power in power_list_panel]

                    print(f"total records {len(newdate)-1}")
                json_data = json.dumps({'date_panel': newdate, 'var_panel': newCurrent, 'reset2':reset2,'date_analisys_2':m_date}, default=str)
                yield f"data:{json_data}\n\n"
            
            time.sleep(1)

    return Response(generate_random_data(), mimetype='text/event-stream')


@app.route('/_sensor3', methods=['GET'])
def sensorVoltPV():
    
    def generate_random_data():
        with app.app_context(): 
            global path,sql_dayrecords,cur,reset,voltage_list_panel,current_list_panel,reset2,date_today,enable_server
            if enable_server >=4:
                m_date = date_today
                newdate =[]
                newCurrent = []
                newVoltage = []
                print("calling _sensor2")
                if(reset2==0):
                    
                    newdate = [date[0] for date in voltage_list_panel]
                    newCurrent = [current[1] for current in current_list_panel]
                    newVoltage = [voltage[1] for voltage in voltage_list_panel]

                    print(f"total records {len(newdate)-1}")
                json_data = json.dumps({'date_panel': newdate, 'var_panel_current': newCurrent,'var_panel_volt':newVoltage, 'reset2':reset2,'date_analisys_2':m_date}, default=str)
                yield f"data:{json_data}\n\n"
            
            time.sleep(1)

    return Response(generate_random_data(), mimetype='text/event-stream')

@app.route('/_sensor4', methods=['GET'])
def sensorCurrentPV():
    
    def generate_random_data():
        with app.app_context(): 
            global path,sql_dayrecords,cur,reset,current_list_panel,reset2,date_today,enable_server
            if enable_server >=4:
                m_date = date_today
                newdate =[]
                newCurrent = []
                print("calling _sensor2")
                if(reset2==0):
               
                    newdate = [date[0] for date in current_list_panel]
                    newCurrent = [power[1] for power in current_list_panel]

                    print(f"total records {len(newdate)-1}")
                json_data = json.dumps({'date_panel': newdate, 'var_panel_cur': newCurrent, 'reset2':reset2,'date_analisys_2':m_date}, default=str)
                yield f"data:{json_data}\n\n"
            
            time.sleep(1)

    return Response(generate_random_data(), mimetype='text/event-stream')



@app.route("/extract_data", methods=['POST'])
def extractData():
    with app.app_context():
        global date_to_find,  avg_pv_power,avg_pv_current,avg_pv_voltage,avg_pv_power_load,avg_pv_power_ac,avg_pv_current_ac,avg_pv_voltage_ac
        date_find =date_to_find
        t1 = "00:00:00"
        t2 = "23:59::00"
        conn = sqlite3.connect(db_backup, check_same_thread=False)
        db = conn.cursor()


        sql_avg_minute ="select avg(power) from parameters where date >= ? and time >= ? and time <= ? and voltage > 200;"           
        db.execute(sql_avg_minute,(date_find,str(t1),str(t2))) 
        rows= db.fetchall()#average power
        avg_pv_power_ac = [value[0] for value in rows]
        avg_pv_power_ac = round(avg_pv_power_ac[0],2)
        #print(f"Power AC avg on {date_find} : {avg_pv_power_ac}")
        
        sql_avg_minute ="select avg(PANEL_CURRENT)*avg(PANEL_VOLTAGE) from parameters where date >= ? and time >= ? and time <= ? and PANEL_VOLTAGE > 5;"           
        db.execute(sql_avg_minute,(date_find,str(t1),str(t2))) 
        rows= db.fetchall()#average power
        avg_pv_power_load = [value[0] for value in rows]
        avg_pv_power_load = round(avg_pv_power_load[0],2)
        #print(f"Power PV Load on {date_find} : {avg_pv_power_load}")


        sql_avg_minute ="select (avg(PANEL_VOLTAGE)*100/22.5) from parameters where date >= ? and time >= ? and time <= ? and PANEL_VOLTAGE > 5;"           
        db.execute(sql_avg_minute,(date_find,str(t1),str(t2))) 
        rows= db.fetchall()#average power
        avg_pv_power = [value[0] for value in rows]
        avg_pv_power = round(avg_pv_power[0],2)
        #print(f"Power PV from voltage on {date_find} : {avg_pv_power}")


        sql_avg_minute ="select avg(PANEL_CURRENT) from parameters where date >= ? and time >= ? and time <= ? and PANEL_VOLTAGE > 5;"           
        db.execute(sql_avg_minute,(date_find,str(t1),str(t2))) 
        rows= db.fetchall()#average power
        avg_pv_current = [value[0] for value in rows]
        avg_pv_current = round(avg_pv_current[0],2)
        #print(f"Current PV on {date_find} : {avg_pv_current}")


        sql_avg_minute ="select avg(PANEL_VOLTAGE) from parameters where date >= ? and time >= ? and time <= ? and PANEL_VOLTAGE > 5;"           
        db.execute(sql_avg_minute,(date_find,str(t1),str(t2))) 
        rows= db.fetchall()#average power
        avg_pv_voltage = [value[0] for value in rows]
        avg_pv_voltage = round(avg_pv_voltage[0],2)
        #print(f"Voltage PV on {date_find} : {avg_pv_voltage}")

        sql_avg_minute ="select avg(CURRENT) from parameters where date >= ? and time >= ? and time <= ? and  VOLTAGE > 200;"           
        db.execute(sql_avg_minute,(date_find,str(t1),str(t2))) 
        rows= db.fetchall()#average power
        avg_pv_current_ac = [value[0] for value in rows]
        avg_pv_current_ac = round(avg_pv_current_ac[0],2)
        #print(f"AC Current on {date_find} : {avg_pv_current_ac}")

        sql_avg_minute ="select avg(VOLTAGE) from parameters where date >= ? and time >= ? and time <= ? and VOLTAGE > 200;"           
        db.execute(sql_avg_minute,(date_find,str(t1),str(t2))) 
        rows= db.fetchall()#average power
        avg_pv_voltage_ac = [value[0] for value in rows]
        avg_pv_voltage_ac = round(avg_pv_voltage_ac[0],2)
        #print(f"AC Voltage on {date_find} : {avg_pv_voltage_ac}")

        return jsonify({'avg_pv_power': avg_pv_power,
                        'avg_pv_current': avg_pv_current,
                        'avg_pv_voltage': avg_pv_voltage,
                        'avg_pv_power_load': avg_pv_power_load,
                        'avg_pv_power_ac': avg_pv_power_ac,
                        'avg_pv_current_ac': avg_pv_current_ac,
                        'avg_pv_voltage_ac': avg_pv_voltage_ac})





if __name__ == '__main__':

    app.run(debug=False, threaded=True, host='0.0.0.0', port=5000)


''' 
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
'''