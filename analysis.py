#!/usr/local/bin/python3.8
# FLASK_APP=app.py
# FLASK_ENV=development
# flask run

import sqlite3
import datetime as dt



#import matplotlib
#matplotlib.use('Tkagg')
#import matplotlib.pyplot as plt
from flask import Flask, Response, render_template, request, session, jsonify
import json

import time

import subprocess


from threading import Thread

from numpy import power

import socket
from datetime import datetime, timedelta
from tzlocal import get_localzone # pip install tzlocal

enable_server = 0
date_power_ac_list =[]
date_volt_pv_list =[]
date_amp_pv_list =[]
power_list =[]
power_list_panel=[]
voltage_list_panel=[]
current_list_panel=[]
solar_power_saved_list =[]

report = []
reset = 0
reset2 = 0
reset4 = 0
db_backup = "/home/nano/projects/electrical_datalogger_jetsonnano_arduino/ac_telemetry_backup.db"
db_result = "/home/nano/projects/electrical_datalogger_jetsonnano_arduino/ac_result.db"
result_bkp="/home/nano/projects/electrical_datalogger_jetsonnano_arduino/ac_result_backup.db"
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
date_ac_tot=[]
power_ac_tot=[]

pv_voltage = 0.0
pv_current = 0.0
pv_enable = False
pv_date = ''
up_to_hour = 24
up_to_min = 59

days    = 1
enable_once=False

counter = 0

enable_reading_bk=False

cmd = "cp -a /home/nano/projects/electrical_datalogger_jetsonnano_arduino/ac_telemetry.db /home/nano/projects/electrical_datalogger_jetsonnano_arduino/ac_telemetry_backup.db"
returned_value = subprocess.call(cmd, shell=True)  # returns the exit code in unix
print("databased backed ac_telemetry")
time.sleep(1)

cmd = "cp -a /home/nano/projects/electrical_datalogger_jetsonnano_arduino/ac_result.db /home/nano/projects/electrical_datalogger_jetsonnano_arduino/ac_result_backup.db"
returned_value = subprocess.call(cmd, shell=True)  # returns the exit code in unix
print("init databased backed ac_result")
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



sql_lastrow = "SELECT * FROM parameters ORDER BY id DESC LIMIT 1;"




def getPanel_voltage():
    global result_bkp,voltage_list_panel,enable_server,date_volt_pv_list
    voltage_list_panel = []
    date_volt_pv_list = []


    conn = sqlite3.connect(result_bkp, check_same_thread=False)
    db = conn.cursor()
    #print("getting PV VOLT AVG list")
    
    date_find =getDate(0)

    sql_avg_minute ="select TIME,PANEL_VOLTAGE from summary where date == ?;"        
    db.execute(sql_avg_minute,(date_find,))
          
    rows= db.fetchall()#average power
    date_volt_pv_list = [date_find+"_"+sl[0] for sl in rows]
    voltage_list_panel = [sl[1] for sl in rows]
            


    #print("done with PV Volt list")
    enable_server +=1 
    return voltage_list_panel



def getPanel_current():
    global result_bkp,current_list_panel,enable_server,date_amp_pv_list

    current_list_panel = []
    date_amp_pv_list = []


    conn = sqlite3.connect(result_bkp, check_same_thread=False)
    db = conn.cursor()
    #print("getting PV CURRENT AVG list")
    
    date_find =getDate(0)

    sql_avg_minute ="select TIME,PANEL_CURRENT from summary where date == ?;"        
    db.execute(sql_avg_minute,(date_find,))
          
    rows= db.fetchall()#average power
    date_amp_pv_list = [date_find+"_"+sl[0] for sl in rows]
    current_list_panel = [sl[1] for sl in rows]
            

    #print("done with PV current list")
    enable_server +=1 
    return current_list_panel
#*************************************** Solar Power produced

