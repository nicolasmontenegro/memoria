import requests
PUBLICKEY = "key-49722d2d33ca7a54a9402144aa4ed089"
MAILMASTER = "Buscador de papers <postmaster@sandbox9f0b2fced6974aa1acadc8d52dd1de23.mailgun.org>"

def send_simple_message():
	return requests.post(
		"https://api.mailgun.net/v3/sandbox9f0b2fced6974aa1acadc8d52dd1de23.mailgun.org/messages",
		auth=("api", PUBLICKEY),
		data={"from": MAILMASTER,
			"to": "Nicolás Montenegro <niko_nmv@live.cl>",
			"subject": "Hello Nicolás Montenegro",
			"text": "Congratulations Nicolás Montenegro, you just sent an email with Mailgun!  You are truly awesome!  You can see a record of this email in your logs: https://mailgun.com/cp/log .  You can send up to 300 emails/day from this sandbox server.  Next, you should add your own domain so you can send 10,000 emails/month for free."
			}
		)