# -*- coding: utf-8 -*-
#Importamos la librería serial
import serial
#Importamos la librería de tiempo
import time
#Librería de MQTT para publicar
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

"""------------------------------------CONTROL DE PINES GPIO------------------------------------"""
idc = ["030","031","032","033","034","035","037","080","081","082","083","084","085","087","088","089",
"040","041","042","043","071","077","090","091","093","103","104","105","108","109","119"
]

numc = [
"3135881855","3135927486","3135670333","3135646220","3135666599","3135691884","3135885660","3135658864",
"3135884387","3135660270","3135664037","3135883144","3135658913","3135639957","3135899636","3135642438",
"3135886941","3135647515","3135881890","3135884424","3135886942","3135886935","3135642457","3135674161",
"3135647517","3135884425","3135639944","3135648787","3135886951","3135687177","3135687198"
]


#Inicia la comunicación serial por el puerto ttyS0 a 38400
#Con ls -l /dev puedo saber cuál es el puerto serial 0 o 1
#Se usa esta velocidad porque no falla el módulo
print ("Iniciando la comunicación con el serial")
serie = serial.Serial("/dev/ttyS0", 38400)
#Se cierra el puerto por si había otra comunicación
serie.close()
print ("Cerrando el puerto serial")
#Se abre el puerto serial
serie.open()
print ("Abriendo el puerto serial")


def inicio():
	"""Acomoda el módulo para recibir mensajes"""
	#Escribe AT para comprobar que se está comunicando con el SIM800L
	serie.write( "AT\r\n")
	time.sleep(1)
	print("Colocando el módulo en modo SMS")
	#Pone el módulo en modo SMS
	serie.write( "AT+CMGF=1\r\n")
	time.sleep(1)
	print("Escribiendo 1,0")
	#Muestra el mensaje por el puerto serial
	serie.write( "AT+CNMI=1,0,0,0,0\r\n")
	time.sleep(1)


	
def conex():
	"""Determina si el módulo GSM esta funcionando 
	   Manda AT, si el módulo no responde ok cierra el ciclo infinito
	   Y abre el ciclo infinito para todos los procesos, de no ser así vuelve a
	   empieza a mandar el ok y empieza a contar hasta 3, si llega a 3 sin tener
	   una respuesta de Ok, entonces me manda un correo"""
	#Variable que controla el ciclo infinito
	mal = True
	#Variable que cuenta los errores
	contador = 0
	#Mientras que el sistema mande error al escribir AT
	while mal:
		#Escribe AT en el puerto serial
		serie.write( "AT\r\n")
		serie.reset_input_buffer()
		print ("Escribiendo AT esperando un OK")
		time.sleep(0.5)
		#Lee la respuesta del puerto serial
		read = serie.readline()
		print (("////////////////////////////" + read))
		read = serie.readline()
		print (("////////////////////////////" + read))
		#Si la respuesta es OK
		if  "OK" in read:
			#Controla la variable del ciclo infinito y la pone en falso
			mal = False
			#Pone el contador de errores en 0
			contador = 0
			return True
		#Si la respuesta no es OK (sino error)
		else:
			#Coloca la variable que controla el ciclo infinito en True
			mal = True
			#Cuenta un error
			contador = contador + 1
			print (contador)
			print ("Apagando el SIM800")
			GPIO.output(sim, True)
			time.sleep(2)
			print ("Encendiendo el SIM800")
			GPIO.output(sim, False)
			time.sleep(1)
			inicio()
			#Si el contador es igual a 3
			if (contador == 5):
				pass
				contador = 0
				#Mandar gmal
				return False

				global control
				control = False


