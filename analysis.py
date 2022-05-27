#!/usr/local/bin/python3.8
# FLASK_APP=app.py
# FLASK_ENV=development
# flask run
from cgitb import enable
import sqlite3
import datetime as dt
from cv2 import split


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
solar_power_saved_list =[]

report = []
reset = 0
reset2 = 0

db_backup = "/home/nano/projects/electrical_datalogger_jetsonnano_arduino/ac_telemetry_backup.db"
avg_pv_power = 0.0
avg_pv_current = 0.0
avg_pv_voltage = 0.0
avg_pv_power_load = 0.0
avg_pv_power_ac = 0.0
avg_pv_current_ac = 0.0
avg_pv_voltage_ac = 0.0

avg_pv_power2 = 0.0
avg_pv_current2 = 0.0
avg_pv_voltage2 = 0.0
avg_pv_power_load2 = 0.0
avg_pv_power_ac2 = 0.0
avg_pv_current_ac2 = 0.0
avg_pv_voltage_ac2 = 0.0

avg_pv_power3 = 0.0
avg_pv_current3 = 0.0
avg_pv_voltage3 = 0.0
avg_pv_power_load3 = 0.0
avg_pv_power_ac3 = 0.0
avg_pv_current_ac3 = 0.0
avg_pv_voltage_ac3 = 0.0

avg_pv_power4 = 0.0
avg_pv_current4 = 0.0
avg_pv_voltage4 = 0.0
avg_pv_power_load4 = 0.0
avg_pv_power_ac4 = 0.0
avg_pv_current_ac4 = 0.0
avg_pv_voltage_ac4 = 0.0

avg_pv_power5 = 0.0
avg_pv_current5 = 0.0
avg_pv_voltage5 = 0.0
avg_pv_power_load5 = 0.0
avg_pv_power_ac5 = 0.0
avg_pv_current_ac5 = 0.0
avg_pv_voltage_ac5 = 0.0

total_day_ac_power_used=[]
total_day_solar_power_produced=[]
total_day_solar_power_used=[]

up_to_hour = 24
up_to_min = 59

enable_once=False

cmd = "cp -a /home/nano/projects/electrical_datalogger_jetsonnano_arduino/ac_telemetry.db /home/nano/projects/electrical_datalogger_jetsonnano_arduino/ac_telemetry_backup.db"
returned_value = subprocess.call(cmd, shell=True)  # returns the exit code in unix
print("databased backed")
time.sleep(1)
def getDate(i):
        DAY = timedelta(i)
        local_tz = get_localzone()   # get local timezone
        now = datetime.now(local_tz) # get timezone-aware datetime object
        day_ago = local_tz.normalize(now - DAY) # exactly 24 hours ago, time may differ
        naive = now.replace(tzinfo=None) - DAY # same time
        yesterday = local_tz.localize(naive, is_dst=None) # but elapsed hours may differ
        date_yesterday,hour = str(yesterday).split(" ")
        #print(date_yesterday)
        return date_yesterday




conn = sqlite3.connect(db_backup, check_same_thread=False)
cur = conn.cursor()

app = Flask(__name__)

from datetime import datetime, timedelta
from tzlocal import get_localzone # pip install tzlocal

sql_lastrow = "SELECT * FROM parameters ORDER BY id DESC LIMIT 1;"