def getPower():
    global power_list,date_power_ac_list,enable_server,result_bkp
    power_list = []
    date_power_ac_list = []


    conn = sqlite3.connect(result_bkp, check_same_thread=False)
    db = conn.cursor()
    #print("getting power WH list")
    
    date_find =getDate(0)

    sql_avg_minute ="select TIME,AC_POWER from summary where date == ?;"        
    db.execute(sql_avg_minute,(date_find,))
          
    rows= db.fetchall()#average power
    date_power_ac_list = [date_find+"_"+sl[0] for sl in rows]
    power_list = [sl[1] for sl in rows]

    #print("done with AC Power list")
    enable_server +=1 
    return power_list

#************************************** Power used by load
def getPower_saved():
    global db_backup,enable_server,up_to_hour,up_to_min,total_day_solar_power_used,solar_power_saved_list,days
    solar_power_saved_list = []
    total_day_solar_power_used=[]

    conn = sqlite3.connect(db_backup, check_same_thread=False)
    db = conn.cursor()
    #print("getting Solar power WH saved list")
    for i in range(days):
        
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

    #print("done with Solar Power saved list")
    enable_server +=1 
    return solar_power_saved_list

#################################
def getPower_min():
    global db_backup
    power_list = []
    date_power_ac_list = []

    date_find =getDate(0)  
    conn = sqlite3.connect(db_backup, check_same_thread=False)
    db = conn.cursor()
    #print("getting power WH list")
         
    rows= db.fetchall()#average power
    step=2
    for hour in range(24):
        for min in range(0,59,step):    
            t1 = dt.datetime.strptime(str(hour)+":"+str(min)+":00", '%H:%M:%S').time()
            t2 = dt.datetime.strptime(str(hour)+":"+str(min+1)+":00", '%H:%M:%S').time()
            #t1 = str(hour)+":00:00"
            #t2 = str(hour)+":59:00"
          
            sql_avg_minute ="select avg(POWER) from parameters where date == ? and time >= ? and time <= ? ;"    
            
            db.execute(sql_avg_minute,(date_find,str(t1),str(t2)))
          
            rows= db.fetchall()#average power
           
            
            if(str(rows)!="[(None,)]"):
                #print(f" Records {str(rows)} time {t2} date: {date_find}")
                for sl in rows:
                    if(sl[0]!=None):
                        date_power_ac_list.append(date_find+"_"+str(t2))
                        power_raw=[round(sl[0],2)]
                        power_list.append(round(power_raw[0],2))
                       # print(f"{date_power_ac_list[-1]} :::::  {power_list[-1]}")
            else:
                break
                
    return date_power_ac_list,power_list

#******************THREADSA

def power_ac_loop():
    global enable_reading_bk
    while True:
        getPower()
        getPanel_current()
        getPanel_voltage()
        time.sleep(60)

def power_detail_loop():
    global  date_ac_tot,power_ac_tot,reset4   
    while True:        
        start = time.time()
        print(f"power detail reading")
        date_ac_tot,power_ac_tot = getPower_min()
        print(power_ac_tot)
        print(f"power detail delta: {time.time()-start}")
        time.sleep(10)


power_ac_thread = Thread(target=power_ac_loop)
power_ac_detail_thread = Thread(target=power_detail_loop)





@app.route('/')
def index():


    return render_template('index.html', title='Sensor1',date_t=getDate(0),date_y=getDate(1), max=30)


#*********************************************************************************AC POWER
@app.route('/_sensor1', methods=['GET'])
def sensorAC():
    
    def generate_random_data():
        with app.app_context(): 
            global reset,power_list,date_power_ac_list,enable_server
            #print(f"enable server: {enable_server}")
            if enable_server >=3:
                m_date = getDate(0)
                json_data = json.dumps({'date': date_power_ac_list, 'current': power_list, 'reset':reset, 'date_analisys':m_date}, default=str)
                yield f"data:{json_data}\n\n"
            
            time.sleep(1)

    return Response(generate_random_data(), mimetype='text/event-stream')
