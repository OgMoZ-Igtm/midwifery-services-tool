import streamlit as st
from components import show_user_info

show_user_info()
st.set_page_config(page_title="💬 Messages", page_icon="💬")
st.title("💬 Messaging Center")
show_welcome_message("Messages")


tab1, tab2 = st.tabs(["📨 Inbox", "✉️ Compose"])

with tab1:
    st.subheader("📨 Received Messages")
    st.info("No new messages.")

with tab2:
    st.subheader("✉️ Send a Message")
    st.text_input("Recipient Username")
    st.text_area("Message")
    st.button("Send")
