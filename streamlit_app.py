import streamlit as st
from Adinaw import Adinaw
from page1 import page1_page
from page2 import page2_page

st.sidebar.title("Content")
page = st.sidebar.radio("Go to", ["Adinaw", "Page 1", "Page 2"])

if page == "Adinaw":
    Adinaw()
elif page == "Page 1":
    page1_page()
elif page == "Page 2":
    page2_page()