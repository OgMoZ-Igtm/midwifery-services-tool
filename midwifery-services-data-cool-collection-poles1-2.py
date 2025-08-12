# -*- coding: utf-8 -*-
import streamlit as st
import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, date
import io
from fpdf import FPDF
import bcrypt
import plotly.express as px
import numpy as np


# --- Correction pour le DeprecationWarning ---
def register_adapters():
    """
    Enregistre un adaptateur pour les objets datetime.date afin de les convertir
    en chaînes de caractères au format ISO 8601 ('YYYY-MM-DD') pour SQLite.
    Cela résout le DeprecationWarning concernant le gestionnaire de dates.
    """
    sqlite3.register_adapter(date, lambda d: d.isoformat())


# --- Fonctions de base de données ---
def get_db_connection():
    """Fonction pour établir la connexion à la base de données SQLite."""
    # Le nom de la base de données est inchangé pour cette mise à jour
    conn = sqlite3.connect("suivi_midwifery_nouvelle.db")
    conn.row_factory = sqlite3.Row  # Permet d'accéder aux colonnes par leur nom
    return conn


# --- Initialisation et gestion de la base SQLite3 ---
def init_all_dbs():
    """Crée toutes les tables nécessaires si elles n'existent pas déjà."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table 'demographics'
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS demographics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chart_number TEXT,
            dob TEXT,
            date_of_referral TEXT,
            age TEXT,
            community_of_residence TEXT,
            status TEXT,
            referred_by TEXT,
            reason_for_referral TEXT,
            successful_first_contact TEXT,
            eligible_to_midwifery_care TEXT,
            reason_for_non_eligibility TEXT,
            weeks_at_first_appointment TEXT,
            reason_if_never_seen TEXT
        )
    """
    )

    # Table 'prenatal_care' (corrigée pour inclure les nouveaux champs)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS prenatal_care (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chart_number TEXT,
            date_collection TEXT,
            gpa TEXT,
            edd_date TEXT,
            tobacco_use TEXT,
            substance_use TEXT,
            bmi REAL,
            ce_cle_status TEXT,
            racism TEXT,
            domestic_violence TEXT,
            housing TEXT,
            pregnancy_loss TEXT,
            previous_c_section TEXT,
            previous_vbac TEXT,
            high_risk_pe TEXT,
            gdm TEXT,
            anemia TEXT,
            stbbis TEXT,
            trainee_involved TEXT,
            referral_worker TEXT,
            prenatal_consultation TEXT,
            reason1 TEXT,
            made_with1 TEXT,
            reason2 TEXT,
            made_with2 TEXT,
            reason3 TEXT,
            made_with3 TEXT,
            notes TEXT,
            telehealth TEXT,
            shared_care TEXT,
            transfer_care TEXT,
            other_transfer_reason TEXT,
            transfer_to TEXT,
            care_ended TEXT,
            patient_age TEXT,
            birthplace TEXT,
            detailed_appointment_type TEXT
        )
        """
    )

    # Table 'rendez_vous' (corrigée pour inclure tous les champs du formulaire)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS rendez_vous (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chart_number TEXT,
            appointment_date TEXT,
            appointment_type TEXT,
            appointment_detail TEXT,
            duration_minutes INTEGER,
            attended TEXT,
            notes TEXT
        )
        """
    )

    # Table 'users'
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            professional_title TEXT
        )
    """
    )

    # Table 'donnees' pour les statistiques (si nécessaire)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS donnees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            sommeil REAL,
            humeur INTEGER,
            sport INTEGER,
            alimentation INTEGER,
            note_sante INTEGER
        )
    """
    )

    # Table 'bebe'
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS bebe (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT,
            poids REAL,
            taille REAL
        )
    """
    )

    # Crée un utilisateur test si aucun n'existe
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'testuser'")
    if cursor.fetchone()[0] == 0:
        hashed_password = bcrypt.hashpw(
            "password123".encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        cursor.execute(
            "INSERT INTO users (username, hashed_password, professional_title) VALUES (?, ?, ?)",
            ("testuser", hashed_password, "Sage-femme"),
        )
        conn.commit()
        st.success("")

    conn.commit()
    conn.close()


def get_all_demographics_data():
    """
    Récupère toutes les données de la table 'demographics' et les retourne
    sous forme de DataFrame pandas.
    """
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM demographics", conn)
    conn.close()
    return df


# --- Fonctions de hachage de mot de passe ---
def hash_password(password):
    """Hache le mot de passe pour le stockage sécurisé."""
    # Convertit la chaîne en bytes
    bytes_password = password.encode("utf-8")
    # Génère un salt et hache le mot de passe
    hashed_password = bcrypt.hashpw(bytes_password, bcrypt.gensalt())
    return hashed_password


def check_password(password, hashed_password):
    """Vérifie le mot de passe haché."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password)


