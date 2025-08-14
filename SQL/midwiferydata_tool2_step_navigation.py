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


# --- Fonctions de base de données ---
def get_db_connection():
    """Fonction pour établir la connexion à la base de données SQLite."""
    conn = sqlite3.connect("suivi_sante.db")
    conn.row_factory = sqlite3.Row  # Permet d'accéder aux colonnes par leur nom
    return conn


def init_all_dbs():
    """Fonction pour initialiser toutes les tables nécessaires."""
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

    # Table 'rendez_vous'
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS rendez_vous (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            medecin TEXT,
            raison TEXT
        )
    """
    )

    # Table 'donnees' - Ajoutée pour que la page d'accueil fonctionne
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

    # Table 'bebe' - Ajoutée pour que la page d'accueil fonctionne
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS bebe (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            poids REAL,
            sommeil REAL,
            humeur TEXT
        )
    """
    )

    # Table 'nutrition' - Ajoutée pour que la page d'accueil fonctionne
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS nutrition (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            repas TEXT,
            quantite TEXT
        )
    """
    )

    # Table 'users' - Corrected syntax and simplified columns for login
    # Correction: 'hashed_password' should be TEXT, not BLOB, for easy storage
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

    # Correction: Ajout d'une table pour les données de soins prénatals,
    # car la page `page_prenatal_care` a été conçue pour les collecter.
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
            care_ended TEXT
        )
        """
    )

    conn.commit()
    conn.close()


def add_user(username, password, professional_title="Sage-femme"):
    """
    Adds a new user to the database after hashing the password.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Hash the password before inserting and store it as a string
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode(
        "utf-8"
    )

    try:
        cursor.execute(
            "INSERT INTO users (username, hashed_password, professional_title) VALUES (?, ?, ?)",
            (username, hashed_password, professional_title),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        # User already exists, which is fine for this automatic creation
        pass
    finally:
        conn.close()


def check_for_initial_user():
    """Checks if there are any users in the database and creates a default one if not."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()

    if count == 0:
        add_user("testuser", "password123")
        st.success("Welcome to the Midwifery Data Collection Tool!")


# Fonctions d'authentification et d'inscription
def check_user(username, password):
    """
    Vérifie si un utilisateur existe et si le mot de passe est correct.
    Correction: Le nom de la fonction a été corrigé pour correspondre à l'appel.
    """
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
    """Enregistre un nouvel utilisateur dans la base de données."""
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
        return False  # Nom d'utilisateur déjà existant
    finally:
        conn.close()


def update_password(username, new_password):
    """Met à jour le mot de passe d'un utilisateur existant."""
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


# --- Fonctions pour les pages d'authentification ---
def login_page():
    """Displays the login page."""
    st.header("Connexion ")
    username_input = st.text_input("Nom d'utilisateur")
    password_input = st.text_input("Mot de passe", type="password")

    login_button = st.button("Se connecter")
    if login_button:
        is_valid, professional_title = check_user(username_input, password_input)
        if is_valid:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username_input
            st.session_state["professional_title"] = professional_title
            st.session_state["login_time"] = datetime.now()
            st.rerun()
        else:
            st.error("Nom d'utilisateur ou mot de passe incorrect.")


def page_inscription():
    """Page d'inscription pour les nouveaux utilisateurs."""
    st.header("✍️ Inscription")
    st.write("Veuillez créer un nouveau compte pour accéder à l'application.")
    username = st.text_input("Nom d'utilisateur")
    professional_title = st.selectbox(
        "Titre professionnel", ["Sage-femme", "Infirmière", "Médecin"]
    )
    password = st.text_input("Mot de passe", type="password")
    password_confirm = st.text_input("Confirmer le mot de passe", type="password")
    if st.button("S'inscrire"):
        if password == password_confirm:
            if username and password:
                # Correction: Appel à la fonction register_user
                if register_user(username, password, professional_title):
                    st.success(
                        "Inscription réussie ! Vous pouvez maintenant vous connecter."
                    )
                    st.session_state["page"] = "login"
                    st.rerun()
                else:
                    st.error(
                        "Ce nom d'utilisateur est déjà pris. Veuillez en choisir un autre."
                    )
            else:
                st.warning("Veuillez remplir tous les champs.")
        else:
            st.error("Les mots de passe ne correspondent pas.")