#*********************************************************************************PANEL POWER PRODUCED
@app.route('/_sensor2', methods=['GET'])
def sensorPowerPV():
    
    def generate_random_data():
        with app.app_context(): 
            global pv_voltage,pv_current,pv_enable,pv_date

            if(pv_enable):
                    pv_enable = False
                    pv_power = pv_voltage*pv_current
                    json_data = json.dumps({'pv_date': pv_date, 'pv_power': pv_power}, default=str)
                    yield f"data:{json_data}\n\n"
                    
            
            time.sleep(1)

    return Response(generate_random_data(), mimetype='text/event-stream')
#CURRENT PANEL

@app.route('/_sensor3', methods=['GET'])
def sensorVoltPV():
    
    def generate_random_data():
        with app.app_context(): 
            global voltage_list_panel,current_list_panel,reset2,enable_server,date_amp_pv_list
            if enable_server >=3:
                m_date = getDate(0)
                json_data = json.dumps({'date_panel': date_amp_pv_list, 'var_panel_current':current_list_panel,'var_panel_volt':voltage_list_panel, 'reset2':reset2,'date_analisys_2':m_date}, default=str)
                yield f"data:{json_data}\n\n"
            
            time.sleep(1)

    return Response(generate_random_data(), mimetype='text/event-stream')
#CURRENT AC
@app.route('/_sensor4', methods=['GET'])
def sensorCurrentPV():
    
    def generate_random_data():
        global reset4,date_ac_tot,power_ac_tot
        #if reset4==1:
        with app.app_context():
                global pv_voltage,pv_current,pv_enable,pv_date
                
                with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
                    line_before = []

                    try:
                        s.connect(("127.0.0.1",12345))
                        data = s.recv(4096)
                        #if not data:
                                #break
                        data = data.decode('utf-8')
                        line = eval(data)
                        if(line[0]!=""):
                                var_date= line[0]
                                var_time=line[1]
                                var_current_ac = line[3]
                                var_power_ac = line[4]
                                var_volt_ac = line[2]
                                var_panel_volt = line[5]
                                var_panel_curr = line[6]
                                var_panel_power = line[7]
                                if(line_before!=line):
                                    #print(line)
                                    line_before = line
                                string_date = var_date +"-"+var_time
                                pv_date = string_date
                                pv_voltage = float(var_panel_volt)
                                pv_current = float(var_panel_curr)
                                pv_enable = True
                                print(f"{string_date}  {var_power_ac}")
                                json_data = json.dumps({'date_ac_power': date_ac_tot, 'ac_power': power_ac_tot,'date_ac_power_sec': string_date, 'ac_power_sec': var_power_ac}, default=str)
                                yield f"data:{json_data}\n\n"
                    except Exception as e:
                        #print("Connection refused")
                        print(e)
        

       # time.sleep(1)

    return Response(generate_random_data(), mimetype='text/event-stream')


