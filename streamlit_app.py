import streamlit as st
import pandas as pd
#import numpy as np
import requests as req
import openpyxl
from bs4 import BeautifulSoup
import time

myn_scb = ('https://myndighetsregistret.scb.se/myndighet/download?myndgrupp=Statliga%20förvaltningsmyndigheter&format=True')
myn_esv = ('https://www.esv.se/myndigheter/ExportExcelAllaArMyndigheter/')

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


st.title('Sök i instruktioner och regleringsbrev')
st.write("Här kan du söka i alla svenska förvaltningsmyndigheters aktuella instruktioner och regleringsbrev.")

search = st.text_input(
	"Sök efter:",
	label_visibility="visible",
	disabled=False
	)

ph = st.empty()
result = ph.container()
result.markdown('*Inga sökresultat*')

scb_data = pd.read_excel(webload(myn_scb))
scb_data.rename(lambda x: str(x).lower(), axis='columns', inplace=True)
scb_data['namn'] = scb_data['namn'].str.capitalize()

esv_data = pd.read_excel(webload(myn_esv))
esv_data.rename(lambda x: str(x).lower(), axis='columns', inplace=True)

data = pd.merge(scb_data, esv_data, how='left', left_on = 'organisationsnr', right_on = 'orgnr')

data = data.reset_index()

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
				result.write(f'- {hits} träffar i instruktionen ([SFS {sfs}](https://rkrattsbaser.gov.se/sfst?bet={sfs}))')
			