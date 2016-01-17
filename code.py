#!/usr/bin/env python

import serial
import time
import os
import grovepi
import sqlite3
import django
import sys
import send
import speakService
import LCD
from djangoConnect import *
from basic import *
import signal

f = open('/home/pi/code.pid', 'w')
f.write(str(os.getpid()))
f.close()

def quit_slow(arg, arg2):
	exit(0)
	
signal.signal(signal.SIGINT, quit_slow)

sys.stdout = open('test', 'w')

CPrint("Initalizing")


#Definition donnees Arduino
try:
	arduino = Sensor.objects.get(place="arduino")
	ser = serial.Serial(arduino.code, 115200)
except:
	CPrint("$$$$ HIGH DAMAGE ERROR, can't connect to the Arduino. ***** Functionality like activating or desactivating alarm are off")
else :
	CPrint("Successfully connected to " + arduino.code)
ser.open()

#Definition GrovePi
try:
	buzzer = Sensor.objects.get(place="buzzer")
	CPrint("Buzzer is at " + str(buzzer.code))
	buzzer = int(buzzer.code)
	grovepi.pinMode(buzzer, "OUTPUT")
	led = Sensor.objects.get(place="LED")
	CPrint("LED is at " + str(led.code))
	led = int(led.code)
	grovepi.pinMode(led, "OUTPUT")
except:
	CPrint("$$$$ HIGH DAMAGE ERROR, progam can't access the buzzer or/and the led")
else:
	CPrint("GrovePi connect success")

#Definition pour recuperer l'etat de l alarme
def getStateAlarm():
	f = open('/webapps/django/RPI/gestion/alarm.txt', 'r')
	stateAlarm = f.read()
	f.close()
	return stateAlarm

#Modification etat alarme
def modifyAlarm(etat):
	f = open('/webapps/django/RPI/gestion/alarm.txt', 'w')
	f.write(etat)
	f.close()
	grovepi.digitalWrite(led, int(etat))
	CPrint("Alarm's state change to " + etat)
	
#Envoi signal PIR
def SignalPIR(sensor):
	f = open('PIR.txt', 'w')
	f.write(sensor)
	f.close()
	print("[F]Signal PIR envoye")
	
def AddNFCEntry(tag):
	tagPassed = NFCTag.objects.get(tag=tag)
	NFCLog(tag=tagPassed).save()
	
users = NFCTag.objects.all()

canHumidity = True
canTemperature = True

while True:
	data = ser.readline()
	if(data[1:5] == "DATA"):
		usrNFC = data[55:62]
		print(usrNFC)
		for user in users:
			if (usrNFC in user.tag):
				AddNFCEntry(usrNFC)
				CPrint("An authentificated user has pass his RFID Tag")
				if("1" in getStateAlarm()):
					CPrint("!!!! Requested alarm to shut down")
					modifyAlarm("0")
					grovepi.digitalWrite(buzzer, 0)
					LCD.setAll("Alarme desactivee", "green")
				elif ("0" in getStateAlarm()):
					CPrint("!!!! Requested alarm to turn on in 15 seconds")
					LCD.setAll("L'alarm va s'enclencher dans 15s", "orange")
					time.sleep(15)
					modifyAlarm("1")
					LCD.setAll("Alarme activee", "red")
				time.sleep(2)
	elif(data[1:5] == "NULL"):
		AddNFCEntry("0")
		LCD.setAll("Aucun id associe. Incident enregistre", "red")
	'''

	elif len(data) >= 4:
		if data[0:2] == "49": #Motion PIR
			if "1" in getStateAlarm():
				SignalPIR(data[2:4])
				print("[/]Capteur " + data[2:4])

		elif data[0:2] == "48": #Humidity
			sensor = data[2:4]
			humidity = int(data[4:6])
			print("[DEBUG]Humidity value " + str(humidity) + " received at sensor " + str(sensor))
			if humidity != 0 and canHumidity == True:
				s = Sensor.objects.get(code=sensor)
				Humidity(sensor=s, value=humidity).save()
				print("[DJANGO]Humidity value successfully inserted")
				canHumidity = False
				canTemperature = True
			else :
				send.sendMail("Sensor "+ str(sensor) + " appears to not work properly. Indeed it returns a humidity of " + str(humidity) + ". Check this out")
		elif data[0:2] == "47": #Temperature
			sensor = data[2:4]
			temp = int(data[4:6])
			print("[DEBUG]Temperature value " + str(temp) + " received at sensor " + str(sensor))
			if canTemperature  == True:
				s = Sensor.objects.get(code=sensor)
				Temperature(sensor=s, value=temp).save()
				print("[DJANGO]Temperature successfully inserted")
				canHumidity = True
				canTemperature = False
		elif data[0:2] == "46": #Light Value
			sensor = data[2:4]
			value = int(data[4:8])
			print("[INFO]Sensor " + str(sensor) + " send " + str(value) + " as a light value")
			s = Sensor.objects.get(code=sensor)
			LightValue(sensor=s, value=value).save()
			print("[DJANGO]Value successfully inserted")
			'''
			
			