def page_mot_de_passe_oublie():
    """Page de réinitialisation du mot de passe."""
    st.header("❓ Mot de passe oublié")
    st.write("Veuillez saisir votre nom d'utilisateur et un nouveau mot de passe.")
    username = st.text_input("Nom d'utilisateur")
    new_password = st.text_input("Nouveau mot de passe", type="password")
    new_password_confirm = st.text_input(
        "Confirmer le nouveau mot de passe", type="password"
    )
    if st.button("Réinitialiser le mot de passe"):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user_exists = cursor.fetchone()
        conn.close()

        if user_exists:
            if new_password == new_password_confirm:
                if new_password:
                    # Correction: Appel à la fonction update_password
                    update_password(username, new_password)
                    st.success("Votre mot de passe a été réinitialisé avec succès.")
                    st.session_state["page"] = "login"
                    st.rerun()
                else:
                    st.warning("Veuillez saisir un nouveau mot de passe.")
            else:
                st.error("Les mots de passe ne correspondent pas.")
        else:
            st.error("Nom d'utilisateur introuvable.")


# --- Fonctions pour les pages de contenu ---


def page_accueil():
    """
    Displays the home page with an introduction to the midwifery data tool.
    Corrected for improved readability and to fix typos.
    """
    st.header("🏡 Welcome to the Midwifery Services Data Collection Tool!")
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
    conn = get_db_connection()
    # Correction: La création des tables est gérée par init_all_dbs() au début de l'application.
    # Ce bloc est redondant et a été commenté pour éviter une incohérence logique.
    # Ajout d'une table 'donnees' pour que la section de métriques fonctionne
    # cursor = conn.cursor()
    # cursor.execute(
    #     """
    #     CREATE TABLE IF NOT EXISTS donnees (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         date TEXT,
    #         sommeil REAL,
    #         humeur INTEGER,
    #         sport INTEGER,
    #         alimentation INTEGER,
    #         note_sante INTEGER
    #     )
    # """
    # )
    # conn.commit()
    # Fin de la correction
    df_donnees = pd.read_sql_query("SELECT * FROM donnees", conn)
    df_bebe = pd.read_sql_query("SELECT * FROM bebe", conn)
    df_nutrition = pd.read_sql_query("SELECT * FROM nutrition", conn)
    conn.close()

    st.subheader("Aperçu rapide")
    col1, col2, col3 = st.columns(3)
    col1.metric("Entrées de santé", len(df_donnees))
    col2.metric("Entrées de suivi bébé", len(df_bebe))
    col3.metric("Entrées de nutrition", len(df_nutrition))


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
):
    """Insère les données de soins prénatals dans la base de données."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO prenatal_care (
            chart_number, date_collection, gpa, edd_date, tobacco_use,
            substance_use, bmi, ce_cle_status, racism, domestic_violence,
            housing, pregnancy_loss, previous_c_section, previous_vbac,
            high_risk_pe, gdm, anemia, stbbis, trainee_involved,
            referral_worker, prenatal_consultation, reason1, made_with1,
            reason2, made_with2, reason3, made_with3, notes, telehealth,
            shared_care, transfer_care, other_transfer_reason, transfer_to,
            care_ended
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
    """,
        (
            chart_number,
            date_collection.isoformat() if date_collection else None,
            gpa,
            edd_date.isoformat() if edd_date else None,
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
        ),
    )
    conn.commit()
    conn.close()


def navigation_buttons():
    # Correction: L'état de session 'current_page' doit être initialisé
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Accueil"

    page_names = list(PAGES.keys())
    current_index = page_names.index(st.session_state.current_page)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Précédent", disabled=(current_index == 0)):
            st.session_state.current_page = page_names[current_index - 1]
            st.rerun()
    with col2:
        if st.button("Suivant ➡️", disabled=(current_index == len(page_names) - 1)):
            st.session_state.current_page = page_names[current_index + 1]
            st.rerun()


