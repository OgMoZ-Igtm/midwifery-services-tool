import streamlit as st
from datetime import date
import pandas as pd
from utils.database import insert_data_postnatal, fetch_history_postnatal
from utils.navigation import navigation_buttons, reset_all_forms

st.set_page_config(page_title="Suivi Postnatal", layout="wide")

if st.session_state.get("role") not in ["admin", "doctor", "sage-femme"]:
    st.warning("⛔ Accès restreint aux professionnels autorisés.")
    st.stop()

st.title("👶 Suivi Postnatal")
st.markdown("---")

with st.form(key="postnatal_form", clear_on_submit=True):
    st.subheader("Entrée de données postnatales")

    nom = st.text_input("Nom")
    date_suivi = st.date_input("Date du suivi", value=None)
    etat_bebe = st.selectbox(
        "État du bébé", ["Bon", "Fiévreux", "Irritable", "Somnolent", "Autre"]
    )
    commentaires = st.text_area("Commentaires")

    submitted = st.form_submit_button("Soumettre")

    if submitted:
        insert_data_postnatal(
            nom,
            str(date_suivi) if date_suivi else None,
            etat_bebe,
            commentaires,
        )
        reset_all_forms()
        st.success("✅ Données enregistrées avec succès.")
        st.rerun()

st.markdown("---")
st.subheader("📚 Historique du suivi postnatal")
df_history = fetch_history_postnatal()
if not df_history.empty:
    st.dataframe(df_history, use_container_width=True)
else:
    st.info("Aucune donnée postnatale enregistrée.")

if st.button("🔄 Réinitialiser la page"):
    reset_all_forms()
    st.rerun()

navigation_buttons()