def primerx():
	"""Lee la primera línea del puerto serial
	Si llegó un SMS (+CMT) lee la segunda línea"""
	global control
	global hora_con
	global hora_sin
	hx = time.strftime("%H:%M:%S")
	print ("Escribiendo cmgl a las: " + hx)
	serie.write('AT+CMGL="ALL"\r\n')
	serie.reset_input_buffer()
	control = True
	while control:
		#+CMGL: 9,"REC READ","3003859853","","18/02/19,11:42:55-20"
		linea = serie.readline()
		if linea.startswith("+CMGL:") is True:
			cm, r, c1, numero, c2, n, c3, fecha, n2 = linea.split('"')
			cmg, nada = cm.split(",")
			cmgl, id_sms = cmg.split(" ")
			print (id_sms)
			print (numero)
			print (fecha)
			print ("--------------------Llamando a la función segundx--------------------\n")
				#Llama a la función segundx
			#hay, netsi = internet()
			#print ("Conexión a internet: " + str(hay))
			fecha_sms = otra_fecha(fecha)
			#if netsi is 1:
				#hora_con = otra_fecha(fecha)
			#elif netsi is 2:
				#hora_sin = otra_fecha(fecha)
			#consulta_bdd(hora_sin, hora_con)
			segundx(numero, fecha_sms, id_sms)

		if  "OK" in linea:
			control = False
		if  "ERROR" in linea:
			control = False
			print ("-----------------------------------------------------------")
	#print ("FIN")



def otra_fecha(fx):
	"""Hola"""
	fx = fx[0:17]
	#xxxx-xx-xx xx:xx:xx
	separadox = fx.split(',')
	fechax, hora = separadox
	fechay = fechax.split('/')
	anio, mes, dia = fechay
	anio = (("20" + anio))
	fechaz = (anio + "-" + mes + "-" + dia + " " + hora)
	return fechaz



def segundx(numero, fecha_sms, id_sms):
	"""Lee la segunda línea del puerto serial dependiendo del mensaje hará cosas"""
	global id_sms_global
	id_sms_global = id_sms
	#Variable de control del ciclo infinito
	qap = True
	#Inicia un ciclo infinito para leer varias veces el puerto serial
	dato=0;
	while qap :
		#Lee el puerto serial
		segunda = serie.readline()
		print ("Segunda linea: ")
		#Imprime lo leido
		print (segunda)
		if (dato < 2) and ("\r\n" not in segunda): 
			if numero in numc:
				print("Enviando dato: "+ str(dato))
				posi=numc.index(numero)
				consumo,t1,h1,t2,h2,t3,h3,t4,h4,fecha,hora,crc=segunda.split(',')
				fecha = fecha_ok(fecha);
				print(fecha)
				datos={
					"numCasa":int(idc[posi]),
					"consumption": float(consumo), 
					"t1": float(t1),
					"h1": hum(h1), 
					"t2": float(t2), 
					"h2": hum(h2), 
					"t3": float(t3),
					"h3": hum(h3), 
					"t4": float(t4),
					"h4": hum(h4), 
					"date":fecha,
					"hour":hora,
				}
				#print(datos)
				response = requests.post("https://graphql.cclimamagdalena.com/api/v1/houses/simple", json = datos)
				#print(response)
				json_response = response.json()
				#json_response['data']
				#print(json_response)
				dato+=1
				if json_response['status']== 'fail' :
					print("Error en el envio de datos")
					print("No se borra el mensaje")
					print("----------------Fin por error de envio-----------\n")
					qap = False
				elif json_response['status'] == 'success' :
					print("----------------Envio Correcto de mensaje-----------\n")

		elif "\r\n" in segunda: 
			print ("Borrando sms: " + id_sms)
			serie.write( "AT+CMGD=" + id_sms + "\r\n")
			time.sleep(1)
			print ("------------------Fin del ciclo otra razón-------------------\n")
			qap = False
			dato = 0


