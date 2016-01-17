import time
import serial
import grovepi
import sys
import picamera
import re
import os
import send
from djangoConnect import *
import bitlyAPI
import LCD
from basic import *
import sqlite3
import signal

CPrint("Initalizing")

pidDB = sqlite3.connect('shareData.db')
pidCursor = pidDB.cursor()
actualPID = os.getpid()
CPrint("I'm PID " + str(actualPID))
pidCursor.execute("""UPDATE pid SET pid = ? WHERE name = ?""", (actualPID, "sqliteAlarm"))
pidDB.commit()
pidCursor.execute("""SELECT pid FROM pid WHERE name = 'camera'""")
camera = pidCursor.fetchone()[0]

try:
	alarm = Sensor.objects.get(place="alarm")
	buzzer = Sensor.objects.get(place="buzzer")
	CPrint("Alarm is at "+ str(alarm.code))
	CPrint("Buzzer is at " + str(buzzer.code))
	buzzer = int(buzzer.code)
	alarm = int(alarm.code)
	grovepi.pinMode(alarm, "INPUT")
	grovepi.pinMode(buzzer, "OUTPUT")
except:
	CPrint("&&&& FATAL ERROR CAN'T ACCESS ALARM SENSOR AND/OR BUZZER")
	CPrint("&&&& SHUTTING DOWN")
	#Envoyer SMS au staff
	sys.exit()
else:
	CPrint("GrovePi connection success")

#Def
def addTimeshot(timeshot):
	pidCursor.execute("""UPDATE timeshot SET timeshot = ? WHERE id = 1""", (str(timeshot),))
	pidDB.commit()

def getStateAlarm():
	f = open('/webapps/django/RPI/gestion/alarm.txt', 'r')
	stateAlarm = f.read()
	f.close()
	return stateAlarm

def getPIR():
	f = open('/home/pi/Desktop/Alarm/PIR.txt', 'r')
	stateAlarm = f.read()
	f.close()
	return stateAlarm

def modifyAlarm(etat):
	f = open('/webapps/django/RPI/gestion/alarm.txt', 'w')
	f.write(etat)
	f.close()
	CPrint("Alarm's state modified to "+ etat)

def modifyPIR():
	f = open('/home/pi/Desktop/Alarm/PIR.txt', 'w')
	f.write("0")
	f.close()


debugMode = False

calibrationTime = 30
waitingTime = 10

grovepi.pinMode(alarm, "INPUT")
grovepi.pinMode(buzzer, "OUTPUT")

grovepi.digitalWrite(alarm, 0)

CPrint("Calibrating sensor")
i = 0

start = time.time()

while i < calibrationTime:
	sys.stdout.write('.')
	time.sleep(1)
	i = i +1

CPrint("Done")
time.sleep(0.5)

i = 0
t = 0

while True:
	try:
		if ("1" in getStateAlarm()):
			#Alarm is on
			a = grovepi.digitalRead(alarm)
			i = i + 1
			if (a == 1):
				t = t +1
			if(i > 50):
				t = 0
				i = 0
			if (t > 4):
				t = 0
				#Movement detected
				CPrint("!!!! Movement detected. Waiting 10 sec for desactivating")
				LCD.setAll("Passez votre tag", "purple")
				time.sleep(waitingTime)
				#Is alarm still on ?
				if ("1" in getStateAlarm()):
					#Yes
					CPrint("!!!! Intruder in the building !")
					#grovepi.digitalWrite(buzzer, 1)
					if(debugMode):
						nowDate = time.strftime('%d/%m a %H:%S')
						send.sendSMSToStaff("Alarme declenche a " + nowDate)
					else:
						timeshot = time.time()
						insertMov(alarm, timeshot)
						addTimeshot(timeshot)
						os.kill(int(camera), signal.SIGUSR1)
						
						nowDate = time.strftime('%d/%m a %H:%S')
						send.sendSMS("Alarme declenchee le " + nowDate +". +INFO http://rpialbrecht.ddns.net/panel .")
						time.sleep(30)
						#send.sendMail('Alarme declenchee le ' + nowDate + '.La video est disponible sur le panel ou a l\'adresse ' + str(url) + ' et l\'image a ' + str(imageurl) + '.') 
					time.sleep(20)
				else:
					#Alarme shut down by user
					CPrint("Alarm shut down by valid user")
					LCD.setAll("Alarme desactivee", "info")
		else:
			time.sleep(60)
			

		
	except KeyboardInterrupt:
		grovepi.digitalWrite(buzzer, 0)
		pidDB.close()
		break
