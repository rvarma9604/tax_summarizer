
import pandas as pd
import streamlit as st

_DEFAULT_BANK_NAME = "Bank-1"

st.title("Document Upload")
st.write(
    """The program expects the content of the file to be in the following format"""
)

sample_data = pd.read_csv("samples/bank_summary.csv")
sample_data.fillna("", inplace=True)

st.dataframe(sample_data, use_container_width=True)

st.write("Upload Bank Transaction History")

upload_column, bank_label_column = st.columns(2)

with upload_column:
    txn_file = st.file_uploader(label="Upload file", label_visibility="collapsed")

with bank_label_column:
    bank_name = st.text_input(label="Bank Name", value=_DEFAULT_BANK_NAME, label_visibility="collapsed").strip()

if txn_file is None:
    st.info("Please upload file to continue")
    if bank_name == "":
        bank_name = _DEFAULT_BANK_NAME

    st.session["data"] = {
        "txn_file": txn_file,
        "bank_name": bank_name
    }
