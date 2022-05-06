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



from threading import Thread


# DECLARATIONS
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



def socket_loop():
    global var_date,var_time,var_current_ac,var_volt_ac, serverup,reconnection,var_panel_volt,var_panel_curr,var_power_ac,var_panel_power
    while reconnection:
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.settimeout(1.0)
        print("Connnecting...")
        try:
            
            s.connect(("127.0.0.1",12345))
            serverup=True
            print("connected")
        except Exception as e:
            print("Connection refused")
            print(e)
            serverup = False
        while serverup ==True:
            
            try:
                time.sleep(1)
                print("send to server")
                send_to_server = "request from client"
                s.send(send_to_server.encode())
                #time.sleep(0.2)
                #ready = select.select([s], [], [], 1)
                #if ready[0]:
                    #data = s.recv(4096)
                print("receive")
                data = s.recv(100)
                data = data.decode('utf-8')
                #time.sleep(0.2)
                #print(data)
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
                    print(line)
            except Exception as e:
                print("Broken pipe on server side restarting")
                print(e)
                #time.sleep(10)
                serverup=False
                #reconnection=False
                s.close()
        
            
            
            #line = data.split(",")
        print("Exit socket_loop")
        time.sleep(1)
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
    global display_i2c,var_date,var_time,var_current_ac,var_volt_ac, serverup,var_panel_volt,var_panel_curr,var_panel_power,var_power_ac
    # 128x32 display with hardware I2C:
    while display_i2c:
        disp = Adafruit_SSD1306.SSD1306_128_64(rst=None, i2c_bus=0, gpio=1) # setting gpio to 1 is hack to avoid platform detection
        time.sleep(0.2)  # Wait for device to actually settle down
        # Initialize library.
        disp.begin()

        # Clear display.
        disp.clear()
        disp.display()

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
                    
                    
                    

                    
                    
            draw.text((x, top), "DATE: " + var_date      ,  font=font, fill=255)
            draw.text((x, top+8), "TIME: " + var_time  ,  font=font, fill=255)
            draw.text((x, top+16), "POWER: " +  var_power_ac + " W"  ,  font=font, fill=255)
            draw.text((x, top+24), "AMP: " +  var_current_ac + " A" ,  font=font, fill=255)
            draw.text((x, top+32), "PV (V): " +var_panel_volt ,  font=font, fill=255)
            named_tuple = time.localtime() # get struct_time
            date,time_str=time.strftime("%Y-%m-%d %H:%M:%S", named_tuple).split(" ")
            draw.text((x, top+40), "PV (A): " +  var_panel_curr  , font=font, fill=255)
            draw.text((x, top+48), date+"."+time_str  ,  font=font, fill=255)
            # Display image.
            disp.image(image)
            end = time.time()
            if(end-start >1):
                print("time elapsed")
                start = end
                try:
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