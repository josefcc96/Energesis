# -*- coding: utf-8 -*-
#Importamos la librería serial
import serial
#Importamos la librería de tiempo
import time
#Librería de MQTT para publicar
import paho.mqtt.publish as publish
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
"""------------------------------------CONTROL DE PINES GPIO------------------------------------"""

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
	serie.write("AT\r\n")
	time.sleep(1)
	print("Colocando el módulo en modo SMS")
	#Pone el módulo en modo SMS
	serie.write("AT+CMGF=1\r\n")
	time.sleep(1)
	print("Escribiendo 1,0")
	#Muestra el mensaje por el puerto serial
	serie.write("AT+CNMI=1,0,0,0,0\r\n")
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
		serie.write("AT\r\n")
		serie.reset_input_buffer()
		print ("Escribiendo AT esperando un OK")
		time.sleep(0.5)
		#Lee la respuesta del puerto serial
		read = serie.readline()
		print (("////////////////////////////" + read))
		read = serie.readline()
		print (("////////////////////////////" + read))
		#Si la respuesta es OK
		if "OK" in read:
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
	print (("Escribiendo cmgl a las: " + hx))
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
		if "OK" in linea:
			control = False
		if "ERROR" in linea:
			control = False
		print ("-----------------------------------------------------------")
	print ("FIN")


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
	while qap:
		#Lee el puerto serial
		segunda = serie.readline()
		#segunda = "18 090 090 0000 24/01/2018 13:40:30\n"
		#segunda = "01 012 067.89 012.34 912.34 056.78 0123.45 1234.56 11/02/2018 19:00:19\n"
		#segunda = "fecha"
		print ("Segunda linea: ")
		#Imprime lo leido
		print (segunda)
##		if "3232474531" or "3209870659" in numero:
##			print("----------Transmisor-----------\n")
##			if net == "si":
##				publish.single("bdd_cocodrilo",segunda, hostname="31.220.62.19")
##			print("----------FIN Transmisor-----------\n")
##		idy = segunda[0:2]
		if idy in id_estacion:
			print ("-------Es una estación meteorológica, llamando a la -------\n")
			mejora_estacion(segunda, fecha_sms)
		elif (idy in id_nivel) or (idy in id_acequia) or (idy in id_humedad):
			print ("----------------Es un nodo, llamando a la mejora-----------------\n")
			mejora(segunda, fecha_sms, numero)
		elif "\r\n" in segunda:
			if "fecha" in segunda:
				print ("------------------Me está pidiendo la fecha------------------\n")
				print ("Determinando la hora actual y agregándole 20 segundos")
				#Ejecuta la función hora_20
				#Encargada de dar la fecha y hora actual + 20 segundos
				ho, fe = hora_20()
				#Guarda el mensaje en el formato adecuado
				ms = "f:" + fe + " h:" + ho
				print (("El mensaje enviado es: " + ms))
				#Manda el mensaje de texto con la hora actual + 20 sg
				sendmensaje("+57" + numero, ms)
				#Cierra el ciclo infinito
				print ("Borrando sms: " + id_sms)
				serie.write("AT+CMGD=" + id_sms + "\r\n")
				time.sleep(1)
				print ("---------------------Fin del ciclo Fecha---------------------\n")
				qap = False
			else:
				print ("Borrando sms: " + id_sms)
				serie.write("AT+CMGD=" + id_sms + "\r\n")
				time.sleep(1)
				print ("------------------Fin del ciclo otra razón-------------------\n")
				qap = False


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


def adecuacion_nueva(linea):
	"""Hola"""
	separado = linea.split(' ')
	print ("Dividiendo el mensaje por espacios")
	idx, nombre, fecha, hora, tipo, valor, bat, fecha_sms, hora_sms = separado
	#2 prueba 2018-04-25 10:30:17 luz 1032.87 82 2018-04-25 11:00:56
	#'50','test',CURRENT_TIMESTAMP, 'ph', '"+msg.payload+"','90',CURRENT_TIMESTAMP)
	#'01', 'test', '2016-01-09 09:05:00', 'temp', '047.34', '080', '2018-05-22 17:46:00'
	publicar = ("'" + idx + "', '" + nombre + "', '" + fecha + " " + hora + "', '" + tipo
		+ "', '" + valor + "', '" + bat + "', '" + fecha_sms + " " + hora_sms + "'")
	print (publicar)