def getPanel_voltage():
    global db_backup,voltage_list_panel,enable_server,up_to_hour,up_to_min
    voltage_list_panel = []
    date_find =getDate(0)

    conn = sqlite3.connect(db_backup, check_same_thread=False)
    db = conn.cursor()
    print("getting PV Volt list")
    for hour in range(up_to_hour):
        #for min in range(up_to_min):
            #t1 = dt.datetime.strptime(str(hour)+":"+str(min)+":00", '%H:%M:%S').time()
            #t2 = dt.datetime.strptime(str(hour)+":"+str(min+1)+":00", '%H:%M:%S').time()
            t1 = dt.datetime.strptime(str(hour)+":00:00", '%H:%M:%S').time()
            t2 = dt.datetime.strptime(str(hour)+":59:00", '%H:%M:%S').time()
            sql_avg_minute ="select avg(PANEL_VOLTAGE) from parameters where date == ? and time >= ? and time <= ?;"
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
    global db_backup,current_list_panel,enable_server,up_to_hour,up_to_min
    current_list_panel = []
    date_find =getDate(0)

    conn = sqlite3.connect(db_backup, check_same_thread=False)
    db = conn.cursor()
    print("getting PanelCurrent list")
    for hour in range(up_to_hour):
        #for min in range(up_to_min):
            #t1 = dt.datetime.strptime(str(hour)+":"+str(min)+":00", '%H:%M:%S').time()
            #t2 = dt.datetime.strptime(str(hour)+":"+str(min+1)+":00", '%H:%M:%S').time()
            t1 = dt.datetime.strptime(str(hour)+":00:00", '%H:%M:%S').time()
            t2 = dt.datetime.strptime(str(hour)+":59:00", '%H:%M:%S').time()
            sql_avg_minute ="select avg(PANEL_CURRENT) from parameters where date == ? and time >= ? and time <= ?;"
            db.execute(sql_avg_minute,(date_find,str(t1),str(t2)))
            rows= db.fetchall()#average power
            for sl in rows:
                if(sl[0]!=None):
                    power_raw=[round(sl[0],2)]
                    current_list_panel.append((date_find+" "+str(t2),power_raw[0]))
            

    print("done with PV current list")
    enable_server +=1 
    return current_list_panel
#*************************************** Solar Power produced
def getPanelPower():
    global db_backup,power_list_panel,enable_server,up_to_hour,up_to_min,total_day_solar_power_produced
    power_list_panel = []
    total_day_solar_power_produced=[]
    

    conn = sqlite3.connect(db_backup, check_same_thread=False)
    db = conn.cursor()
    print("getting Panel Power WH list")
    
    for i in range(5):
        date_find =getDate(i)
        temp = 0.0
        for hour in range(up_to_hour):
            #t1 = dt.datetime.strptime(str(hour)+":"+str(min)+":00", '%H:%M:%S').time()
            #t2 = dt.datetime.strptime(str(hour)+":"+str(min+1)+":00", '%H:%M:%S').time()
                        
            t1 = dt.datetime.strptime(str(hour)+":00:00", '%H:%M:%S').time()
            t2 = dt.datetime.strptime(str(hour)+":59:00", '%H:%M:%S').time()
            sql_avg_minute ="select avg(PANEL_POWER) from parameters where date == ? and time >= ? and time <= ? ;"
            db.execute(sql_avg_minute,(date_find,str(t1),str(t2)))
            rows= db.fetchall()#average power
            #print(f"total Panel records {len(rows)-1} time {t2}")
            for sl in rows:
                if(sl[0]!=None):
                    power_raw=[round(sl[0],2)]
                    temp +=round(power_raw[0],2)*0.75
                    power_list_panel.append((date_find+" "+str(t2),round(power_raw[0],2)*0.75))
        total_day_solar_power_produced.append((date_find,temp))   


    print("done with Panel list")
    enable_server +=1 
    return power_list_panel
#************************************** AC Power
def getPower():
    global db_backup,power_list,enable_server,up_to_hour,total_day_ac_power_used
    power_list = []
    total_day_ac_power_used=[]

    conn = sqlite3.connect(db_backup, check_same_thread=False)
    db = conn.cursor()
    print("getting power WH list")
    for i in range(5):
        date_find =getDate(i)
        temp = 0.0
        for hour in range(up_to_hour):
            
            
            #t1 = dt.datetime.strptime(str(hour)+":"+str(min)+":00", '%H:%M:%S').time()
            #t2 = dt.datetime.strptime(str(hour)+":"+str(min+1)+":00", '%H:%M:%S').time()
            t1 = dt.datetime.strptime(str(hour)+":00:00", '%H:%M:%S').time()
            t2 = dt.datetime.strptime(str(hour)+":59:00", '%H:%M:%S').time()
            sql_avg_minute ="select avg(power) from parameters where date == ? and time >= ? and time <= ?;"        
            db.execute(sql_avg_minute,(date_find,str(t1),str(t2)))
          
            rows= db.fetchall()#average power
    
            for sl in rows:
                if(sl[0]!=None):
                    power_raw=[round(sl[0],2)]
                    temp +=round(power_raw[0],2)
                    power_list.append((date_find+" "+str(t2),round(power_raw[0],2)))
        total_day_ac_power_used.append((date_find,round(temp,2)))    
      

    print("done with AC Power list")
    enable_server +=1 
    return power_list

