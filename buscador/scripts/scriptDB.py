from pymongo import MongoClient
from bson.objectid import ObjectId
from django.core import signing
import time

client = MongoClient('mongodb://niko_nmv:tesista@ds052408.mongolab.com:52408/memoria')

def add(dbname, doc):
	return -1

def readSource(dbname, id):
	return client.memoria[dbname].find_one({"_id": ObjectId(id)})
	#if dbname == "ieee":
	#	return client.memoria.ieee.find_one({"_id": ObjectId(id)})
	#if dbname == "elsevier":
	#	return client.memoria.elsevier.find_one({"_id": ObjectId(id)})

def updateVote (inputdata, inputcookie):
	userid = str(unfold(inputcookie)["_id"])
	results = {}
	if int(inputdata["value"]) == 1:
		results["add"] = client.memoria[inputdata['source']].update_one({"_id": ObjectId(inputdata["id"]), "results.rank": inputdata["rank"]}, {"$addToSet": {"results.$.vote.yes": userid}}).modified_count
		results["remove"] =  client.memoria[inputdata['source']].update_one({"_id": ObjectId(inputdata["id"]), "results.rank": inputdata["rank"]}, {"$pull": {"results.$.vote.no": userid}}).modified_count
	if int(inputdata["value"]) == -1:
		results["add"] = client.memoria[inputdata['source']].update_one({"_id": ObjectId(inputdata["id"]), "results.rank": inputdata["rank"]}, {"$addToSet": {"results.$.vote.no": userid}}).modified_count
		results["remove"] =  client.memoria[inputdata['source']].update_one({"_id": ObjectId(inputdata["id"]), "results.rank": inputdata["rank"]}, {"$pull": {"results.$.vote.yes": userid}}).modified_count
	if int(inputdata["value"]) == 0:
		results["remove"] =  client.memoria[inputdata['source']].update_one({"_id": ObjectId(inputdata["id"]), "results.rank": inputdata["rank"]}, {"$pull": {"results.$.vote.no": userid}}).modified_count
		results["remove"] +=  client.memoria[inputdata['source']].update_one({"_id": ObjectId(inputdata["id"]), "results.rank": inputdata["rank"]}, {"$pull": {"results.$.vote.yes": userid}}).modified_count	
	votes = [item for item in client.memoria[inputdata['source']].find_one({"_id": ObjectId(inputdata["id"])})["results"] if item["rank"] == inputdata["rank"]][0]["vote"]
	#print(votes)
	results["yes"] = results["no"] = 0
	if votes.get("yes") != None:
		results["yes"] = len(votes.get("yes"))
	if votes.get("no") != None:
		results["no"] = len(votes.get("no"))
	results["value"] = inputdata["value"]
	return results

def createFolder (namefolder, inputcookie):
	user = unfold(inputcookie)
	objInsert = {
		"folder": namefolder,
		"date" : time.asctime(time.localtime(time.time())),
		"search": [],
		"user": {str(user["_id"]): "creator"},
		"demand": [],
		}
	folder = str(client.memoria.folder.insert(objInsert))
	client.memoria.username.update_one({"_id": user["_id"]}, {"$addToSet": {"folder": folder}})
	return folder

def addToFolder(idquery, idfolder):
	client.memoria.folder.update_one({"_id": ObjectId(idfolder)}, {"$push": {"search": {"id": idquery}}})
	client.memoria.query.update_one({"_id": ObjectId(idquery)}, {"$set": {"folder": idfolder}})


def readQuery(id):
	algo = client.memoria.query.find_one({"_id": ObjectId(id)})
	return algo

def addUser(inputdata):
	try:
		if client.memoria.username.find_one({"email": inputdata["email"]}):
			return 0
		objInsert = {
			"firstname":  inputdata["firstname"],
			"lastname":  inputdata["lastname"],
			"email":  inputdata["email"],
			"password":  inputdata["password"],
			"folder": [],
			}
		if client.memoria.username.insert(objInsert):
			return 1
		else:
			return -1
	except AttributeError:
		return -1

def checkLogin(inputdata, inputcookie):
	try:
		user = client.memoria.username.find_one({"email": inputdata["email"]})
		if user is None:
			return 0
		if user["password"] != inputdata["password"]:
			return -1
		else:			
			return signing.dumps({inputcookie["csrftoken"] : str((user["_id"]))}).split(':')
	except AttributeError:
		return -2

