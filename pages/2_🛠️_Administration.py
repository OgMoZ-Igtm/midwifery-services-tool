# 📦 Core
import streamlit as st
import sqlite3

# 🔐 Auth
from utils.auth_secure import (
    init_db,
    get_user,
    create_user,
    show_user_info,
    require_role,
)

# ⚙️ Setup
st.set_page_config(page_title="🛠️ Administration", page_icon="🛠️")
init_db()
show_user_info()
require_role("admin")

# 🏁 Intro
st.title("🛠️ Administration")
show_welcome_message("Administration")

st.divider()

# ➕ Add new user
st.subheader("➕ Ajouter un nouvel utilisateur")

with st.form("create_user_form"):
    new_username = st.text_input("Nom d'utilisateur")
    new_password = st.text_input("Mot de passe", type="password")
    new_role = st.selectbox("Rôle", ["user", "admin", "moderator"])
    submitted = st.form_submit_button("Créer l'utilisateur")

    if submitted:
        if not new_username or not new_password:
            st.warning("Veuillez remplir tous les champs.")
        elif get_user(new_username):
            st.error("Ce nom d'utilisateur existe déjà.")
        else:
            success = create_user(new_username, new_password, new_role)
            if success:
                st.success(
                    f"Utilisateur **{new_username}** créé avec le rôle **{new_role}**."
                )
            else:
                st.error("Erreur lors de la création de l'utilisateur.")

st.divider()

# 🔍 Filter by role
st.subheader("🔎 Filtrer les utilisateurs par rôle")
selected_role = st.selectbox(
    "Sélectionnez un rôle", ["Tous", "admin", "user", "moderator"]
)

# 📋 Load users
conn = sqlite3.connect("users.db")
c = conn.cursor()

if selected_role == "Tous":
    c.execute("SELECT username, role FROM users")
else:
    c.execute("SELECT username, role FROM users WHERE role = ?", (selected_role,))
users = c.fetchall()

# 🧑‍💼 Modify or delete users
for username, role in users:
    with st.expander(f"👤 {username} — `{role}`"):
        new_role = st.selectbox(
            f"Changer le rôle de {username}",
            ["user", "admin", "moderator"],
            index=["user", "admin", "moderator"].index(role),
            key=f"role_{username}",
        )
        if st.button(f"✅ Mettre à jour le rôle", key=f"update_{username}"):
            c.execute(
                "UPDATE users SET role = ? WHERE username = ?", (new_role, username)
            )
            conn.commit()
            st.success(f"Rôle mis à jour pour **{username}** → `{new_role}`")

        confirm_delete = st.checkbox(
            f"Confirmer la suppression de {username}", key=f"confirm_{username}"
        )
        if confirm_delete:
            if st.button(f"🗑️ Supprimer {username}", key=f"delete_{username}"):
                c.execute("DELETE FROM users WHERE username = ?", (username,))
                conn.commit()
                st.warning(f"Utilisateur **{username}** supprimé.")

conn.close()
