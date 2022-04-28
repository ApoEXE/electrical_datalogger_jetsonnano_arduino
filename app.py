#!/usr/local/bin/python3.8


#ps -fA | grep python3
from ast import While
from email.utils import localtime

from threading import Thread
import time





from cv2 import sqrt
import smbus2

import signal

import sqlite3

import socket


is_shutdown = False
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
start = 0
index_data = int(0)
path="/home/nano/projects/electrical_datalogger_jetsonnano_arduino/ac_telemetry.db"
named_tuple = time.localtime() # get struct_time
time_str=time.strftime("%Y-%m-%d %H:%M:%S", named_tuple)


print(f"START at {time_str}")





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
    global bus, redifine_voltage, redifine_current,samples,start
    address = 0x20
    try:

        bus.write_byte_data(address, 0, 0x0A)
        time.sleep(0.2)  # Wait for device to actually settle down
        read = bus.read_i2c_block_data(address,0,4)
        time.sleep(0.2)  # Wait for device to actually settle down

        #VOLTAGE-----------
        ac_volt_dig = read[2]<<8 | read[3]
        #print(ac_volt_dig)
        anaVolt = (ac_volt_dig+0.5)*(realvolt / 1024.0)
        volt_in = anaVolt*(1000+880000)/1000
        volt_ac = (volt_in/1.4142135623730950488016887242097)+21



        #current-----------
        ac_curr = read[0]<<8 | read[1]
        
        ac_curr = ac_curr/1000.0
        if(volt_ac < 300 and volt_ac > 200):
            redifine_current += ac_curr
            redifine_voltage +=volt_ac
            samples +=1
            
        
    except Exception as e:
        print(f"ERROR gather 0x20 i2c disconnection")
        print(e)
        volt_ac = 9999
        ac_curr = 9999
        POWER = 0
        #seconds_delay = random.randint(0, 3)
        #time.sleep(seconds_delay)
    d1 = ""
    d2 = ""
    m_volt_ac = ""
    m_current_ac= ""
    end = time.time()
    POWER = 0.0
    if(end-start >=1 and samples!=0):
        start = end
    
        current_avg = round(redifine_current/samples,2)
        voltage_avg = round(redifine_voltage/samples,2)

        m_volt_ac = str(voltage_avg)
        
        m_current_ac = str(current_avg)  
        named_tuple = time.localtime() # get struct_time
        date_str,time_hr = time.strftime("%Y-%m-%d %H:%M:%S", named_tuple).split(" ")
        d1 = date_str
        d2 = time_hr
        POWER = str(round(voltage_avg*current_avg,2))


    return [d1,d2,m_volt_ac,m_current_ac,POWER]

def gather_loop():
    global start,var_volt_ac,var_current_ac,POWER,d1,d2
    print("Gathering DATA")
    start = time.time()
    while not is_shutdown:
        [d1,d2,var_volt_ac,var_current_ac,POWER] = gather_data()
        if(d1!=""):
            conn.execute("INSERT INTO ac_parameters (DATE,TIME,VOLTAGE,CURRENT,POWER) \
            VALUES ( ?, ?, ?, ?, ? )",(d1,d2,var_volt_ac,var_current_ac,POWER))
            conn.commit()
            print(d1,end=" ")
            print(d2,end=" ")
            print('AC Voltage in ',end="")

            print(var_volt_ac,end="")

            print(' Vac',end="")

            print(' AC Current in ',end="")
            print(var_current_ac,end="")
  
            print(' A  ')

            time.sleep(0.2)
    conn.close()
    print("Gather thread stopped")
    

def socket_loop():
    global var_volt_ac,var_current_ac,d1,d2,POWER
    while not is_shutdown:
        s = socket.socket()
        port = 12345
        s.bind(('127.0.0.1', port))
        s.listen(1)
        c, addr = s.accept()
        old_time = ""
        print (f"Socket Up and running with a connection from {addr}")
        while not is_shutdown:

                #if(rcvdData!=''):
                    #print(f"S: {rcvdData.decode('utf-8')}")
                if(d1!=""):
                    old_time = d2
                    print("R<", end=" ")
                    rcvdData = c.recv(4096)
                    list = [d1,d2,var_volt_ac,var_current_ac,POWER]
                    print("S>", end=" ")
                    str_sendData = str(list)
                    #str_sendData = [d1,d2,var_volt_ac,var_current_ac,POWER]
                    try:
                        c.send(str_sendData.encode())
                        #time.sleep(0.2)
                    except Exception as e:
                        print("Broken pipe error on display.py")
                        print(e)
                        break
        s.close()
    


gather_thread = Thread(target=gather_loop)
socket_thread = Thread(target=socket_loop)


#signal handling service

def stop(sig, frame):

    named_tuple = time.localtime() # get struct_time
    time_str=time.strftime("%Y-%m-%d %H:%M:%S", named_tuple)
    print(f"SIGTERM at {time_str}")
    global is_shutdown
    is_shutdown = True
    conn.close()
    gather_thread.join()
    
    #socket_thread.join()
    exit(1)

signal.signal(signal.SIGINT, stop)




if __name__ == '__main__':
   
    gather_thread.start()
    socket_thread.start()

    
    
    while not  is_shutdown:
        time.sleep(1)
    named_tuple = time.localtime() # get struct_time
    time_str=time.strftime("%Y-%m-%d %H:%M:%S", named_tuple)
    print(f"END at {time_str}")

    
    


