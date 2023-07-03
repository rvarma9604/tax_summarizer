import os
import numpy as np
import pandas as pd
import streamlit as st

pd.options.display.float_format = "{:,.2f}".format


def table_generator(transactions, amount_column, number_of_entries):
    dataframes = []

    current_dataframe = pd.DataFrame(
        columns=["DATE", "TRANSACTION DETAILS", amount_column]
    )
    count = 0
    for _, row in transactions.iterrows():
        if len(current_dataframe) == number_of_entries - 1:
            carry_forward = current_dataframe[amount_column].sum()
            current_dataframe.loc[len(current_dataframe)] = [
                "",
                "C/F ->",
                carry_forward,
            ]
            dataframes.append(current_dataframe.reset_index(drop=True))

            current_dataframe = pd.DataFrame(
                columns=["DATE", "TRANSACTION DETAILS", amount_column]
            )
            current_dataframe.loc[len(current_dataframe)] = [
                "",
                "B/F ->",
                carry_forward,
            ]
            current_dataframe.loc[len(current_dataframe)] = row
            count = 2
        else:
            current_dataframe.loc[len(current_dataframe)] = row
            count += 1
    else:
        carry_forward = current_dataframe[amount_column].sum()
        current_dataframe.loc[len(current_dataframe)] = ["", "TOTAL", carry_forward]
        dataframes.append(current_dataframe.reset_index(drop=True))

    return dataframes


def excel_writer(dataframes, writer, sheet_name, padding=1):
    column_size = len(dataframes[0].columns)
    curr_row = 0
    for i in range(len(dataframes)):
        if i % 2 == 0:
            dataframes[i].to_excel(
                writer,
                sheet_name=sheet_name,
                index=False,
                startrow=curr_row,
                float_format="%.2f",
            )
        else:
            dataframes[i].to_excel(
                writer,
                sheet_name=sheet_name,
                index=False,
                startrow=curr_row,
                startcol=column_size + padding,
                float_format="%.2f",
            )
            curr_row += (len(dataframes[i]) + 1) + padding


def splitter():
    st.set_page_config(layout="wide")
    st.title("Transaction Splitter")
    st.write("""Split your transaction history into tables with fixed sized entries""")

    if (
        st.session_state.get("debit_table", None) is None
        or st.session_state.get("credit_table", None) is None
    ):
        st.info("Please upload the data first and then come back to this page :smile:")
        return

    number_of_entries = st.slider("Number of entries per split?", 10, 50, 25)
    preview_data = [
        [f"Date-{i}", f"Transaction-{i}", i]
        for i in range(1, number_of_entries * 2 - 2)
    ]
    preview_table = pd.DataFrame(
        preview_data, columns=["DATE", "TRANSACTION DETAILS", "AMOUNT"]
    )
    preview_table_split = table_generator(preview_table, "AMOUNT", number_of_entries)
    st.write("## Preview")
    preview_col1, preview_col2 = st.columns(2)
    with preview_col1:
        st.dataframe(preview_table_split[0], use_container_width=True)
    with preview_col2:
        st.dataframe(preview_table_split[1], use_container_width=True)

    debit_table = st.session_state["debit_table"]
    credit_table = st.session_state["credit_table"]

    debit_table_split = table_generator(
        debit_table, "WITHDRAWAL AMT", number_of_entries
    )
    credit_table_split = table_generator(credit_table, "DEPOSIT AMT", number_of_entries)

    save_file_path = st.text_input(label="Path to save .csv file")
    if st.button("Dump Data") and save_file_path is not None:
        file_path = os.path.join(save_file_path, "txn_history.xlsx")
        with pd.ExcelWriter(file_path) as writer:
            excel_writer(debit_table_split, writer, "Debit")
            excel_writer(credit_table_split, writer, "Credit")


if __name__ == "__main__":
    splitter()