def consulta_bdd(fecha_menor, fecha_mayor):
	"""Consulta la base de datos entre un intérvalo de fechas"""
	global hora_con
	try:
		if fecha_mayor > fecha_menor:
			print ("Mandando los datos entre " + fecha_menor + " y " + fecha_mayor)
			query = ("SELECT * FROM datos WHERE fecha_sms BETWEEN %s AND %s;")
			datos = (fecha_menor, fecha_mayor)
			cursor_rpi.execute(query, datos)
			for (id, sensor, fecha, tipo, valor, bateria, fecha_sms) in cursor_rpi:
				consulta = ("{} {} {} {} {} {} {}".format(id, sensor,
					fecha, tipo, valor, bateria, fecha_sms))
				print (consulta)
				adecuacion_nueva(consulta)
				hora_con = "0000-00-00 00:00:00"
				publish.single("net", "Se fue el net pero ya regresó", hostname="31.220.62.19")
	except UnboundLocalError:
		print ("No hay nada en la base de datos")


def hum(hume):
	if hume > 99.0:
		return 99.0
	else:
		return hume

	if hume == 0.0:
		return 99.0
	else:
		return hume


	



# def sendmensaje(receptor, mns=""):
# 	"""Función para enviar el mensaje"""
# 	serie.write( 'AT\r\n')
# 	time.sleep(1)
# 	#Le ponemos en modo para SMS
# 	serie.write( 'AT+CMGF=1\r\n')
# 	time.sleep(1)
# 	#Comando para enviar el mensaje, se pasa el valor del número
# 	serie.write( 'AT+CMGS=\"' + receptor + '\"\r\n')
# 	time.sleep(1)
# 	#Se escribe el mensaje
# 	serie.write( mns)
# 	time.sleep(3)
# 	#Termina el menzaje con Ctrl+z
# 	serie.write( ascii.ctrl("z"))
# 	time.sleep(3)
# 	#Le pasamos un fin de linea
# 	serie.write( '\r\n')
# 	print ("Mensaje enviado\n")


# def consulta_bdd_nivel(idx, valor1):
#   """Consulta la base de datos entre un intérvalo de fechas"""
#   try:
#       if idx in id_acequia:
#           if (int(valor1) < 30) or (int(valor1) > 490):
#               print ("Buscando los valores del id: " + idx)
#               query = ("SELECT valor FROM datos WHERE (valor>30) and (valor<490) and (id=" + idx + ");")
#               cursor_rpi.execute(query)
#               for (valor) in cursor_rpi:
#                   consulta = ("{}".format(valor))
#                   valor_ultimo = consulta[1:4]
#               print ("El último valor bueno registrado es: " + valor_ultimo)
#               return valor_ultimo
#           return valor1
#       if idx in id_nivel:
#           if (int(valor1) < 30) or (int(valor1) > 990):
#               print ("Buscando los valores del id: " + idx)
#               query = ("SELECT valor FROM datos WHERE (valor>30) and (valor<990) and (id=" + idx + ");")
#               cursor_rpi.execute(query)
#               for (valor) in cursor_rpi:
#                   consulta = ("{}".format(valor))
#                   valor_ultimo = consulta[1:4]
#               print ("El último valor bueno registrado es: " + valor_ultimo)
#               return valor_ultimo
#           return valor1
#       return valor1
#   except UnboundLocalError:
#       print ("No hay nada en la base de datos")




def fecha_ok(fecha):
	"""Acomoda la fecha y hora para ser guardada en MySQL"""
	#Separa los valores de la fecha por /
	fecha = fecha.split('/')
	#Guarda en una variable el día, mes y año
	dia, mes, anio = fecha
	#Convierte a entero la variable que es un string
	#Con date convierte el día, mes y año al formato de MySQL
	fecha = anio+"/"+mes+"/"+dia
	#Une la fecha y hora para ser guardada en MySQL
	f_h = str(fecha)
	return f_h




