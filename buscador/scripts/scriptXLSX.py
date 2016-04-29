from openpyxl import Workbook
import sys
from io import BytesIO

from . import scriptDB

def xlsfile(inputdata, inputcookie):
	out = scriptDB.readQuery(inputdata['idquery'])
	if out is None  :
		print(id + " no encontrado")
		return None
	user = scriptDB.unfold(inputcookie)
	folder = scriptDB.getFolder({"idquery": out["folder"]}, inputcookie, False)
	
	matchDowload = { "$and": []}

	if inputdata["typeQuery"] is "2":
		for userId in folder["user"] :
			matchDowload["$and"].append( {"results.vote.yes": userId} )
	elif inputdata["typeQuery"] is "1":
		matchDowload["$and"].append({"results.vote.yes": str(user["_id"])})
	elif inputdata["typeQuery"] is "0":
		matchDowload = None
	elif inputdata["typeQuery"] is "-1":
		matchDowload["$and"].append({"results.vote.no": str(user["_id"])})
	elif inputdata["typeQuery"] is "-2":
		for userId in folder["user"] :
			matchDowload["$and"].append( {"results.vote.no": userId} )

	#try:
	wb = Workbook()
	ws = wb.active
	ws.title = out["query"][:10]
	ws['A'+ str(1)] = "query" 
	ws['A'+ str(2)] = out.get("query")
	ws['B'+ str(1)] = "date" 
	ws['B'+ str(1)] = out.get("date")
	for doc in out["sources"]:
		ws = wb.create_sheet()
		ws.title = doc["name"]
		ws['A'+ str(1)] = "rank"
		ws['B'+ str(1)] = "title"
		ws['C'+ str(1)] = "authors"
		ws['D'+ str(1)] = "abstract"
		ws['E'+ str(1)] = "url"
		ws['F'+ str(1)] = "publication name"
		ws['G'+ str(1)] = "publication date"
		ws['H'+ str(1)] = "publication page"
		ws['I'+ str(1)] = "doi"
		row = 2
		docAux = scriptDB.simpleAggregateSource(doc, match = matchDowload, group = {"_id": '$_id', "results": {"$push": "$results"}})
		if docAux:
			for item in docAux['results']:
				ws['A'+ str(row)] = item.get('rank')
				ws['B'+ str(row)] = item.get('title')
				ws['C'+ str(row)] = item.get('authors')
				ws['D'+ str(row)] = item.get('abstract')
				ws['E'+ str(row)] = item.get('mdurl')
				ws['F'+ str(row)] = item.get('pubN')
				ws['G'+ str(row)] = item.get('pubY')
				ws['H'+ str(row)] = item.get('pubP')
				ws['I'+ str(row)] = item.get('doi')
				row += 1
	print("saving " + str(out["_id"]) + '.xlsx')
	out = BytesIO()
	wb.save(out)
	print("saved")
	return out
	#except:
	#	print("error en xlsx")
	#	return None