# =====================================================================
# ---- FONCTIONS SQLITE : DEMOGRAPHICS ----
# =====================================================================
def insert_demographics_data(
    chart_number,
    dob,
    date_of_referral,
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
):
    """Insère les données démographiques dans la base de données."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO demographics (
            chart_number,
            dob,
            date_of_referral,
            age,
            community_of_residence,
            status,
            referred_by,
            reason_for_referral,
            successful_first_contact,
            eligible_to_midwifery_care,
            reason_for_non_eligibility,
            weeks_at_first_appointment,
            reason_if_never_seen
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            chart_number,
            dob,
            date_of_referral,
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
        ),
    )
    conn.commit()
    conn.close()


def get_demographics_data():
    """Récupère toutes les données démographiques."""
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM demographics", conn)
    conn.close()
    return df


# =====================================================================
# ---- FONCTIONS SQLITE : PRENATAL CARE ----
# =====================================================================
def insert_prenatal_care_data(
    chart_number,
    date_collection,
    gpa,
    edd_date,
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
    patient_age,
    birthplace,
    detailed_appointment_type,
):
    """Insère les données de soins prénatals dans la base de données."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO prenatal_care (
            chart_number, date_collection, gpa, edd_date, tobacco_use, substance_use,
            bmi, ce_cle_status, racism, domestic_violence, housing, pregnancy_loss,
            previous_c_section, previous_vbac, high_risk_pe, gdm, anemia, stbbis,
            trainee_involved, referral_worker, prenatal_consultation, reason1,
            made_with1, reason2, made_with2, reason3, made_with3, notes, telehealth,
            shared_care, transfer_care, other_transfer_reason, transfer_to, care_ended,
            patient_age, birthplace, detailed_appointment_type
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            chart_number,
            date_collection,
            gpa,
            edd_date,
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
            patient_age,
            birthplace,
            detailed_appointment_type,
        ),
    )
    conn.commit()
    conn.close()


def get_prenatal_care_data():
    """Récupère toutes les données de soins prénatals."""
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM prenatal_care", conn)
    conn.close()
    return df


# =====================================================================
# ---- FONCTIONS SQLITE : RENDEZ-VOUS ----
# =====================================================================
def insert_rendez_vous(
    chart_number,
    appointment_date,
    appointment_type,
    appointment_detail,
    duration_minutes,
    attended,
    notes,
):
    """Insère un nouveau rendez-vous dans la base de données."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO rendez_vous (
            chart_number, appointment_date, appointment_type, appointment_detail,
            duration_minutes, attended, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        (
            chart_number,
            appointment_date,
            appointment_type,
            appointment_detail,
            duration_minutes,
            attended,
            notes,
        ),
    )
    conn.commit()
    conn.close()


def get_rendez_vous_data():
    """Récupère tous les rendez-vous."""
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM rendez_vous", conn)
    conn.close()
    return df


def reset_all_forms():
    """Réinitialise les valeurs des formulaires dans la session."""
    for key in list(st.session_state.keys()):
        if key not in ["authenticated", "username", "professional_title", "page"]:
            del st.session_state[key]


# =====================================================================
# ---- FONCTIONS D'AUTHENTIFICATION ----
# =====================================================================
def check_user(username, password):
    """Vérifie l'identité de l'utilisateur."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT hashed_password, professional_title FROM users WHERE username = ?",
        (username,),
    )
    user = cursor.fetchone()
    conn.close()
    if user and bcrypt.checkpw(
        password.encode("utf-8"), user["hashed_password"].encode("utf-8")
    ):
        return True, user["professional_title"]
    return False, None


