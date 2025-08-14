# 📁 pages/99_hash_password.py

import streamlit as st
from utils.auth_secure import hash_password

st.set_page_config(page_title="🔐 Générateur de mot de passe haché", page_icon="🔐")

st.title("🔐 Générateur de mot de passe haché")

password = st.text_input("Entrez le mot de passe à hacher", type="password")

if password:
    hashed = hash_password(password)
    st.success("✅ Mot de passe haché généré :")
    st.code(hashed, language="text")
    st.markdown("🔁 Copiez ce hachage dans votre dictionnaire `USERS` dans `auth.py`.")
