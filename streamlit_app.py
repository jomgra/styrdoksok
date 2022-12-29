import streamlit as st
import pandas as pd
#import numpy as np
import requests as req
import openpyxl
from bs4 import BeautifulSoup

myn_scb = ('https://myndighetsregistret.scb.se/myndighet/download?myndgrupp=Statliga%20förvaltningsmyndigheter&format=True')
myn_esv = ('https://www.esv.se/myndigheter/ExportExcelAllaArMyndigheter/')

@st.cache(ttl=2592000)
def webload(url):
	web = req.get(url)
	web.encoding = web.apparent_encoding
	return web.content

@st.cache(persist=True)
def load_sfs(sfs):
	html = webload("https://rkrattsbaser.gov.se/sfst?bet=" + sfs)
	soup = BeautifulSoup(html)
	r = soup.find("div","body-text").get_text()
	return r


st.title('Sök i instruktioner och regleringsbrev')
st.write("Här kan du söka i alla Svenska myndigheters aktuella instruktioner och regleringsbrev.")

search = st.text_input(
	"Sök efter:",
	label_visibility="visible",
	disabled=False
	)

st.write("Sökresultat:")
output = st.text("inget")

data1 = pd.read_excel(webload(myn_scb))
data1.rename(lambda x: str(x).lower(), axis='columns', inplace=True)
data1['namn'] = data1['namn'].str.capitalize()

data2 = pd.read_excel(webload(myn_esv))
data2.rename(lambda x: str(x).lower(), axis='columns', inplace=True)

data3 = pd.merge(data1, data2, how='left', left_on = 'organisationsnr', right_on = 'orgnr')

if search:
	output.text(load_sfs("2007:854"))