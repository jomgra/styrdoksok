import streamlit as st
import pandas as pd
#import numpy as np
import requests as req
import openpyxl
from bs4 import BeautifulSoup

st.title('Sök instruktioner')

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

data1 = pd.read_excel(webload(myn_scb))
data1.rename(lambda x: str(x).lower(), axis='columns', inplace=True)
data1['namn'] = data1['namn'].str.capitalize()

st.subheader('Raw data SCB')
st.write(data1)

data2 = pd.read_excel(webload(myn_esv))
data2.rename(lambda x: str(x).lower(), axis='columns', inplace=True)

st.subheader('Raw data ESV')
st.write(data2)

data3 = pd.merge(data1, data2, how='left', left_on = 'organisationsnr', right_on = 'orgnr')

st.subheader('Raw data merged')
st.write(data3)

st.write(load_sfs("2007:854"))