##	publish.single("bdd", publicar, hostname="31.220.62.19")
	print ("Enviando a ASOCIENAGA")
	fecha_sms = fecha_sms + " " + hora_sms
	f_h = fecha + " " + hora
	fecha_sms_as = fecha_asocienaga(fecha_sms)
	fecha_as = fecha_asocienaga(f_h)
	asocienaga = ("curl -X POST --header 'Content-Type: application/json' --header 'Accept:"
		" application/json' --header 'API-KEY: hZ23Q.A6+hA12sm@4T0i7wrW!XJ9bwm' -d '{ \"tipo\""
		": \"" + tipo + "\", \"valor\": " + valor + ", \"nombre_sensor\": \"" + nombre + "\", "
		"\"fecha_hora_sms\": \"" + fecha_sms_as + "\", \"fecha_hora_captura\": \"" + fecha_as + "\""
		", \"bateria\": \"" + bat + "\" }' http://pruebas.siara.info.tm/sensor/guardar_dato")
	print (asocienaga)
	os.system(asocienaga)
	time.sleep(0.01)


def mejora_estacion(linea, fecha_sms):
	"""Procesa la información que llega en la línea del mensaje"""
	global net
	#linea = "xx xxx xxx.xx xxx.xx xxx.xx xxx.xx xxx.xx xxx.xx xx/xx/xxxx xx:xx:xx\n"
	#linea = "id bat hum    temp   vel    dir    plub   luz    d/m/a      h:m:s"
	#Se separa por espacio la línea, ese es el protocolo
	separado = linea.split(' ')
	print ("Dividiendo el mensaje por espacios")
	print (separado)
	#Guarda en cada variable su valor asignado
	idx, bat, hum, temp, vel, dire, plub, luz, fecha, hora = separado
	#23:34:00
	hora = hora[0:8]
	dic = {"temp": temp, "hum": hum, "vel": vel, "dire": dire, "plub": plub, "luz": luz}
	nombrex = {"temp": "2_Temperatura", "hum": "6_Humedad", "vel": "3_Velocidad del viento",
		"dire": "4_Dirección del viento", "plub": "1_Pluviometro", "luz": "5_Radiación solar"}
	#Arregla la fecha al formato de MySQL
	f_h = fecha_ok(fecha, hora)
	print (("La fecha para MySQL es: " + f_h))
	for abc in s_estacion:
		print (("Enviando por MQTT: " + abc))
		topic = (idx + "/" + abc)
		print (("Topic: " + topic))
		print (("Valor: " + dic[abc]))
		#Para el nombre del sensor será si es la estación 1 y temperatura 1_1
		nombre = idx + "_" + nombrex[abc]
		#Publica por MQTT el valor de del sensor en el topic indicado
		#Guarda en la base de datos el id, cuál es, fecha, el tipo de sensor y valor
		print ("Guardando en base de datos")
		publicar = ("'" + idx + "', '" + nombre + "', '" + f_h + "', '" + abc
			+ "', '" + dic[abc] + "', '" + bat + "', '" + fecha_sms + "'")
		print (publicar)
		bdd(idx, nombre, f_h, abc, dic[abc], bat, fecha_sms)
		print ("Enviando a ASOCIENAGA")
		fecha_sms_as = fecha_asocienaga(fecha_sms)
		fecha_as = fecha_asocienaga(f_h)
		vn = float(dic[abc])
		print (vn)
		#vn = int(vn)
		asocienaga = ("curl -X POST --header 'Content-Type: application/json' --header 'Accept:"
			" application/json' --header 'API-KEY: hZ23Q.A6+hA12sm@4T0i7wrW!XJ9bwm' -d '{ \"tipo\""
			": \"" + abc + "\", \"valor\": " + str(vn) + ", \"nombre_sensor\": \"" + nombre + "\", "
			"\"fecha_hora_sms\": \"" + fecha_sms_as + "\", \"fecha_hora_captura\": \"" + fecha_as + "\""
			", \"bateria\": \"" + bat + "\" }' http://pruebas.siara.info.tm/sensor/guardar_dato")
		print (asocienaga)
		if net == "si":
			publish.single(topic, dic[abc], hostname="31.220.62.19")
			publish.single("bdd", publicar, hostname="31.220.62.19")
			os.system(asocienaga)
	print ("---------------------------Fin de la estación----------------------------\n")


