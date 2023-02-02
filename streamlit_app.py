import streamlit as st
import pandas as pd
import requests as req
import openpyxl
from bs4 import BeautifulSoup
import time, re

scb_url = 'https://myndighetsregistret.scb.se/myndighet/download?myndgrupp=$&format=True'

scb_lists = [
	'Statliga%20förvaltningsmyndigheter',
	'Myndigheter%20under%20riksdagen',
	'Statliga%20affärsverk'
	]

esv_url = "https://www.esv.se/statsliggaren/"

typ = ['Instruktioner', 'Regleringsbrev' ]
styp = ['Bokstavsordning', 'Relevans']

# == WEBLOAD ==

@st.cache(persist=True)
def webload(url):
	web = req.get(url)
	web.encoding = web.apparent_encoding
	return web.content

# == LOAD_DOCLIST ==

def load_doclist(td):
	if td == 0:
		r = pd.DataFrame()
		for part in scb_lists:
			url = scb_url.replace('$', part)
			a = pd.read_excel(webload(url))
			r = pd.concat([r, a], ignore_index=True)
		r.rename(lambda x: str(x).lower(), axis='columns', inplace=True)
		r.drop(r[r['sfs'] == ''].index, inplace = True)
		r['url'] = "https://rkrattsbaser.gov.se/sfst?bet=" + r['sfs'].astype(str)
		return r
	elif td == 1:
		soup = BeautifulSoup(webload(esv_url))
		links = soup.select("a[href*=SenasteRegleringsbrev]")
		n, u = [], []
		for l in links:
			n.append(l.get_text())
			u.append('https://www.esv.se' + l.get("href"))
		data = {'namn': n, 'url': u }
		r = pd.DataFrame(data)
		return r

# == LOAD_DOC ==

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

# == LAYOUT ==
	
st.title('Sök i instruktioner och regleringsbrev')
st.write("Här kan du söka i svenska myndigheters aktuella instruktioner och regleringsbrev.")

search = st.text_input(
	"Sök efter:"
)

col1, col2 = st.columns(2)

doctype = col1.radio(
	"Dokument",
	(typ),
	horizontal = True
)
		
sorttype = col2.radio(
	"Sortering",
	(styp),
	horizontal = True
)

st.write('')

ph = st.empty()
ph.markdown('*Inga sökresultat*')

# == SEARCH ==
tothits = 0
if search:
	t = typ.index(doctype)
	ph.empty()
	res = ph.container()
	df = load_doclist(t)
	df_res = pd.DataFrame()
	
	for index, row in df.iterrows():
		hits = 0
		r = load_doc(row['url'], t)
		if not r is None:
			hits = len(re.findall(search.lower(), r['text']))
			if hits: tothits += 1	
		
		df_res = pd.concat(
			[
				df_res,
				pd.DataFrame.from_dict({
					'org': [row['namn'].strip()], 
					'hit': [hits], 
					'doc': [r['namn'].strip()], 
					'url': [row['url'].strip()]
					})
			],
			ignore_index=True
		)
	
	if styp.index(sorttype):
		df_res = df_res.sort_values(by='hit', ascending=False)
	else:
		df_res = df_res.sort_values(by='org')
	
	for index, row in df_res.iterrows():
		if row['hit']:
			res.markdown('[' + row['doc'] + '](' + row['url'] + ')')
			res.caption(row['org'] + ', ' + str(row['hit']) + ' träff(ar)')	
	
	res.caption('\nAntal dokument med träff: ' + str(tothits))
	
	if tothits:
		csv = df_res.to_csv(
			index=False, 
			header=[ 'myndighet', 'sökträffar', 'styrdokument', 'länk'],
			sep=';'
		)
		res.download_button(
			label='Ladda ner resultat',
			data=csv.encode('latin_1'),
			file_name='sökresultat.csv',
			mime='text/csv'
		)
