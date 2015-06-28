from pymongo import MongoClient
from bson.objectid import ObjectId
import time

def add(dbname, doc):
	client = MongoClient()

def readSource(dbname, id):
	client = MongoClient()
	if dbname == "ieee":
		return client.memoria.ieee.find_one({"_id": ObjectId(id)})
	if dbname == "elsevier":
		return client.memoria.elsevier.find_one({"_id": ObjectId(id)})

def updateVote (dbname, id, rank, value):
	client = MongoClient()
	if dbname == "ieee":
		return client.memoria.ieee.update_one({"_id": ObjectId(id), "results.rank": rank}, {"$set": {"results.$.vote": value}})
	if dbname == "elsevier":
		return client.memoria.elsevier.update_one({"_id": ObjectId(id), "results.rank": rank}, {"$set": {"results.$.vote": value}})

def createFolder (namefolder):
	client = MongoClient()
	objInsert = {
		"folder": namefolder,
		"creator": "none",
		"date" : time.asctime(time.localtime(time.time())),
		"search": [],
		}
	return client.memoria.folder.insert(objInsert)

def addToFolder(idquery, idfolder):
	client = MongoClient()
	client.memoria.folder.update_one({"_id": ObjectId(idfolder)}, {"$push": {"search": {"id": idquery}}})
	client.memoria.query.update_one({"_id": ObjectId(idquery)}, {"$set": {"folder": idfolder}})


def readQuery(id):
	client = MongoClient()
	return client.memoria.query.find_one({"_id": ObjectId(id)})