import pandas as pd
import streamlit as st


def table_generator(transactions, amount_column, number_of_entries):
    dataframes = []

    current_dataframe = pd.DataFrame(
        columns=["DATE", "TRANSACTION DETAILS", amount_column]
    )
    count = 0
    for _, row in transactions.iterrows():
        if len(current_dataframe) == number_of_entries - 1:
            carry_forward = current_dataframe[amount_column].sum()
            current_dataframe.loc[len(current_dataframe)] = ["-", "CF", carry_forward]
            dataframes.append(current_dataframe.reset_index(drop=True))

            current_dataframe = pd.DataFrame(
                columns=["DATE", "TRANSACTION DETAILS", amount_column]
            )
            current_dataframe.loc[len(current_dataframe)] = ["-", "CF", carry_forward]
            current_dataframe.loc[len(current_dataframe)] = row
            count = 2

            print(dataframes)
            print(current_dataframe)
        else:
            current_dataframe.loc[len(current_dataframe)] = row
            count += 1
    else:
        carry_forward = current_dataframe[amount_column].sum()
        current_dataframe.loc[len(current_dataframe)] = ["-", "CF", carry_forward]
        dataframes.append(current_dataframe.reset_index(drop=True))

    return dataframes


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
    st.write(number_of_entries)

    debit_table = st.session_state["debit_table"]
    credit_table = st.session_state["credit_table"]

    debit_table_split = table_generator(
        debit_table, "WITHDRAWAL AMT", number_of_entries
    )
    credit_table_split = table_generator(credit_table, "DEPOSIT AMT", number_of_entries)


if __name__ == "__main__":
    splitter()
