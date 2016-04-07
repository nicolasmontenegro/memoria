from openpyxl import Workbook
import sys

from . import scriptDB

def xlsfile(id):
	print(id)
	out = scriptDB.readQuery(id)
	print(out)
	if out is None :
		print(id + " no encontrado")
		return ""
	try:
		wb = Workbook()
		ws = wb.active
		print("check 1")
		ws.title = out["query"][:10]
		ws['A'+ str(1)] = "query" 
		ws['A'+ str(2)] = out["query"]
		ws['B'+ str(1)] = "date" 
		ws['B'+ str(1)] = out["date"]
		print("check 2")
		for doc in out["sources"]:
			ws = wb.create_sheet()
			ws.title = doc['name']
			print("check 3")
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
			print("check 4")
			docAux = scriptDB.readSource(doc["name"], str(doc["db"])) 
			print(docAux[:20])
			for item in docAux:
				ws['A'+ str(row)] = item['rank']
				ws['B'+ str(row)] = item['title']
				ws['C'+ str(row)] = item['authors']
				ws['D'+ str(row)] = item['abstract']
				ws['E'+ str(row)] = item['mdurl']
				ws['F'+ str(row)] = item['pubN']
				ws['G'+ str(row)] = item['pubY']
				ws['H'+ str(row)] = item['pubP']
				ws['I'+ str(row)] = item['doi']
				row += 1
		print("saving " + 'buscador/xls/' +  str(out["_id"]) + '.xlsx')
		strout = 'buscador/xls/' +  str(out["_id"]) + '.xlsx'
		wb.save(strout)
		print("saved")
		return strout
	except:
		print("error en xlsx")
		return ""