def getParams(date_to_find):
    global result_bkp,counter
    if(counter>=300):
        cmd = "cp -a /home/nano/projects/electrical_datalogger_jetsonnano_arduino/ac_result.db /home/nano/projects/electrical_datalogger_jetsonnano_arduino/ac_result_backup.db"
        returned_value = subprocess.call(cmd, shell=True)  # returns the exit code in unix
        print(f"getParams databased backed ac_result {counter}")
        counter = 0
        
        time.sleep(1)
        
    else:
        counter +=1
    #print(counter)
    try:
        conn2 = sqlite3.connect(result_bkp, check_same_thread=False)
        db2 = conn2.cursor()
        date1=getDate(date_to_find)
        sql_avg_minute ="select SUM(AC_POWER) from summary where date == ?"
        db2.execute(sql_avg_minute,(date1,)) 
        rows= db2.fetchall()#average power
        val = [value[0] for value in rows]
        if(val[0] !=None):
            avg_pv_power_ac = round(val[0],2)
        else:
            avg_pv_power_ac=0
        precio=round(avg_pv_power_ac/1000.00,2)
        #print(f"Power AC avg on {date1} : {precio}")

        sql_avg_minute ="select SUM(PANEL_LOAD) from summary where date == ?"

        db2.execute(sql_avg_minute,(date1,)) 
        rows= db2.fetchall()#average power
        val = [value[0] for value in rows]
        if(val[0] !=None):
            avg_pv_power_load = round(val[0],2)
        else:
            avg_pv_power_load=0
        #print(f"Power PV Load on {date1} : {avg_pv_power_load}")

        sql_avg_minute ="select SUM(PANEL_POWER) from summary where date == ?"
        db2.execute(sql_avg_minute,(date1,)) 
        rows= db2.fetchall()#average power
        val = [value[0] for value in rows]
        if(val[0] !=None):
            avg_pv_power = round(val[0],2)
        else:
            avg_pv_power=0
        #print(f"Power PV from voltage on {date_find} : {avg_pv_power}")


        sql_avg_minute ="select AVG(PANEL_CURRENT) from summary where date == ?"
        db2.execute(sql_avg_minute,(date1,)) 
        rows= db2.fetchall()#average power
        val = [value[0] for value in rows]
        if(val[0] !=None):
            avg_pv_current = round(val[0],2)
        else:
            avg_pv_current=0
        #print(f"Current PV on {date_find} : {avg_pv_current}")


        sql_avg_minute ="select AVG(PANEL_VOLTAGE) from summary where date == ?"
        db2.execute(sql_avg_minute,(date1,)) 
        rows= db2.fetchall()#average power
        val = [value[0] for value in rows]
        if(val[0] !=None):
            avg_pv_voltage = round(val[0],2)
        else:
            avg_pv_voltage=0
        #print(f"Voltage PV on {date_find} : {avg_pv_voltage}")

        sql_avg_minute ="select AVG(AC_CURRENT) from summary where date == ?"
        db2.execute(sql_avg_minute,(date1,)) 
        rows= db2.fetchall()#average power
        val = [value[0] for value in rows]
        if(val[0] !=None):    
            avg_pv_current_ac = round(val[0],2)
        else:
            avg_pv_current_ac=0
        #print(f"AC Current on {date1} : {avg_pv_current_ac}")

        sql_avg_minute ="select AVG(AC_VOLTAGE) from summary where date == ?"
        db2.execute(sql_avg_minute,(date1,)) 
        rows= db2.fetchall()#average power
        val = [value[0] for value in rows]
        if(val[0] !=None):   
            avg_pv_voltage_ac = round(val[0],2)
        else:
            avg_pv_voltage_ac = 0
        #print(f"AC Voltage on {date1} : {avg_pv_voltage_ac}")
        return date1,round(avg_pv_power_ac/1000,2),avg_pv_power_load,avg_pv_power,avg_pv_current,avg_pv_voltage,avg_pv_current_ac,avg_pv_voltage_ac,precio
    except Exception as e:
        print(e)
        cmd = "cp -a /home/nano/projects/electrical_datalogger_jetsonnano_arduino/ac_result.db /home/nano/projects/electrical_datalogger_jetsonnano_arduino/ac_result_backup.db"
        returned_value = subprocess.call(cmd, shell=True)  # returns the exit code in unix
        print("error in getparams databased backed ac_result")
        time.sleep(1)

    

