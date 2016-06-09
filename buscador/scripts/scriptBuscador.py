import requests
from pymongo import MongoClient
from bson.objectid import ObjectId

import time
import threading
import queue

try:
	import xml.etree.cElementTree as ET
except:
	import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import bibtexparser

from . import scriptDB

client = MongoClient('mongodb://niko_nmv:tesista@ds052408.mongolab.com:52408/memoria')
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'}

threadLock = threading.Lock()
	
def putAtributeUn(element):
	try:
		return element.text
	except AttributeError:
		return ""

def putAtribute(ws, x, y, element):
	c = ws.cell(row = y, column = x)
	try:
		c.value = element
	except AttributeError:
		c.value = ""

class threadACM(threading.Thread):
	def __init__(self, querytext, q):
		threading.Thread.__init__(self)
		self.name = "acm"
		self.querytext = querytext
		self.q = q
	def run(self):
		url = "http://dl.acm.org/exportformats_search.cfm?filtered=&within=owners%2Eowner%3DHOSTED&dte=&bfr=&srt=%5Fscore&expformat=bibtex&query=" + self.querytext
		print(time.asctime(time.localtime(time.time()))  + " query from: " + url)
		downBit = requests.get(url, headers=headers).text
		parsered = bibtexparser.loads(downBit)
		totalfound = len(parsered.entries)
		totalsave = 0
		initObj = {
			"query" : self.querytext,
			"date" : time.asctime(time.localtime(time.time())),
			"totalfound" : totalfound,		
			"totalsave": totalsave,
			"update": 1,
			"results" : []}	
		queryObj = client.memoria.acm.insert(initObj)
		results = []
		print(self.name + " to saving!")
		for element in parsered.entries:
			totalsave += 1
			pubN = ""
			if element.get("journal"):
				pubN = element.get("journal")
			elif element.get("booktitle"):
				pubN = element.get("booktitle")
			results.append({
				"rank": str(totalsave),
				"title": element.get("title"),
				"authors": element.get("author"),
	#			"abstract": element.get("author"),
				"mdurl": element.get("link"),
				"pubN": pubN,
				"pubY": element.get("year"),
				"pubP": element.get("pages"),
				"doi": element.get("doi"),
				"vote": {},
				})
			if ((totalsave%100) is 0) or (totalsave == totalfound):
				print(self.name + " " + str(totalsave))
				client.memoria.acm.update_one({"_id": queryObj}, {"$push": {"results": {"$each": results}}, "$set": {"totalsave": totalsave}})				
				results.clear()
				if totalsave is 100:
					self.q.put({"name": self.name, "db": queryObj})
					print(self.name + "return a id")
		if totalfound == 0:
			self.q.put({"name": self.name, "db": queryObj})
		print(self.name + " saved!" + str(totalsave))
		client.memoria.acm.update_one({"_id": queryObj}, {"$set": {"totalsave": totalsave, "update": 0}})


