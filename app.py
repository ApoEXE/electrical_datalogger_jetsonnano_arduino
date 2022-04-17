#!/usr/bin/python3
# FLASK_APP=app.py
# FLASK_ENV=development
# flask run
import json
from threading import Thread
import time
import os
import datetime
from datetime import date,datetime
from flask import Flask, Response, render_template, request, session, jsonify


from cv2 import sqrt
import smbus
import time
import Adafruit_SSD1306
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import subprocess
import datetime
import signal

import csv



is_shutdown = False
realvolt = 4.59
# DECLARATIONS
var_current_ac= 0
var_volt_ac = 0
bus = smbus.SMBus(0)
reset = 0




app = Flask(__name__)


ac_tel_file =  open("ac_telemetry.csv","w")
ac_writer = csv.writer(ac_tel_file,delimiter=',',quoting=csv.QUOTE_MINIMAL)

# 128x64 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_64(rst=None, i2c_bus=0, gpio=1) # 
disp.begin()
disp.clear()
disp.display()
width = disp.width
height = disp.height
image = Image.new('1', (width, height))
draw = ImageDraw.Draw(image)
draw.rectangle((0,0,width,height), outline=0, fill=0)
padding = -2
top = padding
bottom = height-padding
x = 0
font = ImageFont.load_default()
#-------------------------------DISPLAY END


def oled_disp():
    global var_volt_ac, var_current_ac,bus
    try:
        # Draw a black filled box to clear the image.
        draw.rectangle((0,0,width,height), outline=0, fill=0)

        # Shell scripts for system monitoring from here : https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
        cmd = "ifconfig wlan0 | grep 'inet ' | cut -c 14-26"
        IP = subprocess.check_output(cmd, shell = True )
         # Write two lines of text.
        draw.text((x, top),       "IP: " + str(IP.decode('utf-8')),  font=font, fill=255)
        draw.text((x, top+8),      "Amp: " +str(var_current_ac)+"A", font=font, fill=255)
        draw.text((x, top+16),     "Volt: " +var_volt_ac+"Vac",  font=font, fill=255)
        # draw.text((x, top+24),    str(SwapUsage.decode('utf-8')),  font=font, fill=255)
        # draw.text((x, top+32),    str(Disk.decode('utf-8')),  font=font, fill=255)
        # draw.text((x, top+40),    str(Date.decode('utf-8')),  font=font, fill=255)
            # Display image.
        disp.image(image)
        disp.display()
    except:
        print(f"i2c disconnection at {datetime.datetime.now()}")
        print(f"restarting at {datetime.datetime.now()}")
    finally:
        5

def gather_data():
    global var_volt_ac, var_current_ac,bus

    address = 0x20
    try:

        bus.write_byte_data(address, 0, 0x0A)
        read = bus.read_i2c_block_data(address,0,4)
        #print(read)
        #print('\n'.join('{}: {}'.format(*val) for val in enumerate(read)))
        ac_curr = read[0]<<8 | read[1]
        print('AC Current in ',end="")
        ac_curr = ac_curr/1000.0
        var_current_ac = ac_curr
        print("%.3f" %ac_curr,end="")
        print('A  ',end="")
        ac_volt_dig = read[2]<<8 | read[3]
        #print(ac_volt_dig)
        anaVolt = ac_volt_dig*(realvolt / 1023.0)
        volt_in = anaVolt*(1000+880000)/1000
        volt_ac = (volt_in/1.4142135623730950488016887242097)+21
        #print('AC Voltage in ',end="")
        v_string = str(volt_ac)
        volt_ac_string = v_string[0] +v_string[1] +v_string[2] +v_string[3] +v_string[4]+ v_string[5]+ v_string[6]
        var_volt_ac = volt_ac_string
        print(volt_ac_string,end="")
        print("%.3f" %volt_ac,end="")
        print('Vac')

    except:
        print(f"i2c disconnection at {datetime.datetime.now()}")
        print(f"restarting at {datetime.datetime.now()}")
    finally:
        5
    today = date.today()
    d1 = today.strftime("%Y/%m/%d")
    now = datetime.time()
    d2 = now.strftime("%H:%M:%S")
    ac_writer.writerow([d1,d2,volt_ac*ac_curr,volt_ac,ac_curr])
    ac_tel_file.flush()
    return [volt_ac,ac_curr]

gather_thread = Thread(target=gather_data)
display_thread = Thread(target=oled_disp)

#signal handling service

def stop(sig, frame):
  print(f"SIGTERM at {datetime.datetime.now()}")
  global is_shutdown
  is_shutdown = True
  ac_tel_file.close()
  exit(1)

signal.signal(signal.SIGINT, stop)

@app.route('/')
def index():
    return render_template('index.html', title='Sensor1', max=30)



@app.route('/_sensor1', methods=['GET'])
def sensorLive():
    
    def generate_random_data():
        with app.app_context(): 
            global var_current_ac,var_volt_ac
            ac_parameters = gather_data()
            newdate = datetime.datetime.now()
            newtemp = ac_parameters[1]
            oled_disp()

            json_data = json.dumps({'date': newdate, 'temp': newtemp, 'reset':reset}, default=str)
            yield f"data:{json_data}\n\n"
            time.sleep(.3)

    return Response(generate_random_data(), mimetype='text/event-stream')


if __name__ == '__main__':
    print(f"START at {datetime.datetime.now()}")
    #gather_thread.start()
    #display_thread.start()
    app.run(debug=True, threaded=True, host='0.0.0.0', port=5000)
    print(f"END at {datetime.datetime.now()}")
    ac_tel_file.close()


