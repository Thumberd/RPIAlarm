#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  send.py
#  
#  Copyright 2015  Albrecht jJrémy
#  
import requests
import sqlite3
import smtplib
from djangoConnect import *
try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO


print("[MODULE]Loading send library")

#DB Connect
db = sqlite3.connect("/webapps/django/RPI/db.sqlite3")
cursor = db.cursor()
print("[DEBUG]DB connect success")

urlfree = 'https://smsapi.free-mobile.fr/sendmsg'
print("[DEBUG]Url Free SMS is" + urlfree)
def sendSMS(text):
	print("[MODULE]Starting sendSMS() def")
	print("[MODULE]Fetching IDs")
	cursor.execute("SELECT * FROM gestion_APIFree")
	rows = cursor.fetchall()
	print("[MODULE]Fetching complete")
	print("[MODULE]Sending ...")
	for row in rows:
		ids = str(row[1])
		passwd = str(row[2])
		params = dict(
			user= ids,
			password = passwd,
			msg=text
		)
		r = requests.get(url=urlfree, params=params, verify=False)
	print("[MODULE]Sending complete")
	print("[MODULE]sendSMS() finished")

def sendMail(text):
	print("[MODULE]Starting sendMail() def")
	fromaddr = 'alarm@rpialbrecht.com'
	server = smtplib.SMTP('smtp.gmail.com:587')
	server.starttls()
	server.login('nasalbrecht@gmail.com', 'LVeuRET1400RKnas')
	print("[MODULE]Fetching emails")
	cursor.execute("SELECT * FROM auth_user")
	rows = cursor.fetchall()
	print("[MODULE]Fetching complete")
	print("[MODULE]Sending ...")
	for row in rows:
		server.sendmail(fromaddr, row[6] ,text)
	server.quit()
	print("[MODULE]Sending complete")

def sendSMSTo(id, text):
	print("[SMS]Sending SMS to " + str(id) + " " + str(text))
	a = APIFree.objects.get(user=id)
	ids = str(a.user)
	passwd = str(a.passwd)
	params = dict(
		user= ids,
		password = passwd,
		msg=text
	)
	r = requests.get(url=urlfree, params=params, verify=False)

def sendSMSToStaff(text):
	a = APIFree.objects.get(isStaff=True)
	ids = str(a.user)
	passwd = str(a.passwd)
	params = dict(
		user= ids,
		password = passwd,
		msg=text
	)
	r = requests.get(url=urlfree, params=params, verify=False)
	print("SMS sent")
