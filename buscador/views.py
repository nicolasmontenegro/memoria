from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.shortcuts import render
from django.conf import settings
from django.views.static import serve
from django.views.decorators.csrf import ensure_csrf_cookie
from pymongo import MongoClient
from buscador.scripts import scriptDB, scriptBuscador, scriptXLSX, scriptPage
from bson.objectid import ObjectId
import os



# Create your views here.
def revisar(request):
	if request.method == 'GET' and scriptDB.unfold(request.COOKIES) != None:
		if request.GET.get('source') and request.GET.get('page') and request.GET.get('iddb'):
			resultsperpage = 24
			print ("usando " + request.GET['source'] + ": " + request.GET['iddb'] + " pag: " + request.GET['page'])
			out = scriptDB.readSource(request.GET['source'], request.GET['iddb'])
			lapsus = (int(request.GET['page'])-1)*(resultsperpage)
			out["results"] = out["results"][lapsus:(lapsus+resultsperpage)]	
			out["name"] = request.GET['source']
			return render(request, 'resultsPage.html', 
				{'page': scriptPage.countPage(int(request.GET['page']), int(out["totalfound"]), resultsperpage),
				'out': out,
				"userlogin": scriptDB.unfold(request.COOKIES)})	
		elif request.GET.get('idquery'):
			print("revisar dice: " + request.GET['idquery'])
			out = scriptDB.getResults(request.GET, request.COOKIES)
			if isinstance(out, int):
				if out == -2:
					return  render(request, 'forbidden.html', {'out': out, "userlogin": scriptDB.unfold(request.COOKIES)})	
				elif out == -1:
					HttpResponseNotFound('<h1>Página no encontrada</h1>')
			return render(request, 'results.html', 
				{'out': out, 'back': 1, "userlogin": scriptDB.unfold(request.COOKIES)})							
		elif request.GET.get('query'):
			print("busqueda dice: " + request.GET['query'])
			dbId = scriptBuscador.search(request.GET['query'])
			scriptDB.addToFolder(str(dbId), request.GET['idfolder'])
			return HttpResponseRedirect('/revisar?idquery=%s' % str(dbId))	
	if request.method == 'POST' and scriptDB.unfold(request.COOKIES) != None:
		print("hola")
		if request.POST.get('query'):
			print("entrando")
			response_data = {
				'state': scriptBuscador.searchComplete(request.POST['query']),}
			return JsonResponse(response_data )
	else:
		return HttpResponseRedirect('/login')

def descargar(request):
	if request.method == 'GET':
		print("descargar dice: " + request.GET['idquery'])
		client = MongoClient()
		out = client.memoria.query.find_one({"_id": ObjectId(request.GET['idquery'])})
		if out:	
			for doc in out["sources"]:
				doc["doc"] = scriptDB.readSource(doc["name"], doc["db"]) 
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
		print("votos dice: " + request.POST['value'] + " to " + request.POST['rank'] + " " +request.POST['source'] + request.POST['id'])
		result = scriptDB.updateVote(request.POST, request.COOKIES)
		return JsonResponse(result)

def folder(request):
	if request.method == 'GET' and scriptDB.unfold(request.COOKIES) != None:	
		if request.GET.get('query'):
			print("new folder dice: " + request.GET['query'])
			dbId = scriptDB.createFolder(request.GET['query'], request.COOKIES)
			return HttpResponseRedirect('/folder?idquery=%s' % dbId)
		elif request.GET.get('idquery'):
			out = scriptDB.getFolder(request.GET, request.COOKIES, True)
			if isinstance(out, int):
				if out == -1:
					HttpResponseNotFound('<h1>Página no encontrada</h1>')
			if out.get("permission"):
				return render(request, 'folder.html', {'out': out, 'back': 1, "userlogin": scriptDB.unfold(request.COOKIES)})
			else:
				return  render(request, 'forbidden.html', {'out': out, "userlogin": scriptDB.unfold(request.COOKIES)})	
	elif request.method == 'POST' and scriptDB.unfold(request.COOKIES) != None:	
		if request.POST.get("idfolder") and request.POST.get("iduser"):
			return JsonResponse(scriptDB.confirmDemand(request.POST, request.COOKIES))
		elif request.POST.get("idquery"):
			return JsonResponse({"check":scriptDB.addDemand(request.POST, request.COOKIES)})
	else:
		return HttpResponseRedirect('/login')



def indexfolder(request):
	if request.method == 'GET' and scriptDB.unfold(request.COOKIES) != None:						
		lista = scriptDB.getListFolder(request.COOKIES)#list(MongoClient().memoria.folder.find())
		return render(request, 'indexfolder.html', {'out': lista, "userlogin": scriptDB.unfold(request.COOKIES)})
	else:
		return HttpResponseRedirect('/login')

@ensure_csrf_cookie
def signup(request):
	if request.method == 'GET' and scriptDB.unfold(request.COOKIES) != None:
		return HttpResponseRedirect('/')
	elif request.method == 'POST':
		print(request.POST.get('password'))
		return JsonResponse({"check":scriptDB.addUser(request.POST),})
	elif request.method == 'GET':
		c = {}
		return render(request, 'signup.html', c)

@ensure_csrf_cookie
def login(request):	
	if request.method == 'GET' and scriptDB.unfold(request.COOKIES) != None:
		return HttpResponseRedirect('/')
	elif request.method == 'POST':
		check = scriptDB.checkLogin(request.POST, request.COOKIES)
		print(check)
		return JsonResponse({"check":check})
	elif request.method == 'GET':
		c = {}
		return render(request, 'login.html', c)

def profile(request):
	if request.method == 'GET' and scriptDB.unfold(request.COOKIES) != None:
		return render(request, 'profile.html', {"userlogin": scriptDB.unfold(request.COOKIES)})
	elif request.method == 'GET':
		return HttpResponseRedirect('/login')

def logout(request):
	if request.method == 'GET' and scriptDB.unfold(request.COOKIES) != None:
		return render(request, 'logout.html')
	elif request.method == 'GET':
		return HttpResponseRedirect('/login')

def comment(request):
	if request.method == 'GET' and scriptDB.unfold(request.COOKIES) != None:
		print("comment dice: " + request.GET['source'] + request.GET['id'])
		return render(request, 'comment.html', scriptDB.getResult(request.GET))
	if request.method == 'POST' and scriptDB.unfold(request.COOKIES) != None:
		print("comment dice: " + request.POST['source'] + request.POST['id'])
		return render(request, 'comment.html', scriptDB.addComment(request.POST, request.COOKIES))