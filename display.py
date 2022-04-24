#!/usr/local/bin/python3.8
#review https://docs.micropython.org/en/latest/esp8266/tutorial/ssd1306.html
import time

import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import subprocess
import socket

import random

import signal


from threading import Thread





path="file:/home/nano/projects/electrical_datalogger_jetsonnano_arduino/ac_telemetry.db?mode=ro"
# DECLARATIONS
var_current_ac= ""
var_volt_ac = ""
var_date = ""
var_time = ""

serverup =  False

s = socket.socket()


def socket_loop():
    global var_date,var_time,var_current_ac,var_volt_ac, serverup
    while serverup==False:
        try:
            s.connect(('127.0.0.1',12345))
            serverup = True
            send_to_server = "request from client"
            s.send(send_to_server.encode())
            data = s.recv(4096)
            data = data.decode('utf-8')
            line = eval(data)
            var_date= line[0]
            var_time=line[1]
            var_current_ac = line[3]
            var_volt_ac = line[2]
            print(line)
        except:
            print("Broken pipe on server side restarting")
        
        #line = data.split(",")

socket_thread = Thread(target=socket_loop)



def stop(sig, frame):

  s.close()
  exit(1)

signal.signal(signal.SIGINT, stop)

def display_oled():
    global var_date,var_time,var_current_ac,var_volt_ac
    # 128x32 display with hardware I2C:
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
    lines_before = 0
    line = ''
    start = time.time()
    while True:
        
        
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
        draw.text((x, top),       "IP: " + IP.decode('utf-8'),  font=font, fill=255)
        draw.text((x, top+8),   "DATE: " + var_date,  font=font, fill=255)
        draw.text((x, top+16),   "TIME: " + var_time,  font=font, fill=255)
        draw.text((x, top+24),  "AMP: " +  var_current_ac + " A",  font=font, fill=255)
        draw.text((x, top+32),  "VOLT: " +  var_volt_ac + " V",  font=font, fill=255)
        draw.text((x, top+40),     CPU.decode('utf-8'), font=font, fill=255)
        draw.text((x, top+48),  "DISK: " +  Disk.decode('utf-8') ,  font=font, fill=255)
        # Display image.
        disp.image(image)
        time.sleep(0.2)  # Wait for device to actually settle down
        disp.display()
        end = time.time()
        time.sleep(0.2)  # Wait for device to actually settle down
        '''
        if(end-start >5):
            print("time elapsed")
            start = end
            try:
                disp.display()
            except:
                print(f"ERROR display 0x3C i2c disconnection")
            '''
#signal handling service


if __name__ == '__main__':
   
    socket_thread.start()
    display_oled()