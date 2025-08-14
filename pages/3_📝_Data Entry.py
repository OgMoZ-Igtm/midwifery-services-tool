import streamlit as st
from components import show_user_info

show_user_info()
st.set_page_config(page_title="📝 Data Entry", page_icon="📝")
st.title("📝 Data Entry")
show_welcome_message("Data Entry")


tab1, tab2 = st.tabs(["➕ Add Patient", "🩺 Medical Notes"])

with tab1:
    st.subheader("➕ Add New Patient")
    st.text_input("Full Name")
    st.date_input("Date of Birth")
    st.selectbox("Status", ["Pregnant", "Postpartum", "Other"])
    st.button("Save Patient")

with tab2:
    st.subheader("🩺 Add Medical Note")
    st.text_input("Patient Name")
    st.text_area("Note")
    st.button("Save Note")
