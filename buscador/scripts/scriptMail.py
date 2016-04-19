import requests
PUBLICKEY = "key-49722d2d33ca7a54a9402144aa4ed089"
MAILMASTER = "Buscador de papers <postmaster@sandbox9f0b2fced6974aa1acadc8d52dd1de23.mailgun.org>"

def send_simple_message(to, subject, text):
	return requests.post(
		"https://api.mailgun.net/v3/sandbox9f0b2fced6974aa1acadc8d52dd1de23.mailgun.org/messages",
		auth=("api", PUBLICKEY),
		data={"from": MAILMASTER,
			"to": to,
			"subject": subject,
			"text": text
			}
		)

def prepareInvitation(fromUser, toUser, folder):
	outTo =  toUser["firstname"] + " " + toUser["lastname"] + " <" + toUser["email"] + ">"
	outSubject = fromUser["firstname"] + " Te ha invitado a colaborar"
	outText = "Hola " + toUser["firstname"] + "<br>" + fromUser["firstname"] + " " + fromUser["lastname"] + " te ha invitado a colaborar en su carpeta <i>" + folder["query"] + "</i><br>Para entrar, inicia sesión y revisa tu lista de carpetas o entra directamente a <a href=\"https://mysterious-badlands-3295.herokuapp.com/folder?idquery=\"" + folder["_id"] + ">este enlace</a>.<br>Recuerda colaborar en las votaciones para mejorar las selecciones<br><br>Saludos<br>Nicolás Montenegro." 
	send_simple_message(outTo, outSubject, outText)