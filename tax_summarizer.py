import streamlit as st

with open("README.md", "r") as f:
    text = f.read()

st.write(text)
