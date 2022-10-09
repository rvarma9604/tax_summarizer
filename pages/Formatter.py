import pandas as pd
import streamlit as st
from datetime import datetime

from dateutil.parser import parse

def get_debit_credit_tables(data):
    debit_table = (
        data[data["WITHDRAWAL AMT"] != 0][["DATE", "TRANSACTION DETAILS", "WITHDRAWAL AMT"]]
        .reset_index(drop=True)
    )
    credit_table = (
        data[data["DEPOSIT AMT"] != 0][["DATE", "TRANSACTION DETAILS", "DEPOSIT AMT"]]
        .reset_index(drop=True)
    )

    return debit_table, credit_table

def formatter():
    st.title("Formatter")

    # if st.session_state.get("data", None) is None:
    #     st.info("Please upload the data first and then come back to this page :smile:")
    #     return

    from_col, to_col = st.columns(2)

    with from_col:
        from_date = st.date_input("From date")

    with to_col:
        to_date = st.date_input("To date")

    if from_date > to_date:
        st.error("From date cannot be less than To date")

    # data = st.session_state["data"]
    txn_table = pd.read_csv("/home/rajat/Downloads/bank.csv")

    # txn_file = data["txn_file"]
    # bank_name = data["bank_name"]

    # txn_table = pd.read_csv(txn_file)
    txn_table.columns = [col.strip().upper() for col in txn_table.columns]
    txn_table = (
        txn_table
        .sort_values("DATE", ascending=True)
        .reset_index(drop=True)
    )

    txn_table["DATE"] = pd.to_datetime(txn_table["DATE"].apply(parse), format="%d/%m/%Y").apply(datetime.date)

    txn_table = txn_table[
        (txn_table["DATE"] >= from_date)
        & (txn_table["DATE"] <= to_date)
    ]

    if len(txn_table) == 0:
        st.error(
            f"""You don't have any recorded transaction from: {from_date} to: {to_date}.
            Try selecting a different date range"""
        )

    st.write("## Transaction History")
    st.dataframe(txn_table, use_container_width=True)

    debit_table, credit_table = get_debit_credit_tables(txn_table)
    debit_col, credit_col = st.columns(2)
    
    with debit_col:
        st.write("## Withdrawal History")
        st.dataframe(debit_table, use_container_width=True)
    
    with credit_col:
        st.write("## Deposit History")
        st.dataframe(credit_table, use_container_width=True)


if __name__ == "__main__":
    formatter()