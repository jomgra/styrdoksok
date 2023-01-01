import streamlit as st
import pandas as pd
import requests as req
import openpyxl
from bs4 import BeautifulSoup
import time

scb_url = 'https://myndighetsregistret.scb.se/myndighet/download?myndgrupp=Statliga%20förvaltningsmyndigheter&format=True'

esv_url = "https://www.esv.se/statsliggaren/"

@st.cache(persist=True)
def webload(url):
	web = req.get(url)
	web.encoding = web.apparent_encoding
	return web.content

@st.cache(persist=True)
def load_sfs(sfs):
	time.sleep(3)
	html = webload("https://rkrattsbaser.gov.se/sfst?bet=" + sfs)
	soup = BeautifulSoup(html)
	r = soup.find("div","body-text").get_text()
	return r

@st.cache(persist=True)
def load_rb(url):
	time.sleep(3)
	html = webload(url)
	soup = BeautifulSoup(html)
	r = soup.find("section", {"id": "letter"})
	if r is None:
		return ""
	else:
		return r.get_text()

# ================================
	
st.title('Sök i instruktioner och regleringsbrev')
st.write("Här kan du söka i alla svenska förvaltningsmyndigheters aktuella instruktioner och regleringsbrev.")

search = st.text_input(
	"Sök efter:",
	label_visibility="visible"
	)

ph = st.empty()
result = ph.container()
result.markdown('*Inga sökresultat*')
	
if search:
	hits = 0
	sources = []
	ph.empty()
	result=ph.container()
	data = pd.read_excel(webload(scb_url))
	data.rename(lambda x: str(x).lower(), axis='columns', inplace=True)
	data['namn'] = data['namn'].str.capitalize()
	data = data.reset_index()
	soup = BeautifulSoup(webload(esv_url))
	links = soup.select("a[href*=SenasteRegleringsbrev]")
	for link in links:
		namn = link.get_text().strip().capitalize()
		data.loc[data['namn'] == namn, 'rb'] = 'https://www.esv.se' + link.get("href")
		
	for index, row in data.iterrows():
		sfs_hits = 0
		rb_hits = 0
		nullcheck = data.loc[index].isnull()
		sources.append(row['namn'])
		if not nullcheck['sfs']:
			sfs = row['sfs'].strip()
			sfs_hits = load_sfs(sfs).lower().count(search.lower())
		if not nullcheck['rb']:
			rb = row['rb']
			rb_hits = load_rb(rb).lower().count(search.lower())
			
		if sfs_hits > 0 or rb_hits > 0:
			hits += 1
			result.markdown('**' + row['namn'] + '**')
			if sfs_hits > 0:
				result.caption(f'- {sfs_hits} träff(ar) i instruktionen ([SFS {sfs}](https://rkrattsbaser.gov.se/sfst?bet={sfs}))')
			if rb_hits > 0:
				result.caption(f'- {rb_hits} träff(ar) i senaste [regleringsbrevet]({rb})')
				
	if hits == 0:
		result.markdown('*Inga sökresultat*')
	exp = result.expander('Genomsökta källor')
	exp.write('Sökningen sker maskinellt i Regeringskansliets rättdatabas samt Ekonomistyrningsverkets statsliggare. I enstaka fall kan sökningen missa styrdokument. Nedan kan du kontrollera vilka styrdokument som ingick i sökingen.')
	for source in sources:
		exp.write(source)