import streamlit as st
import pandas as pd
import requests as req
import openpyxl
from bs4 import BeautifulSoup
import time

scb_url = 'https://myndighetsregistret.scb.se/myndighet/download?myndgrupp=Statliga%20förvaltningsmyndigheter&format=True'

esv_url = "https://www.esv.se/statsliggaren/"

typ = ['Instruktion', 'Regleringsbrev']

@st.cache(persist=True)
def webload(url):
	web = req.get(url)
	web.encoding = web.apparent_encoding
	return web.content

@st.cache(persist=True)
def load_doc(url, td):
	if not str(url)[0:4] == "http":
		return None
	time.sleep(3)
	html = webload(url)
	soup = BeautifulSoup(html)
	
	if td == 0:
		n = soup.find("span","bold")
		t = soup.find("div","body-text")
	elif td == 1:
		n = soup.find("div",{"id": "BrevInledandeText_Rubrik"})
		t = soup.find("section", {"id": "letter"})		
	
	if n is None or t is None:
		return None
	else:
		return {
			'namn': n.get_text(),
			'text': t.get_text().lower()
			}

def load_mr(td):
	if td == 0:
		r = pd.read_excel(webload(scb_url))
		r.rename(lambda x: str(x).lower(), 
		axis='columns', inplace=True)
		r['namn'] = r['namn'].str.capitalize()
		r['url'] = "https://rkrattsbaser.gov.se/sfst?bet=" + r['sfs'].astype(str)
		r = r.reset_index()
		return r
	elif td == 1:
		soup = BeautifulSoup(webload(esv_url))
		links = soup.select("a[href*=SenasteRegleringsbrev]")
		n, u = [], []
		for l in links:
			n.append(l.get_text().strip().capitalize())
			u.append('https://www.esv.se' + l.get("href"))
		data = {
			'namn': n,
			'url': u
		}
		r = pd.DataFrame(data)
		r = r.reset_index()
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
    (typ), 
		horizontal = True,
		label_visibility = "collapsed")

st.write('')

ph = st.empty()
result = ph.container()
result.markdown('*Inga sökresultat*')
	
if search:
	t = typ.index(doctype)
		
	ph.empty()
	result = ph.container()
	df = load_mr(t)
			
	for index, row in df.iterrows():
		hits = 0
		r = load_doc(row['url'], t)
		if not r is None:
			hits = r['text'].count(search.lower())
			if hits > 0:
				myn = row['namn']
				result.markdown('[' + r['namn'] + '](' + row['url'] + ')<br\>t')
				result.caption(f'{myn}, {hits} träff(ar)')
