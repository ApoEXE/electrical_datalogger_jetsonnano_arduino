#!/usr/local/bin/python3.8
import sqlite3
import datetime
import matplotlib
matplotlib.use('Tkagg')
import matplotlib.pyplot as plt
path="/home/nano/projects/electrical_datalogger_jetsonnano_arduino/ac_telemetry.db"


print(f"START at {datetime.datetime.now()}")
conn = sqlite3.connect(path, check_same_thread=False)
cur = conn.cursor()
cur.execute("SELECT * FROM ac_parameters;")
rows = cur.fetchall()
print(rows[0])
date=[sl[1] for sl in rows]
time=[sl[2] for sl in rows]
power=[sl[5] for sl in rows]

plt.plot(time, power, 'b-')
#plt.axis([0, 6, 0, 20])
plt.show()