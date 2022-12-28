#!/usr/bin/env python3

import re, os, hashlib, time, datetime
import requests as req
from bs4 import BeautifulSoup

search = "kontroll"

def load(url, cache = True):		
	cpath = "./cache/"
	hash = hashlib.md5(url.encode()).hexdigest()
	
	#d = datetime.datetime.now()
	#hash += str(d.year) + str(d.month)
	
	if os.path.isfile(cpath + hash) and cache:
		with open(cpath + hash, "r", encoding="utf-8") as f:
			r = f.read()
	else:
		time.sleep(3)
		web = req.get(url)
		web.encoding = web.apparent_encoding
		r = web.text
		with open(cpath + hash, "w", encoding="utf-8") as f:
			f.write(r)
	return r
	
myndigheter = load("https://myndighetsregistret.scb.se/myndighet/download?myndgrupp=Statliga%20förvaltningsmyndigheter&format=False").splitlines()

for myndighet in myndigheter[1:]:
	data = myndighet.split("\t")	
	if not data[12] == "":
		html = load("https://rkrattsbaser.gov.se/sfst?bet=" + data[12])
		soup = BeautifulSoup(html, "html5lib")
		instruktion = soup.get_text()
		hits = instruktion.count(search)
		if hits > 0:
			print(data[1].capitalize(),":", hits)
