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
def load_doc(url, typ):
	if not str(url)[0:4] == "http":
		return None
	time.sleep(3)
	html = webload(url)
	soup = BeautifulSoup(html)
	
	if typ == 'sfs':
		n = soup.find("span","bold")
		t = soup.find("div","body-text")
	elif typ == 'rb':
		n = soup.find("div",{"id": "BrevInledandeText_Rubrik"})
		t = soup.find("section", {"id": "letter"})		
	
	if n is None or t is None:
		return None
	else:
		return {
			'namn': n.get_text(),
			'text': t.get_text()
			}

def load_mr():
	# Läs in myndighetsregistret
	r = pd.read_excel(webload(scb_url))
	r.rename(lambda x: str(x).lower(), axis='columns', inplace=True)
	r['namn'] = r['namn'].str.capitalize()
	r['sfs'] = "https://rkrattsbaser.gov.se/sfst?bet=" + r['sfs'].astype(str)
	r['cnamn'] = r.loc[:, 'namn']
	r.loc[r['cnamn'].str.contains("Länsstyrelsen"), 'cnamn'] = 'Länsstyrelserna'
	r = r.reset_index()
	
	# Läs in ESVs myndighetslista
	soup = BeautifulSoup(webload(esv_url))
	links = soup.select("a[href*=SenasteRegleringsbrev]")
	
	# Lägg ihop listorna
	for link in links:
		namn = link.get_text().strip().capitalize()
		r.loc[r['cnamn'] == namn, 'rb'] = 'https://www.esv.se' + link.get("href")	
	return r

# ================================
	
st.title('Sök i instruktioner och regleringsbrev')
st.write("Här kan du söka i svenska förvaltningsmyndigheters aktuella instruktioner och regleringsbrev.")

search = st.text_input(
	"Sök efter:",
	label_visibility="visible"
	)

doctype = st.radio(
    "Typ av dokument att sök i:",
    ('Instruktion', 'Regleringsbrev'),
		horizontal = True,
		label_visibility = "collapsed")

st.write('')

ph = st.empty()
result = ph.container()
result.markdown('*Inga sökresultat*')
	
if search:
	hits = 0
	sources = []
	ph.empty()
	result=ph.container()
	df = load_mr()
			
	for index, row in df.iterrows():
		sfs_hits, rb_hits = 0, 0
		source = { 'namn': row['namn'] }
		
		sfs = row['sfs']
		r = load_doc(sfs, "sfs")
		if not r is None:
			source['sfs'] = r['namn']
			sfs_hits = r['text'].lower().count(search.lower())
		else:
			source['sfs'] = '*Saknas*'
			
		rb = row['rb']
		r = load_doc(rb, "rb")
		if not r is None:
			source['rb'] = r['namn']
			rb_hits = r['text'].lower().count(search.lower())
		else:
			source['rb'] = '*Saknas*'
			
		if sfs_hits > 0 or rb_hits > 0:
			hits += 1
			result.write(f'[{sfs}]({sfs})')
			if sfs_hits > 0:
				result.caption(f' {sfs_hits} träff(ar) i [instruktionen]({sfs})')
			if rb_hits > 0:
				result.caption(f' {rb_hits} träff(ar) i senaste [regleringsbrevet]({rb})')
		sources.append(source)
				
	if hits == 0:
		result.write('*Inga sökresultat*')

#	exp = result.expander('Genomsökta källor')
#	exp.write('Sökningen sker maskinellt i Regeringskansliets rättdatabas samt Ekonomistyrningsverkets statsliggare. Nedan redovisas  styrdokumenten som ingick i sökingen.')
#	for s in sources:
#		exp.write(s['namn'])
#		exp.caption("Instruktion: " + s['sfs'])
#		exp.caption("Regleringsbrev: " + s['rb'])
		