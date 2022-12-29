import streamlit as st
import pandas as pd
import numpy as np

st.title('Sök instruktioner')

myn_reg = ('https://myndighetsregistret.scb.se/myndighet/download?myndgrupp=Statliga%20förvaltningsmyndigheter&format=True')

def load_data(url):
		web = req.get(url)
		web.encoding = web.apparent_encoding
    data = pd.read_excel(web)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    return data

# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')
# Load 10,000 rows of data into the dataframe.
data = load_data(myn_reg)
# Notify the reader that the data was successfully loaded.
data_load_state.text('Loading data...done!')
