import streamlit as st
import pandas as pd
import requests as req
import openpyxl
from bs4 import BeautifulSoup
import time

myndighetregistret_url = 'https://myndighetsregistret.scb.se/myndighet/download?myndgrupp=Statliga%20förvaltningsmyndigheter&format=True'

statsliggaren_url = "https://www.esv.se/statsliggaren/"

@st.cache(ttl=2592000)
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

data = pd.read_excel(webload(myndighetregistret_url))
data.rename(lambda x: str(x).lower(), axis='columns', inplace=True)
data['namn'] = data['namn'].str.capitalize()

data = data.reset_index()

esv = webload(statsliggaren_url)
soup = BeautifulSoup(esv)
links = soup.select("a[href*=SenasteRegleringsbrev]")

for link in links:
	data.loc[data['namn'].lower() == link.get_text().strip().lower(), 'rb'] = link.href
	
st.write(data)
	
if search:
	ph.empty()
	result=ph.container()
	for index, row in data.iterrows():
		nullcheck = data.loc[index].isnull()
		myndighet = row['namn']
		if not nullcheck['sfs']:
			sfs = row['sfs'].strip()
			hits = load_sfs(sfs).lower().count(search.lower())
			if hits > 0:
				result.markdown(f'**{myndighet}**')
				result.caption(f'- {hits} träffar i instruktionen ([SFS {sfs}](https://rkrattsbaser.gov.se/sfst?bet={sfs}))')
			