# 📦 Imports
import sqlite3
import pandas as pd
import streamlit as st
from datetime import date

# ⚙️ Configuration
st.set_page_config(page_title="👥 Soins Prénatals", page_icon="👥", layout="wide")
st.title("👥 Soins Prénatals")
st.write(
    "Bienvenue dans la page **Soins Prénatals**. Veuillez saisir les informations de la patiente."
)

# 🔐 (Optionnel) Contrôle d'accès
if st.session_state.get("role") not in ["admin", "sage-femme"]:
    st.warning("⛔ Accès réservé aux professionnels autorisés.")
    st.stop()


# 🗄️ Connexion à la base
def get_db_connection():
    return sqlite3.connect("midwifery_data.db")


def create_prenatal_care_table():
    conn = get_db_connection()
    conn.execute(
        """CREATE TABLE IF NOT EXISTS prenatal_care (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chart_number TEXT, date_collection TEXT, gpa TEXT, edd_date TEXT,
        tobacco_use TEXT, substance_use TEXT, bmi REAL, ce_cle_status TEXT, racism TEXT,
        domestic_violence TEXT, housing TEXT, pregnancy_loss TEXT, previous_c_section TEXT,
        previous_vbac TEXT, high_risk_pe TEXT, gdm TEXT, anemia TEXT, stbbis TEXT,
        trainee_involved TEXT, referral_worker TEXT, prenatal_consultation TEXT,
        reason1 TEXT, made_with1 TEXT, reason2 TEXT, made_with2 TEXT,
        reason3 TEXT, made_with3 TEXT, notes TEXT, telehealth TEXT,
        shared_care TEXT, transfer_care TEXT, other_transfer_reason TEXT,
        transfer_to TEXT, care_ended TEXT
    )"""
    )
    conn.commit()
    conn.close()