class threadELSEVIER(threading.Thread):
	def __init__(self, querytext, q):
		threading.Thread.__init__(self)
		self.name = "elsevier"
		self.querytext = querytext
		self.q = q
	def run(self):
		url = 'http://api.elsevier.com/content/search/scidir?apiKey=3c332dc26c8b79d51d16a786b74fe76b&httpAccept=application/xml&query=' + self.querytext # &oa=true
		print(time.asctime(time.localtime(time.time()))  + " query from: " +url)
		totalfound = int("0"+putAtributeUn(ET.fromstring(requests.get(url, headers=headers).text).find("{http://a9.com/-/spec/opensearch/1.1/}totalResults")))
		totalsave = 0
		now = 0
		count = 200
		rank = 1
		initObj = {
			"query" : self.querytext,
			"date" : time.asctime(time.localtime(time.time())),
			"totalfound" : totalfound,		
			"totalsave": totalsave,
			"update": 1,
			"results" : []}	
		queryObj = client.memoria.elsevier.insert(initObj)
		print(self.name + " to saving!")
		while totalfound > 0:
			results = []
			urlWhile = 'http://api.elsevier.com/content/search/scidir?apiKey=3c332dc26c8b79d51d16a786b74fe76b&httpAccept=application/xml&query=' + self.querytext + '&count=' + str(count) + '&start=' + str(now) # + '&oa=true&view=complete'
			queryResults = ET.fromstring(requests.get(urlWhile, headers=headers).text).findall("{http://www.w3.org/2005/Atom}entry")##BeautifulSoup(requests.get(urlWhile).text).find_all("entry"):
			if len(queryResults):
				for element in queryResults:
					strAuthor = ""
					if element.find("{http://www.w3.org/2005/Atom}authors"):
						for author in element.find("{http://www.w3.org/2005/Atom}authors").findall("{http://www.w3.org/2005/Atom}author"):
							strAuthor = strAuthor + putAtributeUn(author.find("{http://www.w3.org/2005/Atom}given-name")) + " " + putAtributeUn(author.find("{http://www.w3.org/2005/Atom}surname")) + "; "
					results.append({
						"rank": str(rank),
						"title": putAtributeUn(element.find("{http://purl.org/dc/elements/1.1/}title")),
						"authors": strAuthor[:-2],
						##"abstract" : putAtributeUn(element.description)[8:],
						##"abstract" : putAtributeUn(element.find("{http://prismstandard.org/namespaces/basic/2.0/}description"))[8:],
						"abstract" : putAtributeUn(element.find("{http://prismstandard.org/namespaces/basic/2.0/}teaser")),
						"mdurl": element.find("{http://www.w3.org/2005/Atom}link[@ref='scidir']").attrib["href"],
						"pubN": putAtributeUn(element.find("{http://prismstandard.org/namespaces/basic/2.0/}publicationName")),
						"pubY": putAtributeUn(element.find("{http://prismstandard.org/namespaces/basic/2.0/}coverDate")),
						"pubP": putAtributeUn(element.find("{http://prismstandard.org/namespaces/basic/2.0/}startingPage")) + " - " + putAtributeUn(element.find("{http://prismstandard.org/namespaces/basic/2.0/}endingPage")),
						"doi": putAtributeUn(element.find("{http://prismstandard.org/namespaces/basic/2.0/}doi")),
						"vote": {},
						})
					totalsave += 1
					rank += 1
				now += count
				print(self.name + " " +  str(now))
				client.memoria.elsevier.update_one({"_id": queryObj}, {"$push": {"results": {"$each": results}}, "$set": {"totalsave": totalsave}})
				if now == 200:
					self.q.put({"name": self.name, "db": queryObj})
			else:
				break
		if totalfound == 0:
			self.q.put({"name": self.name, "db": queryObj})
		print(self.name + " saved!" + str(totalsave))
		client.memoria.elsevier.update_one({"_id": queryObj}, {"$set": {"totalsave": totalsave, "update": 0}})

class threadIEEE(threading.Thread):
	def __init__(self, querytext, q):
		threading.Thread.__init__(self)
		self.name = "ieee"
		self.querytext = querytext
		self.q = q
	def run(self):
		url = 'http://ieeexplore.ieee.org/gateway/ipsSearch.jsp?hc=0&md=' + self.querytext
		print(time.asctime(time.localtime(time.time()))  + " query from: " +url)
		totalfound = int("0"+putAtributeUn(ET.fromstring(requests.get(url, headers=headers).text).find("totalfound")))
		totalsave = 0
		now = 1
		count = 300
		rank = 1
		initObj = {
		"query" : self.querytext,
		"date" : time.asctime(time.localtime(time.time())),
		"totalfound" : totalfound,		
		"totalsave": totalsave,
		"update": 1,
		"results" : []}	
		queryObj = client.memoria.ieee.insert(initObj)
		print(self.name + " to saving!")
		while totalfound > 0:
			results = []
			urlWhile = 'http://ieeexplore.ieee.org/gateway/ipsSearch.jsp?sort=relevancy&md=' + self.querytext + '&hc=' + str(count) + '&rs=' + str(now)
			queryResults = ET.fromstring(requests.get(urlWhile, headers=headers).text).findall("document")
			if len(queryResults):
				for element in queryResults:
					results.append({
						"rank": putAtributeUn(element.find("rank")),
						"title": putAtributeUn(element.find("title")),
						"authors": putAtributeUn(element.find("authors")),
						"abstract" : putAtributeUn(element.find("abstract")),
						"mdurl": putAtributeUn(element.find("mdurl")),
						"pubN": putAtributeUn(element.find("pubtitle")),
						"pubY": putAtributeUn(element.find("py")),
						"pubP": putAtributeUn(element.find("epage")),
						"doi": putAtributeUn(element.find("doi")),
						"vote": {},
						})
					totalsave += 1
				now += count
				print(self.name + " " + str(now))
				client.memoria.ieee.update_one({"_id": queryObj}, {"$push": {"results": {"$each": results}}, "$set": {"totalsave": totalsave}})
				if now == 301:
					self.q.put({"name": self.name, "db": queryObj})
			else:
				break
		if totalfound == 0:
			self.q.put({"name": self.name, "db": queryObj})
		print(self.name + " saved!" + str(totalsave))
		client.memoria.ieee.update_one({"_id": queryObj}, {"$set": {"totalsave": totalsave, "update": 0}})