def page_demographics():
    st.title("👥 Données Démographiques")
    st.markdown("---")

    # Correction: La fonction init_demographics_table() n'existe pas
    # La table est déjà créée par init_all_dbs() au début.
    # Cette ligne a été supprimée pour éviter une erreur.

    # Définition des options pour les menus déroulants basés sur le CSV
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
    status_options = [
        "Indigenous; Cree",
        "Indigenous; non-Cree",
        "Non-Indigenous",
        "",  # Vide pour les entrées sans valeur
    ]
    referred_by_options = [
        "Self-referral",
        "Midwife trainee",
        "Birth assistant",
        "PCCR",
        "Nurse",
        "Doctor",
        "Midwife",
        "Other",
        "",
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
        "",
    ]
    contact_options = ["Yes", "No", "Never reached", "N/A", ""]
    eligible_options = ["Yes", "No", "N/A", ""]
    weeks_options = [
        "<12 weeks",
        "12 to 20 weeks",
        ">20 weeks",
        "Postpartum",
        "Non-pregnant",
        "Never seen",
        "N/A",
        "",
    ]
    never_seen_options = [
        "Early pregnancy loss",
        "Termination of pregnancy",
        "Never came to appointments",
        "Declines Midwifery care",
        "Moved elsewhere",
        "Unknown",
        "N/A",
        "",
    ]

    with st.form(key="demographics_form", clear_on_submit=True):
        st.subheader("Entrée de nouvelles données démographiques")

        chart_number = st.text_input("Numéro de dossier")
        dob = st.date_input("Date de naissance du client (DOB) YYYY-MM-DD", value=None)
        date_of_referral = st.date_input("Date de référence YYYY-MM-DD", value=None)
        age = st.text_input("Âge (YY)")

        # Menus déroulants basés sur les options prédéfinies du CSV
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
            dob_str = dob.isoformat() if dob else None
            date_of_referral_str = (
                date_of_referral.isoformat() if date_of_referral else None
            )

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
            st.success("Données démographiques enregistrées avec succès!")

    st.markdown("---")
    st.subheader("Historique des données démographiques")
    df_demographics = get_demographics_data()
    if not df_demographics.empty:
        st.dataframe(df_demographics)
    else:
        st.info("Aucune donnée démographique n'a encore été enregistrée.")


# Liste des options pour les menus déroulants.
# Les options sont basées sur le contenu du fichier "prenatal care.xlsx - Sheet1.csv"
# Ces listes peuvent être ajustées si d'autres options sont nécessaires.
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


