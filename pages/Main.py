# main.py
import streamlit as st
import subprocess

st.set_page_config(page_title="Gestion des pages", layout="centered")

st.title("🧩 Gestion des conflits de pages Streamlit")

mode = st.radio(
    "Choisir le mode d'exécution :",
    ["Analyse simple", "Simulation (dry-run)", "Correction automatique"],
)

if st.button("🚀 Lancer l'analyse"):
    st.info("Exécution en cours...")

    command = ["python", "manage_pages.py"]
    if mode == "Simulation (dry-run)":
        command.append("--dry-run")
    elif mode == "Correction automatique":
        command.append("--auto-fix")

    result = subprocess.run(command, capture_output=True, text=True)

    st.code(result.stdout, language="bash")

    if result.stderr:
        st.error("⚠️ Une erreur est survenue :")
        st.code(result.stderr, language="bash")
from utils.navigation import PAGES, navigation_buttons
from utils.notifications import (
    get_notifications,
    mark_notifications_seen,
    create_private_message_table,
    get_unseen_message_count,
)

st.set_page_config(page_title="Midwifery Tool", layout="wide")

# 📍 Navigation
navigation_buttons()

# 🧭 Affichage de la page actuelle
current_page = st.session_state.get("current_page", "Accueil")
module_name = PAGES.get(current_page)

if module_name:
    module = __import__(f"pages.{module_name}", fromlist=[""])
    module.app()
else:
    st.error("Page introuvable.")

# 🛡️ Rôle affiché
role = st.session_state.get("role")
if role == "admin":
    st.sidebar.success("🛡️ Accès administrateur")
elif role == "sage-femme":
    st.sidebar.info("👩‍⚕️ Accès sage-femme")

# 🔔 Notifications
username = st.session_state.get("username")
if username:
    notifs = get_notifications(username)
    if notifs:
        st.sidebar.subheader("🔔 Notifications")
        for notif in notifs:
            st.sidebar.info(notif["message"])
        mark_notifications_seen(username)

    # 📬 Messagerie privée
    create_private_message_table()
    unseen_count = get_unseen_message_count(username)
    if unseen_count > 0:
        st.sidebar.markdown(f"🔔 **{unseen_count} nouveau(x) message(s)**")

st.set_page_config(page_title="Gestion des pages", layout="centered")

st.title("🧩 Gestion des conflits de pages Streamlit")

mode = st.radio(
    "Choisir le mode d'exécution :",
    ["Analyse simple", "Simulation (dry-run)", "Correction automatique"],
)

if st.button("🚀 Lancer l'analyse"):
    st.info("Exécution en cours...")

    command = ["python", "manage_pages.py"]
    if mode == "Simulation (dry-run)":
        command.append("--dry-run")
    elif mode == "Correction automatique":
        command.append("--auto-fix")

    result = subprocess.run(command, capture_output=True, text=True)

    st.code(result.stdout, language="bash")

    if result.stderr:
        st.error("⚠️ Une erreur est survenue :")
        st.code(result.stderr, language="bash")

import os

LOG_FILE = "page_conflicts.log"

st.subheader("📜 Historique des conflits")

if os.path.exists(LOG_FILE):
    if st.button("📂 Afficher le journal des conflits"):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            log_content = f.read()
        st.text_area("📝 Contenu du journal :", log_content, height=300)
else:
    st.warning("Aucun journal trouvé. Lance une correction pour générer le fichier.")
