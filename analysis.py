#!/usr/local/bin/python3.8
# FLASK_APP=app.py
# FLASK_ENV=development
# flask run
import sqlite3
from datetime import datetime
import numpy as np
import matplotlib
matplotlib.use('Tkagg')
import matplotlib.pyplot as plt
from flask import Flask, Response, render_template, request, session, jsonify
import json

import time

reset = 0.0

path="ac_telemetry.db"
conn = sqlite3.connect(path, check_same_thread=False)
cur = conn.cursor()

app = Flask(__name__)


sql_lastrow = "SELECT * FROM ac_parameters ORDER BY id DESC LIMIT 1;"
sql_dayrecords =" select * from ac_parameters where date > '2022/04/24' and time > '00:00:00' and time < '23:59:59' and voltage > 200 ;"


def matplot_records():
    #

    cur.execute(sql_lastrow)
    rows = cur.fetchall()

    print("Total rows are:  ", len(rows))
    print(rows[0])
    print(rows[len(rows)-1])
    date=[sl[1] for sl in rows]
    time_clock=[sl[2] for sl in rows]
    power=[sl[5] for sl in rows]
    power_np = np.array(power)

    times = np.array(time_clock)
    #times = np.array([datetime.strptime(time, '%H:%M:%S') for time in  time_clock])
    print(times)
    #time_deltas = np.array([(time - times[0]).total_seconds()/60. for time in times])
    #print(f"lenght of time deltas: {len(time_deltas)}")

    plt_times = times
    plt_values = power_np

    #plt_times = times[time_deltas%10==0]
    #plt_values = power_np[time_deltas%10==0]


    plt.plot_date(plt_times, plt_values, 'b-')
    plt.show()

    #plt.plot(time, power, 'b-')
    #plt.xticks(time, rotation='vertical')
    #plt.plot([1,2,3,4], [1,2,3,4], 'b-')
    #plt.axis([0, 6, 0, 20])

    plt.show()


@app.route('/')
def index():
    return render_template('index.html', title='Sensor1', max=30)



@app.route('/_sensor1', methods=['GET'])
def sensorLive():
    
    def generate_random_data():
        with app.app_context(): 
            global path,sql_lastrow,cur

            cur.execute(sql_lastrow)
            rows = cur.fetchall()
    
            newCurrent = rows[0][5]
            newdate = str(rows[0][1]+" "+rows[0][2])
            print(newdate)
            print(newCurrent)

            
            json_data = json.dumps({'date': newdate, 'current': newCurrent, 'reset':reset}, default=str)
            yield f"data:{json_data}\n\n"
            time.sleep(1)

    return Response(generate_random_data(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, threaded=True, host='172.23.6.205', port=5000)