def getUser(userid):
	return client.memoria.username.find_one({"_id": ObjectId(userid)})

def unfold(inputcookie):
	try:
		resolved = signing.loads(inputcookie["head"] + ":" + inputcookie["body"] + ":" +inputcookie["usr"])
		user = resolved[inputcookie["csrftoken"]]
		return getUser(user)
	except KeyError:
		print("error unfold")
		return None
	
def getListFolder(inputcookie):
	listFolder = []
	for item in unfold(inputcookie)["folder"]:
		listFolder.append(getFolder({"idquery": item}, inputcookie, False))
	#print(listFolder)
	return listFolder

def getFolderPermission(folderid, userid):
	folder = client.memoria.folder.find_one({"_id": ObjectId(folderid)})
	return folder["user"].get(str(user["_id"]))

def getFolder(inputdata, inputcookie, complete):
	try:
		folder = client.memoria.folder.find_one({"_id": ObjectId(inputdata['idquery'])})
		user = unfold(inputcookie)	
		if folder is None:
			return -1
		if folder["user"].get(str(user["_id"]))	is None:
			return {"idquery": inputdata['idquery'], "demand": folder.get("demand")}	
		folder["permission"] = folder["user"].get(str(user["_id"]))	
		if complete:
			for doc in folder["search"]:
				doc["doc"] = readQuery(doc["id"]) 
		return folder
	except Exception:
		print("error en getFolder")
		return -1

def getPageResults():
	resultsperpage = 24
	#print ("usando " + request.GET['source'] + ": " + request.GET['iddb'] + " pag: " + request.GET['page'])
	out = readSource(request.GET['source'], request.GET['iddb'])
	lapsus = (int(request.GET['page'])-1)*(resultsperpage)
	out["results"] = out["results"][lapsus:(lapsus+resultsperpage)]	
	out["name"] = request.GET['source']

def getResults(inputdata, inputcookie):
	results = client.memoria.query.find_one({"_id": ObjectId(inputdata['idquery'])})
	folder = client.memoria.folder.find_one({"_id": ObjectId(results['folder'])})
	folder["permission"] = folder["user"][str(unfold(inputcookie)["_id"])]		
	if folder["permission"] is None:
		return -2	
	for doc in results["sources"]:
		doc["doc"] = readSource(doc["name"], doc["db"]) 
	return results

def getResult(inputdata):	
	result = [item for item in client.memoria[inputdata["source"]].find_one({"_id": ObjectId(inputdata["id"])})["results"] if item["rank"] == inputdata["rank"]][0]
	if result.get("comment"):
		for item in result["comment"]:
			item["user"] = getUser(item["user"])
	return result


def addComment(inputdata, inputcookie):
	user = unfold(inputcookie)
	newComment = {
		"user": str(user["_id"]),
		"action": "comment",
		"date": time.asctime(time.localtime(time.time())),
		"comment": inputdata["comment"],
		}
	client.memoria[inputdata['source']].update_one({"_id": ObjectId(inputdata["id"]), "results.rank": inputdata["rank"]}, {"$push": {"results.$.comment": newComment}})
	return getResult(inputdata)

def addDemand(inputdata, inputcookie):
	user = unfold(inputcookie)
	return client.memoria.folder.update_one({"_id": ObjectId(inputdata["idquery"])}, {"$addToSet": {"demand": str(user["_id"])}}).modified_count

def confirmDemand(inputdata, inputcookie):
	try:
		folder = getFolder({"idquery": inputdata["idfolder"]}, inputcookie, False)
		user = getUser(inputdata["iduser"])
		if user is None:
			return {"check": 0}
		if folder.get("permission") == "admin" or folder.get("permission") == "creator":
			infoUser = "user." + str(user["_id"])
			client.memoria.folder.update_one({"_id": folder["_id"]}, {"$set": {infoUser: "guest"}})
			client.memoria.username.update_one({"_id": user["_id"]}, {"$addToSet": {"folder": inputdata["idfolder"]}})
			client.memoria.folder.update_one({"_id": folder["_id"]}, {"$pull": {"demand": inputdata["iduser"]}})
			return {"check": 1}
	except Exception:
		return {"check": -1}

