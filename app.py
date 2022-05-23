#!/usr/local/bin/python3.8


#ps -fA | grep python3
from ast import While
from email.utils import localtime

from threading import Thread
import time


import math 


from cv2 import sqrt
import smbus2

import signal

import sqlite3

import socket


#from signal import signal, SIGPIPE, SIG_DFL  
#signal(SIGPIPE,SIG_DFL)


shutdown = True
serverup =True
connected =True
realvolt = 4.47
# DECLARATIONS
var_current_ac= ""
var_volt_ac = ""
POWER = ""
reset = 0
redifine_current = 0.0
redifine_voltage = 0.0
samples = 0
redifine_panel_current = 0.0
redifine_panel_voltage = 0.0
samples_panel = 0
panel_power = 0.0
start = 0
index_data = int(0)
path="/home/nano/projects/electrical_datalogger_jetsonnano_arduino/ac_telemetry.db"
path_result="/home/nano/projects/electrical_datalogger_jetsonnano_arduino/ac_result.db"
named_tuple = time.localtime() # get struct_time
date_str,time_hr = time.strftime("%Y-%m-%d %H:%M:%S", named_tuple).split(" ")
d1 = date_str
d2 = time_hr
m_panel_volt =""
m_panel_current =""
m_panel_power =""

time_str = time.strptime(d2, "%H:%M:%S")
hour_before = str(time_str.tm_hour)



print(f"START at {time_hr} and hour_before: {hour_before}")





#print(f"FIRST ROW: {string_tmp}  {ac_value}")

bus = smbus2.SMBus(0)

conn = sqlite3.connect(path, check_same_thread=False)

conn.execute('''CREATE TABLE IF NOT EXISTS parameters
            (ID INTEGER PRIMARY KEY AUTOINCREMENT,
            DATE           TEXT    NOT NULL,
            TIME            TEXT     NOT NULL,
            VOLTAGE        REAL,
            CURRENT         REAL,
            POWER          REAL,
            PANEL_VOLTAGE   REAL,
            PANEL_CURRENT   REAL,
            PANEL_POWER     REAL);''')

conn2 = sqlite3.connect(path_result, check_same_thread=False)
print ("Opened database successfully")
conn2.execute('''CREATE TABLE IF NOT EXISTS summary
            (ID INTEGER PRIMARY KEY AUTOINCREMENT,
            DATE           TEXT    NOT NULL,
            TIME            TEXT     NOT NULL,
            AC_VOLTAGE        REAL,
            AC_CURRENT         REAL,
            AC_POWER          REAL,
            PANEL_VOLTAGE   REAL,
            PANEL_CURRENT   REAL,
            PANEL_POWER     REAL,
            PANEL_LOAD  REAL);''')
print ("Opened database  RESULTS successfully")
db = conn.cursor()

