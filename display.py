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


line_before = []
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