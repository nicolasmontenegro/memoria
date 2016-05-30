from pymongo import MongoClient
from bson.objectid import ObjectId
from django.core import signing
import time

from . import scriptMail

client = MongoClient('mongodb://niko_nmv:tesista@ds052408.mongolab.com:52408/memoria')

def readSource(dbname, id):
	return client.memoria[dbname].find_one({"_id": ObjectId(id)})

def countingVotes (inputdata, modified = None):
	paper = [item for item in client.memoria[inputdata['source']].find_one({"_id": ObjectId(inputdata["id"])})["results"] if item["rank"] == inputdata["rank"]][0]
	results = {}
	results["yes"] = results["no"] = results["comment"] = 0
	if paper["vote"].get("yes") != None:
		results["yes"] = len(paper["vote"].get("yes"))
	if paper["vote"].get("no") != None:
		results["no"] = len(paper["vote"].get("no"))
	if paper.get("comment") != None:
		results["comment"] = len(paper.get("comment"))
	results["value"] = inputdata.get("value")
	if modified:
		if modified.get("add") != None:
			results["add"] = modified.get("add")
		if modified.get("remove") != None:
			results["remove"] = modified.get("remove")
	return results

def updateVote (inputdata, inputcookie):
	userid = str(unfold(inputcookie)["_id"])
	modifiedValues = {}
	if int(inputdata["value"]) == 1:
		modifiedValues["add"] = client.memoria[inputdata['source']].update_one({"_id": ObjectId(inputdata["id"]), "results.rank": inputdata["rank"]}, {"$addToSet": {"results.$.vote.yes": userid}}).modified_count
		modifiedValues["remove"] =  client.memoria[inputdata['source']].update_one({"_id": ObjectId(inputdata["id"]), "results.rank": inputdata["rank"]}, {"$pull": {"results.$.vote.no": userid}}).modified_count
	if int(inputdata["value"]) == -1:
		modifiedValues["add"] = client.memoria[inputdata['source']].update_one({"_id": ObjectId(inputdata["id"]), "results.rank": inputdata["rank"]}, {"$addToSet": {"results.$.vote.no": userid}}).modified_count
		modifiedValues["remove"] =  client.memoria[inputdata['source']].update_one({"_id": ObjectId(inputdata["id"]), "results.rank": inputdata["rank"]}, {"$pull": {"results.$.vote.yes": userid}}).modified_count
	if int(inputdata["value"]) == 0:
		modifiedValues["remove"] =  client.memoria[inputdata['source']].update_one({"_id": ObjectId(inputdata["id"]), "results.rank": inputdata["rank"]}, {"$pull": {"results.$.vote.no": userid}}).modified_count
		modifiedValues["remove"] +=  client.memoria[inputdata['source']].update_one({"_id": ObjectId(inputdata["id"]), "results.rank": inputdata["rank"]}, {"$pull": {"results.$.vote.yes": userid}}).modified_count	
	return countingVotes(inputdata, modified = modifiedValues)

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
	return client.memoria.query.find_one({"_id": ObjectId(id)})

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

def getUser(userid = None, email = None):
	if userid:
		return client.memoria.username.find_one({"_id": ObjectId(userid)})
	if email:
		return client.memoria.username.find_one({"email": email})

def unfold(inputcookie):
	try:
		resolved = signing.loads(inputcookie["head"] + ":" + inputcookie["body"] + ":" +inputcookie["usr"])
		user = resolved[inputcookie["csrftoken"]]
		return getUser(userid = user)
	except:
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

# def getPageResults():
# 	resultsperpage = 24
# 	#print ("usando " + request.GET['source'] + ": " + request.GET['iddb'] + " pag: " + request.GET['page'])
# 	out = readSource(request.GET['source'], request.GET['iddb'])
# 	lapsus = (int(request.GET['page'])-1)*(resultsperpage)
# 	out["results"] = out["results"][lapsus:(lapsus+resultsperpage)]	
# 	out["name"] = request.GET['source']

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
			item["user"] = getUser(userid = item["user"])
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

def confirmDemand(inputdata, inputcookie, email=None):
	try:
		folder = getFolder({"idquery": inputdata["idquery"]}, inputcookie, False)
		user = getUser(userid = inputdata["iduser"])
		if user is None:
			return {"check": 0}
		if folder.get("permission") == "admin" or folder.get("permission") == "creator":
			infoUser = "user." + str(user["_id"])
			client.memoria.folder.update_one({"_id": folder["_id"]}, {"$set": {infoUser: "guest"}})
			client.memoria.username.update_one({"_id": user["_id"]}, {"$addToSet": {"folder": inputdata["idquery"]}})
			client.memoria.folder.update_one({"_id": folder["_id"]}, {"$pull": {"demand": inputdata["iduser"]}})
			if email == "invitation":
				scriptMail.prepareInvitation(unfold(inputcookie), user, folder, "te ha invitado a colaborar en su carpeta")
			elif email == "confirm":
				scriptMail.prepareInvitation(unfold(inputcookie), user, folder, "ha aceptado tu solicitud a colaborar en su carpeta")
			return {"check": 1}
	except Exception:
		return {"check": -1}

def recoverPassword(inputdata):
	user = getUser(email = inputdata.get('query'))
	if user is not None:
		timeRecover = time.asctime(time.localtime(time.time()))
		client.memoria.username.update_one({"_id": user["_id"]}, {"$set": {"recoverDate": timeRecover}})
		signed = signing.dumps({str(user["_id"]) : timeRecover})
		scriptMail.prepareRecoverPassword(user, signed)