def insert_prenatal_care_data(*args):
    conn = get_db_connection()
    conn.execute(
        """INSERT INTO prenatal_care (
        chart_number, date_collection, gpa, edd_date,
        tobacco_use, substance_use, bmi, ce_cle_status, racism,
        domestic_violence, housing, pregnancy_loss, previous_c_section,
        previous_vbac, high_risk_pe, gdm, anemia, stbbis, trainee_involved,
        referral_worker, prenatal_consultation, reason1, made_with1,
        reason2, made_with2, reason3, made_with3, notes, telehealth,
        shared_care, transfer_care, other_transfer_reason, transfer_to, care_ended
    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        args,
    )
    conn.commit()
    conn.close()


def get_prenatal_care_data():
    conn = get_db_connection()
    df = pd.read_sql_query(
        "SELECT * FROM prenatal_care ORDER BY date_collection DESC", conn
    )
    conn.close()
    return df


# 🧩 Options
options_oui_non = ["", "Oui", "Non"]
options_tabac = ["", "Oui", "Non", "Parfois"]
options_ce_cle = ["", "Oui", "Non", "Partiel"]
options_consultation_raison = [
    "",
    "Grossesse à risque élevé pour la pré-éclampsie",
    "Diabète gestationnel",
    "Anémie en grossesse",
    "IST pendant la grossesse",
    "Trainee impliqué dans les soins prénatals",
    "Référence à un autre professionnel de la santé",
    "Autre",
]
options_consultation_professionnel = [
    "",
    "Médecin",
    "Infirmière",
    "Sage-femme",
    "Pédiatre",
    "Autre professionnel de la santé",
]
options_transfert_soins = [
    "",
    "Médecin de famille",
    "Obstétricien",
    "Centre hospitalier",
]
options_fin_soins = [
    "",
    "Fausses couches",
    "Décès intra-utérin",
    "Arrêt de la grossesse",
    "Accouchement prématuré",
    "Transfert à un autre professionnel",
]

# 📝 Formulaire
create_prenatal_care_table()

with st.form("prenatal_care_form", clear_on_submit=True):
    st.subheader("Informations de base")
    col1, col2, col3 = st.columns(3)
    chart_number = col1.text_input("Numéro de dossier")
    date_collection = col2.date_input("Date de la collecte", value=date.today())
    gpa = col3.text_input("GPA (texte libre)")

    col4, col5, col6, col7 = st.columns(4)
    edd_date = col4.date_input("Date prévue d'accouchement (EDD)", value=date.today())
    tobacco_use = col5.selectbox("Consommation de tabac", options_tabac)
    substance_use = col6.selectbox(
        "Consommation de substances pendant la grossesse", options_oui_non
    )
    bmi = col7.number_input("IMC", min_value=0.0, step=0.1)

    st.subheader("Antécédents et Risques")
    ce_cle_status = st.selectbox("Statut CE CLE", options_ce_cle)
    racism = st.selectbox("Expérience de racisme", options_oui_non)
    domestic_violence = st.selectbox("Violence domestique", options_oui_non)
    housing = st.selectbox("Défis de logement", options_oui_non)
    pregnancy_loss = st.selectbox("Perte de grossesse", options_oui_non)
    previous_c_section = st.selectbox("Césarienne antérieure", options_oui_non)
    previous_vbac = st.selectbox("VBAC antérieur", options_oui_non)
    high_risk_pe = st.selectbox("Risque élevé de pré-éclampsie", options_oui_non)
    gdm = st.selectbox("Diabète gestationnel (GDM)", options_oui_non)
    anemia = st.selectbox("Anémie en grossesse", options_oui_non)
    stbbis = st.selectbox("IST en grossesse", options_oui_non)

    st.subheader("Consultations et Références")
    trainee_involved = st.selectbox(
        "Stagiaire impliqué dans les soins prénatals", options_oui_non
    )
    referral_worker = st.selectbox(
        "Référence à un autre professionnel de la santé", options_oui_non
    )

    prenatal_consultation = st.selectbox(
        "Consultation médicale prénatale ?", options_oui_non
    )
    reason1 = st.selectbox("Raison de la consultation 1", options_consultation_raison)
    made_with1 = st.selectbox(
        "Consultation 1 faite avec", options_consultation_professionnel
    )
    reason2 = st.selectbox("Raison de la consultation 2", options_consultation_raison)
    made_with2 = st.selectbox(
        "Consultation 2 faite avec", options_consultation_professionnel
    )
    reason3 = st.selectbox("Raison de la consultation 3", options_consultation_raison)
    made_with3 = st.selectbox(
        "Consultation 3 faite avec", options_consultation_professionnel
    )
    notes = st.text_area("Notes, explications")

    st.subheader("Suivi des Soins")
    telehealth = st.selectbox("Télésanté pendant la grossesse ?", options_oui_non)
    shared_care = st.selectbox("Soins partagés ?", options_oui_non)
    transfer_care = st.selectbox("Transfert de soins prénatals ?", options_oui_non)
    other_transfer_reason = st.text_area(
        "Autre raison pour le transfert des soins prénatals"
    )
    transfer_to = st.selectbox(
        "Transfert des soins prénatals vers", options_transfert_soins
    )
    care_ended = st.selectbox("Fin des soins de sage-femme", options_fin_soins)

    submitted = st.form_submit_button("✅ Soumettre")
    if submitted:
        if not chart_number:
            st.warning("Veuillez entrer un numéro de dossier.")
        else:
            insert_prenatal_care_data(
                chart_number,
                str(date_collection),
                gpa,
                str(edd_date),
                tobacco_use,
                substance_use,
                bmi,
                ce_cle_status,
                racism,
                domestic_violence,
                housing,
                pregnancy_loss,
                previous_c_section,
                previous_vbac,
                high_risk_pe,
                gdm,
                anemia,
                stbbis,
                trainee_involved,
                referral_worker,
                prenatal_consultation,
                reason1,
                made_with1,
                reason2,
                made_with2,
                reason3,
                made_with3,
                notes,
                telehealth,
                shared_care,
                transfer_care,
                other_transfer_reason,
                transfer_to,
                care_ended,
            )
            st.success("✅ Formulaire soumis et enregistré avec succès !")
            st.rerun()

# 📋 Historique
st.markdown("---")
