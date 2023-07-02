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
    debit_table = data[data["WITHDRAWAL AMT"] != 0][
        ["DATE", "TRANSACTION DETAILS", "WITHDRAWAL AMT"]
    ].reset_index(drop=True)
    credit_table = data[data["DEPOSIT AMT"] != 0][
        ["DATE", "TRANSACTION DETAILS", "DEPOSIT AMT"]
    ].reset_index(drop=True)

    return debit_table, credit_table


def formatter():
    st.set_page_config(layout="wide")
    st.title("Formatter")

    if st.session_state.get("data", None) is None:
        st.info("Please upload the data first and then come back to this page :smile:")
        return

    from_col, to_col = st.columns(2)

    with from_col:
        from_date = st.date_input("From date")

    with to_col:
        to_date = st.date_input("To date")

    if from_date > to_date:
        st.error("From date cannot be less than To date")
        return

    data = st.session_state["data"]
    if st.session_state.get("saved_data", None) is None:
        txn_table = load_data(data["txn_file"])
        txn_table.columns = [col.strip().upper() for col in txn_table.columns]
        txn_table = txn_table[
            ["DATE", "TRANSACTION DETAILS", "WITHDRAWAL AMT", "DEPOSIT AMT"]
        ]

        txn_table["DATE"] = pd.to_datetime(
            txn_table["DATE"].apply(parse), format="%d/%m/%Y"
        ).apply(datetime.date)

        def parse_numbers(number):
            if isinstance(number, str):
                return float(re.sub(r"[^0-9\.-]", "", number))
            if isinstance(number, float) or isinstance(number, int):
                return number
            else:
                return 0.0

        for col in ["WITHDRAWAL AMT", "DEPOSIT AMT"]:
            txn_table[col] = txn_table[col].apply(parse_numbers)

        txn_table.fillna(
            value={"WITHDRAWAL AMT": 0.0, "DEPOSIT AMT": 0.0}, inplace=True
        )

        txn_table = txn_table.sort_values(by="DATE", ascending=True).reset_index(
            drop=True
        )

        st.session_state["saved_data"] = {}
        st.session_state["saved_data"]["txn_table"] = txn_table
    else:
        txn_table = st.session_state.get("saved_data")["txn_table"]

    # txn_file = data["txn_file"]
    # bank_name = data["bank_name"]

    # txn_table = pd.read_csv(txn_file)

    txn_table = txn_table[
        (txn_table["DATE"] >= from_date) & (txn_table["DATE"] <= to_date)
    ]

    if len(txn_table) == 0:
        st.error(
            f"""You don't have any recorded transaction from: {from_date} to: {to_date}.
            Try selecting a different date range"""
        )
        return

    st.write("## Transaction History")
    st.dataframe(txn_table, use_container_width=True)

    if "debit_table" not in st.session_state or "credit_table" not in st.session_state:
        debit_table, credit_table = get_debit_credit_tables(txn_table)
    else:
        debit_table = st.session_state["debit_table"]
        credit_table = st.session_state["credit_table"]

    debit_col, credit_col = st.columns(2)

    with debit_col:
        st.write("## Withdrawal History")
        st.dataframe(debit_table, use_container_width=True)

    with credit_col:
        st.write("## Deposit History")
        st.dataframe(credit_table, use_container_width=True)

    rename_description = st.radio(
        "Rename descriptions?", options=["Yes", "No"], index=1, horizontal=True
    )

    if rename_description == "Yes":
        (
            debit_desc_col,
            debit_rename_col,
            credit_desc_col,
            credit_rename_col,
        ) = st.columns(4)

        debit_descriptions = debit_table["TRANSACTION DETAILS"].unique()
        credit_descriptions = credit_table["TRANSACTION DETAILS"].unique()

        debit_descriptions_map = {desc: desc for desc in debit_descriptions}
        credit_descriptions_map = {desc: desc for desc in credit_descriptions}

        with debit_desc_col:
            st.write("Rename Debit Description:")
            for desc in debit_descriptions:
                st.text_input(
                    label=f"debito-{desc}",
                    value=desc,
                    label_visibility="collapsed",
                    disabled=True,
                )

        with debit_rename_col:
            st.write("To:")
            for desc in debit_descriptions:
                renamed_to = st.text_input(
                    label=f"debit-{desc}", value=desc, label_visibility="collapsed"
                )
                debit_descriptions_map[desc] = renamed_to

        # credit
        with credit_desc_col:
            st.write("Rename Credit Description:")
            for desc in credit_descriptions:
                st.text_input(
                    label=f"credito-{desc}",
                    value=desc,
                    label_visibility="collapsed",
                    disabled=True,
                )

        with credit_rename_col:
            st.write("To:")
            for desc in credit_descriptions:
                renamed_to = st.text_input(
                    label=f"credit-{desc}", value=desc, label_visibility="collapsed"
                )
                credit_descriptions_map[desc] = renamed_to

        st.session_state["debit_desc_map"] = debit_descriptions_map
        st.session_state["credit_desc_map"] = credit_descriptions_map

        use_find_replace = st.radio(
            "Want to use find and replace?",
            options=["Yes", "No"],
            help="find and replace will override the above behaviour",
            horizontal=True,
        )

        if use_find_replace == "Yes":
            fr_placeholder = st.empty()

            if "debit_fr_count" not in st.session_state:
                st.session_state["debit_fr_count"] = 1

            if "credit_fr_count" not in st.session_state:
                st.session_state["credit_fr_count"] = 1

            debit_find_replace_map = {}
            credit_find_replace_map = {}

            with fr_placeholder.container():
                (
                    debit_find_desc_col,
                    debit_replace_col,
                    credit_find_desc_col,
                    credit_replace_col,
                ) = st.columns(4)

                with debit_find_desc_col:
                    if st.button("Add", key=1):
                        st.session_state["debit_fr_count"] += 1

                with debit_replace_col:
                    if (
                        st.button("Delete", key=2)
                        and st.session_state["debit_fr_count"] > 1
                    ):
                        st.session_state["debit_fr_count"] -= 1

                with debit_find_desc_col:
                    for row in range(st.session_state["debit_fr_count"]):
                        debit_find = st.text_input(
                            label=f"debit_f_{row}", label_visibility="collapsed"
                        )
                        debit_find_replace_map[row] = (debit_find,)

                with debit_replace_col:
                    for row in range(st.session_state["debit_fr_count"]):
                        debit_replace = st.text_input(
                            label=f"debit_r_{row}", label_visibility="collapsed"
                        )
                        debit_find_replace_map[row] = (
                            debit_find_replace_map[row][0],
                            debit_replace,
                        )

                # credit
                with credit_find_desc_col:
                    if st.button("Add", key=3):
                        st.session_state["credit_fr_count"] += 1

                with credit_replace_col:
                    if (
                        st.button("Delete", key=4)
                        and st.session_state["credit_fr_count"] > 1
                    ):
                        st.session_state["credit_fr_count"] -= 1

                with credit_find_desc_col:
                    for row in range(st.session_state["credit_fr_count"]):
                        credit_find = st.text_input(
                            label=f"credit_f_{row}", label_visibility="collapsed"
                        )
                        credit_find_replace_map[row] = (credit_find,)

                with credit_replace_col:
                    for row in range(st.session_state["credit_fr_count"]):
                        credit_replace = st.text_input(
                            label=f"credit_r_{row}", label_visibility="collapsed"
                        )
                        credit_find_replace_map[row] = (
                            credit_find_replace_map[row][0],
                            credit_replace,
                        )

            if "" in debit_find_replace_map:
                del debit_find_replace_map[""]

            if "" in credit_find_replace_map:
                del credit_find_replace_map[""]

            st.session_state["debit_desc_fr_map"] = debit_find_replace_map
            st.session_state["credit_desc_fr_map"] = credit_find_replace_map

    if st.button("Update"):

        def find_replace_logic(text, find_replace_mapping):
            # print(find_replace_mapping)
            for key, value in find_replace_mapping.items():
                # print(key, text, value)
                if key in text:
                    return value
            return text

        debit_table["TRANSACTION DETAILS"] = debit_table["TRANSACTION DETAILS"].map(
            st.session_state["debit_desc_map"]
        )
        debit_fr_transformed_map = {
            row[0]: row[1] for row in st.session_state["debit_desc_fr_map"].values()
        }
        st.write(debit_fr_transformed_map)
        debit_table["TRANSACTION DETAILS"] = debit_table["TRANSACTION DETAILS"].apply(
            lambda desc: find_replace_logic(desc, debit_fr_transformed_map)
        )
        st.session_state["debit_table"] = debit_table

        # credit
        credit_table["TRANSACTION DETAILS"] = credit_table["TRANSACTION DETAILS"].map(
            st.session_state["credit_desc_map"]
        )
        credit_fr_transformed_map = {
            row[0]: row[1] for row in st.session_state["credit_desc_fr_map"].values()
        }
        credit_table["TRANSACTION DETAILS"] = credit_table["TRANSACTION DETAILS"].apply(
            lambda desc: find_replace_logic(desc, credit_fr_transformed_map)
        )
        st.session_state["credit_table"] = credit_table

        # find-replace logic

        del st.session_state["debit_desc_map"]
        del st.session_state["credit_desc_map"]
        del st.session_state["debit_desc_fr_map"]
        del st.session_state["credit_desc_fr_map"]
        st.experimental_rerun()

    if st.button("Clear Data"):
        session_keys_to_delete = [
            "saved_data",
            "debit_table",
            "dredit_table",
            "debit_desc_map",
            "credit_desc_map",
            "debit_desc_fr_map",
            "credit_desc_fr_map",
        ]
        for key in session_keys_to_delete:
            if key in st.session_state:
                del st.session_state[key]

        st.experimental_rerun()

    save_file_path = st.text_input(label="Path to save .csv file")
    if st.button("Dump Data") and save_file_path is not None:
        st.session_state["debit_table"].to_csv("debit.csv", index=False)
        st.session_state["credit_table"].to_csv("credit.csv", index=False)


if __name__ == "__main__":
    formatter()