def page_prenatal_care():
    """
    Crée une application Streamlit pour la saisie des données de soins prénatals.
    """
    st.title("Formulaire de Soins Prénatals")
    st.write("Veuillez saisir les informations de la patiente.")

    # Utilisation de st.form pour regrouper tous les widgets
    with st.form("prenatal_care_form"):
        st.subheader("Informations de base")
        st.info("Les champs de texte libre ne sont pas des menus déroulants.")

        # Première ligne d'informations
        col1, col2, col3 = st.columns(3)
        with col1:
            chart_number = st.text_input("Numéro de dossier")
        with col2:
            date_collection = st.date_input("Date de la collecte")
        with col3:
            gpa = st.text_input("GPA (texte libre)")

        # Deuxième ligne d'informations
        col4, col5, col6, col7 = st.columns(4)
        with col4:
            edd_date = st.date_input("Date prévue d'accouchement (EDD)")
        with col5:
            tobacco_use = st.selectbox("Consommation de tabac", options_tabac)
        with col6:
            substance_use = st.selectbox(
                "Consommation de substances pendant la grossesse", options_oui_non
            )
        with col7:
            bmi = st.number_input("IMC", min_value=0.0, step=0.1)

        # Troisième ligne d'informations - Expériences et risques
        st.subheader("Antécédents et Risques")
        col8, col9, col10 = st.columns(3)
        with col8:
            ce_cle_status = st.selectbox("Statut CE CLE", options_ce_cle)
        with col9:
            racism = st.selectbox(
                "Expérience de racisme dans les soins de santé", options_oui_non
            )
        with col10:
            domestic_violence = st.selectbox("Violence domestique", options_oui_non)

        col11, col12, col13 = st.columns(3)
        with col11:
            housing = st.selectbox("Défis de logement", options_oui_non)
        with col12:
            pregnancy_loss = st.selectbox("Perte de grossesse", options_oui_non)
        with col13:
            previous_c_section = st.selectbox("Césarienne antérieure", options_oui_non)

        col14, col15, col16, col17 = st.columns(4)
        with col14:
            previous_vbac = st.selectbox(
                "Accouchement vaginal après césarienne (VBAC) antérieur",
                options_oui_non,
            )
        with col15:
            high_risk_pe = st.selectbox(
                "Risque élevé de pré-éclampsie", options_oui_non
            )
        with col16:
            gdm = st.selectbox("Diabète gestationnel (GDM)", options_oui_non)
        with col17:
            anemia = st.selectbox("Anémie en grossesse", options_oui_non)

        stbbis = st.selectbox("IST en grossesse", options_oui_non)

        # Quatrième ligne d'informations - Consultations
        st.subheader("Consultations et Références")
        col18, col19 = st.columns(2)
        with col18:
            trainee_involved = st.selectbox(
                "Stagiaire impliqué dans les soins prénatals", options_oui_non
            )
        with col19:
            referral_worker = st.selectbox(
                "Référence à un autre professionnel de la santé", options_oui_non
            )

        st.markdown("---")
        st.write("Détails des consultations prénatales")
        col20, col21, col22 = st.columns(3)
        with col20:
            prenatal_consultation = st.selectbox(
                "Consultation médicale prénatale ?", options_oui_non
            )
        with col21:
            reason1 = st.selectbox(
                "Raison de la consultation 1", options_consultation_raison
            )
        with col22:
            made_with1 = st.selectbox(
                "Consultation 1 faite avec", options_consultation_professionnel
            )

        col23, col24, col25 = st.columns(3)
        with col23:
            reason2 = st.selectbox(
                "Raison de la consultation 2", options_consultation_raison
            )
        with col24:
            made_with2 = st.selectbox(
                "Consultation 2 faite avec", options_consultation_professionnel
            )
        with col25:
            reason3 = st.selectbox(
                "Raison de la consultation 3", options_consultation_raison
            )

        made_with3 = st.selectbox(
            "Consultation 3 faite avec", options_consultation_professionnel
        )

        # Zone de texte libre pour les notes
        notes = st.text_area("Notes, explications (texte libre)")

        # Cinquième ligne d'informations - Soins
        st.subheader("Suivi des Soins")
        col26, col27, col28 = st.columns(3)
        with col26:
            telehealth = st.selectbox(
                "Télésanté pendant la grossesse ?", options_oui_non
            )
        with col27:
            shared_care = st.selectbox("Soins partagés ?", options_oui_non)
        with col28:
            transfer_care = st.selectbox(
                "Transfert de soins prénatals ?", options_oui_non
            )

        other_transfer_reason = st.text_area(
            "Autre raison pour le transfert des soins prénatals (texte libre)"
        )

        col29, col30 = st.columns(2)
        with col29:
            transfer_to = st.selectbox(
                "Transfert des soins prénatals vers", options_transfert_soins
            )
        with col30:
            care_ended = st.selectbox(
                "Fin des soins de sage-femme pendant la grossesse", options_fin_soins
            )

        # Bouton pour soumettre le formulaire
        submitted = st.form_submit_button("Soumettre")

    if submitted:
        # Correction: Appel à la nouvelle fonction pour insérer les données
        # Le formulaire n'enregistrait pas les données dans la base de données.
        insert_prenatal_care_data(
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
        )
        st.success("Formulaire soumis et enregistré avec succès!")
        st.write("Données soumises :")
        data = {
            "Numéro de dossier": chart_number,
            "Date de la collecte": date_collection,
            "GPA": gpa,
            "Date EDD": edd_date,
            "Consommation de tabac": tobacco_use,
            "Consommation de substances": substance_use,
            "IMC": bmi,
            "Statut CE CLE": ce_cle_status,
            "Expérience de racisme": racism,
            "Violence domestique": domestic_violence,
            "Défis de logement": housing,
            "Perte de grossesse": pregnancy_loss,
            "Césarienne antérieure": previous_c_section,
            "VBAC antérieur": previous_vbac,
            "Risque élevé PE": high_risk_pe,
            "GDM": gdm,
            "Anémie": anemia,
            "IST": stbbis,
            "Stagiaire impliqué": trainee_involved,
            "Référence à un autre pro": referral_worker,
            "Consultation prénatale": prenatal_consultation,
            "Raison consult 1": reason1,
            "Avec consult 1": made_with1,
            "Raison consult 2": reason2,
            "Avec consult 2": made_with2,
            "Raison consult 3": reason3,
            "Avec consult 3": made_with3,
            "Notes": notes,
            "Télésanté": telehealth,
            "Soins partagés": shared_care,
            "Transfert de soins": transfer_care,
            "Autre raison transfert": other_transfer_reason,
            "Transfert à": transfer_to,
            "Fin des soins": care_ended,
        }
        st.json(data)


