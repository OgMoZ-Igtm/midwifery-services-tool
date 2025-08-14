# pages/page_accueil.py
import streamlit as st
import pandas as pd
import bcrypt
from utils.database import get_db_connection
from utils.navigation import reset_all_forms
from utils.notifications import (
    get_notifications,
    mark_notifications_seen,
    create_private_message_table,
    get_unseen_message_count,
)
from utils.auth import login, logout, generate_temp_password, send_email


def app():
    st.set_page_config(page_title="Accueil", layout="wide")

    if "authenticated" not in st.session_state or not st.session_state.authenticated:
        login()
        st.stop()

    if st.session_state.role != "admin":
        st.warning("⛔ Cette page est réservée à l'administrateur.")
        st.stop()

    st.header("🏡 Welcome to the Midwifery Services Data Collection Tool!")
    st.write("Thank you for taking the time to fill out this tool!")

    st.markdown(
        """
        For any questions, suggestions, or modification requests, please do not hesitate to contact Katia Lessard, PPRO-Midwifery, at:
        **Katia.Lessard.reg18@ssss.gouv.qc.ca**

        This tool has been created to support the continuous improvement and provision of high-quality midwifery care in Eeyou Istchee. It will allow us to operate a constant follow-up on the services, outcomes, and impacts of Midwifery Services amongst our clientele.

        Some variables collected here were specifically requested by Nishiyuu. Other variables were selected through various consultations with Midwifery Services and are inspired by different databases and organizations, including:
        * The National Indigenous Association of Midwives
        * I-CLSC, Care 4, CHB, RSFQ
        * The Canadian Midwifery Minimum Database
        * MSSS

        Data analysis is a public matter and will be reported back yearly to Eeyou Istchee Communities via the Midwifery Services' and Cree Health Board's Annual Report.

        Thank you all for your commitment to providing high-quality midwifery care to families in Eeyou Istchee.
        """
    )

    conn = get_db_connection()
    df_demographics = pd.read_sql_query("SELECT * FROM demographics", conn)
    df_prenatal_care = pd.read_sql_query("SELECT * FROM prenatal_care", conn)
    df_rendez_vous = pd.read_sql_query("SELECT * FROM rendez_vous", conn)
    conn.close()

    st.subheader("📊 Aperçu rapide")
    col1, col2, col3 = st.columns(3)
    col1.metric("Entrées démographiques", len(df_demographics))
    col2.metric("Entrées de soins prénatals", len(df_prenatal_care))
    col3.metric("Entrées de rendez-vous", len(df_rendez_vous))

    if st.button("🔄 Réinitialiser la page"):
        reset_all_forms()
        st.rerun()

    user = st.session_state.get(
        "user", {"username": st.session_state.username, "id": st.session_state.user_id}
    )

    logout()

    with st.expander(f"🔧 Options pour {user['username']}"):
        email = st.text_input("Email de l'utilisateur", key=f"email_{user['id']}")
        if st.button("📧 Envoyer mot de passe temporaire", key=f"send_pw_{user['id']}"):
            temp_pw = generate_temp_password()
            hashed_pw = bcrypt.hashpw(temp_pw.encode("utf-8"), bcrypt.gensalt()).decode(
                "utf-8"
            )

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET password = ?, email = ? WHERE id = ?",
                (hashed_pw, email, user["id"]),
            )
            conn.commit()
            conn.close()

            if send_email(email, temp_pw):
                st.success(f"Mot de passe temporaire envoyé à {email}.")
