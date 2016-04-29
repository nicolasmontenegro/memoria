from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseNotFound
from django.template import RequestContext, loader
from django.shortcuts import render
from django.conf import settings
from django.views.static import serve
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.cache import never_cache
from django.core.servers.basehttp import FileWrapper

from pymongo import MongoClient
from buscador.scripts import scriptDB, scriptBuscador, scriptXLSX, scriptPage
from bson.objectid import ObjectId
import os

def isLogged(func = None):
	def decorator(a_view):
		def _dec(request, *args, **kwargs):
			if scriptDB.unfold(request.COOKIES) == None:
				return HttpResponseRedirect('/logout')
			return a_view(request, *args, **kwargs) 
		return _dec
	if func:
		return decorator(func)
	return decorator

@never_cache
@isLogged
def revisar(request):
	if request.method == 'GET':
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
				{'out': out, "userlogin": scriptDB.unfold(request.COOKIES), "progress": scriptDB.Progress(request.GET, request.COOKIES)})
		elif request.GET.get('query'):
			print("busqueda dice: " + request.GET['query'])
			dbId = scriptBuscador.search(request.GET['query'])
			scriptDB.addToFolder(str(dbId), request.GET['idfolder'])
			return HttpResponseRedirect('/revisar?idquery=%s' % str(dbId))	
	if request.method == 'POST':
		if request.POST.get('query'):
			response_data = {
				'state': scriptBuscador.searchComplete(request.POST['query']),}
			return JsonResponse(response_data )

@isLogged
def descargar(request):
	if request.method == 'GET':
		print("downloading " + request.GET['idquery'])
		filepath = scriptXLSX.xlsfile(request.GET['idquery'])
		if filepath:
			response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
			response['Content-Disposition'] = 'attachment; filename=' + request.GET['idquery'] + '.xlsx'
			xlsx = filepath.getvalue()
			filepath.close()
			response.write(xlsx)
			return response
		else:
			print ("no hay fichero :(")
			return HttpResponseBadRequest("Error de descarga")

@isLogged
def vote(request):
	if request.method == 'GET' and request.GET.get("update"):
		return JsonResponse(scriptDB.countingVotes(request.GET))
	elif request.method == 'POST':
		return JsonResponse(scriptDB.updateVote(request.POST, request.COOKIES))

@never_cache
@isLogged
def folder(request):
	if request.method == 'GET':
		if request.GET.get('query'):
			#print("new folder dice: " + request.GET['query'])
			dbId = scriptDB.createFolder(request.GET['query'], request.COOKIES)
			return HttpResponseRedirect('/folder?idquery=%s' % dbId)
		elif request.GET.get('idquery'):
			out = scriptDB.getFolder(request.GET, request.COOKIES, True)
			if isinstance(out, int):
				if out == -1:
					HttpResponseNotFound('<h1>Página no encontrada</h1>')
			if out.get("permission"):
				return render(request, 'folder.html', {'out': out, "userlogin": scriptDB.unfold(request.COOKIES)})
			else:
				return  render(request, 'forbidden.html', {'out': out, "userlogin": scriptDB.unfold(request.COOKIES)})	
	elif request.method == 'POST':	
		if request.POST.get("idquery") and request.POST.get("iduser"):
			return JsonResponse(scriptDB.confirmDemand(request.POST, request.COOKIES, email="confirm"))
		if request.POST.get("idquery") and request.POST.get("email"):
			userChecked = scriptDB.getUser(email = request.POST.get("email"))
			if userChecked:
				out = scriptDB.getFolder(request.POST, request.COOKIES, False)
				if (not isinstance(out, int)) and out["user"].get(str(userChecked["_id"])):
					return JsonResponse({"check":2, "name": userChecked["firstname"] + " " + userChecked["lastname"]})
				else:	
					if request.POST.get("confirm"):
						inputdata = {"idquery": request.POST.get("idquery"), "iduser":userChecked["_id"]}
						return JsonResponse(scriptDB.confirmDemand(inputdata, request.COOKIES, email="invitation"))
					return JsonResponse({"check":1, "name": userChecked["firstname"] + " " + userChecked["lastname"]})
			else:
				return JsonResponse({"check":0})
		elif request.POST.get("idquery"):
			return JsonResponse({"check":scriptDB.addDemand(request.POST, request.COOKIES)})

@never_cache
@isLogged
def indexfolder(request):
	if request.method == 'GET':
		lista = scriptDB.getListFolder(request.COOKIES)#list(MongoClient().memoria.folder.find())
		return render(request, 'indexfolder.html', {'out': lista, "userlogin": scriptDB.unfold(request.COOKIES)})

@ensure_csrf_cookie
def signup(request):
	if request.method == 'GET' and scriptDB.unfold(request.COOKIES) != None:
		return HttpResponseRedirect('/')
	elif request.method == 'POST':
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
		return JsonResponse({"check":check})
	elif request.method == 'GET':
		return render(request, 'login.html', {'new': request.GET.get('new'), 'recover': request.GET.get('recover') })


@ensure_csrf_cookie
def recover(request):	
	if request.method == 'GET' and scriptDB.unfold(request.COOKIES) != None:
		return HttpResponseRedirect('/')
	elif request.method == 'GET' and request.GET.get("idRecover"):
		user = scriptDB.recoverPasswordCheck(request.GET)
		return render(request, 'recoverPassword.html',{"user": user, "idRecover": request.GET.get("idRecover")})
	elif request.method == 'POST' and request.POST.get("idRecover"):
		return JsonResponse({"check": scriptDB.recoverPasswordReplace(request.POST)})
	elif request.method == 'POST':		
		scriptDB.recoverPassword(request.POST)
		return HttpResponseRedirect('/login')
	elif request.method == 'GET':
		return render(request, 'recover.html')

@isLogged
def profile(request):
	if request.method == 'GET':
		return render(request, 'profile.html', {"userlogin": scriptDB.unfold(request.COOKIES)})

def logout(request):
	if request.method == 'GET':
		return render(request, 'logout.html')

def comment(request):
	if request.method == 'GET' and scriptDB.unfold(request.COOKIES) != None:
		#print("comment dice: " + request.GET['source'] + request.GET['id'])
		return render(request, 'comment.html', scriptDB.getResult(request.GET))
	if request.method == 'POST' and scriptDB.unfold(request.COOKIES) != None:
		#print("comment dice: " + request.POST['source'] + request.POST['id'])
		return render(request, 'comment.html', scriptDB.addComment(request.POST, request.COOKIES))

def testing(request):
	return JsonResponse({"elseiver": scriptBuscador.testing()})
