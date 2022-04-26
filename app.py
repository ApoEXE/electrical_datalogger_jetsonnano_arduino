#!/usr/local/bin/python3.8


#ps -fA | grep python3
from ast import While

from threading import Thread
import time
import datetime
from datetime import date,datetime



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

index_data = int(0)
path="/home/nano/projects/electrical_datalogger_jetsonnano_arduino/ac_telemetry.db"


print(f"START at {datetime.datetime.now()}")





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
    global var_volt_ac, var_current_ac,bus,POWER,d1,d2, redifine_voltage, redifine_current
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


        
    except:
        #print(f"ERROR gather 0x20 i2c disconnection")
        volt_ac = 9999
        ac_curr = 9999
        POWER = 0
        #seconds_delay = random.randint(0, 3)
        #time.sleep(seconds_delay)
    d1 = ""
    d2 = ""
    m_volt_ac = ""
    m_current_ac= ""
    if(volt_ac < 300 and volt_ac > 200):
    #if(volt_ac < 300 and volt_ac > 200 and (redifine_current != round(ac_curr,2) or redifine_voltage != round(volt_ac,2))):

        redifine_current = round(ac_curr,2)
        redifine_voltage = round(volt_ac,2)

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
    print("Gathering DATA")

    while not is_shutdown:
        [d1,d2,var_volt_ac,var_current_ac,POWER] = gather_data()
        if(d1!=""):
            conn.execute("INSERT INTO ac_parameters (DATE,TIME,VOLTAGE,CURRENT,POWER) \
            VALUES ( ?, ?, ?, ?, ? )",(d1,d2,var_volt_ac,var_current_ac,POWER))
            conn.commit()
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
        s.bind(('0.0.0.0', port))
        s.listen(5)
        c, addr = s.accept()
        print (f"Socket Up and running with a connection from {addr}")
        while not is_shutdown:
                rcvdData = c.recv(4096)
                #print(f"S: {rcvdData}")
                if(d1!=""):
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
  gather_thread.join()
  
  #socket_thread.join()
  exit(1)

signal.signal(signal.SIGINT, stop)




if __name__ == '__main__':
   
    gather_thread.start()
    socket_thread.start()

    
    
    while not  is_shutdown:
        time.sleep(1)

    print(f"END at {datetime.datetime.now()}")

    
    