#************************************** Power used by load
def getPower_saved():
    global db_backup,enable_server,up_to_hour,up_to_min,total_day_solar_power_used,solar_power_saved_list
    solar_power_saved_list = []
    total_day_solar_power_used=[]

    conn = sqlite3.connect(db_backup, check_same_thread=False)
    db = conn.cursor()
    print("getting Solar power WH saved list")
    for i in range(5):
        date_find =getDate(i)
        temp = 0.0
        for hour in range(up_to_hour):
            
            #t1 = dt.datetime.strptime(str(hour)+":"+str(min)+":00", '%H:%M:%S').time()
            #t2 = dt.datetime.strptime(str(hour)+":"+str(min+1)+":00", '%H:%M:%S').time()
            t1 = dt.datetime.strptime(str(hour)+":00:00", '%H:%M:%S').time()
            t2 = dt.datetime.strptime(str(hour)+":59:00", '%H:%M:%S').time()
            sql_avg_minute ="select avg(PANEL_CURRENT*PANEL_VOLTAGE) from parameters where date == ? and time >= ? and time <= ? ;"    
            
            db.execute(sql_avg_minute,(date_find,str(t1),str(t2)))
          
            rows= db.fetchall()#average power

            #print(f"PANEL SAVED total Panel records {len(rows)-1} time {t2}")
            for sl in rows:
                if(sl[0]!=None):
                    power_raw=[round(sl[0],2)]
                    temp +=round(power_raw[0],2)
                    #print(f"{date_find}_{t1} :::::  {total_day_solar_power_used}:::::::::{round(power_raw[0],2)}")
                    solar_power_saved_list.append((date_find+" "+str(t2),round(power_raw[0],2)))
        total_day_solar_power_used.append((date_find,temp))        

    print("done with Solar Power saved list")
    enable_server +=1 
    return solar_power_saved_list


#******************THREADSA

def power_ac_loop():
    while True:
        getPower()
        time.sleep(5)

def power_solar_loop():
    while True:
        getPanelPower()
        time.sleep(5)

def power_saved_solar_loop():
    while True:
        getPower_saved()
        time.sleep(5)

def panel_current_loop():
    while True:
        getPanel_current()
        time.sleep(5)

def panel_voltage_loop():
    while True:
        getPanel_voltage()
        time.sleep(5)

current_pv_thread = Thread(target=getPanel_current)
voltage_pv_thread = Thread(target=getPanel_voltage)

power_ac_thread = Thread(target=getPower)
power_pv_thread = Thread(target=getPanelPower)
solar_saved_thread = Thread(target=getPower_saved)


loop_power_ac_thread = Thread(target=power_ac_loop)
loop_power_solar_thread = Thread(target=power_solar_loop)
loop_power_solar_saved_thread = Thread(target=power_saved_solar_loop)
loop_solar_current_thread = Thread(target=getPanel_current)
loop_solar_voltage_thread = Thread(target=getPanel_voltage)


@app.route('/')
def index():
    global power_ac_thread,power_pv_thread,current_pv_thread,voltage_pv_thread,enable_server,power_list,solar_saved_thread
    #power_ac_thread.start()
    #power_pv_thread.start()
    #current_pv_thread.start()
    #voltage_pv_thread.start()
    #solar_saved_thread.start()

    return render_template('index.html', title='Sensor1',date_t=getDate(0),date_y=getDate(1), max=30)


#*********************************************************************************AC POWER
@app.route('/_sensor1', methods=['GET'])
def sensorAC():
    
    def generate_random_data():
        with app.app_context(): 
            global reset,power_list,enable_server
            print(f"enable server: {enable_server}")
            if enable_server >=4:
                m_date = getDate(0)
                newdate =[]
                newCurrent = []
                print("calling _sensor1 power ac")
            
                date_val = ""
                if(reset==0):
                    for value in power_list:
                        date_val,hour_val = value[0].split(" ")
                        if(date_val==m_date):
                            newdate.append(value[0])
                            newCurrent.append(value[1])
                    print(f"total records {len(power_list)-1}")


                json_data = json.dumps({'date': newdate, 'current': newCurrent, 'reset':reset, 'date_analisys':m_date}, default=str)
                yield f"data:{json_data}\n\n"
            
            time.sleep(1)

    return Response(generate_random_data(), mimetype='text/event-stream')
