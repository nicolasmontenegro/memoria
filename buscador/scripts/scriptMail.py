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

def prepareInvitation(fromUser, toUser, folder, propose):
    outTo =  toUser["firstname"] + " " + toUser["lastname"] + " <" + toUser["email"] + ">"
    outSubject = fromUser["firstname"] + " Te ha invitado a colaborar"
    outText = "Hola " + toUser["firstname"] + ",\n\n" + fromUser["firstname"] + " " + fromUser["lastname"] + " " + propose + " \"" + folder["folder"] + "\".\nPara entrar, inicia sesión y revisa tu lista de carpetas o entra directamente a https://mysterious-badlands-3295.herokuapp.com/folder?idquery=" + str(folder["_id"]) + " \nRecuerda colaborar en las votaciones para mejorar las selecciones de los resultados.\n\nSaludos... y sigue investigando." 
    send_simple_message(outTo, outSubject, outText)    
    print ("enviado a " + outTo)
