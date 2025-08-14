import streamlit as st
from datetime import datetime


def get_greeting():
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning"
    elif hour < 18:
        return "Good afternoon"
    else:
        return "Good evening"


def show_user_info():
    if "username" in st.session_state:
        greeting = get_greeting()

        if "photo" in st.session_state:
            st.image(st.session_state["photo"], width=100)

        st.markdown(f"## 👋 {greeting}, {st.session_state['username']}!")
        st.success(
            f"You are logged in as **{st.session_state['username']}** "
            f"({st.session_state['role']})"
        )
        st.info(f"🕒 Login time: {st.session_state.get('login_time', 'unknown')}")


def show_welcome_message(page_name: str):
    st.write(
        f"Welcome to the **{page_name}**. Cette section est en cours de développement."
    )
