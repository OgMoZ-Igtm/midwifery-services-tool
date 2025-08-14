import streamlit as st
from datetime import date
import pandas as pd
from utils.database import insert_data_demographics, fetch_history_demographics
from utils.navigation import navigation_buttons, reset_all_forms

st.set_page_config(page_title="Données démographiques", layout="wide")

# 🔐 Contrôle d'accès
if st.session_state.get("role") not in ["admin", "doctor", "sage-femme"]:
    st.warning("⛔ Accès restreint aux professionnels autorisés.")
    st.stop()

# 👥 Titre
st.title("👥 Données Démographiques")
st.markdown("---")

# 📝 Formulaire
with st.form(key="demographics_form", clear_on_submit=True):
    st.subheader("Entrée de nouvelles données démographiques")

    chart_number = st.text_input("Numéro de dossier")
    nom = st.text_input("Nom")
    prenom = st.text_input("Prénom")
    date_naissance = st.date_input("Date de naissance", value=None)
    sexe = st.selectbox("Sexe", ["Femme", "Homme", "Autre"])
    adresse = st.text_input("Adresse")
    telephone = st.text_input("Téléphone")

    submitted = st.form_submit_button("Soumettre")

    if submitted:
        insert_data_demographics(
            chart_number,
            nom,
            prenom,
            str(date_naissance) if date_naissance else None,
            sexe,
            adresse,
            telephone,
        )
        reset_all_forms()
        st.success("✅ Données enregistrées avec succès.")
        st.rerun()

# 📋 Historique des données
st.markdown("---")
st.subheader("📚 Historique des données démographiques")
df_history = fetch_history_demographics()
if not df_history.empty:
    st.dataframe(df_history, use_container_width=True)
else:
    st.info("Aucune donnée démographique n'a encore été enregistrée.")

# 🔄 Réinitialisation
if st.button("🔄 Réinitialiser la page"):
    reset_all_forms()
    st.rerun()

# 🧭 Navigation
navigation_buttons()
