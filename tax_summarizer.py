import streamlit as st

st.set_page_config(layout="wide")
with open("README.md", "r") as f:
    text = f.read()

st.write(text)
