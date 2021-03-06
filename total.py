# -*- coding: utf-8 -*-
# Importamos la librería serial
import serial
# Importamos la librería de tiempo
import time
# Librería de email
import smtplib
# Conectar a la base de datos
import mysql.connector
# Importa la librería para modificaciones de tiempo
from datetime import date
# Librería para usar los pines GPIO
import RPi.GPIO as GPIO
# Importamos la librería de ascii para el control z
from curses import ascii
import os
# Importamos la librería que nos permite manejar varios hilos
import threading
import requests
import json

"""------------------------------------CONTROL DE PINES GPIO------------------------------------"""
idc = [
    "112", "089", "088", "126", "118", "127", "030", "124", "032", "034", "033", "082", "037", "080", "083",
    "041", "137", "105", "139", "091", "090", "106", "109", "099", "077", "103", "093", "071", "046", "104",
    "094", "038", "113", "049", "075", "128", "029", "023", "028", "074", "022", "024", "102", "026", "027",
    "072", "068", "063", "098", "004", "067", "122", "006", "007", "130", "008", "001", "095", "009", "097",
    "065", "016", "069", "019", "017", "018", "015", "061", "012", "066", "138", "133", "131", "134", "115",
    "107", "101", "055", "057", "117", "045", "135", "121", "078", "039",
    "136", "100", "120", "073", "005", "010", "085", "129", "044", "096", "025", "035", "031", "040", "042"
    "043", "110", "108", "070", "079", "011", "114", "064", "000", "084", "092", "086", "013", "111", "132"

]


numc = [
    "3135927486", "3135642438", "3135899636", "3135883144", "3135639957", "3135691884", "3135881855", "3135658913", "3135670333", "3135666599", "3135646220", "3135660270", "3135885660", "3135658864", "3135664037",
    "3135647515", "3135886941", "3135648787", "3135884424", "3135674161", "3135642457", "3135687198", "3135687177", "3135886951", "3135886935", "3135884425", "3135647517", "3135886942", "3135881890", "3135639944",
    "3135691897", "3135643699", "3135666597", "3135883169", "3135648800", "3135884384", "3135691913", "3135901879", "3135885651", "3135692052", "3135687137", "3135665323", "3135885658", "3135671662", "3135638646",
    "3135687183", "3135650065", "3135653823", "3135883161", "3135884387", "3135645018", "3135672866", "3135657659", "3135886913", "3135671669", "3135671611", "3135886949", "3135662813", "3135646267", "3135647542",
    "3106527703", "3142691595", "3106535298", "3106553483", "3106534164", "3106554617", "3106486474", "3142644808", "3106549270", "3142651109", "3106485364", "3106546073", "3106522321", "3106524471", "3106557786",
    "3128269625", "3128257527", "3128237225", "3128377438", "3128242606", "3128267068", "3106525593", "3128239772", "3126502500", "3128247070",
    "3128271571", "3126441918", "3203404863", "3203447900", "3203416206", "3203440210", "3203423833", "3203455475", "3203441497", "3203420082", "3203432664", "3203430173", "3203412591", "3203435239", "3203417431"
    "3118848577", "3118815205", "3118828434", "3118827718", "3118817700", "3118813924", "3118811338", "3118808863", "3118806345", "3118849991", "3118846667", "3118829863", "3118831241", "3118842785", "3118844215",

]
# Inicia la comunicación serial por el puerto ttyS0 a 38400
# Con ls -l /dev puedo saber cuál es el puerto serial 0 o 1
# Se usa esta velocidad porque no falla el módulo
print("Iniciando la comunicación con el serial")
serie = serial.Serial("/dev/ttyS0", 38400)
# Se cierra el puerto por si había otra comunicación
serie.close()
print("Cerrando el puerto serial")
# Se abre el puerto serial
serie.open()
print("Abriendo el puerto serial")


def inicio():
    """Acomoda el módulo para recibir mensajes"""
    # Escribe AT para comprobar que se está comunicando con el SIM800L
    serie.write("AT\r\n")
    time.sleep(1)
    print("Colocando el módulo en modo SMS")
    # Pone el módulo en modo SMS
    serie.write("AT+CMGF=1\r\n")
    time.sleep(1)
    print("Escribiendo 1,0")
    # Muestra el mensaje por el puerto serial
    serie.write("AT+CNMI=1,0,0,0,0\r\n")
    time.sleep(1)