class threadDuplicates(threading.Thread):
	def __init__(self, threads, iddb):
		threading.Thread.__init__(self)
		self.name = "duplicates"		
		self.threads = threads
		self.iddb = iddb
	def run(self):
		for t in self.threads:
			t.join()
		query = client.memoria.query.find_one({"_id": ObjectId(self.iddb)})
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
	
def searchComplete(idquery):
	print("actualizacion" + idquery)
	objInsert = client.memoria.query.find_one({"_id": ObjectId(idquery)})
	retval = 0
	if objInsert:
		#try:
		for doc in objInsert["sources"]:
			if doc["name"] == "ieee":
				client.memoria.ieee.update_one({"_id": doc["db"]}, {"$set": {"update": 1}})
				item = client.memoria.ieee.find_one({"_id": doc["db"]})
				results = requestIEEE(objInsert["query"], 1, item["totalfound"])
				client.memoria.query.update_one({"_id": ObjectId(idquery), "sources.name": "ieee"}, {"$set": {"sources.$.db": results}})
			if doc["name"] == "elsevier":
				client.memoria.elsevier.update_one({"_id": doc["db"]}, {"$set": {"update": 1}})
				item = client.memoria.elsevier.find_one({"_id": doc["db"]})
				results = requestELSEVIER(objInsert["query"], 1, item["totalfound"])
				client.memoria.query.update_one({"_id": ObjectId(idquery), "sources.name": "elsevier"}, {"$set": {"sources.$.db": results}})
			if doc["name"] == "acm":
				client.memoria.acm.update_one({"_id": doc["db"]}, {"$set": {"update": 1}})
				item = client.memoria.acm.find_one({"_id": doc["db"]})
				results = requestACM(objInsert["query"], full = True)
				client.memoria.query.update_one({"_id": ObjectId(idquery), "sources.name": "acm"}, {"$set": {"sources.$.db": results}})
		client.memoria.query.update_one({"_id": ObjectId(idquery)}, {"$set": {"date" : time.asctime(time.localtime(time.time()))}, "$currentDate": {"lastModified": True}})
		#except:
		#	#raise e
		#	print("Error en actualizacion " + idquery)
		#	retval = -1
		#finally:			
		#	retval = 1
	return retval

def search(querytext):
	#Create new threads
	q = queue.Queue()
	thread2 = threadACM(querytext, q)
	thread1 = threadIEEE(querytext, q)
	#thread3 = threadELSEVIER(2, querytext)

	# Start new Threads
	thread1.start()
	thread2.start()
	#thread3.start()
	threads = [thread1, thread2]

	# Wait for all threads to respond
	while q.qsize() < 2:
		pass

	results = []
	while q.empty() is False:
		results.append(q.get())

	objInsert = {
		"query" :  querytext,
		"date" : time.asctime(time.localtime(time.time())),
		"sources": results,
#	[
#		{"name": "ieee", "db": outObjectId["ieee"]},
#		{"name": "elsevier", "db" : outObjectId["elsevier"]},
#		{"name": "acm", "db": outObjectId["acm"]}]
		}
	saved = client.memoria.query.insert(objInsert)
	threadDuplicates(threads, str(saved)).start()
	print("return " + querytext)
	return saved


def getAbstract(inputdata):
	returnObject = {"update": 0, "code": "nothing"}
	if inputdata.get("source") == "acm":
		match = scriptDB.simpleAggregateSource({"name": inputdata.get("source"), "db": ObjectId(inputdata.get("iddb"))}, match = {"results.rank": inputdata.get("rank")})
		try:
			response = requests.get(match["results"]["mdurl"] + "&preflayout=flat", headers=headers)
			soup = BeautifulSoup(response.text, 'html.parser')
			abstract = soup.find("div", {"class":"flatbody"}).div.text
			print("abst from acm: " + abstract)
			if abstract:
				modifiedValues = client.memoria[inputdata['source']].update_one({"_id": ObjectId(inputdata["iddb"]), "results.rank": inputdata["rank"]}, {"$set": {"results.$.abstract": abstract}}).modified_count
				if modifiedValues:
					returnObject["update"] = modifiedValues
					returnObject["abstract"] = abstract
		except:
			returnObject = {"update": 0, "code": "fail"}
	return returnObject

def testing():
	urlWhile = 'http://api.elsevier.com/content/search/scidir?apiKey=0d60bd360e3210fb90c335d1c538fe19&httpAccept=application/xml&oa=true&query=math'
	return requests.get(urlWhile).text
