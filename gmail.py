# -*- coding: utf-8 -*-
#Importamos la librería serial
import serial
#Importamos la librería de tiempo
import time
#Librería de email
import smtplib
#Conectar a la base de datos
import mysql.connector
#Importa la librería para modificaciones de tiempo
from datetime import date
#Librería para usar los pines GPIO
import RPi.GPIO as GPIO
#Importamos la librería de ascii para el control z
from curses import ascii
import os
#Importamos la librería que nos permite manejar varios hilos
import threading
import requests
import json

def mail(mensaje, asunto ):

	remitente = "Servidor <ingenieria.energesis@gmail.com>"
	destinatario = "josefcc96@gmail.com"
	

	'''
	Preparo el mail y agrego campos
	'''
	email = """From: %s 
	To: %s 
	MIME-Version: 1.0 
	Content-type: text/html 
	Subject: %s 
	 
	%s
	""" % (remitente, destinatario, asunto, mensaje)
	
	try:
		smtp = smtplib.SMTP('smtp.gmail.com:587')
		smtp.starttls()
		smtp.login('ingenieria.energesis@gmail.com', 'Energesis1.')
		smtp.sendmail(remitente, destinatario, email)
		smtp.quit()
	except Exception as e:
		print(e)



mail("Prueba","prueba")
print("Enviando")