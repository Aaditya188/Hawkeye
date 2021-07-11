# imports
import streamlit as st
import cv2
import csv
from PIL import Image
import pandas as pd
import time
import os
import numpy as np
from datetime import time
from search_word import search_word


# sidebar
st.sidebar.image("../assets/logo.png")
st.sidebar.header("Search Module")
st.sidebar.markdown(
    "Providing an extra feature to look for specific events along with exact time in the log file so that no critical event is missed. "
)
st.sidebar.header("Special Features")
st.sidebar.markdown("""- Get a visualization of the CCTV Cameras""")
st.sidebar.markdown("""- Define keywords of the event""")
st.sidebar.markdown("""- Define time of the event""")
st.sidebar.markdown("[Github]()")
st.sidebar.markdown("[Video Demo]()")


# Data Uploads
st.header("Look for Events")
# uploading results
st.subheader("Upload the CCTV CSV Log File")
file = st.file_uploader("CCTV Logs")


# loading results
@st.cache
def load_data(nrows):
    data = pd.read_csv(file, nrows=nrows, error_bad_lines=False)
    lower = lambda x: str(x).lower()
    data.rename(lower, axis="columns", inplace=True)
    return data


if file is not None:
    data_load_state = st.text("")
    data = load_data(10000)
    # seeing data
    st.subheader("Raw data")
    st.write(data)

# sample cctv map
st.subheader("Upload the CCTV Map Coordinates here")
cctv_map = st.file_uploader("CCTV Map Co-ordinates")
if cctv_map is not None:
    st.subheader("CCTV Map Detection")
    df = pd.read_csv(cctv_map)
    st.map(df)


# Search
st.header("Searching Logs")

# keywords
st.subheader("Enter the keywords related to the Event")
keywords = st.text_input("")
keywords = keywords.split(sep=" ")
list(keywords)
# button
if st.button("Look for it"):
    row = search_word(data, keywords)
    for k in row:
        st.write(data.loc[[k], :])
