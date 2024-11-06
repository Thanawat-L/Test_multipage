import streamlit as st
from home import home_page
from page1 import page1_page
from page2 import page2_page

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Page 1", "Page 2"])

if page == "Home":
    home_page()
elif page == "Page 1":
    page1_page()
elif page == "Page 2":
    page2_page()
