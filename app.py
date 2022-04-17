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
index_data = int(0)

print(f"START at {datetime.datetime.now()}")

file =  open("/home/nano/projects/electrical_datalogger_jetsonnano_arduino/ac_telemetry.csv","r+")
ac_writer = csv.writer(file,delimiter=',',quoting=csv.QUOTE_MINIMAL)
reader = csv.reader(file)
data = list(reader)
n_lines= len(data)
print(f"number of lines: {n_lines}  ")

app = Flask(__name__)



#print(f"FIRST ROW: {string_tmp}  {ac_value}")



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
        # Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)
#-------------------------------DISPLAY END


def oled_disp():
    global var_volt_ac, var_current_ac,bus
    while not is_shutdown:


        # Shell scripts for system monitoring from here : https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
        cmd = "ifconfig wlan0 | grep 'inet ' | cut -c 14-26"
        IP = subprocess.check_output(cmd, shell = True )
            # Write two lines of text.
        draw.text((x, top),       "IP: " + str(IP.decode('utf-8')),  font=font, fill=255)
        draw.text((x, top+8),      "Amp: " +str(var_current_ac)+"A", font=font, fill=255)
        draw.text((x, top+16),     "Volt: " +str(var_volt_ac)+"Vac",  font=font, fill=255)
        # draw.text((x, top+24),    str(SwapUsage.decode('utf-8')),  font=font, fill=255)
        # draw.text((x, top+32),    str(Disk.decode('utf-8')),  font=font, fill=255)
        # draw.text((x, top+40),    str(Date.decode('utf-8')),  font=font, fill=255)
        # Display image.
        disp.image(image)
        disp.display()
        time.sleep(1)

def gather_data():
    global var_volt_ac, var_current_ac,bus

    address = 0x20
    try:

        bus.write_byte_data(address, 0, 0x0A)
        read = bus.read_i2c_block_data(address,0,4)
        #print(read)
        #print('\n'.join('{}: {}'.format(*val) for val in enumerate(read)))
        ac_curr = read[0]<<8 | read[1]
        #print('AC Current in ',end="")
        ac_curr = ac_curr/1000.0
        var_current_ac = ac_curr
        #print("%.3f" %ac_curr,end="")
        #print('A  ',end="")
        ac_volt_dig = read[2]<<8 | read[3]
        #print(ac_volt_dig)
        anaVolt = ac_volt_dig*(realvolt / 1023.0)
        volt_in = anaVolt*(1000+880000)/1000
        volt_ac = (volt_in/1.4142135623730950488016887242097)+21
        #print('AC Voltage in ',end="")
        v_string = str(volt_ac)
        volt_ac_string = v_string[0] +v_string[1] +v_string[2] +v_string[3] +v_string[4]+ v_string[5]+ v_string[6]
        var_volt_ac = volt_ac_string
        #print(volt_ac_string,end="")
        #print("%.3f" %volt_ac,end="")
        #print('Vac')

    except:
        print(f"ERROR gather 0x20 i2c disconnection at {datetime.datetime.now()}")
        print(f"ERROR gather 0x20 restarting at {datetime.datetime.now()}")
    finally:
        5
    today = date.today()
    d1 = today.strftime("%Y/%m/%d")
    from datetime import datetime
    now = datetime.now()
    d2 = now.strftime("%H:%M:%S")
    ac_writer.writerow([d1,d2,volt_ac*ac_curr,volt_ac,ac_curr])
    file.flush()

    oled_disp()
    return [volt_ac,ac_curr]

def gather_loop():
    global var_volt_ac,var_current_ac
    while not is_shutdown:
        [ac_current, ac_voltage] = gather_data()
        var_volt_ac = ac_voltage
        var_current_ac = ac_current
        time.sleep(0.1)

gather_thread = Thread(target=gather_loop)
display_thread = Thread(target=oled_disp)


#signal handling service

def stop(sig, frame):
  print(f"SIGTERM at {datetime.datetime.now()}")
  global is_shutdown
  is_shutdown = True
  file.close()
  exit(1)

signal.signal(signal.SIGINT, stop)

@app.route('/')
def index():
    return render_template('index.html', title='Sensor1', max=30)



@app.route('/_sensor1', methods=['GET'])
def sensorLive():
    
    def generate_random_data():
        with app.app_context(): 
            global data,index_data, var_current_ac
            newdate = ""
            newCurrent = 0.0
            if(index_data < n_lines):
                newdate =  data[int(index_data)][0] + " " + data[int(index_data)][1]
                newCurrent = data[int(index_data)][4]
            if(index_data >= n_lines):
                newdate = datetime.datetime.now()
                newCurrent = var_current_ac
            index_data=int(index_data)+1
            json_data = json.dumps({'date': newdate, 'current': newCurrent, 'reset':reset}, default=str)
            yield f"data:{json_data}\n\n"
            time.sleep(.1)

    return Response(generate_random_data(), mimetype='text/event-stream')


if __name__ == '__main__':
   
    #gather_thread.start()
    #display_thread.start()
    
    app.run(debug=True, threaded=True, host='0.0.0.0', port=5000)
    gather_data()
    print(f"END at {datetime.datetime.now()}")
    #gather_thread.join()
    #ac_tel_file.close()
    
    