def register_user(username, password, professional_title):
    """Enregistre un nouvel utilisateur."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        password_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        cursor.execute(
            "INSERT INTO users (username, hashed_password, professional_title) VALUES (?, ?, ?)",
            (username, password_hash, professional_title),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def update_password(username, new_password):
    """Met à jour le mot de passe d'un utilisateur."""
    conn = get_db_connection()
    cursor = conn.cursor()
    password_hash = bcrypt.hashpw(
        new_password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")
    cursor.execute(
        "UPDATE users SET hashed_password = ? WHERE username = ?",
        (password_hash, username),
    )
    conn.commit()
    conn.close()


# =====================================================================
# ---- PAGES DE L'APPLICATION ----
# =====================================================================


def page_accueil():
    """Displays the home page"""
    st.header("🏡 Welcome to the Midwifery Services Data Tool Collection !")
    st.write("Thank you for taking the time to fill out this tool!")
    st.markdown(
        """
        For any questions, suggestions, or modification requests, please do not hesitate to contact Katia Lessard, PPRO-Midwifery, at:
        **Katia.Lessard.reg18@ssss.gouv.qc.ca**
        This tool has been created to support the continuous improvement and provision of high-quality midwifery care in Eeyou Istchee. It will allow us to operate a constant follow-up on the services, outcomes, and impacts of Midwifery Services amongst our clientele.
        Some variables collected here were specifically requested by Nishiyuu. Other variables were selected through various consultations with Midwifery Services and are inspired by different databases and organizations, including:
        * The National Indigenous Association of Midwives
        * I-CLSC, Care 4, CHB, RSFQ
        * The Canadian Midwifery Minimum Database
        * MSSS
        Data analysis is a public matter and will be reported back yearly to Eeyou Istchee Communities via the Midwifery Services' and Cree Health Board's Annual Report.
        Thank you all for your commitment to providing high-quality midwifery care to families in Eeyou Istchee.
        """
    )
    st.write(
        """
        Use the "Previous" or "Next" navigation buttons below to move between different sections.
        """
    )

    # Affiche un aperçu des données si l'utilisateur est authentifié
    if st.session_state.authenticated:
        conn = get_db_connection()
        df_demographics = pd.read_sql_query("SELECT * FROM demographics", conn)
        df_prenatal_care = pd.read_sql_query("SELECT * FROM prenatal_care", conn)
        df_rendez_vous = pd.read_sql_query("SELECT * FROM rendez_vous", conn)
        conn.close()

        st.subheader("Aperçu rapide")
        col1, col2, col3 = st.columns(3)
        col1.metric("Entrées démographiques", len(df_demographics))
        col2.metric("Entrées de soins prénatals", len(df_prenatal_care))
        col3.metric("Entrées de rendez-vous", len(df_rendez_vous))


def page_demographics():
    st.title("👥 Données Démographiques")
    st.markdown("---")
    with st.form(key="demographics_form", clear_on_submit=True):
        st.subheader("Entrée de nouvelles données démographiques")

        # Variables des menus déroulants
        community_options = [
            "Waskaganish",
            "Chisasibi",
            "Eastmain",
            "Mistissini",
            "Nemaska",
            "Oujé-Bougoumou",
            "Waswanipi",
            "Wemindji",
            "Whapmagoostui",
            "Other",
        ]
        status_options = ["Indigenous-Cree", "Indigenous-nonCree", "Non-Indigenous"]
        referred_by_options = [
            "Self-referral",
            "Midwife trainee",
            "Birth assistant",
            "PCCR",
            "Nurse",
            "Doctor",
            "Midwife",
            "Other",
        ]
        reason_for_referral_options = [
            "Information request",
            "Complete Midwifery Care",
            "Prenatal Care",
            "Shared Care",
            "Birth Preparation",
            "Postpartum",
            "Postpartum home doula care",
            "Breastfeeding support",
            "Perinatal loss support",
            "Pap smear",
            "STBBIs screening",
            "Pregnancy interruption",
            "Birth control",
            "Other",
        ]
        contact_options = ["Yes", "No", "Never reached", "N/A"]
        eligible_options = ["Yes", "No", "N/A"]
        weeks_options = [
            "<12 weeks",
            "12 to 20 weeks",
            ">20 weeks",
            "Postpartum",
            "Non-pregnant",
            "Never seen",
            "N/A",
        ]
        never_seen_options = [
            "Early pregnancy loss",
            "Termination of pregnancy",
            "Never came to appointments",
            "Declines Midwifery care",
            "Moved elsewhere",
            "Unknown",
            "N/A",
        ]

        # Champs du formulaire
        chart_number = st.text_input("Numéro de dossier")
        dob = st.date_input("Date de naissance du client (DOB) YYYY-MM-DD", value=None)
        date_of_referral = st.date_input("Date de référence YYYY-MM-DD", value=None)
        age = st.text_input("Âge (YY)")

        community_of_residence = st.selectbox(
            "Communauté de résidence", options=[""] + community_options
        )
        status = st.selectbox("Statut", options=[""] + status_options)
        referred_by = st.selectbox("Référence par", options=[""] + referred_by_options)
        reason_for_referral = st.selectbox(
            "Raison de la référence", options=[""] + reason_for_referral_options
        )
        successful_first_contact = st.selectbox(
            "Premier contact réussi", options=[""] + contact_options
        )
        eligible_to_midwifery_care = st.selectbox(
            "Éligible aux soins de sage-femme ?", options=[""] + eligible_options
        )
        reason_for_non_eligibility = st.text_area(
            "Raison de la non-éligibilité (texte libre)"
        )
        weeks_at_first_appointment = st.selectbox(
            "Nombre de semaines au 1er rendez-vous", options=[""] + weeks_options
        )
        reason_if_never_seen = st.selectbox(
            "Raison si jamais vu", options=[""] + never_seen_options
        )

        submitted = st.form_submit_button("Soumettre")

        if submitted:
            # Conversion des dates en chaînes de caractères
            dob_str = dob if dob else None
            date_of_referral_str = date_of_referral if date_of_referral else None

            insert_demographics_data(
                chart_number,
                dob_str,
                date_of_referral_str,
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
            st.success("✅ Formulaire soumis et enregistré avec succès !")
            st.rerun()

    st.markdown("---")
    st.subheader("Historique des données démographiques")
    df_demographics = get_demographics_data()
    if not df_demographics.empty:
        st.dataframe(df_demographics)
    else:
        st.info("Aucune donnée démographique n'a encore été enregistrée.")


def page_prenatal_care():
    st.title("🤰 Soins Prénatals")
    st.write("Veuillez saisir les informations de la patiente.")

    champs = [
        "chart_number",
        "date_collection",
        "gpa",
        "edd_date",
        "tobacco_use",
        "substance_use",
        "bmi",
        "ce_cle_status",
        "racism",
        "domestic_violence",
        "housing",
        "pregnancy_loss",
        "previous_c_section",
        "previous_vbac",
        "high_risk_pe",
        "gdm",
        "anemia",
        "stbbis",
        "trainee_involved",
        "referral_worker",
        "prenatal_consultation",
        "reason1",
        "made_with1",
        "reason2",
        "made_with2",
        "reason3",
        "made_with3",
        "notes",
        "telehealth",
        "shared_care",
        "transfer_care",
        "other_transfer_reason",
        "transfer_to",
        "care_ended",
        "patient_age",
        "birthplace",
        "detailed_appointment_type",
    ]
    for champ in champs:
        if champ not in st.session_state:
            st.session_state[champ] = None

    with st.form("prenatal_care_form", clear_on_submit=True):
        st.subheader("Informations de base")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.session_state.chart_number = st.text_input(
                "Numéro de dossier", value=st.session_state.chart_number or ""
            )
        with col2:
            st.session_state.date_collection = st.date_input(
                "Date de la collecte",
                value=st.session_state.date_collection or date.today(),
            )
        with col3:
            st.session_state.gpa = st.text_input(
                "GPA (texte libre)", value=st.session_state.gpa or ""
            )

        col4, col5, col6, col7 = st.columns(4)
        with col4:
            st.session_state.edd_date = st.date_input(
                "Date prévue d'accouchement (EDD)",
                value=st.session_state.edd_date or date.today(),
            )
        with col5:
            st.session_state.tobacco_use = st.selectbox(
                "Consommation de tabac",
                ["", "Oui", "Non"],
                index=(
                    0
                    if not st.session_state.tobacco_use
                    else ["", "Oui", "Non"].index(st.session_state.tobacco_use)
                ),
            )
        with col6:
            st.session_state.substance_use = st.selectbox(
                "Consommation de substances pendant la grossesse",
                ["", "Oui", "Non"],
                index=(
                    0
                    if not st.session_state.substance_use
                    else ["", "Oui", "Non"].index(st.session_state.substance_use)
                ),
            )
        with col7:
            st.session_state.bmi = st.number_input(
                "IMC",
                min_value=0.0,
                step=0.1,
                value=float(st.session_state.bmi) if st.session_state.bmi else 0.0,
            )

        st.subheader("Antécédents et Risques")
        col8, col9, col10 = st.columns(3)
        with col8:
            st.session_state.ce_cle_status = st.selectbox(
                "Statut CE CLE",
                ["", "Positif", "Négatif"],
                index=(
                    0
                    if not st.session_state.ce_cle_status
                    else ["", "Positif", "Négatif"].index(
                        st.session_state.ce_cle_status
                    )
                ),
            )
        with col9:
            st.session_state.racism = st.selectbox(
                "Expérience de racisme",
                ["", "Oui", "Non"],
                index=(
                    0
                    if not st.session_state.racism
                    else ["", "Oui", "Non"].index(st.session_state.racism)
                ),
            )
        with col10:
            st.session_state.domestic_violence = st.selectbox(
                "Violence domestique",
                ["", "Oui", "Non"],
                index=(
                    0
                    if not st.session_state.domestic_violence
                    else ["", "Oui", "Non"].index(st.session_state.domestic_violence)
                ),
            )

        col11, col12, col13 = st.columns(3)
        with col11:
            st.session_state.housing = st.selectbox(
                "Défis de logement",
                ["", "Oui", "Non"],
                index=(
                    0
                    if not st.session_state.housing
                    else ["", "Oui", "Non"].index(st.session_state.housing)
                ),
            )
        with col12:
            st.session_state.pregnancy_loss = st.selectbox(
                "Perte de grossesse",
                ["", "Oui", "Non"],
                index=(
                    0
                    if not st.session_state.pregnancy_loss
                    else ["", "Oui", "Non"].index(st.session_state.pregnancy_loss)
                ),
            )
        with col13:
            st.session_state.previous_c_section = st.selectbox(
                "Césarienne antérieure",
                ["", "Oui", "Non"],
                index=(
                    0
                    if not st.session_state.previous_c_section
                    else ["", "Oui", "Non"].index(st.session_state.previous_c_section)
                ),
            )

        col14, col15, col16, col17 = st.columns(4)
        with col14:
            st.session_state.previous_vbac = st.selectbox(
                "VBAC antérieur",
                ["", "Oui", "Non"],
                index=(
                    0
                    if not st.session_state.previous_vbac
                    else ["", "Oui", "Non"].index(st.session_state.previous_vbac)
                ),
            )
        with col15:
            st.session_state.high_risk_pe = st.selectbox(
                "Risque élevé de pré-éclampsie",
                ["", "Oui", "Non"],
                index=(
                    0
                    if not st.session_state.high_risk_pe
                    else ["", "Oui", "Non"].index(st.session_state.high_risk_pe)
                ),
            )
        with col16:
            st.session_state.gdm = st.selectbox(
                "Diabète gestationnel (GDM)",
                ["", "Oui", "Non"],
                index=(
                    0
                    if not st.session_state.gdm
                    else ["", "Oui", "Non"].index(st.session_state.gdm)
                ),
            )
        with col17:
            st.session_state.anemia = st.selectbox(
                "Anémie en grossesse",
                ["", "Oui", "Non"],
                index=(
                    0
                    if not st.session_state.anemia
                    else ["", "Oui", "Non"].index(st.session_state.anemia)
                ),
            )
        st.session_state.stbbis = st.selectbox(
            "IST en grossesse",
            ["", "Oui", "Non"],
            index=(
                0
                if not st.session_state.stbbis
                else ["", "Oui", "Non"].index(st.session_state.stbbis)
            ),
        )

        st.subheader("Consultations et Références")
        col18, col19 = st.columns(2)
        with col18:
            st.session_state.trainee_involved = st.selectbox(
                "Stagiaire impliqué",
                ["", "Oui", "Non"],
                index=(
                    0
                    if not st.session_state.trainee_involved
                    else ["", "Oui", "Non"].index(st.session_state.trainee_involved)
                ),
            )
        with col19:
            st.session_state.referral_worker = st.selectbox(
                "Référence à un autre professionnel",
                ["", "Oui", "Non"],
                index=(
                    0
                    if not st.session_state.referral_worker
                    else ["", "Oui", "Non"].index(st.session_state.referral_worker)
                ),
            )

        st.markdown("---")
        col20, col21, col22 = st.columns(3)
        with col20:
            st.session_state.prenatal_consultation = st.selectbox(
                "Consultation médicale prénatale ?",
                ["", "Oui", "Non"],
                index=(
                    0
                    if not st.session_state.prenatal_consultation
                    else ["", "Oui", "Non"].index(
                        st.session_state.prenatal_consultation
                    )
                ),
            )

        st.subheader("Raison de la consultation (si applicable)")
        col23, col24 = st.columns(2)
        with col23:
            st.session_state.reason1 = st.text_input(
                "Raison 1", value=st.session_state.reason1 or ""
            )
        with col24:
            st.session_state.made_with1 = st.text_input(
                "Effectuée avec 1", value=st.session_state.made_with1 or ""
            )

        col25, col26 = st.columns(2)
        with col25:
            st.session_state.reason2 = st.text_input(
                "Raison 2", value=st.session_state.reason2 or ""
            )
        with col26:
            st.session_state.made_with2 = st.text_input(
                "Effectuée avec 2", value=st.session_state.made_with2 or ""
            )

        col27, col28 = st.columns(2)
        with col27:
            st.session_state.reason3 = st.text_input(
                "Raison 3", value=st.session_state.reason3 or ""
            )
        with col28:
            st.session_state.made_with3 = st.text_input(
                "Effectuée avec 3", value=st.session_state.made_with3 or ""
            )

        st.subheader("Notes et Fin de Soins")
        st.session_state.notes = st.text_area(
            "Notes", value=st.session_state.notes or ""
        )

        col29, col30, col31, col32, col33, col34 = st.columns(6)
        with col29:
            st.session_state.telehealth = st.selectbox(
                "Télésanté",
                ["", "Oui", "Non"],
                index=(
                    0
                    if not st.session_state.telehealth
                    else ["", "Oui", "Non"].index(st.session_state.telehealth)
                ),
            )
        with col30:
            st.session_state.shared_care = st.selectbox(
                "Soins partagés",
                ["", "Oui", "Non"],
                index=(
                    0
                    if not st.session_state.shared_care
                    else ["", "Oui", "Non"].index(st.session_state.shared_care)
                ),
            )
        with col31:
            st.session_state.transfer_care = st.selectbox(
                "Transfert de soins",
                ["", "Oui", "Non"],
                index=(
                    0
                    if not st.session_state.transfer_care
                    else ["", "Oui", "Non"].index(st.session_state.transfer_care)
                ),
            )
        with col32:
            st.session_state.other_transfer_reason = st.text_input(
                "Autre raison de transfert",
                value=st.session_state.other_transfer_reason or "",
            )
        with col33:
            st.session_state.transfer_to = st.text_input(
                "Transféré à", value=st.session_state.transfer_to or ""
            )
        with col34:
            st.session_state.care_ended = st.selectbox(
                "Soins terminés",
                ["", "Oui", "Non"],
                index=(
                    0
                    if not st.session_state.care_ended
                    else ["", "Oui", "Non"].index(st.session_state.care_ended)
                ),
            )

        # Nouveaux champs
        st.subheader("Informations supplémentaires")
        col35, col36, col37 = st.columns(3)
        with col35:
            st.session_state.patient_age = st.text_input(
                "Âge de la patiente", value=st.session_state.patient_age or ""
            )
        with col36:
            st.session_state.birthplace = st.text_input(
                "Lieu de naissance", value=st.session_state.birthplace or ""
            )
        with col37:
            st.session_state.detailed_appointment_type = st.text_input(
                "Type de rendez-vous détaillé",
                value=st.session_state.detailed_appointment_type or "",
            )

        submitted = st.form_submit_button("Soumettre le formulaire de soins prénatals")
        if submitted:
            insert_prenatal_care_data(
                st.session_state.chart_number,
                st.session_state.date_collection,
                st.session_state.gpa,
                st.session_state.edd_date,
                st.session_state.tobacco_use,
                st.session_state.substance_use,
                st.session_state.bmi,
                st.session_state.ce_cle_status,
                st.session_state.racism,
                st.session_state.domestic_violence,
                st.session_state.housing,
                st.session_state.pregnancy_loss,
                st.session_state.previous_c_section,
                st.session_state.previous_vbac,
                st.session_state.high_risk_pe,
                st.session_state.gdm,
                st.session_state.anemia,
                st.session_state.stbbis,
                st.session_state.trainee_involved,
                st.session_state.referral_worker,
                st.session_state.prenatal_consultation,
                st.session_state.reason1,
                st.session_state.made_with1,
                st.session_state.reason2,
                st.session_state.made_with2,
                st.session_state.reason3,
                st.session_state.made_with3,
                st.session_state.notes,
                st.session_state.telehealth,
                st.session_state.shared_care,
                st.session_state.transfer_care,
                st.session_state.other_transfer_reason,
                st.session_state.transfer_to,
                st.session_state.care_ended,
                st.session_state.patient_age,
                st.session_state.birthplace,
                st.session_state.detailed_appointment_type,
            )
            st.success("✅ Formulaire soumis et enregistré avec succès !")
            st.rerun()

    st.markdown("---")
    st.subheader("Historique des données de soins prénatals")
    df_prenatal_care = get_prenatal_care_data()
    if not df_prenatal_care.empty:
        st.dataframe(df_prenatal_care)
    else:
        st.info("Aucune donnée de soins prénatals n'a encore été enregistrée.")


def page_rendez_vous():
    st.title("📅 Rendez-vous")
    st.markdown("---")
    st.subheader("Entrée de nouveaux rendez-vous")

    with st.form(key="rendez_vous_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            chart_number = st.text_input("Numéro de dossier")
        with col2:
            appointment_date = st.date_input("Date du rendez-vous", value=None)

        appointment_type = st.selectbox(
            "Type de rendez-vous",
            options=[
                "",
                "Initial",
                "Suivi",
                "Postpartum",
                "Perinatal Loss Support",
                "Conseil",
                "Autre",
            ],
        )
        appointment_detail = st.text_input("Détails du rendez-vous")
        duration_minutes = st.number_input("Durée (minutes)", min_value=0, value=60)
        attended = st.selectbox(
            "Présence", options=["", "Oui", "Non", "Annulé", "Reporté"]
        )
        notes = st.text_area("Notes")

        submitted = st.form_submit_button("Soumettre")

        if submitted:
            appointment_date_str = appointment_date if appointment_date else None

            if chart_number and appointment_date_str and appointment_type:
                insert_rendez_vous(
                    chart_number,
                    appointment_date_str,
                    appointment_type,
                    appointment_detail,
                    duration_minutes,
                    attended,
                    notes,
                )
                st.success("✅ Rendez-vous enregistré avec succès !")
                st.rerun()
            else:
                st.error(
                    "Veuillez remplir au moins le numéro de dossier, la date et le type de rendez-vous."
                )

    st.markdown("---")
    st.subheader("Historique des rendez-vous")
    df_rendez_vous = get_rendez_vous_data()
    if not df_rendez_vous.empty:
        st.dataframe(df_rendez_vous)
    else:
        st.info("Aucun rendez-vous n'a encore été enregistré.")


def reset_all_forms():
    """Resets all forms by removing session state keys
    except those related to navigation and form submitters"""
    for key in list(
        st.session_state.keys()
    ):  # Use list() to iterate over a copy of keys
        if key not in PAGES and not key.startswith("FormSubmitter:"):
            del st.session_state[key]


def page_login():
    """Page de connexion pour l'utilisateur."""
    st.title("Connexion")
    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Se connecter"):
            if username and password:
                is_valid, professional_title = check_user(username, password)
                if is_valid:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.professional_title = professional_title
                    st.session_state.page = "accueil_apres_connexion"
                    st.rerun()
                else:
                    st.error("Nom d'utilisateur ou mot de passe incorrect.")

    with col2:
        if st.button("S'inscrire"):
            st.session_state.page = "inscription"
            st.rerun()

    with col3:
        if st.button("Mot de passe oublié"):
            st.session_state.page = "mot_de_passe_oublie"
            st.rerun()


def page_inscription():
    """Page d'inscription pour un nouvel utilisateur."""
    st.title("Inscription")
    new_username = st.text_input("Nouveau nom d'utilisateur")
    new_password = st.text_input("Nouveau mot de passe", type="password")
    professional_title = st.text_input("Titre professionnel")

    if st.button("Créer un compte"):
        if new_username and new_password and professional_title:
            if register_user(new_username, new_password, professional_title):
                st.success(
                    "Compte créé avec succès ! Vous pouvez maintenant vous connecter."
                )
                st.session_state.page = "login"
                st.rerun()
            else:
                st.error(
                    "Ce nom d'utilisateur existe déjà. Veuillez en choisir un autre."
                )
        else:
            st.error("Veuillez remplir tous les champs.")


def page_mot_de_passe_oublie():
    """Page de récupération de mot de passe."""
    st.title("Réinitialiser le mot de passe")
    reset_username = st.text_input("Nom d'utilisateur")
    new_password_reset = st.text_input("Nouveau mot de passe", type="password")

    if st.button("Réinitialiser le mot de passe"):
        if reset_username and new_password_reset:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (reset_username,))
            user = cursor.fetchone()
            conn.close()

            if user:
                update_password(reset_username, new_password_reset)
                st.success("Mot de passe mis à jour avec succès.")
                st.session_state.page = "login"
                st.rerun()
            else:
                st.error("Nom d'utilisateur non trouvé.")
        else:
            st.error("Veuillez entrer un nom d'utilisateur et un nouveau mot de passe.")


# =====================================================================
# ---- PAGES DE L'APPLICATION ----
# =====================================================================

# Dictionnaire des pages de l'application principale
PAGES = {
    "Accueil": "page_accueil",
    "Données Démographiques": "page_demographics",
    "Soins Prénatals": "page_prenatal_care",
    "Rendez-vous": "page_rendez_vous",
    "Rapports": "page_rapports",
}


def navigation_buttons():
    """
    Crée et gère les boutons de navigation "Précédent" et "Suivant".
    """
    # L'état de session 'current_page' doit être initialisé
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Accueil"

    page_names = list(PAGES.keys())
    current_index = page_names.index(st.session_state.current_page)

    col1, col2 = st.columns(2)
    with col1:
        # Bouton "Précédent", désactivé sur la première page
        if st.button("⬅️ Précédent", disabled=(current_index == 0)):
            st.session_state.current_page = page_names[current_index - 1]
            st.rerun()
    with col2:
        # Bouton "Suivant", désactivé sur la dernière page
        if st.button("Suivant ➡️", disabled=(current_index == len(page_names) - 1)):
            st.session_state.current_page = page_names[current_index + 1]
            st.rerun()


# =====================================================================
# ---- FONCTIONS DE RAPPORTS FPDF AVEC LE CORRECTIF ----
# =====================================================================


class PDF(FPDF):
    """
    Classe personnalisée pour FPDF, ajoutant un en-tête et un pied de page
    pour une mise en forme cohérente.
    """

    def __init__(self, title, orientation="P", unit="mm", format="A4"):
        super().__init__(orientation, unit, format)
        self.title = title

    def header(self):
        # Logo ou autre image de l'en-tête
        # self.image('logo.png', 10, 8, 33)
        # Police Arial gras 15
        self.set_font("Arial", "B", 15)
        # Décalage vers la droite
        self.cell(80)
        # Titre
        self.cell(30, 10, self.title, 0, 1, "C")
        # Saut de ligne
        self.ln(20)

    def footer(self):
        # Positionnement à 1.5 cm du bas
        self.set_y(-15)
        # Police Arial italique 8
        self.set_font("Arial", "I", 8)
        # Numéro de page
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", 0, 0, "C")


def create_pdf(title, content):
    """
    Génère un PDF avec le titre et le contenu spécifiés en utilisant une approche
    qui contourne l'erreur de type.
    """
    pdf = PDF(title)
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font("Times", size=12)
    pdf.multi_cell(0, 10, content)

    # Utilise 'S' pour obtenir la sortie sous forme de chaîne de caractères
    # puis encode la chaîne en bytes pour Streamlit.
    return pdf.output(dest="S").encode("latin-1")


def page_rapports():
    """
    Fonction de la page "Rapports" avec un exemple de génération de PDF et un graphique.
    """
    st.title("Générer des rapports �")
    st.write(
        "Outils pour créer des rapports PDF à partir des données de l'application."
    )

    # Récupère les données pour l'affichage et les rapports
    df_demographics = get_all_demographics_data()
    st.write("Aperçu des données démographiques :")
    st.dataframe(df_demographics)

    # Ajout d'un graphique de démonstration
    if not df_demographics.empty:
        st.subheader("Distribution des âges")
        # Utilisation de Plotly pour une visualisation interactive
        try:
            fig = px.histogram(
                df_demographics,
                x="age",
                title="Distribution des âges des patientes",
            )
            st.plotly_chart(fig)
        except Exception as e:
            st.warning(f"Impossible de générer le graphique d'âge : {e}")

    else:
        st.info("Aucune donnée démographique à afficher pour le moment.")

    report_title = st.text_input("Titre du rapport", "Rapport de Suivi")
    report_content = st.text_area(
        "Contenu du rapport", "Ceci est un exemple de contenu pour le rapport PDF."
    )

    if st.button("Générer le PDF"):
        if report_title and report_content:
            try:
                pdf_bytes = create_pdf(report_title, report_content)
                st.download_button(
                    label="Télécharger le PDF",
                    data=pdf_bytes,
                    file_name=f"{report_title.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                )
            except Exception as e:
                st.error(f"Une erreur est survenue lors de la génération du PDF: {e}")
        else:
            st.warning("Veuillez saisir un titre et un contenu pour le rapport.")

    # Téléchargements CSV et XLSX (pour les données démographiques)
    st.markdown("---")
    st.markdown("**Télécharger les données démographiques :**")
    if not df_demographics.empty:
        # Bouton de téléchargement CSV
        csv_buffer = df_demographics.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label="Télécharger en .csv",
            data=csv_buffer,
            file_name="donnees_demographiques.csv",
            mime="text/csv",
        )

        # Bouton de téléchargement Excel (.xlsx)
        xlsx_buffer = io.BytesIO()
        with pd.ExcelWriter(xlsx_buffer, engine="xlsxwriter") as writer:
            df_demographics.to_excel(
                writer, index=False, sheet_name="Données Démographiques"
            )
        st.download_button(
            label="Télécharger en .xlsx",
            data=xlsx_buffer.getvalue(),
            file_name="donnees_demographiques.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        # Analyse et visualisation
        st.markdown("---")
        st.subheader("Analyse de données et Visualisation")

        # Exemple d'analyse avec Pandas et Numpy
        st.markdown("**Analyse descriptive simple**")
        st.write(f"Nombre total de patients : {len(df_demographics)}")
        if (
            "age" in df_demographics.columns
            and pd.to_numeric(df_demographics["age"], errors="coerce").notna().any()
        ):
            df_demographics["age"] = pd.to_numeric(
                df_demographics["age"], errors="coerce"
            )
            df_demographics.dropna(subset=["age"], inplace=True)
            mean_age = np.mean(df_demographics["age"])
            st.write(f"Âge moyen des patients : {mean_age:.2f} ans")
            st.write(
                f"Âge médian des patients : {df_demographics['age'].median():.2f} ans"
            )
            st.write(
                f"Âge le plus fréquent (mode) : {df_demographics['age'].mode()[0]:.2f} ans"
            )
            st.write(f"Écart-type des âges : {df_demographics['age'].std():.2f} ans")
            st.write(f"Variance des âges : {df_demographics['age'].var():.2f}")
            st.write(
                f"Quartile 25% (Q1) des âges : {df_demographics['age'].quantile(0.25):.2f} ans"
            )
            st.write(
                f"Quartile 75% (Q3) des âges : {df_demographics['age'].quantile(0.75):.2f} ans"
            )
        else:
            st.warning(
                "La colonne 'age' ne contient pas de données numériques valides."
            )

        if "community_of_residence" in df_demographics.columns:
            st.write(
                f"Communauté de résidence la plus fréquente : {df_demographics['community_of_residence'].mode()[0]}"
            )

        if (
            "age" in df_demographics.columns
            and "weeks_at_first_appointment" in df_demographics.columns
        ):
            # Calcul de la corrélation
            try:
                # S'assurer que les colonnes sont numériques
                df_demographics["age"] = pd.to_numeric(
                    df_demographics["age"], errors="coerce"
                )
                correlation = (
                    df_demographics[["age", "weeks_at_first_appointment"]]
                    .corr()
                    .iloc[0, 1]
                )
                st.write(
                    f"Coefficient de corrélation entre l'âge et les semaines au premier rendez-vous : {correlation:.2f}"
                )
            except Exception as e:
                st.warning(
                    f"Impossible de calculer la corrélation (vérifiez les types de données) : {e}"
                )

        st.markdown("---")

        # Visualisation avec Matplotlib
        st.markdown("**Visualisation avec Matplotlib (Histogramme)**")
        if (
            "age" in df_demographics.columns
            and not df_demographics["age"].isnull().all()
        ):
            fig, ax = plt.subplots()
            ax.hist(df_demographics["age"], bins=10, color="skyblue", edgecolor="black")
            ax.set_title("Distribution des âges")
            ax.set_xlabel("Âge")
            ax.set_ylabel("Nombre de patients")
            st.pyplot(fig)
        else:
            st.warning(
                "La colonne 'age' est manquante ou vide pour la visualisation Matplotlib."
            )

        # Visualisation avec Plotly (Heatmap)
        st.markdown("---")
        st.markdown("**Visualisation avec Plotly (Carte de chaleur)**")
        if (
            "age" in df_demographics.columns
            and "weeks_at_first_appointment" in df_demographics.columns
            and not df_demographics[["age", "weeks_at_first_appointment"]]
            .isnull()
            .any()
            .any()
        ):
            # Création du DataFrame pour la heatmap
            heatmap_data = df_demographics.pivot_table(
                index="age",
                columns="weeks_at_first_appointment",
                aggfunc="size",
                fill_value=0,
            )

            fig = px.imshow(
                heatmap_data,
                labels=dict(
                    x="Semaines au premier RDV", y="Âge", color="Nombre de patients"
                ),
                x=heatmap_data.columns,
                y=heatmap_data.index,
                title="Corrélation entre l'âge et les semaines au premier RDV",
            )
            fig.update_xaxes(side="top")
            st.plotly_chart(fig)
        else:
            st.warning(
                "Les colonnes 'age' ou 'weeks_at_first_appointment' sont manquantes ou vides pour la visualisation Plotly."
            )

    else:
        st.info("Aucune donnée disponible pour générer des rapports.")


# =====================================================================
# ---- APPLICATION PRINCIPALE ----
# =====================================================================
def main():
    st.sidebar.title("Navigation")

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if "page" not in st.session_state:
        st.session_state.page = "login"

    if "current_page" not in st.session_state:
        st.session_state.current_page = "Accueil"

    if st.session_state.authenticated:
        page_names = list(PAGES.keys())
        # Utilise l'état de la session pour la sélection du menu, le synchronisant avec les boutons de navigation.
        selection = st.sidebar.radio(
            "Aller à",
            page_names,
            key="main_navigation",
            index=page_names.index(st.session_state.current_page),
        )
        st.session_state.current_page = selection

        st.sidebar.markdown("---")
        st.sidebar.write(f"Connecté en tant que : **{st.session_state.username}**")
        if st.sidebar.button("Déconnexion"):
            st.session_state.authenticated = False
            st.session_state.page = "login"
            st.rerun()

        selected_page = PAGES[selection]
        globals()[selected_page]()

        # Appel de la fonction de navigation pour afficher les boutons
        st.markdown("---")
        navigation_buttons()

    else:
        # Affiche le contenu de la page de login, d'inscription ou de mot de passe oublié
        if st.session_state.page == "login":
            page_login()
        elif st.session_state.page == "inscription":
            page_inscription()
            if st.button("Retour à la connexion", key="back_to_login"):
                st.session_state["page"] = "login"
                st.rerun()
        elif st.session_state.page == "mot_de_passe_oublie":
            page_mot_de_passe_oublie()
            if st.button("Retour à la connexion", key="back_to_login_from_forgot"):
                st.session_state["page"] = "login"
                st.rerun()
        elif st.session_state.page == "accueil_apres_connexion":
            st.session_state.page = (
                "Accueil"  # Redirige vers la page d'accueil par défaut
            )
            st.rerun()


# Cette ligne lance l'application Streamlit.
if __name__ == "__main__":
    register_adapters()  # Appel de la fonction de correction avant toute opération sur la BD
    init_all_dbs()
    main()
