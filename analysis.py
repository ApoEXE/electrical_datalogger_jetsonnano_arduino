#!/usr/local/bin/python3.8
import sqlite3
from datetime import datetime
import numpy as np
import matplotlib
matplotlib.use('Tkagg')
import matplotlib.pyplot as plt
path="ac_telemetry.db"



conn = sqlite3.connect(path, check_same_thread=False)
cur = conn.cursor()
cur.execute(" select * from ac_parameters where date > '2022/04/20' and time > '00:00:00' and time < '23:59:59' and voltage > 200 ;")
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

#plt.show()

