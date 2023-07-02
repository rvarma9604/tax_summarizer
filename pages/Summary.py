import streamlit as st


def summarizer():
    st.set_page_config(layout="wide")
    st.title("Summary")

    if (
        st.session_state.get("debit_table", None) is None
        or st.session_state.get("credit_table", None) is None
    ):
        st.info("Please upload the data first and then come back to this page :smile:")
        return

    debit_table = st.session_state["debit_table"]
    credit_table = st.session_state["credit_table"]

    debit_summary = (
        debit_table[["TRANSACTION DETAILS", "WITHDRAWAL AMT"]]
        .groupby("TRANSACTION DETAILS")
        .sum()
        .reset_index()
    )

    debit_summary.loc[len(debit_summary)] = [
        "TOTAL",
        debit_summary["WITHDRAWAL AMT"].sum(),
    ]
    credit_summary = (
        credit_table[["TRANSACTION DETAILS", "DEPOSIT AMT"]]
        .groupby("TRANSACTION DETAILS")
        .sum()
        .reset_index()
    )
    credit_summary.loc[len(credit_summary)] = [
        "TOTAL",
        credit_summary["DEPOSIT AMT"].sum(),
    ]

    debit_col, credit_col = st.columns(2)

    with debit_col:
        st.write("## Debit Summary")
        st.dataframe(debit_summary, use_container_width=True)

    with credit_col:
        st.write("## Credit Summary")
        st.dataframe(credit_summary, use_container_width=True)

    save_file_path = st.text_input(label="Path to save .csv file")
    if st.button("Dump Data") and save_file_path is not None:
        debit_summary.to_csv("debit_summary.csv", index=False)
        credit_summary.to_csv("debit_summary.csv", index=False)


if __name__ == "__main__":
    summarizer()