#*********************************************************************************PANEL POWER PRODUCED
@app.route('/_sensor2', methods=['GET'])
def sensorPowerPV():
    
    def generate_random_data():
        with app.app_context(): 
            global power_list_panel,reset2,enable_server
            if enable_server >=4:
                m_date = getDate(0)
                newdate =[]
                newCurrent = []
                print("calling _sensor2 Panel power produced")
                if(reset2==0):
                    for value in power_list_panel:
                        date_val,hour_val = value[0].split(" ")
                        if(date_val==m_date):
                            newdate.append(value[0])
                            newCurrent.append(value[1])
                    print(f"total records {len(power_list_panel)-1}")
                json_data = json.dumps({'date_panel': newdate, 'var_panel': newCurrent, 'reset2':reset2,'date_analisys_2':m_date}, default=str)
                yield f"data:{json_data}\n\n"
            
            time.sleep(1)

    return Response(generate_random_data(), mimetype='text/event-stream')
#CURRENT PANEL

@app.route('/_sensor3', methods=['GET'])
def sensorVoltPV():
    
    def generate_random_data():
        with app.app_context(): 
            global voltage_list_panel,current_list_panel,reset2,enable_server
            if enable_server >=4:
                m_date = getDate(0)
                newdate =[]
                newCurrent = []
                newVoltage = []
                print("calling _sensor3 voltage current panel")
                if(reset2==0):
                                   
                    for value in voltage_list_panel:
                        date_val,hour_val = value[0].split(" ")
                        if(date_val==m_date):
                            newdate.append(value[0])
                            newCurrent = [current[1] for current in current_list_panel]
                            newVoltage = [voltage[1] for voltage in voltage_list_panel]
                    print(f"total records {len(power_list_panel)-1}")
                json_data = json.dumps({'date_panel': newdate, 'var_panel_current': newCurrent,'var_panel_volt':newVoltage, 'reset2':reset2,'date_analisys_2':m_date}, default=str)
                yield f"data:{json_data}\n\n"
            
            time.sleep(1)

    return Response(generate_random_data(), mimetype='text/event-stream')
