from django import template
import time
register = template.Library()

@register.filter(name='id')
def id(value):
	try:
		return str(value['_id'])
	except AttributeError:
		return ""

@register.filter(name='permission')
def permission(value):
	if value["permission"] == "creator":
		return "Creador"
	elif value["permission"] == "admin":
		return "Administrador"
	elif value["permission"] == "guest":
		return "Invitado"
	else:
		return "none"

@register.filter(name='date')
def date(value):
	struct_time = time.strptime(value['date'])
	return str(struct_time.tm_mday) + "/" + str(struct_time.tm_mon) + "/" + str(struct_time.tm_year) + " " + str(struct_time.tm_hour).zfill(2) + ":" + str(struct_time.tm_min).zfill(2) + ":" + str(struct_time.tm_sec).zfill(2)