def conex():
    mal = True
    # Variable que cuenta los errores
    contador = 0
    # Mientras que el sistema mande error al escribir AT
    while mal:
        # Escribe AT en el puerto serial
        serie.write("AT\r\n")
        serie.reset_input_buffer()
        print("Escribiendo AT esperando un OK")
        time.sleep(0.5)
        # Lee la respuesta del puerto serial
        read = serie.readline()
        print(("////////////////////////////" + read))
        read = serie.readline()
        print(("////////////////////////////" + read))
        # Si la respuesta es OK
        if "OK" in read:
            # Controla la variable del ciclo infinito y la pone en falso
            mal = False
            # Pone el contador de errores en 0
            contador = 0
            return True
        # Si la respuesta no es OK (sino error)
        else:
            # Coloca la variable que controla el ciclo infinito en True
            mal = True
            # Cuenta un error
            contador = contador + 1
            print(contador)
            print("Apagando el SIM800")
            GPIO.output(sim, True)
            time.sleep(2)
            print("Encendiendo el SIM800")
            GPIO.output(sim, False)
            time.sleep(1)
            inicio()
            # Si el contador es igual a 3
            if (contador == 5):
                pass
                contador = 0
                # Mandar gmal
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
    serie.write('AT+CMGL="ALL"\r\n')
    serie.reset_input_buffer()
    control = True
    while control:
        # +CMGL: 9,"REC READ","3003859853","","18/02/19,11:42:55-20"
        linea = serie.readline()
        if linea.startswith("+CMGL:") is True:
            print("LEYENDO cmgl a las: " + hx)
            # smst = open('/home/pi/codigos/sms.txt','a')
            # smst.write('\n' + linea)
            # smst.close()
            cm, r, c1, numero, c2, n, c3, fecha, n2 = linea.split('"')
            cmg, nada = cm.split(",")
            cmgl, id_sms = cmg.split(" ")
            print(id_sms)
            print(numero)
            print(fecha)
            print(
                "--------------------Llamando a la función segundx--------------------\n")
            # Llama a la función segundx
            # hay, netsi = internet()
            # print ("Conexión a internet: " + str(hay))
            fecha_sms = otra_fecha(fecha)
            # if netsi is 1:
            # hora_con = otra_fecha(fecha)
            # elif netsi is 2:
            # hora_sin = otra_fecha(fecha)
            # consulta_bdd(hora_sin, hora_con)
            segundx(numero, fecha_sms, id_sms)

        if "OK" in linea:
            control = False
        if "ERROR" in linea:
            control = False
            print("-----------------------------------------------------------")
    # print ("FIN")


def otra_fecha(fx):
    """Hola"""
    fx = fx[0:17]
    # xxxx-xx-xx xx:xx:xx
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
    # Variable de control del ciclo infinito
    qap = True
    # Inicia un ciclo infinito para leer varias veces el puerto serial
    dato = 0
    while qap:
        # Lee el puerto serial
        segunda = serie.readline()
        # smst = open('/home/pi/codigos/sms.txt','a')
        # smst.write('\n' + segunda)
        # smst.close()
        print("Segunda linea: ")
        # Imprime lo leido
        print(segunda)
        if (dato < 2) and ("\r\n" not in segunda):
            if numero in numc:
                print("Enviando dato: " + str(dato))
                posi = numc.index(numero)
                consumo, t1, h1, t2, h2, t3, h3, t4, h4, fecha, hora, crc = segunda.split(
                    ',')
                fecha = fecha_ok(fecha)
                print(fecha)

                bdd(int(idc[posi]), float(consumo), float(t1), hum(h1), float(t2), hum(
                    h2), float(t3), hum(h3), float(t4), hum(h4), str(fecha), str(hora))

                datos = {
                    "numCasa": int(idc[posi]),
                    "consumption": float(consumo),
                    "t1": float(t1),
                    "h1": hum(h1),
                    "t2": float(t2),
                    "h2": hum(h2),
                    "t3": float(t3),
                    "h3": hum(h3),
                    "t4": float(t4),
                    "h4": hum(h4),
                    "date": fecha,
                    "hour": hora,
                }
                # print(datos)

                response = requests.post(
                    "https://graphql.cclimamagdalena.com/api/v1/houses/simple", json=datos)
                print(response)
                json_response = response.json()
                json_response['data']
                print(json_response)
                dato += 1
                # f = open("/home/pi/codigos/datos.txt",'a')
                # f.write('\n' + str(json_response))
                # f.close()
                if json_response['status'] == 'fail':
                    print("Error en el envio de datos")
                    print("No se borra el mensaje")
                    mail("Fallo en el envio de datos",
                         "FALLO EN EL ENVIO \n"+str(datos))
                    print("----------------Fin por error de envio-----------\n")
                    qap = False
                elif json_response['status'] == 'success':
                    print("----------------Envio Correcto de mensaje-----------\n")

        elif "\r\n" in segunda:
            print("Borrando sms: " + id_sms)
            serie.write("AT+CMGD=" + id_sms + "\r\n")
            time.sleep(1)
            print("------------------Fin del ciclo otra razón-------------------\n")
            qap = False
            dato = 0


def hum(hume):
    if float(hume) > 99.0:
        return 99.0
    elif float(hume) == 0.0:
        return 99.0
    else:
        return float(hume)


def mail(mensaje, asunto):

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


def fecha_ok(fecha):
    """Acomoda la fecha y hora para ser guardada en MySQL"""
    # Separa los valores de la fecha por /
    fecha = fecha.split('/')
    # Guarda en una variable el día, mes y año
    dia, mes, anio = fecha
    # Convierte a entero la variable que es un string
    # Con date convierte el día, mes y año al formato de MySQL
    fecha = anio+"/"+mes+"/"+dia
    # Une la fecha y hora para ser guardada en MySQL
    f_h = str(fecha)
    return f_h


