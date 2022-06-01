#!/usr/local/bin/python3.8
#review https://docs.micropython.org/en/latest/esp8266/tutorial/ssd1306.html
from cmath import e
from email.utils import localtime
import time

import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import subprocess
import socket


import signal

import sqlite3

from threading import Thread
from datetime import datetime, timedelta
from tzlocal import get_localzone # pip install tzlocal

# DECLARATIONS
db_result = "/home/nano/projects/electrical_datalogger_jetsonnano_arduino/ac_result.db"
var_current_ac= ""
var_volt_ac = ""
var_date = ""
var_time = ""
var_panel_volt = ""
var_panel_curr = ""
var_panel_power = ""
var_power_ac = ""

serverup =  True
reconnection =  True
displayup =  True
display_i2c = True


line_before = []


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

def socket_loop():
    global line_before,var_date,var_time,var_current_ac,var_volt_ac,reconnection,var_panel_volt,var_panel_curr,var_power_ac,var_panel_power
    while reconnection:
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
           
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
                            print(line)
                            line_before = line
                time.sleep(1)
            except Exception as e:
                print("Connection refused")
                print(e)
    print("Exit socket_reconnection")


socket_thread = Thread(target=socket_loop)



def stop(sig, frame):
    global reconnection, serverup, displayup
    serverup ==False
    reconnection =  False
    displayup = False
    exit(1)

signal.signal(signal.SIGINT, stop)

def display_oled():
    global displayup,display_i2c,var_date,var_time,var_current_ac,var_volt_ac, serverup,var_panel_volt,var_panel_curr,var_panel_power,var_power_ac
    # 128x32 display with hardware I2C:
    while display_i2c:
        disp = Adafruit_SSD1306.SSD1306_128_64(rst=None, i2c_bus=0, gpio=1) # setting gpio to 1 is hack to avoid platform detection
        time.sleep(0.2)  # Wait for device to actually settle down
        # Initialize library.
        disp.begin()

        # Clear display.
        disp.clear()
        try:
            disp.display()
            displayup = True
        except Exception as e:
                print(f"error I2C display")
                print(e)
                displayup = False
        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.
        width = disp.width
        height = disp.height
        image = Image.new('1', (width, height))

        # Get drawing object to draw on image.
        draw = ImageDraw.Draw(image)

        # Draw a black filled box to clear the image.
        draw.rectangle((0,0,width,height), outline=0, fill=0)

        # Draw some shapes.
        # First define some constants to allow easy resizing of shapes.
        padding = -2
        top = padding
        bottom = height-padding
        # Move left to right keeping track of the current x position for drawing shapes.
        x = 0

        # Load default font.
        font = ImageFont.load_default()

        print("ready to display")

        start = time.time()
        precio = 0.0
        date1 = ''
        hour_counter = 3600
        while displayup == True:
            
            
                    # Draw a black filled box to clear the image.
            draw.rectangle((0,0,width,height), outline=0, fill=0)

                    # Shell scripts for system monitoring from here : https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
            cmd = "ifconfig wlan0 | grep 'inet ' | cut -c 14-26"
            IP = subprocess.check_output(cmd, shell = True )
            cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
            CPU = subprocess.check_output(cmd, shell = True )
            cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%sMB %.2f%%\", $3,$2,$3*100/$2 }'"
            MemUsage = subprocess.check_output(cmd, shell = True )
            cmd = "free -m | awk 'NR==3{printf \"Swap: %s/%sMB %.2f%%\", $3,$2,$3*100/$2 }'"
            SwapUsage = subprocess.check_output(cmd, shell = True )
            cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%dGB %s\", $3,$2,$5}'"
            Disk = subprocess.check_output(cmd, shell = True )
            cmd = "date"
            Date = subprocess.check_output(cmd, shell = True )

                    # Write two lines of text.
                    
            named_tuple = time.localtime() # get struct_time
            date,time_str=time.strftime("%Y-%m-%d %H:%M:%S", named_tuple).split(" ")       
                    
            line1= var_date+"."+ var_time
            line2= "POWER: " +  var_power_ac + " W"
            line3 ="AMP: " +  var_current_ac + " A"
            line4 = "PV (V): " +var_panel_volt
            line5 ="PV (A): " +  var_panel_curr
            line6 =date1
            line7 = "kWh:"+str(precio)
                    
            draw.text((x, top),  line1    ,  font=font, fill=255)
            
            draw.text((x, top+8),line2  ,  font=font, fill=255)
            
            draw.text((x, top+16), line3 ,  font=font, fill=255)
            
            draw.text((x, top+24),line4  ,  font=font, fill=255)
            
            draw.text((x, top+32),line5 ,  font=font, fill=255)
            
            draw.text((x, top+40),line6   , font=font, fill=255)
            
            draw.text((x, top+48), line7  ,  font=font, fill=255)
            # Display image.
            disp.image(image)
            end = time.time()
            if(end-start >1):
                print("time elapsed")
                start = end
                try:
                    if hour_counter >= 7200:
                        result_bkp="/home/nano/projects/electrical_datalogger_jetsonnano_arduino/ac_result_backup.db"
                        cmd = "cp -a /home/nano/projects/electrical_datalogger_jetsonnano_arduino/ac_result.db /home/nano/projects/electrical_datalogger_jetsonnano_arduino/ac_result_backup.db"
                        returned_value = subprocess.call(cmd, shell=True)  # returns the exit code in unix
                        print("databased backed")
                        time.sleep(1)
                        conn2 = sqlite3.connect(result_bkp, check_same_thread=False)
                        db2 = conn2.cursor()
                        date1=getDate(1)
                        sql_avg_minute ="select SUM(AC_POWER) from summary where date == ?"
                        db2.execute(sql_avg_minute,(date1,)) 
                        rows= db2.fetchall()#average power
                        val = [value[0] for value in rows]
                        if(val[0] !=None):
                            avg_pv_power_ac = round(val[0],2)
                        else:
                            avg_pv_power_ac=0
                        precio=round(avg_pv_power_ac/1000.00,2)
                        hour_counter= 0
                    else:
                        hour_counter+=1
                    #print(hour_counter)
                    time.sleep(0.2)  # Wait for device to actually settle down
                    disp.display()
                    time.sleep(0.2)  # Wait for device to actually settle down
                except Exception as e:
                    print(f"ERROR display 0x3C i2c disconnection")
                    print(e)
                    displayup = False
        print("Exit display_loop")
        time.sleep(1)
#signal handling service


if __name__ == '__main__':
   
    socket_thread.start()
    display_oled()