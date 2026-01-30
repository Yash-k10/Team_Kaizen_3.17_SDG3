import streamlit as st
import pandas as pd

from database import (
    create_tables,
    add_donor,
    add_recipient,
    get_donors,
    get_recipients
)

from matching_engine import find_matches

# Initialize DB
create_tables()

st.set_page_config(page_title="Organ Donation Platform", layout="wide")

st.title("🫀 Organ Donation Matching Platform")
st.caption("SDG 3.17 – AI-powered donor–recipient matching")

menu = st.sidebar.radio(
    "Navigation",
    ["Add Donor", "Add Recipient", "View Matches", "Admin Dashboard"]
)

# ---------------- ADD DONOR ----------------
if menu == "Add Donor":
    st.header("➕ Register Donor")

    with st.form("donor_form"):
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=1, max_value=100)
        blood = st.selectbox("Blood Group", ["O", "A", "B", "AB"])
        organ = st.selectbox("Organ", ["Kidney", "Liver", "Heart", "Lung"])
        city = st.text_input("City")
        urgency = st.slider("Urgency Level", 1, 5)

        submit = st.form_submit_button("Add Donor")

        if submit:
            add_donor(name, age, blood, organ, city, urgency)
            st.success("Donor added successfully")

# ---------------- ADD RECIPIENT ----------------
elif menu == "Add Recipient":
    st.header("➕ Register Recipient")

    with st.form("recipient_form"):
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=1, max_value=100)
        blood = st.selectbox("Blood Group", ["O", "A", "B", "AB"])
        organ = st.selectbox("Organ Needed", ["Kidney", "Liver", "Heart", "Lung"])
        city = st.text_input("City")
        urgency = st.slider("Urgency Level", 1, 5)

        submit = st.form_submit_button("Add Recipient")

        if submit:
            add_recipient(name, age, blood, organ, city, urgency)
            st.success("Recipient added successfully")

# ---------------- VIEW MATCHES ----------------
elif menu == "View Matches":
    st.header("🔍 Matching Results")

    matches = find_matches()

    if matches:
        df = pd.DataFrame(matches)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No matches found yet.")