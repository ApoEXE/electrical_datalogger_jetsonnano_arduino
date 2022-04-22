#!/usr/local/bin/python3.8
#review https://docs.micropython.org/en/latest/esp8266/tutorial/ssd1306.html
import time

import board
import busio
import adafruit_ssd1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import subprocess
import socket

import random

s = socket.socket()
serverup =  False
while serverup==False:
    try:
        s.connect(('127.0.0.1',12345))
        serverup = True
    except:
        print("Broken pipe on server side restarting")


path="file:/home/nano/projects/electrical_datalogger_jetsonnano_arduino/ac_telemetry.db?mode=ro"
# DECLARATIONS
var_current_ac= ""
var_volt_ac = ""
var_date = ""
var_time = ""

WIDTH = 128
HEIGHT = 64  # Change to 64 if needed
BORDER = 5
# 128x32 display with hardware I2C:
i2c = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3c)
# Clear display.
oled.fill(0)
oled.show()



# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
image = Image.new("1", (oled.width, oled.height))
# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
image = Image.new("1", (oled.width, oled.height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a white background
draw.rectangle((0, 0, oled.width, oled.height), outline=255, fill=255)

# Draw a smaller inner rectangle
draw.rectangle(
    (BORDER, BORDER, oled.width - BORDER - 1, oled.height - BORDER - 1),
    outline=0,
    fill=0,
)

# Load default font.
font = ImageFont.load_default()




print("before while")
lines_before = 0
line = ''
start = time.time()
while True:
    send_to_server = "request from client"
    try:
        s.send(send_to_server.encode())
        data = s.recv(4096)
        data = data.decode('utf-8')
        line = eval(data)
    except:
        print("Broken pipe on server side restarting")


    
    print(line)
    #line = data.split(",")
  
    var_date= line[0]
    var_time=line[1]
    var_current_ac = line[3]
    var_volt_ac = line[2]
    
            # Draw a black filled box to clear the image.
   

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
    (font_width, font_height) = font.getsize(IP)
    draw.text((oled.width // 2 - font_width // 2, oled.height // 2 - font_height // 2 ),       "IP: " + IP.decode('utf-8'),  font=font, fill=255)
    (font_width, font_height) = font.getsize(var_date)
    draw.text((oled.width // 2 - font_width // 2, oled.height // 2 - font_height // 2 +8),   "DATE: " + var_date,  font=font, fill=255)
    (font_width, font_height) = font.getsize(var_time)
    draw.text((oled.width // 2 - font_width // 2, oled.height // 2 - font_height // 2 +16),   "TIME: " + var_time,  font=font, fill=255)
    (font_width, font_height) = font.getsize(var_current_ac)
    draw.text((oled.width // 2 - font_width // 2, oled.height // 2 - font_height // 2 +24),  "AMP: " +  var_current_ac + " A",  font=font, fill=255)
    (font_width, font_height) = font.getsize(var_volt_ac)
    draw.text((oled.width // 2 - font_width // 2, oled.height // 2 - font_height // 2 +32),  "VOLT: " +  var_volt_ac + " V",  font=font, fill=255)
    (font_width, font_height) = font.getsize(CPU)
    draw.text((oled.width // 2 - font_width // 2, oled.height // 2 - font_height // 2 +40),     CPU.decode('utf-8'), font=font, fill=255)
    (font_width, font_height) = font.getsize(Disk)
    draw.text((oled.width // 2 - font_width // 2, oled.height // 2 - font_height // 2 +48),  "DISK: " +  Disk.decode('utf-8') ,  font=font, fill=255)
    # Display image.
    # Display image
    oled.image(image)
    
    end = time.time()
    if(end-start >5):
        print("time elapsed")
        start = end
        try:
            oled.show()
        except:
            print(f"ERROR display 0x3C i2c disconnection")

    
        
s.close()
