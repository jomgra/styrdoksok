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

@st.cache(persist=True)
def load_rb(url):
	time.sleep(3)
	html = webload(url)
	soup = BeautifulSoup(html)
	r = soup.find("section", {"id": "letter"}).get_text()
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

soup = BeautifulSoup(webload(statsliggaren_url))
links = soup.select("a[href*=SenasteRegleringsbrev]")

for link in links:
	namn = link.get_text().strip().capitalize()
	data.loc[data['namn'] == namn, 'rb'] = 'https://www.esv.se' + link.get("href")
	
if search:
	ph.empty()
	result=ph.container()
	sfs_hits = 0
	rb_hits = 0
	for index, row in data.iterrows():
		nullcheck = data.loc[index].isnull()
		myndighet = row['namn']
		if not nullcheck['sfs']:
			sfs = row['sfs'].strip()
			sfs_hits = load_sfs(sfs).lower().count(search.lower())
		if not nullcheck['rb']:
			rb = row['rb']
			rb_hits = load_rb(rb).lower().count(search.lower())
			
		if sfs_hits > 0 or rb_hits > 0:
			result.markdown(f'**{myndighet}**')
			if sfs_hits > 0:
				result.caption(f'- {sfs_hits} träffar i instruktionen ([SFS {sfs}](https://rkrattsbaser.gov.se/sfst?bet={sfs}))')
			if rb_hits > 0:
				result.caption(f'- {rb_hits} träffar i regleringsbrevet ([rb]({rb}))')