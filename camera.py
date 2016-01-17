#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  camera.py
#  
#  Copyright 2015 Jérémy  Albrecht <ajeremyalbrecht@gmail.com>
#  

import time
import picamera
import sqlite3
import signal
import os
from basic import *

pidDB = sqlite3.connect('shareData.db')
pidCursor = pidDB.cursor()
actualPID = os.getpid()
CPrint("I'm PID " + str(actualPID))
pidCursor.execute("""UPDATE pid SET pid = ? WHERE name = ?""", (actualPID, "camera"))
pidDB.commit()
pidCursor.execute("""SELECT pid FROM pid WHERE name = 'sqliteAlarm'""")
sqliteAlarm = pidCursor.fetchone()[0]

def CameraFootage(signum, stack):
	CPrint("Received:" + str(signum))
	if signum == 10:
		CPrint("Beginning timelapse")
		with picamera.PiCamera() as camera:
			camera.start_preview()
			camera.annotate_text = time.strftime('%Y-%m-%d %H:%M:%S')
			time.sleep(1)
			timeShot = pidCursor.execute("""SELECT timeshot FROM timeshot WHERE id = 1""").fetchone()[0]
			os.mkdir("/webapps/django/RPI/gestion/templates/media/" + str(timeShot) + "/")
			i = 0
			for filename in camera.capture_continuous('/webapps/django/RPI/gestion/templates/media/' + str(timeShot) + '/img{counter:03d}.jpg'):
				if i < 20:
					print("Captured %s" %filename)
					time.sleep(1)
					i = i +1
				else:
					i = 0
					break

signal.signal(signal.SIGUSR1, CameraFootage)

while True:
	time.sleep(3)
