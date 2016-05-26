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

from . import scriptDB

import random

results = []
threadLock = threading.Lock()

class myThread (threading.Thread):
	def __init__(self, threadID, querytext):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = "acm"
		self.querytext = querytext
	def run(self):

		print ("Starting " + self.name)
		# Get lock to synchronize threads
		url = "http://dl.acm.org/exportformats_search.cfm?filtered=&within=owners%2Eowner%3DHOSTED&dte=&bfr=&srt=%5Fscore&expformat=bibtex&query=" + self.querytext
		print(time.asctime(time.localtime(time.time()))  + " query from: " + url)
		downBit = requests.get(url).text
		parsered = bibtexparser.loads(downBit)
		totalfound = len(parsered.entries)
		self.val = str(len(parsered.entries)) + " " + str(random.randint(1, 100)  )

def callThreads(querytext):	
	threads = []

	# Create new threads
	thread1 = myThread(1, querytext)
	thread2 = myThread(2, querytext)

	# Start new Threads
	thread1.start()
	thread2.start()

	# Add threads to thread list
	threads.append(thread1)
	threads.append(thread2)

	# Wait for all threads to complete
	for t in threads:
		t.join()
	print (results)