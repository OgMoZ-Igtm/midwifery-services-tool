import streamlit as st
from datetime import date
import pandas as pd
from utils.database import insert_data_intrapartum, fetch_history_intrapartum
from utils.navigation import navigation_buttons, reset_all_forms

st.set_page_config(page_title="Soins Intrapartum", layout="wide")

if st.session_state.get("role") not in ["admin", "doctor", "sage-femme"]:
    st.warning("⛔ Accès restreint aux professionnels autorisés.")
    st.stop()

st.title("🩻 Soins Intrapartum")
st.markdown("---")

with st.form(key="intrapartum_form", clear_on_submit=True):
    st.subheader("Entrée de données intrapartum")

    nom = st.text_input("Nom")
    date_accouchement = st.date_input("Date d'accouchement", value=None)
    type_accouchement = st.selectbox(
        "Type d'accouchement", ["Spontané", "Césarienne", "Instrumental", "Autre"]
    )
    observations = st.text_area("Observations")

    submitted = st.form_submit_button("Soumettre")

    if submitted:
        insert_data_intrapartum(
            nom,
            str(date_accouchement) if date_accouchement else None,
            type_accouchement,
            observations,
        )
        reset_all_forms()
        st.success("✅ Données enregistrées avec succès.")
        st.rerun()

st.markdown("---")
st.subheader("📚 Historique des soins intrapartum")
df_history = fetch_history_intrapartum()
if not df_history.empty:
    st.dataframe(df_history, use_container_width=True)
else:
    st.info("Aucune donnée intrapartum enregistrée.")

if st.button("🔄 Réinitialiser la page"):
    reset_all_forms()
    st.rerun()

navigation_buttons()
