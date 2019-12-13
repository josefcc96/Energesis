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