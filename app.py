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


from signal import signal, SIGPIPE, SIG_DFL  
signal(SIGPIPE,SIG_DFL)


is_shutdown = False
serverup =True
connected =True
realvolt = 4.59
# DECLARATIONS
var_current_ac= ""
var_volt_ac = ""
d1 = ""
d2 = ""
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
named_tuple = time.localtime() # get struct_time
time_str=time.strftime("%Y-%m-%d %H:%M:%S", named_tuple)
m_panel_volt =""
m_panel_current =""
m_panel_power =""

print(f"START at {time_str}")





#print(f"FIRST ROW: {string_tmp}  {ac_value}")

bus = smbus2.SMBus(0)

conn = sqlite3.connect(path, check_same_thread=False)
print ("Opened database successfully")
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



def gather_data():
    global bus, redifine_voltage, redifine_current,samples,start,redifine_panel_current,redifine_panel_voltage,samples_panel,panel_power
    address = 0x20
    try:

        bus.write_byte_data(address, 0, 0x0A)
        time.sleep(0.2)  # Wait for device to actually settle down
        read = bus.read_i2c_block_data(address,0,8)
        time.sleep(0.2)  # Wait for device to actually settle down
        #bus.write_byte_data(address, 0, 0x0B)
        #time.sleep(0.2)  # Wait for device to actually settle down
        #VOLTAGE-----------
        ac_volt_dig = read[2]<<8 | read[3]
        #print(ac_volt_dig)
        anaVolt = (ac_volt_dig+0.5)*(realvolt / 1024.0)
        volt_in = anaVolt*(1000+880000)/1000
        volt_ac = (volt_in/math.sqrt(2))

        
        #--reading from panel power
        ac_volt_dig_panel = read[6]<<8 | read[7]
        anaVolt_panel = (ac_volt_dig_panel+0.5)*(realvolt / 1024.0)
        volt_in_panel = anaVolt_panel*(28200+10000)/10000
        volt_in_panel = round(volt_in_panel,2)
        #--reading from panel current
        ac_curr_dig_panel = read[4]<<8 | read[5]  
        ac_curr_dig_panel = round(ac_curr_dig_panel,2)




        #current-----------
        ac_curr = read[0]<<8 | read[1]
        
        ac_curr = ac_curr/1000.0
        
        if(volt_ac < 300 and volt_ac > 200):
            redifine_current += ac_curr
            redifine_voltage +=volt_ac
            samples +=1
        if(volt_in_panel < 46 and volt_in_panel >= 1):
            redifine_panel_current += (ac_curr_dig_panel/1000.0)
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
        if(samples != 0 or samples_panel !=0):
            m_volt_ac = str(voltage_avg)
            m_current_ac = str(current_avg)  
            named_tuple = time.localtime() # get struct_time
            date_str,time_hr = time.strftime("%Y-%m-%d %H:%M:%S", named_tuple).split(" ")
            d1 = date_str
            d2 = time_hr
            POWER = str(round(voltage_avg*current_avg,2))

            m_panel_current = str(round(panel_current_avg,2))
            m_panel_volt = str(round(panel_voltage_avg,2))
            panel_power = panel_voltage_avg*100/18.2 #regla de tres para llegar a los watios
            m_panel_power = str(round(panel_power,2))


            redifine_current = 0
            redifine_voltage =0
            samples =0
            redifine_panel_voltage = 0
            redifine_panel_current = 0
            samples_panel = 0

    return [d1,d2,m_volt_ac,m_current_ac,POWER,m_panel_volt,m_panel_current,m_panel_power]

def gather_loop():
    global start,var_volt_ac,var_current_ac,POWER,d1,d2,m_panel_volt,m_panel_current,m_panel_power
    print("Gathering DATA")
    start = time.time()
    while not is_shutdown:
        [d1,d2,var_volt_ac,var_current_ac,POWER,m_panel_volt,m_panel_current,m_panel_power] = gather_data()
        if(d1!=""):
            conn.execute("INSERT INTO parameters (DATE,TIME,VOLTAGE,CURRENT,POWER,PANEL_VOLTAGE,PANEL_CURRENT,PANEL_POWER) \
            VALUES ( ?, ?, ?, ?, ?,?,?,? )",(d1,d2,var_volt_ac,var_current_ac,POWER,m_panel_volt,m_panel_current,m_panel_power))
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
    conn.close()
    print("Gather thread stopped")
    

def socket_loop():
    global var_volt_ac,var_current_ac,d1,d2,POWER,m_panel_volt,m_panel_current,m_panel_power,serverup,connected
    while True:
        s = socket.socket()
        port = 12345
        try:    
            s.bind(('127.0.0.1', port))
            s.listen(1)
            c, addr = s.accept()
            print (f"Socket Up and running with a connection from {addr}")
            connected = False
        except Exception as e:
            print("error binding")
            print(e)
            connected = False
            time.sleep(1)
            
        while True:

                #if(rcvdData!=''):
                    #print(f"S: {rcvdData.decode('utf-8')}")
                if(d1!=""):
                    old_time = d2
                    print("R<", end=" ")
                    rcvdData = c.recv(100)
                    #       0   1    2              3          4        5              6              7
                    list = [d1,d2,var_volt_ac,var_current_ac,POWER,m_panel_volt,m_panel_current,m_panel_power]
                    print("S>", end=" ")
                    str_sendData = str(list)
                    #str_sendData = [d1,d2,var_volt_ac,var_current_ac,POWER]
                    try:
                        c.send(str_sendData.encode())
                        #
                    except Exception as e:
                        print("Broken pipe error on display.py")
                        print(e)
                        time.sleep(1)
                        #connected = False

        s.close()
        time.sleep(1)
    


gather_thread = Thread(target=gather_loop)
socket_thread = Thread(target=socket_loop)


#signal handling service

def stop(sig, frame):
    global is_shutdown,serverup,connected
    named_tuple = time.localtime() # get struct_time
    time_str=time.strftime("%Y-%m-%d %H:%M:%S", named_tuple)
    print(f"SIGTERM at {time_str}")
    
    is_shutdown = True
    serverup=False
    connected=False
    conn.close()
    gather_thread.join()
    
    #socket_thread.join()
    exit(1)

#signal(signal., stop)




if __name__ == '__main__':
   
    gather_thread.start()
    socket_thread.start()

    
    
    while not  is_shutdown:
        time.sleep(1)
    named_tuple = time.localtime() # get struct_time
    time_str=time.strftime("%Y-%m-%d %H:%M:%S", named_tuple)
    print(f"END at {time_str}")

    
    


