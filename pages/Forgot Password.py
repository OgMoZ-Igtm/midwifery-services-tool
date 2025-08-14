import streamlit as st
import bcrypt
from utils.database import update_password, get_db_connection


def page_mot_de_passe_oublie():
    st.set_page_config(page_title="🔁 Mot de passe oublié", page_icon="🔁")
    st.title("🔁 Réinitialiser le mot de passe")

    reset_username = st.text_input("Nom d'utilisateur")
    new_password_reset = st.text_input("Nouveau mot de passe", type="password")
    confirm_password = st.text_input("Confirmer le mot de passe", type="password")

    if st.button("🔐 Réinitialiser le mot de passe"):
        if not reset_username or not new_password_reset or not confirm_password:
            st.warning("⚠️ Veuillez remplir tous les champs.")
        elif new_password_reset != confirm_password:
            st.error("❌ Les mots de passe ne correspondent pas.")
        else:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (reset_username,))
            user = cursor.fetchone()
            conn.close()

            if user:
                hashed_pw = bcrypt.hashpw(new_password_reset.encode(), bcrypt.gensalt())
                update_password(reset_username, hashed_pw)
                st.success("✅ Mot de passe mis à jour avec succès.")
                st.session_state.page = "login"
                st.rerun()
            else:
                st.error("❌ Nom d'utilisateur non trouvé.")
