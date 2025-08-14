import streamlit as st
import datetime
from utils.notifications import (
    get_private_messages,
    send_private_message,
    mark_messages_seen,
)
import smtplib
from email.message import EmailMessage
from twilio.rest import Client

# 🔐 Contrôle d'accès
if st.session_state.get("role") not in ["admin", "doctor", "nurse", "sage-femme"]:
    st.warning("⛔ Accès restreint aux professionnels autorisés.")
    st.stop()


def page_boite_reception():
    st.set_page_config(page_title="Boîte de réception", page_icon="📥")
    st.title("📥 Boîte de réception")

    username = st.session_state.get("username")
    messages = get_private_messages(username)
    mark_messages_seen(username)

    # 🔍 Filtres
    senders = sorted(set(msg["sender"] for msg in messages))
    selected_sender = st.selectbox("Filtrer par expéditeur", ["Tous"] + senders)
    selected_date = st.date_input("Filtrer par date", value=None)

    filtered = []
    for msg in messages:
        if selected_sender != "Tous" and msg["sender"] != selected_sender:
            continue
        if selected_date and msg["timestamp"][:10] != selected_date.strftime(
            "%Y-%m-%d"
        ):
            continue
        filtered.append(msg)

    # 📬 Affichage des messages
    if filtered:
        for msg in filtered:
            with st.expander(f"📨 De {msg['sender']} à {msg['timestamp']}"):
                st.write(msg["message"])
                if msg.get("file_name"):
                    st.download_button(
                        "📎 Télécharger la pièce jointe",
                        data=msg["file_data"],
                        file_name=msg["file_name"],
                    )
                reply = st.text_area(
                    f"Répondre à {msg['sender']}", key=f"reply_{msg['id']}"
                )
                if st.button(f"📤 Envoyer la réponse", key=f"btn_{msg['id']}"):
                    if reply.strip():
                        send_private_message(
                            username,
                            msg["sender"],
                            reply.strip(),
                            thread_id=msg["thread_id"] or msg["id"],
                        )
                        st.success("✅ Réponse envoyée.")
                        st.rerun()
                    else:
                        st.warning("⚠️ Le message ne peut pas être vide.")
    else:
        st.info("📭 Aucun message trouvé avec ces filtres.")


# ------------------ Notifications (optionnelles) ------------------
def send_sms_notification(to_number, message):
    client = Client("TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN")
    client.messages.create(
        body=message, from_="+1234567890", to=to_number  # ton numéro Twilio
    )


def send_email_notification(to_email, subject, body):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = "ton_email@example.com"
    msg["To"] = to_email
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login("ton_email@example.com", "mot_de_passe_app")
        smtp.send_message(msg)