#CURRENT AC
@app.route('/_sensor4', methods=['GET'])
def sensorCurrentPV():
    
    def generate_random_data():
        with app.app_context(): 
            global current_list_panel,reset2,enable_server
            if enable_server >=4:
                m_date = getDate(0)
                newdate =[]
                newCurrent = []
                print("calling _sensor4 Current AC")
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
        global avg_pv_power,avg_pv_current,avg_pv_voltage,avg_pv_power_load,avg_pv_power_ac,avg_pv_current_ac,avg_pv_voltage_ac
        global total_day_ac_power_used,total_day_solar_power_produced,total_day_solar_power_used,date_today,enable_server
        global avg_pv_power,avg_pv_current,avg_pv_voltage,avg_pv_power_load,avg_pv_power_ac,avg_pv_current_ac,avg_pv_voltage_ac
        global avg_pv_power2,avg_pv_current2,avg_pv_voltage2,avg_pv_power_load2,avg_pv_power_ac2,avg_pv_current_ac2,avg_pv_voltage_ac2
        global avg_pv_power3,avg_pv_current3,avg_pv_voltage3,avg_pv_power_load3,avg_pv_power_ac3,avg_pv_current_ac3,avg_pv_voltage_ac3
        global avg_pv_power4,avg_pv_current4,avg_pv_voltage4,avg_pv_power_load4,avg_pv_power_ac4,avg_pv_current_ac4,avg_pv_voltage_ac4
        global avg_pv_power5,avg_pv_current5,avg_pv_voltage5,avg_pv_power_load5,avg_pv_power_ac5,avg_pv_current_ac5,avg_pv_voltage_ac5
        t1 = "00:00:00"
        t2 = "23:59::00"
        conn = sqlite3.connect(db_backup, check_same_thread=False)
        db = conn.cursor()
        date_find =''
        date1 =''
        date2 =''
        date3 =''
        date4 =''
        date5 =''



        if(enable_server>=4):
            #*********************************************************TODAY  1
            avg_pv_power_ac = total_day_ac_power_used[0]
            date_find = avg_pv_power_ac[0]
            date1=date_find
            avg_pv_power_ac = round(avg_pv_power_ac[1],2)
            #print(f"Power AC avg on {date_find} : {avg_pv_power_ac}")

            avg_pv_power_load = total_day_solar_power_used[0]
            avg_pv_power_load = round(avg_pv_power_load[1],2)
            #print(f"Power PV Load on {date_find} : {avg_pv_power_load}")

            avg_pv_power = total_day_solar_power_produced[0]
            avg_pv_power = round(avg_pv_power[1],2)
            #print(f"Power PV from voltage on {date_find} : {avg_pv_power}")


            sql_avg_minute ="select avg(PANEL_CURRENT) from parameters where date == ? and time >= ? and time <= ? and PANEL_VOLTAGE > 5;"           
            db.execute(sql_avg_minute,(date_find,str(t1),str(t2))) 
            rows= db.fetchall()#average power
            avg_pv_current = [value[0] for value in rows]
            avg_pv_current = round(avg_pv_current[0],2)
            #print(f"Current PV on {date_find} : {avg_pv_current}")


            sql_avg_minute ="select avg(PANEL_VOLTAGE) from parameters where date == ? and time >= ? and time <= ? and PANEL_VOLTAGE > 5;"           
            db.execute(sql_avg_minute,(date_find,str(t1),str(t2))) 
            rows= db.fetchall()#average power
            avg_pv_voltage = [value[0] for value in rows]
            avg_pv_voltage = round(avg_pv_voltage[0],2)
            #print(f"Voltage PV on {date_find} : {avg_pv_voltage}")

            sql_avg_minute ="select avg(CURRENT) from parameters where date == ? and time >= ? and time <= ? and  VOLTAGE > 200;"           
            db.execute(sql_avg_minute,(date_find,str(t1),str(t2))) 
            rows= db.fetchall()#average power
            avg_pv_current_ac = [value[0] for value in rows]
            avg_pv_current_ac = round(avg_pv_current_ac[0],2)
            #print(f"AC Current on {date_find} : {avg_pv_current_ac}")

            sql_avg_minute ="select avg(VOLTAGE) from parameters where date == ? and time >= ? and time <= ? and VOLTAGE > 200;"           
            db.execute(sql_avg_minute,(date_find,str(t1),str(t2))) 
            rows= db.fetchall()#average power
            avg_pv_voltage_ac = [value[0] for value in rows]
            avg_pv_voltage_ac = round(avg_pv_voltage_ac[0],2)
            #print(f"AC Voltage on {date_find} : {avg_pv_voltage_ac}")

             #*********************************************************2
            avg_pv_power_ac2 = total_day_ac_power_used[1]
            date_find = avg_pv_power_ac2[0]
            date2=date_find
            avg_pv_power_ac2 = round(avg_pv_power_ac2[1],2)
            #print(f"Power AC avg on {date_find} : {avg_pv_power_ac2}")

            avg_pv_power_load2 = total_day_solar_power_used[1]
            avg_pv_power_load2 = round(avg_pv_power_load2[1],2)
            #print(f"Power PV Load on {date_find} : {avg_pv_power_load2}")

            avg_pv_power2 = total_day_solar_power_produced[1]
            avg_pv_power2 = round(avg_pv_power2[1],2)
            #print(f"Power PV from voltage on {date_find} : {avg_pv_power2}")


            sql_avg_minute ="select avg(PANEL_CURRENT) from parameters where date == ? and time >= ? and time <= ? and PANEL_VOLTAGE > 5;"           
            db.execute(sql_avg_minute,(date_find,str(t1),str(t2))) 
            rows= db.fetchall()#average power
            avg_pv_current2 = [value[0] for value in rows]
            avg_pv_current2 = round(avg_pv_current2[0],2)
           # print(f"Current PV on {date_find} : {avg_pv_current2}")


            sql_avg_minute ="select avg(PANEL_VOLTAGE) from parameters where date == ? and time >= ? and time <= ? and PANEL_VOLTAGE > 5;"           
            db.execute(sql_avg_minute,(date_find,str(t1),str(t2))) 
            rows= db.fetchall()#average power
            avg_pv_voltage2 = [value[0] for value in rows]
            avg_pv_voltage2 = round(avg_pv_voltage2[0],2)
            #print(f"Voltage PV on {date_find} : {avg_pv_voltage2}")

            sql_avg_minute ="select avg(CURRENT) from parameters where date == ? and time >= ? and time <= ? and  VOLTAGE > 200;"           
            db.execute(sql_avg_minute,(date_find,str(t1),str(t2))) 
            rows= db.fetchall()#average power
            avg_pv_current_ac2 = [value[0] for value in rows]
            avg_pv_current_ac2 = round(avg_pv_current_ac2[0],2)
            #print(f"AC Current on {date_find} : {avg_pv_current_ac2}")

            sql_avg_minute ="select avg(VOLTAGE) from parameters where date == ? and time >= ? and time <= ? and VOLTAGE > 200;"           
            db.execute(sql_avg_minute,(date_find,str(t1),str(t2))) 
            rows= db.fetchall()#average power
            avg_pv_voltage_ac2 = [value[0] for value in rows]
            avg_pv_voltage_ac2 = round(avg_pv_voltage_ac2[0],2)
            #print(f"AC Voltage on {date_find} : {avg_pv_voltage_ac2}")
             #*********************************************************3
            avg_pv_power_ac3 = total_day_ac_power_used[2]
            date_find = avg_pv_power_ac3[0]
            date3=date_find
            avg_pv_power_ac3 = round(avg_pv_power_ac3[1],2)
            #print(f"Power AC avg on {date_find} : {avg_pv_power_ac3}")

            avg_pv_power_load3 = total_day_solar_power_used[2]
            avg_pv_power_load3 = round(avg_pv_power_load3[1],2)
            #print(f"Power PV Load on {date_find} : {avg_pv_power_load3}")

            avg_pv_power3 = total_day_solar_power_produced[2]
            avg_pv_power3 = round(avg_pv_power3[1],2)
            #print(f"Power PV from voltage on {date_find} : {avg_pv_power3}")


            sql_avg_minute ="select avg(PANEL_CURRENT) from parameters where date == ? and time >= ? and time <= ? and PANEL_VOLTAGE > 5;"           
            db.execute(sql_avg_minute,(date_find,str(t1),str(t2))) 
            rows= db.fetchall()#average power
            avg_pv_current3 = [value[0] for value in rows]
            avg_pv_current3 = round(avg_pv_current3[0],2)
            #print(f"Current PV on {date_find} : {avg_pv_current3}")


            sql_avg_minute ="select avg(PANEL_VOLTAGE) from parameters where date == ? and time >= ? and time <= ? and PANEL_VOLTAGE > 5;"           
            db.execute(sql_avg_minute,(date_find,str(t1),str(t2))) 
            rows= db.fetchall()#average power
            avg_pv_voltage3 = [value[0] for value in rows]
            avg_pv_voltage3 = round(avg_pv_voltage3[0],2)
            #print(f"Voltage PV on {date_find} : {avg_pv_voltage3}")

            sql_avg_minute ="select avg(CURRENT) from parameters where date == ? and time >= ? and time <= ? and  VOLTAGE > 200;"           
            db.execute(sql_avg_minute,(date_find,str(t1),str(t2))) 
            rows= db.fetchall()#average power
            avg_pv_current_ac3 = [value[0] for value in rows]
            avg_pv_current_ac3 = round(avg_pv_current_ac3[0],2)
            #print(f"AC Current on {date_find} : {avg_pv_current_ac3}")

            sql_avg_minute ="select avg(VOLTAGE) from parameters where date == ? and time >= ? and time <= ? and VOLTAGE > 200;"           
            db.execute(sql_avg_minute,(date_find,str(t1),str(t2))) 
            rows= db.fetchall()#average power
            avg_pv_voltage_ac3 = [value[0] for value in rows]
            avg_pv_voltage_ac3 = round(avg_pv_voltage_ac3[0],2)
            #print(f"AC Voltage on {date_find} : {avg_pv_voltage_ac3}")
             #*********************************************************4
            avg_pv_power_ac4 = total_day_ac_power_used[3]
            date_find = avg_pv_power_ac4[0]
            date4=date_find
            avg_pv_power_ac4 = round(avg_pv_power_ac4[1],2)
            #print(f"Power AC avg on {date_find} : {avg_pv_power_ac4}")

            avg_pv_power_load4 = total_day_solar_power_used[3]
            avg_pv_power_load4 = round(avg_pv_power_load4[1],2)
            #print(f"Power PV Load on {date_find} : {avg_pv_power_load4}")

            avg_pv_power4 = total_day_solar_power_produced[3]
            avg_pv_power4 = round(avg_pv_power4[1],2)
            #print(f"Power PV from voltage on {date_find} : {avg_pv_power4}")


            sql_avg_minute ="select avg(PANEL_CURRENT) from parameters where date == ? and time >= ? and time <= ? and PANEL_VOLTAGE > 5;"           
            db.execute(sql_avg_minute,(date_find,str(t1),str(t2))) 
            rows= db.fetchall()#average power
            avg_pv_current4 = [value[0] for value in rows]
            avg_pv_current4 = round(avg_pv_current4[0],2)
            #print(f"Current PV on {date_find} : {avg_pv_current4}")


            sql_avg_minute ="select avg(PANEL_VOLTAGE) from parameters where date == ? and time >= ? and time <= ? and PANEL_VOLTAGE > 5;"           
            db.execute(sql_avg_minute,(date_find,str(t1),str(t2))) 
            rows= db.fetchall()#average power
            avg_pv_voltage4 = [value[0] for value in rows]
            avg_pv_voltage4 = round(avg_pv_voltage4[0],2)
            #print(f"Voltage PV on {date_find} : {avg_pv_voltage4}")

            sql_avg_minute ="select avg(CURRENT) from parameters where date == ? and time >= ? and time <= ? and  VOLTAGE > 200;"           
            db.execute(sql_avg_minute,(date_find,str(t1),str(t2))) 
            rows= db.fetchall()#average power
            avg_pv_current_ac4 = [value[0] for value in rows]
            avg_pv_current_ac4 = round(avg_pv_current_ac4[0],2)
            #print(f"AC Current on {date_find} : {avg_pv_current_ac4}")

            sql_avg_minute ="select avg(VOLTAGE) from parameters where date == ? and time >= ? and time <= ? and VOLTAGE > 200;"           
            db.execute(sql_avg_minute,(date_find,str(t1),str(t2))) 
            rows= db.fetchall()#average power
            avg_pv_voltage_ac4 = [value[0] for value in rows]
            avg_pv_voltage_ac4 = round(avg_pv_voltage_ac4[0],2)
            #print(f"AC Voltage on {date_find} : {avg_pv_voltage_ac4}")
             #*********************************************************5
            avg_pv_power_ac5 = total_day_ac_power_used[4]
            date_find = avg_pv_power_ac5[0]
            date5=date_find
            avg_pv_power_ac5 = round(avg_pv_power_ac5[1],2)
            #print(f"Power AC avg on {date_find} : {avg_pv_power_ac5}")

            avg_pv_power_load5 = total_day_solar_power_used[4]
            avg_pv_power_load5 = round(avg_pv_power_load5[1],2)
            #print(f"Power PV Load on {date_find} : {avg_pv_power_load5}")

            avg_pv_power5 = total_day_solar_power_produced[4]
            avg_pv_power5 = round(avg_pv_power5[1],2)
            #print(f"Power PV from voltage on {date_find} : {avg_pv_power5}")


            sql_avg_minute ="select avg(PANEL_CURRENT) from parameters where date == ? and time >= ? and time <= ? and PANEL_VOLTAGE > 5;"           
            db.execute(sql_avg_minute,(date_find,str(t1),str(t2))) 
            rows= db.fetchall()#average power
            avg_pv_current5 = [value[0] for value in rows]
            avg_pv_current5 = round(avg_pv_current5[0],2)
            #print(f"Current PV on {date_find} : {avg_pv_current5}")


            sql_avg_minute ="select avg(PANEL_VOLTAGE) from parameters where date == ? and time >= ? and time <= ? and PANEL_VOLTAGE > 5;"           
            db.execute(sql_avg_minute,(date_find,str(t1),str(t2))) 
            rows= db.fetchall()#average power
            avg_pv_voltage5 = [value[0] for value in rows]
            avg_pv_voltage5 = round(avg_pv_voltage5[0],2)
            #print(f"Voltage PV on {date_find} : {avg_pv_voltage5}")

            sql_avg_minute ="select avg(CURRENT) from parameters where date == ? and time >= ? and time <= ? and  VOLTAGE > 200;"           
            db.execute(sql_avg_minute,(date_find,str(t1),str(t2))) 
            rows= db.fetchall()#average power
            avg_pv_current_ac5 = [value[0] for value in rows]
            avg_pv_current_ac5 = round(avg_pv_current_ac5[0],2)
            #print(f"AC Current on {date_find} : {avg_pv_current_ac5}")

            sql_avg_minute ="select avg(VOLTAGE) from parameters where date == ? and time >= ? and time <= ? and VOLTAGE > 200;"           
            db.execute(sql_avg_minute,(date_find,str(t1),str(t2))) 
            rows= db.fetchall()#average power
            avg_pv_voltage_ac5 = [value[0] for value in rows]
            avg_pv_voltage_ac5 = round(avg_pv_voltage_ac5[0],2)
            #print(f"AC Voltage on {date_find} : {avg_pv_voltage_ac5}")

        return jsonify({
                        'date1':date1,
                        'avg_pv_power': avg_pv_power,
                        'avg_pv_current': avg_pv_current,
                        'avg_pv_voltage': avg_pv_voltage,
                        'avg_pv_power_load': avg_pv_power_load,
                        'avg_pv_power_ac': avg_pv_power_ac,
                        'avg_pv_current_ac': avg_pv_current_ac,
                        'avg_pv_voltage_ac': avg_pv_voltage_ac,

                        'date2':date2,
                        'avg_pv_power2': avg_pv_power2,
                        'avg_pv_current2': avg_pv_current2,
                        'avg_pv_voltage2': avg_pv_voltage2,
                        'avg_pv_power_load2': avg_pv_power_load2,
                        'avg_pv_power_ac2': avg_pv_power_ac2,
                        'avg_pv_current_ac2': avg_pv_current_ac2,
                        'avg_pv_voltage_ac2': avg_pv_voltage_ac2,

                        'date3':date3,
                        'avg_pv_power3': avg_pv_power3,
                        'avg_pv_current3': avg_pv_current3,
                        'avg_pv_voltage3': avg_pv_voltage3,
                        'avg_pv_power_load3': avg_pv_power_load3,
                        'avg_pv_power_ac3': avg_pv_power_ac3,
                        'avg_pv_current_ac3': avg_pv_current_ac3,
                        'avg_pv_voltage_ac3': avg_pv_voltage_ac3,

                        'date4':date4,
                        'avg_pv_power4': avg_pv_power4,
                        'avg_pv_current4': avg_pv_current4,
                        'avg_pv_voltage4': avg_pv_voltage4,
                        'avg_pv_power_load4': avg_pv_power_load4,
                        'avg_pv_power_ac4': avg_pv_power_ac4,
                        'avg_pv_current_ac4': avg_pv_current_ac4,
                        'avg_pv_voltage_ac4': avg_pv_voltage_ac4,

                        'date5':date5,
                        'avg_pv_power5': avg_pv_power5,
                        'avg_pv_current5': avg_pv_current5,
                        'avg_pv_voltage5': avg_pv_voltage5,
                        'avg_pv_power_load5': avg_pv_power_load5,
                        'avg_pv_power_ac5': avg_pv_power_ac5,
                        'avg_pv_current_ac5': avg_pv_current_ac5,
                        'avg_pv_voltage_ac5': avg_pv_voltage_ac5,
                        
                        
                        
                        
                        
                        
                        })




if __name__ == '__main__':
    start = time.time()
    try:
        power_ac_thread.start()
        power_pv_thread.start()
        current_pv_thread.start()
        voltage_pv_thread.start()
        solar_saved_thread.start()
        power_ac_thread.join()
        power_pv_thread.join()
        current_pv_thread.join()
        voltage_pv_thread.join()
        solar_saved_thread.join()
        delta_time = round((time.time()-start)/60,2)
        print(f"delta time: {delta_time} min")
        #loop_power_ac_thread.start()
        #loop_power_solar_saved_thread.start()
        #loop_power_solar_thread.start()
        #loop_solar_current_thread.start()
        #loop_solar_voltage_thread.start()
    except Exception as e:
        print("Cannot restart thread")
        print(e)
    print(enable_server)

    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
        #app.run(debug=False, threaded=True, host='0.0.0.0', port=5000)


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
