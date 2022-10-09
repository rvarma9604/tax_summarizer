import re
import pandas as pd
from requests import session
import streamlit as st
from datetime import datetime

from dateutil.parser import parse

pd.options.display.float_format = "{:,.2f}".format


def load_data(path):
    return pd.read_csv(path)


def get_debit_credit_tables(data):
    debit_table = (
        data[data["WITHDRAWAL AMT"] != 0][[
            "DATE", "TRANSACTION DETAILS", "WITHDRAWAL AMT"]]
        .reset_index(drop=True)
    )
    credit_table = (
        data[data["DEPOSIT AMT"] != 0][[
            "DATE", "TRANSACTION DETAILS", "DEPOSIT AMT"]]
        .reset_index(drop=True)
    )

    return debit_table, credit_table


def formatter():
    st.set_page_config(layout="wide")
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
    if st.session_state.get("saved_data", None) is None:
        txn_table = load_data("/home/rajat/Downloads/bank.csv")
        txn_table.columns = [col.strip().upper() for col in txn_table.columns]
        txn_table = txn_table[[
            "DATE", "TRANSACTION DETAILS", "WITHDRAWAL AMT", "DEPOSIT AMT"]]

        txn_table["DATE"] = (
            pd.to_datetime(txn_table["DATE"].apply(parse), format="%d/%m/%Y")
            .apply(datetime.date)
        )

        def parse_numbers(number):
            if isinstance(number, str):
                return float(re.sub(r"[^0-9\.-]", "", number))
            if isinstance(number, float) or isinstance(number, int):
                return number
            else:
                return 0.0

        for col in ["WITHDRAWAL AMT", "DEPOSIT AMT"]:
            txn_table[col] = txn_table[col].apply(parse_numbers)

        txn_table.fillna(value={"WITHDRAWAL AMT": 0.0,
                         "DEPOSIT AMT": 0.0}, inplace=True)
        st.write(f"""{txn_table["DEPOSIT AMT"].sum()}""")

        txn_table = (
            txn_table
            .sort_values(by="DATE", ascending=True)
            .reset_index(drop=True)
        )

        st.session_state["saved_data"] = {}
        st.session_state["saved_data"]["txn_table"] = txn_table
    else:
        txn_table = st.session_state.get("saved_data")["txn_table"]

    # txn_file = data["txn_file"]
    # bank_name = data["bank_name"]

    # txn_table = pd.read_csv(txn_file)

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

    rename_description = st.radio("Rename descriptions?", options=[
                                  "Yes", "No"], index=1, horizontal=True)

    if rename_description == "Yes":
        (
            debit_desc_col,
            debit_rename_col,
            credit_desc_col,
            credit_rename_col
        ) = st.columns(4)

        debit_descriptions = debit_table["TRANSACTION DETAILS"].unique()[:10]
        credit_descriptions = credit_table["TRANSACTION DETAILS"].unique()[:10]

        debit_descriptions = {"a": "a", "b": "b", "c": "c", "d": "d"}

        with debit_desc_col:
            st.write("Rename Debit Description:")
            for desc in debit_descriptions:
                st.text_input(label=f"debito-{desc}", value=desc,
                              label_visibility="collapsed",
                              disabled=True)

        with debit_rename_col:
            st.write("To:")
            for desc in debit_descriptions:
                renamed_to = st.text_input(label=f"debit-{desc}", value=desc,
                                           label_visibility="collapsed")
                debit_descriptions[desc] = renamed_to

        with credit_desc_col:
            st.write("Rename Credit Description:")
            for desc in credit_descriptions:
                st.text_input(label=f"credito-{desc}", value=desc,
                              label_visibility="collapsed",
                              disabled=True)

        with credit_rename_col:
            st.write("To:")
            for desc in credit_descriptions:
                st.text_input(label=f"credit-{desc}", value=desc,
                              label_visibility="collapsed")

        st.write(f"{debit_descriptions}")
        print(st.session_state)

    if st.button("Clear Data"):
        del st.session_state["saved_data"]
        st.experimental_rerun()


if __name__ == "__main__":
    formatter()