def bdd(idcasa, consumo, t1, h1, t2, h2, t3, h3, t4, h4, fecha, hora):
    datos = (idcasa, consumo, t1, h1, t2, h3, t3, h3, t4, h4, fecha, hora)
    """Función para guardar en la base de datos"""

    agregar = "INSERT INTO datos (ID_Casa,COSNSUMO,T1,H1,T2,H2,T3,H3,T4,H4,FECHA,HORA) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\"%s\",\"%s\");"
    # Ejecuta el comando agregar con los valores datos en MySQL
    cursor_rpi.execute(agregar, datos)
    # Es necesario ejecutar commit para que funcione
    # cnx.commit()
    cnx_rpi.commit()


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
    print("Función de perro guardian")
    while infinito:
        while control:
            print("Esperando ")
            contador = contador + 1
            time.sleep(3)
            if contador == 100:
                mail("REINICIANDO", "PERRO GUARDIAN REINICIANDO RPI")
                print("Finalizado, reboot")
                os.system("sudo reboot")
        contador = 0
        time.sleep(3)


hilo_perro = threading.Thread(target=perro)
hilo_perro.start()

# Inicia el ciclo infinito del proyecto
while True:
    # Trata de realizar todo el proyecto
    try:
        # Colocamos la placa en modo BCM
        GPIO.setmode(GPIO.BCM)
        # Definimos el pin donde está el sim
        sim = 23
        # Colocamos el sim como salida
        GPIO.setup(sim, GPIO.OUT)
        print("Apagando el SIM800")
        # Ponemos el sim en True para apagarlo
        GPIO.output(sim, True)
        # Esperamos dos segundos
        time.sleep(1)
        print("Encendiendo el SIM800")
        # Ponemos el sim en False para encenderlo
        GPIO.output(sim, False)
        time.sleep(6)
        print("Llamando a la función de inicio")
        # Llama a la función de inicio
        inicio()
        # Conecta al MySQL de la raspberry
        cnx_rpi = mysql.connector.connect(user='root', password='Contrasena1',
                                          host='127.0.0.1', database='casas')
        # Crea la variable cursor
        cursor_rpi = cnx_rpi.cursor()
        print("Infinito: " + str(infinito))
        while infinito:
            ya = time.strftime("%S")
            if (ya[1] == "0"):
                # print ("Llamando a primerx")
                primerx()
                cnt = cnt + 1
                if cnt == 200:
                    print("Apagando el SIM800")
                    GPIO.output(sim, True)
                    time.sleep(1)
                    print("Encendiendo el SIM800")
                    GPIO.output(sim, False)
                    time.sleep(6)
                    inicio()
                    cnt = 0
            time.sleep(1)
    # Si hay un error de nombre de variable o no se puede dividir algún mensaje
    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))
    except (ValueError, NameError, AttributeError):
        print("Hay un error al separar o en una variable o un atributo")
        print("Borrando sms: " + id_sms_global)
        serie.write("AT+CMGD=" + id_sms_global + "\r\n")
        time.sleep(1)
        print("Fin del proceso")
        # Si interrumpo con ctrl c
    except KeyboardInterrupt:
        GPIO.cleanup()
        infinito = False
        control = False
        serie.close()
        # cursor.close()
        cursor_rpi.close()
        # cnx.close()
        cnx_rpi.close()
        print("Fin del proceso")
        break
    # Cuando finalice el ciclo try
    finally:
        GPIO.cleanup()
        print("Fin del try")


# Final del codigo


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


# def consulta_bdd(fecha_menor, fecha_mayor):
# 	"""Consulta la base de datos entre un intérvalo de fechas"""
# 	global hora_con
# 	try:
# 		if fecha_mayor > fecha_menor:
# 			print ("Mandando los datos entre " + fecha_menor + " y " + fecha_mayor)
# 			query = ("SELECT * FROM datos WHERE fecha_sms BETWEEN %s AND %s;")
# 			datos = (fecha_menor, fecha_mayor)
# 			cursor_rpi.execute(query, datos)
# 			for (id, sensor, fecha, tipo, valor, bateria, fecha_sms) in cursor_rpi:
# 				consulta = ("{} {} {} {} {} {} {}".format(id, sensor,
# 					fecha, tipo, valor, bateria, fecha_sms))
# 				print (consulta)
# 				adecuacion_nueva(consulta)
# 				hora_con = "0000-00-00 00:00:00"
# 				publish.single("net", "Se fue el net pero ya regresó", hostname="31.220.62.19")
# 	except UnboundLocalError:
# 		print ("No hay nada en la base de datos")

# def hora_now():
# 	"""Función para entregar la hora actual"""
# 	#Obtiene la hora actual
# 	hora = time.strftime("%H:%M:%S")
# 	#Obtiene la fecha actual
# 	fecha = time.strftime("%Y-%m-%d")
# 	fecha_total = fecha + " " + hora
# 	return fecha_total