@app.route("/extract_data", methods=['POST'])
def extractData():
    with app.app_context():
        



        
        [date1,avg_pv_power_ac,avg_pv_power_load,avg_pv_power,avg_pv_current,avg_pv_voltage,avg_pv_current_ac,avg_pv_voltage_ac,precio] = getParams(0)
        [date2,avg_pv_power_ac2,avg_pv_power_load2,avg_pv_power2,avg_pv_current2,avg_pv_voltage2,avg_pv_current_ac2,avg_pv_voltage_ac2,precio2] = getParams(1)
        [date3,avg_pv_power_ac3,avg_pv_power_load3,avg_pv_power3,avg_pv_current3,avg_pv_voltage3,avg_pv_current_ac3,avg_pv_voltage_ac3,precio3] = getParams(2)
        [date4,avg_pv_power_ac4,avg_pv_power_load4,avg_pv_power4,avg_pv_current4,avg_pv_voltage4,avg_pv_current_ac4,avg_pv_voltage_ac4,precio4] = getParams(3)
        [date5,avg_pv_power_ac5,avg_pv_power_load5,avg_pv_power5,avg_pv_current5,avg_pv_voltage5,avg_pv_current_ac5,avg_pv_voltage_ac5,precio5] = getParams(4)
        return jsonify({
                        'date1':date1,
                        'avg_pv_power': avg_pv_power,
                        'avg_pv_current': avg_pv_current,
                        'avg_pv_voltage': avg_pv_voltage,
                        'avg_pv_power_load': avg_pv_power_load,
                        'avg_pv_power_ac': avg_pv_power_ac,
                        'avg_pv_current_ac': avg_pv_current_ac,
                        'avg_pv_voltage_ac': avg_pv_voltage_ac,
                        'precio': precio,

                        'date2':date2,
                        'avg_pv_power2': avg_pv_power2,
                        'avg_pv_current2': avg_pv_current2,
                        'avg_pv_voltage2': avg_pv_voltage2,
                        'avg_pv_power_load2': avg_pv_power_load2,
                        'avg_pv_power_ac2': avg_pv_power_ac2,
                        'avg_pv_current_ac2': avg_pv_current_ac2,
                        'avg_pv_voltage_ac2': avg_pv_voltage_ac2,
                        'precio2': precio2,

                        'date3':date3,
                        'avg_pv_power3': avg_pv_power3,
                        'avg_pv_current3': avg_pv_current3,
                        'avg_pv_voltage3': avg_pv_voltage3,
                        'avg_pv_power_load3': avg_pv_power_load3,
                        'avg_pv_power_ac3': avg_pv_power_ac3,
                        'avg_pv_current_ac3': avg_pv_current_ac3,
                        'avg_pv_voltage_ac3': avg_pv_voltage_ac3,
                        'precio3': precio3,

                        'date4':date4,
                        'avg_pv_power4': avg_pv_power4,
                        'avg_pv_current4': avg_pv_current4,
                        'avg_pv_voltage4': avg_pv_voltage4,
                        'avg_pv_power_load4': avg_pv_power_load4,
                        'avg_pv_power_ac4': avg_pv_power_ac4,
                        'avg_pv_current_ac4': avg_pv_current_ac4,
                        'avg_pv_voltage_ac4': avg_pv_voltage_ac4,
                        'precio4': precio4,

                        'date5':date5,
                        'avg_pv_power5': avg_pv_power5,
                        'avg_pv_current5': avg_pv_current5,
                        'avg_pv_voltage5': avg_pv_voltage5,
                        'avg_pv_power_load5': avg_pv_power_load5,
                        'avg_pv_power_ac5': avg_pv_power_ac5,
                        'avg_pv_current_ac5': avg_pv_current_ac5,
                        'avg_pv_voltage_ac5': avg_pv_voltage_ac5,
                        'precio5': precio5,
                        
                        
                        
                        
                        
                        
                        })

@app.route('/reset4', methods=['POST'])
def test():
    global reset4
    output = request.get_json()
    result = json.loads(output) #this converts the json output to a python dictionary
    reset4=result.get("reset_value_4")
    #print(f"############################# {reset4}") # Printing the new dictionary
    
    return result


if __name__ == '__main__':
    print("version 1.0.5")
     
    start = time.time()
    try:
        power_ac_thread.start()
        power_ac_detail_thread.start()
    except Exception as e:
        print("Cannot restart thread")
        print(e)
    #print(enable_server)

    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
        #app.run(debug=False, threaded=True, host='0.0.0.0', port=5000)