def page_rendez_vous():
    st.title("📅 Rendez-vous médicaux")
    conn = get_db_connection()
    cursor = conn.cursor()
    df = pd.read_sql_query(
        "SELECT date, medecin, raison FROM rendez_vous ORDER BY date DESC", conn
    )
    st.subheader("Historique")
    st.dataframe(df)

    st.subheader("➕ Nouveau rendez-vous")
    with st.form("form_rendez_vous"):
        date = st.date_input("Date", value=datetime.today())
        medecin = st.text_input("Nom du médecin")
        raison = st.text_input("Raison du rendez-vous")
        submitted = st.form_submit_button("Enregistrer rendez-vous")
        if submitted:
            cursor.execute(
                "INSERT INTO rendez_vous (date, medecin, raison) VALUES (?, ?, ?)",
                (str(date), medecin, raison),
            )
            conn.commit()
            st.success("Rendez-vous enregistré avec succès !")
    conn.close()


# --- Page de rapports et d'exportations ---
def page_rapports_exportations():
    st.title("📈 Rapports et Exportations")
    conn = get_db_connection()

    menu_tables = {
        "Données de santé": "donnees",
        "Données démographiques": "demographics",
        "Rendez-vous médicaux": "rendez_vous",
        "Données de suivi du bébé": "bebe",  # Ajout pour la clarté
        "Données de nutrition": "nutrition",  # Ajout pour la clarté
        "Soins prénatals": "prenatal_care",  # Ajout pour la clarté
    }
    selected_table_name = st.selectbox(
        "Sélectionnez la table à analyser", list(menu_tables.keys())
    )
    table_name = menu_tables[selected_table_name]

    try:
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    except pd.io.sql.DatabaseError:
        st.error(
            f"Erreur lors du chargement de la table {table_name}. Assurez-vous qu'elle existe."
        )
        return
    finally:
        conn.close()

    if df.empty:
        st.info(f"Aucune donnée disponible dans la table '{table_name}'.")
        return

    st.subheader(f"Statistiques et Métriques pour '{selected_table_name}'")
    st.write(df.describe(include="all"))

    st.subheader(f"Visualisation des données pour '{selected_table_name}'")

    numerical_columns = df.select_dtypes(include=["number"]).columns.tolist()

    # Correction: Condition pour vérifier si la colonne 'date' existe avant de tracer le graphique
    if "date" in df.columns and numerical_columns:
        st.write("---")
        st.markdown("##### Visualisation des données numériques")
        df["date"] = pd.to_datetime(df["date"])
        for col in numerical_columns:
            fig = px.line(df, x="date", y=col, title=f"Évolution de {col}")
            st.plotly_chart(fig)
    else:
        st.info("Aucune donnée numérique ou colonne de date pour la visualisation.")

    st.subheader("Outils d'Exportation")

    st.write("---")
    st.markdown("##### Exporter en PDF")

    def create_pdf(dataframe, title):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=title, ln=1, align="C")
        pdf.ln(5)

        # Correction: Ajustement de la largeur des colonnes
        col_width = pdf.w / (len(dataframe.columns) + 1)
        row_height = 10
        for col in dataframe.columns:
            pdf.cell(col_width, row_height, str(col), border=1)
        pdf.ln(row_height)

        for row in dataframe.itertuples(index=False):
            for item in row:
                pdf.cell(col_width, row_height, str(item), border=1)
            pdf.ln(row_height)

        # Correction: Le résultat doit être un objet BytesIO pour le téléchargement
        output_buffer = io.BytesIO(pdf.output(dest="S").encode("latin-1"))
        return output_buffer

    # Correction: l'argument data doit être un objet BytesIO
    pdf_buffer = create_pdf(df, f"Rapport de données pour {selected_table_name}")
    st.download_button(
        label="Télécharger en PDF",
        data=pdf_buffer,
        file_name=f"{table_name}_rapport.pdf",
        mime="application/pdf",
    )

    st.write("---")
    st.markdown("##### Exporter en CSV")
    csv_file = df.to_csv(index=False)
    st.download_button(
        label="Télécharger en CSV",
        data=csv_file,
        file_name=f"{table_name}_rapport.csv",
        mime="text/csv",
    )

    st.write("---")
    st.markdown("##### Exporter en Excel (XLS)")
    buffer = io.BytesIO()
    # Correction: Le nom du moteur pour le format .xlsx doit être 'openpyxl'
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=table_name)
    st.download_button(
        label="Télécharger en Excel (XLS)",
        data=buffer,
        file_name=f"{table_name}_rapport.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


def main():
    """Fonction principale pour exécuter l'application Streamlit."""
    init_all_dbs()
    check_for_initial_user()
    st.set_page_config(layout="wide")

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.session_state["professional_title"] = ""
        st.session_state["login_time"] = None
        st.session_state["logout_time"] = None
        st.session_state["page"] = "login"

    st.sidebar.title("🤰 Midwifery Data Tool")

    if st.session_state["logged_in"]:
        st.sidebar.success(
            f"Connecté(e) en tant que: **{st.session_state['professional_title']}** {st.session_state['username']}"
        )
        st.sidebar.info(
            f"Heure de connexion: {st.session_state['login_time'].strftime('%H:%M:%S')}"
        )
        if st.session_state["logout_time"]:
            st.sidebar.info(
                f"Dernière déconnexion: {st.session_state['logout_time'].strftime('%H:%M:%S')}"
            )

        if st.sidebar.button("Déconnexion"):
            st.session_state["logged_in"] = False
            st.session_state["username"] = ""
            st.session_state["professional_title"] = ""
            st.session_state["logout_time"] = datetime.now()
            st.rerun()

        st.sidebar.subheader("Navigation")
        pages = {
            "Accueil": page_accueil,
            "Données Démographiques": page_demographics,
            "Soins Prénatals": page_prenatal_care,
            "Rendez-vous médicaux": page_rendez_vous,
            "Rapports et Exportations": page_rapports_exportations,
            # Vous pouvez ajouter d'autres pages ici, par exemple pour le suivi du bébé.
        }
        selection = st.sidebar.radio("Aller à", list(pages.keys()))
        pages[selection]()

    else:
        # Gère la navigation avant la connexion
        if st.session_state.get("page") == "inscription":
            page_inscription()
            if st.button("Retour à la connexion", key="back_to_login"):
                st.session_state["page"] = "login"
                st.rerun()
        elif st.session_state.get("page") == "mot_de_passe_oublie":
            page_mot_de_passe_oublie()
            if st.button("Retour à la connexion", key="back_to_login_from_forgot"):
                st.session_state["page"] = "login"
                st.rerun()
        else:
            # Page de connexion
            st.session_state["page"] = "login"
            st.header("Connexion")
            username_input = st.text_input("Nom d'utilisateur")
            password_input = st.text_input("Mot de passe", type="password")

            login_button = st.button("Se connecter")
            if login_button:
                is_valid, professional_title = check_user(
                    username_input, password_input
                )
                if is_valid:
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = username_input
                    st.session_state["professional_title"] = professional_title
                    st.session_state["login_time"] = datetime.now()
                    st.success(
                        f"Connexion réussie! Bienvenue, {professional_title} {username_input}."
                    )
                    st.rerun()
                else:
                    st.error("Nom d'utilisateur ou mot de passe incorrect.")

            if st.button("S'inscrire", key="to_register"):
                st.session_state["page"] = "inscription"
                st.rerun()

            if st.button("Mot de passe oublié", key="to_forgot_password"):
                st.session_state["page"] = "mot_de_passe_oublie"
                st.rerun()


if __name__ == "__main__":
    main()


# === Ajout : Navigation par étapes ===

# --- Navigation par étapes avec Précédent / Suivant ---
if 'step_index' not in st.session_state:
    st.session_state.step_index = 0

step_pages = pages [page_demographics, page_prenatal_care, page_rendez_vous, age_rapports_exportations]

st.markdown(f"### Étape {st.session_state.step_index + 1} : {step_pages[st.session_state.step_index]['titre']}")

step_pages[st.session_state.step_index]['func']()

col1, col2, col3 = st.columns([1, 4, 1])
with col1:
    if st.session_state.step_index > 0:
        if st.button("⬅️ Précédent", key="prev"):
            st.session_state.step_index -= 1
            st.rerun()
with col3:
    if st.session_state.step_index < len(step_pages) - 1:
        if st.button("➡️ Suivant", key="next"):
            st.session_state.step_index += 1
            st.rerun()


# Définition du dictionnaire de pages pour résoudre l'erreur 'NameError'
    pages = {
            "Accueil": page_accueil,
            "Données Démographiques": page_demographics,
            "Soins Prénatals": page_prenatal_care,
            "Rendez-vous médicaux": page_rendez_vous,
            "Rapports et Exportations": page_rapports_exportations,
            # Vous pouvez ajouter d'autres pages ici, par exemple pour le suivi du bébé.
    }

    if "page" not in st.session_state:
        st.session_state["page"] = "login"

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if st.session_state["logged_in"]:
        with st.sidebar:
            st.title("Navigation")
            if st.session_state["page"] != "accueil":
                st.button("Tableau de bord", on_click=lambda: st.session_state.update({"page": "accueil"}))
            if st.session_state.get("professional_title") == "Patient":
                st.button("Données Démographiques", on_click=lambda: st.session_state.update({"page": "page_demographics"}))
                st.button("Soins Prénatals", on_click=lambda: st.session_state.update({"page": "page_prenatal_care"}))
                st.button("Rendez-vous médicaux", on_click=lambda: st.session_state.update({"page": "page_rendez_vous"}))
                st.button("Rapports et Exportations", on_click=lambda: st.session_state.update({"page": "page_rapports_exportations"}))
            st.button("Déconnexion", on_click=lambda: st.session_state.update({"logged_in": False, "page": "login", "user_id": None}))
            st.write(f"Connecté en tant que: {st.session_state.get('username')}")
            st.write(f"Dernière connexion: {st.session_state.get('login_time')}")

        # La navigation utilise le dictionnaire 'pages'
        current_page_func = pages.get(st.session_state["page"])
        if current_page_func:
            current_page_func()
        else:
            st.error("Page introuvable.")

    else:
        # La navigation pour les pages non connectées utilise aussi le dictionnaire 'pages'
        current_page_func = pages.get(st.session_state["page"])
        if current_page_func:
            current_page_func()
        else:
            st.error("Page introuvable.")