def fecha_asocienaga(fecha):
	"""Hola"""
	#2018-05-15 03:00:14
	separado_fecha = fecha.split(' ')
	fechax, horax = separado_fecha
	fechay = fechax.replace('-', '/')
	horay = horax[0:5]
	corregido = fechay + " " + horay
	return corregido


def hora_20():
	"""Función para entregar la hora al nodo con 20 sg de más"""
	#Obtiene la hora actual
	hh = time.strftime("%H:%M:%S")
	print ("La hora actual es: " + hh)
	#Separa la hora por :
	horx = hh.split(':')
	hora, minuto, segundo = horx
	#Convierte a entero la hora, minuto y segundo
	hora = int(hora)
	minuto = int(minuto)
	segundo = int(segundo)
	#Le agrega 20 segundos a los segundos
	nw_sg = segundo + 20
	#Si hay más de 60 segundos corrige toda la hora
	if nw_sg >= 60:
		nw_sg = nw_sg - 60
		minuto = minuto + 1
		if minuto >= 60:
			minuto = minuto - 60
			hora = hora + 1
	#Convierte a string la hora, minuto y segundo
	segundo = str(nw_sg)
	minuto = str(minuto)
	hora = str(hora)
	#Guarda en hh la hora de nuevo
	hh = hora + ":" + minuto + ":" + segundo
	#Obtiene la fecha actual
	yy = time.strftime("%d/%m/%Y")
	print ("La fecha actual es: " + yy)
	print (("La hora actual sumándole 20 segundos es: " + hh))
	return hh, yy


def sendmensaje(receptor, mns=""):
	"""Función para enviar el mensaje"""
	serie.write('AT\r\n')
	time.sleep(1)
	#Le ponemos en modo para SMS
	serie.write('AT+CMGF=1\r\n')
	time.sleep(1)
	#Comando para enviar el mensaje, se pasa el valor del número
	serie.write('AT+CMGS=\"' + receptor + '\"\r\n')
	time.sleep(1)
	#Se escribe el mensaje
	serie.write(mns)
	time.sleep(3)
	#Termina el menzaje con Ctrl+z
	serie.write(ascii.ctrl("z"))
	time.sleep(3)
	#Le pasamos un fin de linea
	serie.write('\r\n')
	print ("Mensaje enviado\n")


def consulta_bdd_nivel(idx, valor1):
	"""Consulta la base de datos entre un intérvalo de fechas"""
	try:
		if idx in id_acequia:
			if (int(valor1) < 30) or (int(valor1) > 490):
				print ("Buscando los valores del id: " + idx)
				query = ("SELECT valor FROM datos WHERE (valor>30) and (valor<490) and (id=" + idx + ");")
				cursor_rpi.execute(query)
				for (valor) in cursor_rpi:
					consulta = ("{}".format(valor))
					valor_ultimo = consulta[1:4]
				print ("El último valor bueno registrado es: " + valor_ultimo)
				return valor_ultimo
			return valor1
		if idx in id_nivel:
			if (int(valor1) < 30) or (int(valor1) > 990):
				print ("Buscando los valores del id: " + idx)
				query = ("SELECT valor FROM datos WHERE (valor>30) and (valor<990) and (id=" + idx + ");")
				cursor_rpi.execute(query)
				for (valor) in cursor_rpi:
					consulta = ("{}".format(valor))
					valor_ultimo = consulta[1:4]
				print ("El último valor bueno registrado es: " + valor_ultimo)
				return valor_ultimo
			return valor1
		return valor1
	except UnboundLocalError:
		print ("No hay nada en la base de datos")


