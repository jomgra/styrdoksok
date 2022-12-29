import streamlit as st
import pandas as pd
import numpy as np
import requests as req
import openpyxl

st.title('Sök instruktioner')

myn_reg = ('https://myndighetsregistret.scb.se/myndighet/download?myndgrupp=Statliga%20förvaltningsmyndigheter&format=True')

@st.cache(ttl=2592000)
def webload(url):
	web = req.get(url)
	web.encoding = web.apparent_encoding
	return web.content

data_load_state = st.text('Loading data...')

data = pd.read_excel(webload(url))
lowercase = lambda x: str(x).lower()
data.rename(lambda x: str(x).lower(), axis='columns', inplace=True)

data_load_state.text('Loading data...done!')

data['namn'] = data['namn'].str.capitalize()

st.subheader('Raw data')
st.write(data)


