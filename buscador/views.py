from django.http import HttpResponse, JsonResponse
from django.template import RequestContext, loader
from django.shortcuts import render
from django.conf import settings
from pymongo import MongoClient
from buscador.scripts import scriptDB, scriptBuscador, scriptXLSX
from bson.objectid import ObjectId
from django.views.static import serve
import os

# Create your views here.
def revisar(request):
	if request.method == 'GET':
		if request.GET.get('idquery'):
			print("revisar dice: " + request.GET['idquery'])
			dbId = ObjectId(request.GET['idquery'])							
		elif request.GET.get('query'):
			print("busqueda dice: " + request.GET['query'])
			dbId = scriptBuscador.buscar(request.GET['query'], 200)
		client = MongoClient()
		out = client.memoria.query.find_one({"_id": dbId})
		for doc in out["sources"]:
			doc["doc"] = scriptDB.read(doc["name"], doc["db"]) 
		print("uploading")
		return render(request, 'busqueda.html', 
			{'out': out,
			'back': 1})
			

def descargar(request):
	if request.method == 'GET':
		print("descargar dice: " + request.GET['idquery'])
		client = MongoClient()
		out = client.memoria.query.find_one({"_id": ObjectId(request.GET['idquery'])})
		if out:	
			for doc in out["sources"]:
				doc["doc"] = scriptDB.read(doc["name"], doc["db"]) 
			filepath = scriptXLSX.xlsfile(out)
			print ("fichero de salida: " + filepath)
			if filepath:
				print("up up up!!")
				return serve(request, os.path.basename(filepath), os.path.dirname(filepath))
			else:
				print ("no hay fichero :(")
		else:
			print ("no existe id")

def vote(request):
	if request.method == 'POST':
		print("votos dice: " + request.POST['value'] + " to " + request.POST['rank'])
		result = scriptDB.updateVote (request.POST['source'], request.POST['id'], request.POST['rank'], request.POST['value'])
		print(result.modified_count)
		response_data = {
			'modified': result.modified_count,
			'matched': result.matched_count,
			'value': request.POST['value'],}
		return JsonResponse(response_data)
		

def getMongo():
	client = MongoClient()
	db = client.memoria

def index(request):
	lista = list(MongoClient().memoria.query.find())
	return render(request, 'index.html', {'out': lista})