def mejora(linea, fecha_sms, numero):
	"""Procesa la información que llega en la línea del mensaje"""
	#linea = "18 090 090 0000 24/01/2018 13:40:30\n"
	#Se separa por espacio la línea, ese es el protocolo
	separado = linea.split(' ')
	print ("Dividiendo el mensaje por espacios")
	print (separado)
	#Guarda en cada variable su valor asignado
	idx, bat, hum, nivel, fecha, hora = separado
	hora = hora[0:8]
	hum1 = round(466.203 * 2 ** (-0.00700884 * ((float(hum) * 2 + 300) - 38.1629)) - 12.937, 2)
	if hum1 > 100:
		hum1 = 100
	if hum1 < 0:
		hum1 = 0
	if numero == "3122455278":
		if idx == "05":
			idx = "06"
	if idx in id_humedad:
		nombre = idx + "_1_Humedad"
	elif idx in id_acequia:
		nombre = idx + "_1_Acequia"
	elif idx in id_nivel:
		nombre = idx + "_1_Rio"
	hum1 = str(hum1)
	print (hum1)
	#Arregla la fecha al formato de MySQL
	f_h = fecha_ok(fecha, hora)
	print ("La fecha para MySQL es: " + f_h)
	#Convierte a entero el id para poder compararlo
	#Guarda el valor y el tipo de sensor dependiendo del id si es humedad o nivel
	tipo_sensor, valor = valor_s(idx, hum, nivel)
	if valor == hum:
		valor1 = hum1
	if valor == nivel:
		valor1 = nivel
	valor1 = consulta_bdd_nivel(idx, valor1)
	print("Enviando mqtt...")
	#Arregla el topic dependiendo del id y el tipo de sensor
	topic = idx + "/" + tipo_sensor
	print ("Topic: " + topic)
	print ("Valor: " + valor1)
	#Publica por MQTT el valor de del sensor en el topic indicado
	#Guarda en la base de datos el id, cuál es, fecha, el tipo de sensor y valor
	print ("Guardando en base de datos")
	publicar = ("'" + idx + "', '" + nombre + "', '" + f_h + "', '" + tipo_sensor
		+ "', '" + valor1 + "', '" + bat + "', '" + fecha_sms + "'")
	print (publicar)
	bdd(idx, nombre, f_h, tipo_sensor, valor1, bat, fecha_sms)
	print ("Enviando a ASOCIENAGA")
	fecha_sms_as = fecha_asocienaga(fecha_sms)
	fecha_as = fecha_asocienaga(f_h)
	vn = float(valor)
	asocienaga = ("curl -X POST --header 'Content-Type: application/json' --header 'Accept:"
		" application/json' --header 'API-KEY: hZ23Q.A6+hA12sm@4T0i7wrW!XJ9bwm' -d '{ \"tipo\""
		": \"" + tipo_sensor + "\", \"valor\": " + str(vn) + ", \"nombre_sensor\": \"" + nombre + "\", "
		"\"fecha_hora_sms\": \"" + fecha_sms_as + "\", \"fecha_hora_captura\": \"" + fecha_as + "\""
		", \"bateria\": \"" + bat + "\" }' http://pruebas.siara.info.tm/sensor/guardar_dato")
	print (asocienaga)
	if net == "si":
		publish.single(topic, valor1, hostname="31.220.62.19")
		publish.single("bdd", publicar, hostname="31.220.62.19")
		os.system(asocienaga)
	if idx == "36":
		idx = "12"
		print("Añadiendo dato falso")
		nombre = idx + "_1_Acequia"
		valor1 = consulta_bdd_nivel(idx, "0")
		print("Enviando mqtt...")
		#Arregla el topic dependiendo del id y el tipo de sensor
		tipo_sensor = "Acequia"
		topic = idx + "/" + tipo_sensor
		print ("Topic: " + topic)
		print ("Valor: " + valor1)
		#Publica por MQTT el valor de del sensor en el topic indicado
		#Guarda en la base de datos el id, cuál es, fecha, el tipo de sensor y valor
		print ("Guardando en base de datos")
		publicar = ("'" + idx + "', '" + nombre + "', '" + f_h + "', '" + tipo_sensor
			+ "', '" + valor1 + "', '" + bat + "', '" + fecha_sms + "'")
		print (publicar)
		bdd(idx, nombre, f_h, tipo_sensor, valor1, bat, fecha_sms)
		print ("Enviando a ASOCIENAGA")
		fecha_sms_as = fecha_asocienaga(fecha_sms)
		fecha_as = fecha_asocienaga(f_h)
		vn = float(valor1)
		asocienaga = ("curl -X POST --header 'Content-Type: application/json' --header 'Accept:"
			" application/json' --header 'API-KEY: hZ23Q.A6+hA12sm@4T0i7wrW!XJ9bwm' -d '{ \"tipo\""
			": \"" + tipo_sensor + "\", \"valor\": " + str(vn) + ", \"nombre_sensor\": \"" + nombre + "\", "
			"\"fecha_hora_sms\": \"" + fecha_sms_as + "\", \"fecha_hora_captura\": \"" + fecha_as + "\""
			", \"bateria\": \"" + bat + "\" }' http://pruebas.siara.info.tm/sensor/guardar_dato")
		print (asocienaga)
		if net == "si":
			publish.single(topic, valor1, hostname="31.220.62.19")
			publish.single("bdd", publicar, hostname="31.220.62.19")
			os.system(asocienaga)
	print ("---------------------------Fin del nodo----------------------------------\n")


