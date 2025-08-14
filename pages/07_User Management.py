import streamlit as st
import pandas as pd
import sqlite3
import bcrypt
import random
import string
import smtplib
from email.mime.text import MIMEText


# ------------------ Fonctions utilitaires ------------------
def generate_temp_password(length=10):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def send_email(recipient_email, temp_password):
    sender_email = "ton.email@gmail.com"
    sender_password = "ton_mot_de_passe_app"  # Mot de passe d'application sécurisé
    subject = "🔐 Nouveau mot de passe temporaire"
    body = f"Bonjour,\n\nVoici votre mot de passe temporaire : {temp_password}\n\nVeuillez le changer après connexion."

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = recipient_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        return True
    except Exception as e:
        st.error(f"Erreur lors de l'envoi : {e}")
        return False


def get_db_connection():
    conn = sqlite3.connect("users.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


# ------------------ Contrôle d'accès ------------------
if st.session_state.get("role") != "admin":
    st.error("⛔ Accès réservé à l'administrateur.")
    st.stop()

st.set_page_config(page_title="Gestion des utilisateurs", page_icon="👥")
st.title("👥 Gestion des utilisateurs")

conn = get_db_connection()
cursor = conn.cursor()

# ------------------ Filtrage ------------------
st.subheader("🔎 Filtrer les utilisateurs")

search_username = st.text_input("Rechercher par nom d'utilisateur")
filter_role = st.selectbox(
    "Filtrer par rôle", ["Tous", "admin", "sage-femme", "médecin", "infirmier"]
)

query = "SELECT id, username, professional_title FROM users WHERE 1=1"
params = []

if search_username:
    query += " AND username LIKE ?"
    params.append(f"%{search_username}%")

if filter_role != "Tous":
    query += " AND professional_title = ?"
    params.append(filter_role)

cursor.execute(query, params)
users = cursor.fetchall()

df_users = pd.DataFrame(users, columns=["id", "username", "professional_title"])
st.download_button(
    label="📥 Télécharger la liste en CSV",
    data=df_users.to_csv(index=False).encode("utf-8"),
    file_name="utilisateurs.csv",
    mime="text/csv",
)

# ------------------ Liste des utilisateurs ------------------
st.subheader("📋 Utilisateurs existants")

for user in users:
    st.write(f"**{user['username']}** — {user['professional_title']}")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button(f"✏️ Modifier", key=f"edit_{user['id']}"):
            st.session_state.edit_user_id = user["id"]
    with col2:
        if st.button(f"🗑️ Supprimer", key=f"delete_{user['id']}"):
            cursor.execute("DELETE FROM users WHERE id = ?", (user["id"],))
            conn.commit()
            st.success(f"Utilisateur {user['username']} supprimé.")
            st.rerun()

# ------------------ Modification ------------------
if "edit_user_id" in st.session_state:
    user_id = st.session_state.edit_user_id
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    st.subheader(f"✏️ Modifier {user['username']}")
    new_title = st.selectbox(
        "Nouveau rôle", ["admin", "sage-femme", "médecin", "infirmier"], index=0
    )
    if st.button("✅ Enregistrer les modifications"):
        cursor.execute(
            "UPDATE users SET professional_title = ? WHERE id = ?", (new_title, user_id)
        )
        conn.commit()
        st.success("Rôle mis à jour.")
        del st.session_state.edit_user_id
        st.rerun()

# ------------------ Ajout d'utilisateur ------------------
st.subheader("➕ Ajouter un utilisateur")

new_username = st.text_input("Nom d'utilisateur")
new_password = st.text_input("Mot de passe", type="password")
new_role = st.selectbox("Rôle", ["admin", "sage-femme", "médecin", "infirmier"])

if st.button("Créer le compte"):
    if new_username and new_password:
        hashed_pw = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())
        try:
            cursor.execute(
                "INSERT INTO users (username, hashed_password, professional_title) VALUES (?, ?, ?)",
                (new_username, hashed_pw, new_role),
            )
            conn.commit()
            st.success(f"✅ Utilisateur {new_username} ajouté.")
            st.rerun()
        except sqlite3.IntegrityError:
            st.error("⚠️ Ce nom d'utilisateur existe déjà.")
    else:
        st.warning("Veuillez remplir tous les champs.")

conn.close()
