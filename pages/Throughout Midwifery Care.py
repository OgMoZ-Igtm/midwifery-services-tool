import streamlit as st
from datetime import date
import pandas as pd
from utils.database import insert_data_midwifery, fetch_history_midwifery
from utils.navigation import navigation_buttons, reset_all_forms

st.set_page_config(page_title="Suivi Global Sage-Femme", layout="wide")

if st.session_state.get("role") not in ["admin", "doctor", "sage-femme"]:
    st.warning("⛔ Accès restreint aux professionnels autorisés.")
    st.stop()

st.title("🌿 Suivi Global Sage-Femme")
st.markdown("---")

with st.form(key="midwifery_form", clear_on_submit=True):
    st.subheader("Entrée de données de suivi global")

    nom = st.text_input("Nom")
    date_debut = st.date_input("Date de début", value=None)
    date_fin = st.date_input("Date de fin", value=None)
    types_soins = st.multiselect(
        "Types de soins",
        ["Prénatal", "Accouchement", "Postnatal", "Éducation", "Autre"],
    )
    resume = st.text_area("Résumé des soins")

    submitted = st.form_submit_button("Soumettre")

    if submitted:
        insert_data_midwifery(
            nom,
            str(date_debut) if date_debut else None,
            str(date_fin) if date_fin else None,
            ", ".join(types_soins),
            resume,
        )
        reset_all_forms()
        st.success("✅ Données enregistrées avec succès.")
        st.rerun()

st.markdown("---")
st.subheader("📚 Historique du suivi sage-femme")
df_history = fetch_history_midwifery()
if not df_history.empty:
    st.dataframe(df_history, use_container_width=True)
else:
    st.info("Aucune donnée de suivi sage-femme enregistrée.")

if st.button("🔄 Réinitialiser la page"):
    reset_all_forms()
    st.rerun()

navigation_buttons()
