import requests
from pymongo import MongoClient
from bson.objectid import ObjectId

import time
import threading

try:
	import xml.etree.cElementTree as ET
except:
	import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import bibtexparser

client = MongoClient('mongodb://niko_nmv:tesista@ds052408.mongolab.com:52408/memoria')
	
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

def requestACM(querytext, full = False):
	url = "http://dl.acm.org/exportformats_search.cfm?filtered=&within=owners%2Eowner%3DHOSTED&dte=&bfr=&srt=%5Fscore&expformat=bibtex&query=" + querytext
	print(time.asctime(time.localtime(time.time()))  + " query from: " + url)
	downBit = requests.get(url).text
	parsered = bibtexparser.loads(downBit)
	totalfound = len(parsered.entries)
	totalsave = 0
	initObj = {
		"query" : querytext,
		"date" : time.asctime(time.localtime(time.time())),
		"totalfound" : totalfound,		
		"totalsave": totalsave,
		"results" : []}	
	queryObj = client.memoria.acm.insert(initObj)

	results = []
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
			"mdurl": element.get("url"),
			"pubN": pubN,
			"pubY": element.get("year"),
			"pubP": element.get("pages"),
			"doi": element.get("doi"),
			"vote": {},
			})
		if ((totalsave%100) is 0) or (totalsave is totalfound):
			client.memoria.acm.update_one({"_id": queryObj}, {"$push": {"results": {"$each": results}}})				
			results.clear()
			if (totalsave is 100) and (full is False):
				break
	client.memoria.acm.update_one({"_id": queryObj}, {"$set": {"totalsave": totalsave}})
	return queryObj


def requestELSEVIER(querytext, now, maxres):
	url = 'http://api.elsevier.com/content/search/scidir?apiKey=3c332dc26c8b79d51d16a786b74fe76b&httpAccept=application/xml&oa=true&query=' + querytext
	print(time.asctime(time.localtime(time.time()))  + " query from: " +url)
	totalfound = int("0"+putAtributeUn(ET.fromstring(requests.get(url).text).find("{http://a9.com/-/spec/opensearch/1.1/}totalResults")))
	totalsave = 0
	now -=1
	count = 100
	rank = 1
	initObj = {
		"query" : querytext,
		"date" : time.asctime(time.localtime(time.time())),
		"totalfound" : totalfound,		
		"totalsave": totalsave,
		"results" : []}	
	queryObj = client.memoria.elsevier.insert(initObj)
	while totalfound > 0:
		if now <= maxres:
			results = []
			urlWhile = 'http://api.elsevier.com/content/search/scidir?apiKey=3c332dc26c8b79d51d16a786b74fe76b&httpAccept=application/xml&oa=true&query=' + querytext + '&count=' + str(count) + '&start=' + str(now) # + '&view=complete'
			for element in ET.fromstring(requests.get(urlWhile).text).findall("{http://www.w3.org/2005/Atom}entry"):##BeautifulSoup(requests.get(urlWhile).text).find_all("entry"):
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
			client.memoria.elsevier.update_one({"_id": queryObj}, {"$push": {"results": {"$each": results}}})
		else:
			break
	client.memoria.elsevier.update_one({"_id": queryObj}, {"$set": {"totalsave": totalsave}})
	return queryObj

def requestIEEE(querytext, now, maxres):
	url = 'http://ieeexplore.ieee.org/gateway/ipsSearch.jsp?hc=0&md=' + querytext
	print(time.asctime(time.localtime(time.time()))  + " query from: " +url)
	totalfound = int("0"+putAtributeUn(ET.fromstring(requests.get(url).text).find("totalfound")))
	totalsave = 0
	count = 100
	initObj = {
		"query" : querytext,
		"date" : time.asctime(time.localtime(time.time())),
		"totalfound" : totalfound,		
		"totalsave": totalsave,
		"results" : []}	
	queryObj = client.memoria.ieee.insert(initObj)
	while totalfound > 0:
		if now <= maxres:
			results = []
			urlWhile = 'http://ieeexplore.ieee.org/gateway/ipsSearch.jsp?sort=relevancy&md=' + querytext + '&hc=' + str(count) + '&rs=' + str(now)
			for element in ET.fromstring(requests.get(urlWhile).text).findall("document"):	
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
			client.memoria.ieee.update_one({"_id": queryObj}, {"$push": {"results": {"$each": results}}})
		else:
			break
	client.memoria.ieee.update_one({"_id": queryObj}, {"$set": {"totalsave": totalsave}})		
	return queryObj

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
	maxres = 100
	objInsert = {
		"query" :  querytext,
		"date" : time.asctime(time.localtime(time.time())),
		"sources": [{"name": "ieee", "db": requestIEEE(querytext, 1, maxres)},
			{"name": "elsevier", "db" : requestELSEVIER(querytext, 1, maxres)},
			{"name": "acm", "db": requestACM(querytext, full = False)}]
		}
	return client.memoria.query.insert(objInsert)

def testing():
	urlWhile = 'http://api.elsevier.com/content/search/scidir?apiKey=0d60bd360e3210fb90c335d1c538fe19&httpAccept=application/xml&oa=true&query=math'
	return requests.get(urlWhile).text
