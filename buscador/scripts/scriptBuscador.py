from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
import time
try:
	import xml.etree.cElementTree as ET
except:
	import xml.etree.ElementTree as ET
	
maxres = 100

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

def requestELSEVIER(querytext):
	url = 'http://api.elsevier.com/content/search/scidir?apiKey=0d60bd360e3210fb90c335d1c538fe19&httpAccept=application/xml&oa=true&query=' + querytext
	print(url)
	print(time.asctime(time.localtime(time.time()))  + " query from: " +url)
	##totalfound = int("0"+putAtributeUn(BeautifulSoup(requests.get(url).text, "xml").find("totalResults")))
	totalfound = int("0"+putAtributeUn(ET.fromstring(requests.get(url).text).find("{http://a9.com/-/spec/opensearch/1.1/}totalResults")))
	print(totalfound)
	now = 0
	count = 200
	rank = 1
	results = []
	while totalfound > 0:
		if now <= maxres:
			urlWhile = 'http://api.elsevier.com/content/search/scidir?apiKey=0d60bd360e3210fb90c335d1c538fe19&httpAccept=application/xml&oa=true&query=' + querytext + '&count=' + str(count) + '&start=' + str(now) ##+ '&view=complete'
			print(urlWhile)
			##for element in BeautifulSoup(requests.get(urlWhile).text, "xml").find_all("entry"):
			for element in ET.fromstring(requests.get(urlWhile).text).findall("{http://www.w3.org/2005/Atom}entry"):##BeautifulSoup(requests.get(urlWhile).text).find_all("entry"):
				strAuthor = ""
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
					"vote": 0,
					})
				rank += 1
			now += count				
		else:
			break
	print(time.asctime( time.localtime(time.time())) + " returning")
	return {
		"query" : querytext,
		"date" : time.asctime(time.localtime(time.time())),
		"totalfound" : str(totalfound),
		"results" : results}


def requestIEEE(querytext):
	url = 'http://ieeexplore.ieee.org/gateway/ipsSearch.jsp?hc=0&md=' + querytext
	print(time.asctime(time.localtime(time.time()))  + " query from: " +url)
	##totalfound = int("0"+putAtributeUn(BeautifulSoup(requests.get(url).text, "xml").totalfound))
	totalfound = int("0"+putAtributeUn(ET.fromstring(requests.get(url).text).find("totalfound")))
	print(totalfound)
	now = 1
	count = 200
	results = []
	while totalfound > 0:
		if now <= maxres:
			urlWhile = 'http://ieeexplore.ieee.org/gateway/ipsSearch.jsp?sort=relevancy&md=' + querytext + '&hc=' + str(count) + '&rs=' + str(now)
			print(urlWhile)
			##for element in BeautifulSoup(requests.get(urlWhile).text, "xml").find_all("document"):
			for element in ET.fromstring(requests.get(urlWhile).text).findall("document"):	
				results.append({
					"rank": putAtributeUn(element.find("rank")),
					"title": putAtributeUn(element.find("title")),
					"authors": putAtributeUn(element.find("authors")),
					"abstract" : putAtributeUn(element.find("abstract")),
					"mdurl": putAtributeUn(element.find("mdurl")),
					"pdfurl": putAtributeUn(element.find("pdf")),
					"pubN": putAtributeUn(element.find("pubtitle")),
					"pubY": putAtributeUn(element.find("py")),
					"pubP": putAtributeUn(element.find("epage")),
					"doi": putAtributeUn(element.find("doi")),
					"vote": 0,})
			now += count
		else:
			break
	print(time.asctime( time.localtime(time.time())) + " returning")
	return {
		"query" : querytext,
		"date" : time.asctime(time.localtime(time.time())),
		"totalfound" : str(totalfound),
		"results" : results}

def buscar(querytext, max):
	maxres = max
	client = MongoClient()
	db = client.memoria
	objInsert = {
		"query" :  querytext,
		"date" : time.asctime(time.localtime(time.time())),
		"sources": [{"name": "ieee", "db": db.ieee.insert(requestIEEE(querytext))},
			{"name": "elsevier", "db" : db.elsevier.insert(requestELSEVIER(querytext))}]
		}
	return db.query.insert(objInsert)