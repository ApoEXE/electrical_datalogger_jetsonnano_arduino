#!/usr/local/bin/python3.8
import sqlite3
import datetime
import matplotlib
matplotlib.use('Tkagg')
import matplotlib.pyplot as plt
path="ac_telemetry3.db"


print(f"START at {datetime.datetime.now()}")
conn = sqlite3.connect(path, check_same_thread=False)
cur = conn.cursor()
cur.execute(" select * from ac_parameters where date > '2022/04/20' and time > '06:00:00' and time < '08:00:00' and voltage > 200 ;")
rows = cur.fetchall()
print(rows[0])
date=[sl[1] for sl in rows]
time=[sl[2] for sl in rows]
power=[sl[5] for sl in rows]
print("Total rows are:  ", len(rows))
plt.plot(time, power, 'b-')
#plt.plot([1,2,3,4], [1,2,3,4], 'b-')
#plt.axis([0, 6, 0, 20])
plt.show()