def recoverPasswordCheck(inputdata):
	try:
		unsigned = signing.loads(inputdata.get("idRecover"))
		user = getUser(userid = list(unsigned)[0])
		if (user is not None) and (user.get("recoverDate") == unsigned[list(unsigned)[0]]):
			now = time.localtime(time.time())
			before = time.strptime(unsigned[list(unsigned)[0]])
			delta = time.mktime(now) - time.mktime(before)
			print(delta)
			if delta > 86400 :
				client.memoria.username.update_one({"_id": user["_id"]}, {"$unset": {"recoverDate": ""}})
				return None
			else:
				return user
	except Exception:
		return None

def recoverPasswordReplace(inputdata):
	try:
		unsigned = signing.loads(inputdata.get("idRecover"))
		user = getUser(userid = list(unsigned)[0])
		if (user is not None) and (user.get("recoverDate") == unsigned[list(unsigned)[0]]):
			now = time.localtime(time.time())
			before = time.strptime(unsigned[list(unsigned)[0]])
			delta = time.mktime(now) - time.mktime(before)
			print(delta)
			if delta > 86400 :
				client.memoria.username.update_one({"_id": user["_id"]}, {"$unset": {"recoverDate": ""}})			
				return 0
			else:
				client.memoria.username.update_one({"_id": user["_id"]}, {"$set": {"password": inputdata.get("password")}, "$unset": {"recoverDate": ""}})
				return 1
	except Exception:
		return -1

def Progress(inputdata, inputcookie):
	user = unfold(inputcookie)
	results = getResults(inputdata, inputcookie)
	folder = client.memoria.folder.find_one({"_id": ObjectId(results["folder"])})	

	matchAll = {"yes":[{"results.isDuplicate": {"$in": [False, None]}}], "no":[{"results.isDuplicate": {"$in": [False, None]}}]}
	for userId in folder["user"] :
		matchAll["yes"].append( {"results.vote.yes": userId} )
		matchAll["no"].append( {"results.vote.no": userId} )
	matchMy = {"yes":[{"results.vote.yes": str(user["_id"])}, {"results.isDuplicate": {"$in": [False, None]}} ], 
		"no":[{"results.vote.no": str(user["_id"])}, {"results.isDuplicate": {"$in": [False, None]}} ]}
	
	for doc in results["sources"]:
		if doc["doc"]["totalfound"] > 0:
			doc["votes"] = {"my": progressQuery(doc, matchMy), "all": progressQuery(doc, matchAll)}

	return results

def progressQuery(doc, match):
	values = {"yes": 0 , "yesPercent": 0,  "no": 0, "noPercent": 0}

	auxyes = simpleAggregateSource(doc, match =  { "$and": match["yes"]}, group = {"_id": '$_id', "count": { "$sum": 1 }})
	if auxyes:
		values["yes"] = auxyes["count"]
		values["yesPercent"] = round((auxyes["count"] / doc["doc"]["totalfound"]) * 100, 0)
	
	auxno = simpleAggregateSource(doc, match =  { "$and": match["no"]}, group = {"_id": '$_id', "count": { "$sum": 1 }})
	if auxno:
		values["no"] = auxno["count"]
		values["noPercent"] = round((auxno["count"] / doc["doc"]["totalfound"]) * 100, 0)
	
	values["votesComplete"] = values["no"] + values["yes"]
	values["votesPercentComplete"] = round((values["votesComplete"]/ doc["doc"]["totalfound"])*100, 0)
	
	values["votesRemain"] = doc["doc"]["totalsave"] - values["votesComplete"]
	values["votesPercentRemain"] = round((values["votesRemain"]/ doc["doc"]["totalfound"])*100, 0)
	
	return values

def simpleAggregateSource(doc, match = None, group = None):
	query = [{ "$match": {"_id": doc["db"]} }, { "$unwind": '$results' }]
	if match:
		query.append({ "$match": match })
	if group:
		query.append({ "$group": group })

	result = list(client.memoria[doc["name"]].aggregate(query))
	if len(result):
		return result[0]
	else:
		return None

def bookmark(inputdata, inputcookie):
	user = unfold(inputcookie)
	query = readQuery(inputdata.get("idquery"))
	if query:
		bookmarkQuery = "bookmark." +  str(user["_id"])
		results = client.memoria.query.update_one({"_id": query["_id"]}, {"$set":{bookmarkQuery: {"source": inputdata.get("source"), "rank": inputdata.get("rank"), "iddb": inputdata.get("iddb")}}})
		return {"modified" : results.modified_count}
	else:
		return {"modified" : 0}

def duplicates(iddb):
	query = readQuery(iddb)
	for doc in query["sources"]:
		titles = list(client.memoria[doc["name"]].aggregate([{ 
			"$match": {"_id": doc["db"]} }, 
			{ "$unwind": '$results' }, 
			{ "$match": {"results.isDuplicate": {"$in": [False, None]}}},
			{ "$group": {"_id":"_id", "results": {"$push": {"$toLower": "$results.title"}}}},
			]))
		if len(titles) and titles[0].get("results"):
			for toComapre in query["sources"]:				
				if toComapre["name"] != doc["name"]:
					matches = list(client.memoria[toComapre["name"]].aggregate([
						{ "$match": {"_id": toComapre["db"]} }, 
						{ "$unwind": '$results' },
						{ "$project" :{ "rank": "$results.rank", "title": {"$toLower": "$results.title"}}},
						{ "$match": { "title": {"$in":titles[0].get("results")}}},
						{ "$group": { "_id": "_id", "matches": {"$push": "$rank"}}},
						]))
					if len(matches) and matches[0].get("matches"):
						for match in matches[0].get("matches"):
							client.memoria[toComapre["name"]].update_one(
								{"_id": toComapre["db"], "results.rank": match}, 
								{"$set": {"results.$.isDuplicate": True} })





