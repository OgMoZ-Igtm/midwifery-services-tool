import streamlit as st
from utils.database import get_all_patients, get_all_rendez_vous
from components import show_user_info

show_user_info()
st.set_page_config(page_title="📊 Statistics", page_icon="📊")
st.title("📊 Statistics Dashboard")
show_welcome_message("Statistics")


patients = get_all_patients()
appointments = get_all_rendez_vous()

st.metric("Total Patients", len(patients))
st.metric("Upcoming Appointments", len(appointments))

# 📈 Graphs (à ajouter plus tard avec matplotlib, plotly, altair)
st.subheader("📈 Appointment Trends")
st.info("Graphs coming soon...")