def gather_data():
    global bus, hour_before,redifine_voltage, redifine_current,samples,start,redifine_panel_current,redifine_panel_voltage,samples_panel,panel_power
    address = 0x20
    try:

        bus.write_byte_data(address, 0, 0x0A)
        time.sleep(0.2)  # Wait for device to actually settle down
        read = bus.read_i2c_block_data(address,0,8)
        time.sleep(0.2)  # Wait for device to actually settle down
        named_tuple = time.localtime() # get struct_time
        date_str,time_hr = time.strftime("%Y-%m-%d %H:%M:%S", named_tuple).split(" ")
        time_turnon ='06:30:00'
        time_turnoff='23:59:00'
        time_midnight='00:00:00'
        turnON = time.strptime(time_turnon, "%H:%M:%S")
        turnOFF = time.strptime(time_turnoff, "%H:%M:%S")
        time_hr = time.strptime(time_hr, "%H:%M:%S")
        time_midnight = time.strptime(time_midnight, "%H:%M:%S")
        #print(f"{turnOFF} {turnON} {time_hr}")
        if(time_hr>=turnON and time_hr < turnOFF):
            bus.write_byte_data(address, 0, 0x0C)#LOW  TURN ON
            print("TURN ON")
        if(time_hr<turnON and time_hr >= time_midnight):
            bus.write_byte_data(address, 0, 0x0B)#HIGH TURN OFF
            print("TURN OFF")

        #bus.write_byte_data(address, 0, 0x0B)
        #time.sleep(0.2)  # Wait for device to actually settle down
        #VOLTAGE-----------
        ac_volt_dig = read[2]<<8 | read[3]
        #print(ac_volt_dig)
        anaVolt = (ac_volt_dig+0.5)*(realvolt / 1024.0)
        volt_in = anaVolt*(1000+880000)/1000
        volt_ac = (volt_in/math.sqrt(2))+14
        #current-----------
        ac_curr = read[0]<<8 | read[1]
        
        #--reading from panel power
        ac_volt_dig_panel = read[6]<<8 | read[7]
        anaVolt_panel = (ac_volt_dig_panel+0.5)*(realvolt / 1024.0)
        R1 = 40389.61
        R2 = 10000
        volt_in_panel = anaVolt_panel*(R1+R2)/R2
        volt_in_panel = round(volt_in_panel+0.1,2)
        #--reading from panel current
        ac_curr_dig_panel = read[4]<<8 | read[5]  
        ac_curr_dig_panel = (ac_curr_dig_panel+0.5) * (4.47 / 1024.0)
        #print(f"voltage {ac_curr_dig_panel} current ", end="")
        ac_curr_dig_panel = ((ac_curr_dig_panel)-2.22  )/0.066
        ac_curr_dig_panel = round(ac_curr_dig_panel,2)
        #print(ac_curr_dig_panel)

        
        if(volt_ac < 300 and volt_ac > 200):
            redifine_current += ac_curr/1000.0
            redifine_voltage +=volt_ac
            samples +=1
        #print(f"volt_panel {volt_in_panel} cur_panel {ac_curr_dig_panel}")
        if(volt_in_panel < 46 ):
            redifine_panel_current += (ac_curr_dig_panel)
            redifine_panel_voltage +=volt_in_panel
            samples_panel +=1
        
    except Exception as e:
        print(f"ERROR gather 0x20 i2c disconnection")
        print(e)
        volt_ac = 9999
        ac_curr = 9999

        POWER = 0
        #seconds_delay = random.randint(0, 3)
        time.sleep(1)
    d1 = ""
    d2 = ""
    m_volt_ac = ""
    m_current_ac= ""
    m_panel_volt = ""
    m_panel_current= ""
    m_panel_power = 0.0
    end = time.time()
    POWER = 0.0
    if(end-start >=1) :
        #print(f"second {samples} samples_panel {samples_panel}")
        start = end
        if(samples !=0):
            current_avg = round(redifine_current/samples,2)
            voltage_avg = round(redifine_voltage/samples,2)
        else:
            current_avg = 0
            voltage_avg = 0
        if(samples_panel !=0):
            panel_current_avg = redifine_panel_current/samples_panel
            panel_voltage_avg = redifine_panel_voltage/samples_panel
        else:
            panel_current_avg = 0
            panel_voltage_avg = 0
        if(samples != 0 and samples_panel !=0):
            m_volt_ac = str(voltage_avg)
            m_current_ac = str(current_avg)  
            named_tuple = time.localtime() # get struct_time
            date_str,time_hr = time.strftime("%Y-%m-%d %H:%M:%S", named_tuple).split(" ")
            d1 = date_str
            d2 = time_hr

            POWER = str(round(voltage_avg*current_avg,2))

            m_panel_current = str(round(panel_current_avg,2))
            m_panel_volt = str(round(panel_voltage_avg,2))
            panel_power = panel_voltage_avg*100/22.5 #regla de tres para llegar a los vatios
            m_panel_power = str(round(panel_power,2))

            redifine_current = 0
            redifine_voltage =0
            samples =0
            redifine_panel_voltage = 0
            redifine_panel_current = 0
            samples_panel = 0
        
    return [d1,d2,m_volt_ac,m_current_ac,POWER,m_panel_volt,m_panel_current,m_panel_power]

