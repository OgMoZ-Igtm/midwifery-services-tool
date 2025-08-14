import streamlit as st
from utils.auth_secure import verify_password  # à créer avec bcrypt

USERS = {
    "admin": {"password": "$2b$12$...", "role": "admin"},  # mot de passe haché
    "marie": {"password": "$2b$12$...", "role": "sage-femme"},
}


def login():
    st.sidebar.title("🔐 Connexion")
    username = st.sidebar.text_input("Nom d'utilisateur")
    password = st.sidebar.text_input("Mot de passe", type="password")

    if st.sidebar.button("Se connecter"):
        user = USERS.get(username)
        if user and verify_password(password, user["password"]):
            st.session_state["username"] = username
            st.session_state["role"] = user["role"]
            st.sidebar.success(f"✅ Connecté en tant que {username} ({user['role']})")
            st.rerun()
        else:
            st.sidebar.error("❌ Identifiants incorrects")


def logout():
    if st.sidebar.button("Se déconnecter"):
        st.session_state.clear()
        st.rerun()


def require_login():
    if "username" not in st.session_state:
        st.warning("🔒 Vous devez être connecté pour accéder à cette page.")
        st.stop()


def require_role(role):
    if st.session_state.get("role") != role:
        st.error(f"⛔ Accès réservé aux utilisateurs avec le rôle : {role}")
        st.stop()


def show_auth_sidebar():
    if "username" in st.session_state:
        st.sidebar.markdown(f"👤 Connecté : `{st.session_state['username']}`")
        logout()
    else:
        login()
