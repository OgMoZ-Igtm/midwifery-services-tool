import streamlit as st
from utils.notifications import send_private_message
from utils.database import get_all_usernames, get_db_connection, get_private_messages
import datetime

# 🔐 Contrôle d'accès
if st.session_state.get("role") not in ["admin", "doctor", "nurse", "sage-femme"]:
    st.warning("⛔ Accès restreint aux professionnels autorisés.")
    st.stop()

st.set_page_config(page_title="Messages privés", page_icon="💬")
st.title("💬 Envoyer un message privé")

# ------------------ Envoi de message ------------------
sender = st.session_state.get("username")
usernames = [u for u in get_all_usernames() if u != sender]
receiver = st.selectbox("Destinataire", usernames)
message = st.text_area("Message")

uploaded_file = st.file_uploader(
    "📎 Joindre un fichier (PDF, image, etc.)", type=["pdf", "png", "jpg", "jpeg"]
)

if st.button("📤 Envoyer le message"):
    if receiver and message.strip():
        file_data = uploaded_file.read() if uploaded_file else None
        file_name = uploaded_file.name if uploaded_file else None
        send_private_message(sender, receiver, message.strip(), file_data, file_name)
        st.success(f"✅ Message envoyé à {receiver}.")
    else:
        st.warning("⚠️ Veuillez remplir tous les champs.")

# ------------------ Boîte de réception ------------------
st.markdown("---")
st.subheader("📥 Boîte de réception")

messages = get_private_messages(st.session_state.username)
threads = {}

for msg in messages:
    tid = msg["thread_id"] or msg["id"]
    threads.setdefault(tid, []).append(msg)

for tid, msgs in threads.items():
    with st.expander(f"💬 Conversation avec {msgs[0]['sender']}"):
        for msg in msgs:
            st.write(f"🕒 {msg['timestamp']} — **{msg['sender']}** : {msg['message']}")
            if msg["file_name"]:
                st.download_button(
                    "📎 Télécharger le fichier",
                    data=msg["file_data"],
                    file_name=msg["file_name"],
                )
        reply = st.text_area("Répondre", key=f"reply_{tid}")
        if st.button("📨 Envoyer la réponse", key=f"btn_{tid}"):
            if reply.strip():
                send_private_message(
                    sender, msgs[0]["sender"], reply.strip(), thread_id=tid
                )
                st.success("✅ Réponse envoyée.")
                st.rerun()
            else:
                st.warning("⚠️ Le message ne peut pas être vide.")