def gather_loop():
    global db,conn,conn2,shutdown,start,var_volt_ac,var_current_ac,POWER,d1,d2,m_panel_volt,m_panel_current,m_panel_power,hour_before
    print("Gathering DATA")
    start = time.time()
    while shutdown:
        [d1,d2,var_volt_ac,var_current_ac,POWER,m_panel_volt,m_panel_current,m_panel_power] = gather_data()
        if(d1!=""):
            conn.execute("INSERT INTO parameters (DATE,TIME,VOLTAGE,CURRENT,POWER,PANEL_VOLTAGE,PANEL_CURRENT,PANEL_POWER) \
            VALUES ( ?, ?, ?, ?, ?,?,?,?)",(d1,d2,var_volt_ac,var_current_ac,POWER,m_panel_volt,m_panel_current,m_panel_power))
            tmp = time.strptime(d2, "%H:%M:%S")
            print(f"{tmp.tm_hour}  vs {hour_before}")
            if(int(tmp.tm_hour)!=int(hour_before)):
                try:

                    string_t1 = hour_before+":00:00"
                    string_t2 = str(tmp.tm_hour)+":00:00"
                    sql_avg_minute ="select avg(power) from parameters where date == ? and time >= ? and time <= ?;"           
                    db.execute(sql_avg_minute,(d1,string_t1,string_t2)) 
                    rows= db.fetchall()#average power
                    avg_ac_power_wh = [value[0] for value in rows]
                    avg_ac_power_wh = round(avg_ac_power_wh[0],2)
                    print(f"----------------------------------------------------AC POWER Wh on {string_t2}-{string_t1}: {avg_ac_power_wh}")


                    sql_avg_minute ="select avg(voltage) from parameters where date == ? and time >= ? and time <= ?;"           
                    db.execute(sql_avg_minute,(d1,string_t1,string_t2)) 
                    rows= db.fetchall()#average power
                    avg_ac_voltage = [value[0] for value in rows]
                    avg_ac_voltage = round(avg_ac_voltage[0],2)
                    print(f"----------------------------------------------------AC VOLTAGE on {string_t2}-{string_t1}: {avg_ac_voltage}")



                    sql_avg_minute ="select avg(current) from parameters where date == ? and time >= ? and time <= ?;"           
                    db.execute(sql_avg_minute,(d1,string_t1,string_t2)) 
                    rows= db.fetchall()#average power
                    avg_ac_current = [value[0] for value in rows]
                    avg_ac_current = round(avg_ac_current[0],2)
                    print(f"----------------------------------------------------AC CURRENT Ah on {string_t2}-{string_t1}: {avg_ac_current}")

                    sql_avg_minute ="select avg(PANEL_POWER) from parameters where date == ? and time >= ? and time <= ?;"           
                    db.execute(sql_avg_minute,(d1,string_t1,string_t2)) 
                    rows= db.fetchall()#average power
                    avg_pv_power_produced = [value[0] for value in rows]
                    avg_pv_power_produced = round(avg_pv_power_produced[0],2)*0.75
                    print(f"----------------------------------------------------PV POWER PRODUCED Wh on {string_t2}-{string_t1}: {avg_pv_power_produced}")


                    sql_avg_minute ="select avg(PANEL_CURRENT*PANEL_VOLTAGE) from parameters where date == ? and time >= ? and time <= ?;"           
                    db.execute(sql_avg_minute,(d1,string_t1,string_t2)) 
                    rows= db.fetchall()#average power
                    avg_pv_power_consumed = [value[0] for value in rows]
                    avg_pv_power_consumed = round(avg_pv_power_consumed[0],2)
                    print(f"----------------------------------------------------PV POWER CONSUMED on {string_t2}-{string_t1}: {avg_pv_power_consumed}")


                    sql_avg_minute ="select avg(PANEL_CURRENT) from parameters where date == ? and time >= ? and time <= ?;"           
                    db.execute(sql_avg_minute,(d1,string_t1,string_t2)) 
                    rows= db.fetchall()#average power
                    avg_pv_current = [value[0] for value in rows]
                    avg_pv_current = round(avg_pv_current[0],2)
                    print(f"----------------------------------------------------PV CURRENT on {string_t2}-{string_t1}: {avg_pv_current}")


                    sql_avg_minute ="select avg(PANEL_VOLTAGE) from parameters where date == ? and time >= ? and time <= ?;"           
                    db.execute(sql_avg_minute,(d1,string_t1,string_t2)) 
                    rows= db.fetchall()#average power
                    avg_pv_voltage = [value[0] for value in rows]
                    avg_pv_voltage = round(avg_pv_voltage[0],2)
                    print(f"----------------------------------------------------AvgPV VOLTAGE Wh on {string_t2}-{string_t1}: {avg_pv_voltage}")
                    hour_before= str(tmp.tm_hour)
                    conn2.execute("INSERT INTO summary (DATE,TIME,AC_VOLTAGE,AC_CURRENT,AC_POWER,PANEL_VOLTAGE,PANEL_CURRENT,PANEL_POWER,PANEL_LOAD) \
                VALUES ( ?, ?, ?, ?, ?,?,?,? ,?)",(d1,str(tmp.tm_hour)+":00:00",avg_ac_voltage,avg_ac_current,avg_ac_power_wh,avg_pv_voltage,avg_pv_current,avg_pv_power_produced,avg_pv_power_consumed))
                    conn2.commit()
                except Exception as e:
                    print(f"error SQLITE summary")
                    print(e)
            try:
                conn.commit()

                print(d1,end=" ")
                print(d2,end=" ")
                print(f"panel Volt: {m_panel_volt }V",end=" ")
                print(f"panel Watts: {m_panel_power }W",end=" ")
                print(f"panel Amp: {m_panel_current }A")
                print(d1,end=" ")
                print(d2,end=" ")
                print('AC Voltage in ',end="")

                print(var_volt_ac,end="")

                print(' V',end="")

                print(' AC Current in ',end="")
                print(var_current_ac,end="")
    
                print(' A  ', end='')
                print(' AC POWER ',end="")
                print(POWER,end="")
    
                print(' W ')

                time.sleep(0.2)
            except Exception as e:
                print(f"error SQLITE")
                print(e)
    conn.close()
    print("Gather thread stopped")
    

