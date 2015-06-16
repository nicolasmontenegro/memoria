from pymongo import MongoClient
from bson.objectid import ObjectId

def add(dbname, doc):
	client = MongoClient()

def read(dbname, id):
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