import requests
PUBLICKEY = "key-49722d2d33ca7a54a9402144aa4ed089"
#MAILMASTER = "Papered <postmaster@sandbox9f0b2fced6974aa1acadc8d52dd1de23.mailgun.org>"
MAILMASTER = "Papered <postmaster@papered.xyz>"
#APIBase =  "https://api.mailgun.net/v3/sandbox9f0b2fced6974aa1acadc8d52dd1de23.mailgun.org"
APIBase = "https://api.mailgun.net/v3/papered.xyz"

def send_simple_message(to, subject, text):
    return requests.post(
        APIBase + "/messages",
        auth=("api", PUBLICKEY),
        data={"from": MAILMASTER,
            "to": to,
            "subject": subject,
            "text": text
            }
        )

def prepareInvitation(fromUser, toUser, folder, propose):
    outTo =  toUser["firstname"] + " " + toUser["lastname"] + " <" + toUser["email"] + ">"
    outSubject = fromUser["firstname"] + " Te ha invitado a colaborar"
    outText = "Hola " + toUser["firstname"] + ",\n\n" + fromUser["firstname"] + " " + fromUser["lastname"] + " " + propose + " \"" + folder["folder"] + "\".\nPara entrar, inicia sesión y revisa tu lista de carpetas o entra directamente a http://www.papered.xyz/folder?idquery=" + str(folder["_id"]) + " \nRecuerda colaborar en las votaciones para mejorar las selecciones de los resultados.\n\nSaludos\nPapered" 
    send_simple_message(outTo, outSubject, outText)    
    print ("enviada invitacion a " + outTo)

def prepareRecoverPassword(toUser, Url):
    outTo =  toUser["firstname"] + " " + toUser["lastname"] + " <" + toUser["email"] + ">"
    outSubject = "Recuperación de contraseña"
    outText = "Hola " + toUser["firstname"] + ",\n\nHas recibido este correo porque has solicitado recuperar tu contraseña. Para continuar, entra a http://www.papered.xyz/recoverpassword?idRecover=" + Url + " y sigue las instrucciones.\nSi no has solicitado recuperar tu contraseña, simplemente omite este correo.\n\nSaludos\nPapered" 
    send_simple_message(outTo, outSubject, outText)    
    print ("enviado Recuperación a " + outTo)