def bdd(idx, sensor, fecha, tipo, valor, bateria, fecha_sms):
	"""Función para guardar en la base de datos"""
	datos = (idx, sensor, fecha, tipo, valor, bateria, fecha_sms)
	agregar = ("INSERT INTO datos (id, sensor, fecha, tipo, valor, bateria, fecha_sms)VALUES "
		"(%s, %s, %s, %s, %s, %s, %s);")
	#Ejecuta el comando agregar con los valores datos en MySQL
	#cursor.execute(agregar, datos)
	cursor_rpi.execute(agregar, datos)
	#Es necesario ejecutar commit para que funcione
	#cnx.commit()
	cnx_rpi.commit()


def hora_now():
	"""Función para entregar la hora actual"""
	#Obtiene la hora actual
	hora = time.strftime("%H:%M:%S")
	#Obtiene la fecha actual
	fecha = time.strftime("%Y-%m-%d")
	fecha_total = fecha + " " + hora
	return fecha_total


global infinito
infinito = True
global id_sms_global
id_sms_global = 0
cnt = 0
global net
net = "si"
global hora_con
global hora_sin
hora_con = "0000-00-00 00:00:00"
hora_sin = "0000-00-00 00:00:00"


def perro():
	"""Perro guardian"""
	global control 
	global infinito
	contador = 0
	control = True
	print ("Función de perro guardian")
	while infinito:
		while control:
			print ("Esperando ")
			contador = contador + 1
			time.sleep(3)
			if contador == 100:
				print ("Finalizado, reboot")
				os.system("sudo reboot")
		contador = 0
		time.sleep(3)

hilo_perro = threading.Thread(target=perro)
hilo_perro.start()

#Inicia el ciclo infinito del proyecto
while True:
	#Trata de realizar todo el proyecto
	try:
		#Colocamos la placa en modo BCM
		GPIO.setmode(GPIO.BCM)
		#Definimos el pin donde está el sim
		sim = 23
		#Colocamos el sim como salida
		GPIO.setup(sim, GPIO.OUT)
		print ("Apagando el SIM800")
		#Ponemos el sim en True para apagarlo
		GPIO.output(sim, True)
		#Esperamos dos segundos
		time.sleep(1)
		print ("Encendiendo el SIM800")
		#Ponemos el sim en False para encenderlo
		GPIO.output(sim, False)
		time.sleep(6)
		print ("Llamando a la función de inicio")
		#Llama a la función de inicio
		inicio()
		#Conecta al MySQL de la raspberry
		cnx_rpi = mysql.connector.connect(user='root', password='Contrasena1',
			host='127.0.0.1', database='casas')
		#Crea la variable cursor
		cursor_rpi = cnx_rpi.cursor()
		print ("Infinito: " + str(infinito))
		while infinito:
			ya = time.strftime("%S")
			if (ya[1] == "0"):
				#print ("Llamando a primerx")
				primerx()
				cnt = cnt + 1
				if cnt == 200:
					print ("Apagando el SIM800")
					GPIO.output(sim, True)
					time.sleep(1)
					print ("Encendiendo el SIM800")
					GPIO.output(sim, False)
					time.sleep(6)
					inicio()
					cnt = 0
			time.sleep(1)
	#Si hay un error de nombre de variable o no se puede dividir algún mensaje
	except mysql.connector.Error as err:
		print("Something went wrong: {}".format(err))
	except (ValueError, NameError, AttributeError):
		print ("Hay un error al separar o en una variable o un atributo")
		print(ValueError)
		print(NameError)
		print(AttributeError)
		print ("Borrando sms: " + id_sms_global)
		serie.write( "AT+CMGD=" + id_sms_global + "\r\n")
		time.sleep(1)
		print ("Fin del proceso")
		#Si interrumpo con ctrl c
	except KeyboardInterrupt:
		GPIO.cleanup()
		infinito = False
		control = False
		serie.close()
		#cursor.close()
		cursor_rpi.close()
		#cnx.close()
		cnx_rpi.close()
		print ("Fin del proceso")
		break
	#Cuando finalice el ciclo try
	finally:
		GPIO.cleanup()	
		print ("Fin del try")
