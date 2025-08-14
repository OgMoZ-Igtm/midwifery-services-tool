import streamlit as st
from utils.database import insert_initial_consultation, fetch_initial_consultation
from utils.navigation import navigation_buttons, reset_all_forms

st.set_page_config(page_title="Consultation initiale", layout="wide")

# 🔐 Contrôle d'accès
if st.session_state.get("role") not in ["admin", "doctor", "sage-femme"]:
    st.warning("⛔ Accès restreint aux professionnels autorisés.")
    st.stop()

# 🩺 Titre
st.title("🩺 Consultation Initiale")
st.markdown("---")

# 📝 Formulaire
with st.form(key="initial_consultation_form", clear_on_submit=True):
    st.subheader("Données de la première consultation")

    chart_number = st.text_input("Numéro de dossier")
    date_of_referral = st.date_input("Date de référence")
    age = st.number_input("Âge", min_value=0, max_value=120, step=1)
    community_of_residence = st.text_input("Communauté de résidence")
    status = st.selectbox("Statut", ["Résidente", "Visiteuse", "Autre"])
    referred_by = st.text_input("Référé par")
    reason_for_referral = st.text_area("Raison de la référence")
    successful_first_contact = st.selectbox("Premier contact réussi ?", ["Oui", "Non"])
    eligible_to_midwifery_care = st.selectbox(
        "Admissible aux soins de sage-femme ?", ["Oui", "Non"]
    )
    reason_for_non_eligibility = st.text_area(
        "Raison de non-admissibilité", placeholder="Si applicable"
    )
    weeks_at_first_appointment = st.number_input(
        "Semaines à la première visite", min_value=0, max_value=42
    )
    reason_if_never_seen = st.text_area(
        "Raison si jamais vue", placeholder="Si applicable"
    )

    submitted = st.form_submit_button("Soumettre")

    if submitted:
        insert_initial_consultation(
            chart_number,
            str(date_of_referral),
            age,
            community_of_residence,
            status,
            referred_by,
            reason_for_referral,
            successful_first_contact,
            eligible_to_midwifery_care,
            reason_for_non_eligibility,
            weeks_at_first_appointment,
            reason_if_never_seen,
        )
        reset_all_forms()
        st.success("✅ Données enregistrées avec succès.")
        st.rerun()

# 📋 Historique
st.markdown("---")
st.subheader("📚 Historique des consultations initiales")
df_history = fetch_initial_consultation()
if not df_history.empty:
    st.dataframe(df_history, use_container_width=True)
else:
    st.info("Aucune donnée enregistrée pour le moment.")

# 🔄 Réinitialisation
if st.button("🔄 Réinitialiser la page"):
    reset_all_forms()
    st.rerun()

# 🧭 Navigation
navigation_buttons()