def fecha_ok(fecha, hora):
	"""Acomoda la fecha y hora para ser guardada en MySQL"""
	#Separa los valores de la fecha por /
	fecha = fecha.split('/')
	#Guarda en una variable el día, mes y año
	dia, mes, anio = fecha
	#Convierte a entero la variable que es un string
	dia = int(dia)
	mes = int(mes)
	anio = int(anio)
	#Con date convierte el día, mes y año al formato de MySQL
	fecha = date(anio, mes, dia)
	#Une la fecha y hora para ser guardada en MySQL
	f_h = str(fecha) + " " + hora
	return f_h


def valor_s(idx, hum, nivel):
	"""Devuelve el tipo de sensor y el valor a guarda de cada punto según la id"""
	#Si el id está dentro del grupo de sensores de humedad
	if idx in id_humedad:
		print ("Es un sensor de humedad")
		#Guarda como tipo de sensor "Humedad"
		tipo_sensor = "Humedad"
		#Guarda como valor del sensor el valor de la humedad
		vx = hum
		return tipo_sensor, vx
	if idx in id_nivel:
		print ("Es un sensor de nivel de agua en río")
		#Guarda como tipo de sensor "Nivel"
		tipo_sensor = "Nivel"
		#Guarda como valor del sensor el valor del nivel
		vx = nivel
		return tipo_sensor, vx
	if idx in id_acequia:
		print ("Es un sensor de nivel de agua en Acequia")
		#Guarda como tipo de sensor "Acequia"
		tipo_sensor = "Acequia"
		#Guarda como valor del sensor el valor del nivel
		vx = nivel
		return tipo_sensor, vx


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
			host='127.0.0.1', database='riorancheria')
		#Crea la variable cursor
		cursor_rpi = cnx_rpi.cursor()
		print ("Infinito: " + str(infinito))
		while infinito:
			ya = time.strftime("%S")
			if (ya[1] == "0"):
				print ("Llamando a primerx")
				primerx()
				cnt = cnt + 1
				if cnt == 100:
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
		print ("Borrando sms: " + id_sms_global)
		serie.write("AT+CMGD=" + id_sms_global + "\r\n")
		time.sleep(1)
		print ("Fin del proceso")
	#Si interrumpo con ctrl c
	except KeyboardInterrupt:
		GPIO.cleanup()
		infinito = False
		break
		serie.close()
		#cursor.close()
		cursor_rpi.close()
		#cnx.close()
		cnx_rpi.close()
		print ("Fin del proceso")
	#Cuando finalice el ciclo try
	finally:
		GPIO.cleanup()
		print ("Fin del try")