def socket_loop():
    global shutdown,c,s,var_volt_ac,var_current_ac,d1,d2,POWER,m_panel_volt,m_panel_current,m_panel_power,serverup,connected
    while shutdown:
        with socket.socket() as s:
            port = 12345
            try:    
                s.bind(('127.0.0.1', port))
                s.listen(1)
                connected = True
            except Exception as e:
                print("error binding")
                print(e)
                connected = False
                time.sleep(1)
            while connected:
                c, addr = s.accept()
                print (f"Socket Up and running with a connection from {addr}")
                            
                                #old_time = d2
                                #print("R<", end=" ")
                                
                                #rcvdData = c.recv(4096)
                                #       0   1    2              3          4        5              6              7
                list = [d1,d2,var_volt_ac,var_current_ac,POWER,m_panel_volt,m_panel_current,m_panel_power]
                #print("S>")
                str_sendData = str(list)
                        
                try:
                    c.sendall(str_sendData.encode('utf-8'))
                except Exception as e:
                    print("Broken pipe error on display.py")
                    print(e)
                    time.sleep(1)
                    connected = False
                    c.close()
                    break
                  


            time.sleep(1)
    


gather_thread = Thread(target=gather_loop)
socket_thread = Thread(target=socket_loop)


#signal handling service

def stop(sig, frame):
    global shutdown,serverup,connected
    named_tuple = time.localtime() # get struct_time
    time_str=time.strftime("%Y-%m-%d %H:%M:%S", named_tuple)
    print(f"SIGTERM at {time_str}")
    
    shutdown = False
    serverup=False
    connected=False
    conn.close()
    gather_thread.join()
    
    #socket_thread.join()
    exit(1)

signal.signal(signal.SIGINT, stop)




if __name__ == '__main__':
   
    gather_thread.start()
    socket_thread.start()

    
    
    while shutdown:
        time.sleep(1)
    named_tuple = time.localtime() # get struct_time
    time_str=time.strftime("%Y-%m-%d %H:%M:%S", named_tuple)
    print(f"END at {time_str}")

    
    


