from django import template
import time
from ..scripts import scriptDB

register = template.Library()

@register.filter(name='id')
def id(value):
	try:
		return str(value['_id'])
	except AttributeError:
		return ""

@register.filter(name='permission')
def permission(value):
	if value == "creator":
		return "Creador"
	elif value == "admin":
		return "Administrador"
	elif value == "guest":
		return "Invitado"
	else:
		return "none"

@register.filter(name='date')
def date(value):
	struct_time = time.strptime(value['date'])
	return str(struct_time.tm_mday) + "/" + str(struct_time.tm_mon) + "/" + str(struct_time.tm_year) + " " + str(struct_time.tm_hour).zfill(2) + ":" + str(struct_time.tm_min).zfill(2) + ":" + str(struct_time.tm_sec).zfill(2)

@register.filter(name='nameById')
def nameById(value):
	user = scriptDB.getUser(value)
	return user["firstname"] + " " + user["lastname"]

@register.filter(name='getItem')
def getItem(dictionary, key):
    return dictionary.get(key)


@register.filter(name='getBookmark')
def getBookmark(dictionary, user):
	return getItem(dictionary, id(user))