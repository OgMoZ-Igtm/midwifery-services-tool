import bcrypt
import sqlite3
import streamlit as st

DB_PATH = "users.db"


# 🔧 Initialisation de la base si elle n'existe pas
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """
    )
    conn.commit()
    conn.close()


# 🔐 Hachage du mot de passe
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


# 🔍 Vérification du mot de passe
def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


# 🔎 Récupération d’un utilisateur
def get_user(username: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT username, password_hash, role FROM users WHERE username = ?",
        (username,),
    )
    user = c.fetchone()
    conn.close()
    return user


# ➕ Création d’un nouvel utilisateur
def create_user(username: str, password: str, role: str = "user") -> bool:
    if get_user(username):
        return False  # utilisateur déjà existant
    password_hash = hash_password(password)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, password_hash, role),
    )
    conn.commit()
    conn.close()
    return True


# 🔓 Authentification
def login(username: str, password: str) -> bool:
    user = get_user(username)
    if user and verify_password(password, user[1]):
        st.session_state["user"] = {"username": user[0], "role": user[2]}
        return True
    return False


# 🚪 Déconnexion
def logout():
    st.session_state.pop("user", None)


# 🔐 Vérification de rôle
def require_role(required_role: str):
    user = st.session_state.get("user")
    if not user or user["role"] != required_role:
        st.error("Accès refusé. Rôle requis : " + required_role)
        st.stop()


# 🧑 Affichage des infos utilisateur
def show_user_info():
    user = st.session_state.get("user")
    if user:
        st.sidebar.markdown(f"👤 Connecté en tant que **{user['username']}**")
        st.sidebar.markdown(f"🔐 Rôle : `{user['role']}`")
        if st.sidebar.button("Se déconnecter"):
            logout()
            st.experimental_rerun()
