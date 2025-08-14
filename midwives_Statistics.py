# -*- coding: utf-8 -*-
import streamlit as st
import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np
from datetime import datetime
from fpdf import FPDF
import bcrypt
import io
from utils import load_data, filter_data

# ------------------ CONFIG ------------------
st.set_page_config(page_title="Sage-Femme | Collecte", layout="wide")
st.set_page_config(
    page_title="Sage-Femme | Collecte",
    page_icon="🧑‍⚕️",
    layout="wide",
    initial_sidebar_state="expanded",
)

with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Midwife_icon.svg/1200px-Midwife_icon.svg.png",
        width=100,
    )
    st.title("🧑‍⚕️ Sage-Femme")
    st.markdown("**Bienvenue dans l'outil de collecte de données.**")
    if st.session_state.user:
        st.success(f"Connectée : {st.session_state.user}")


# --- SIDEBAR ---
st.sidebar.title("🔍 Filtres")
region = st.sidebar.selectbox("Choisir une région", ["Toutes", "Nord", "Sud", "Est", "Ouest"])
date_range = st.sidebar.date_input("Plage de dates", [])
service = st.sidebar.multiselect("Services", ["Accouchement", "Consultation", "Vaccination"])

# --- PAGE D'ACCUEIL ---
st.title("👩‍⚕️ Tableau de bord des services de sages-femmes")
st.markdown("""
Bienvenue sur la plateforme d’analyse des services de sages-femmes.  
Utilisez les filtres à gauche pour explorer les données par région, date ou type de service.
""")

# --- CHARGEMENT ET FILTRAGE DES DONNÉES ---
df = load_data("data/services.csv")
filtered_df = filter_data(df, region, date_range, service)

st.dataframe(filtered_df)

# ------------------ DATABASE ------------------
conn = sqlite3.connect("midwifery.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password BLOB
)
"""
)

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    service TEXT,
    pole TEXT,
    date TEXT
)
"""
)
conn.commit()


# ------------------ AUTH ------------------
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)


def register_user(username, password):
    hashed = hash_password(password)
    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def authenticate(username, password):
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    if result and check_password(password, result[0]):
        return True
    return False


# ------------------ PDF EXPORT ------------------
def generate_pdf(data_dict):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Rapport Sage-Femme", ln=True, align="C")
    for key, value in data_dict.items():
        pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)
    return pdf.output(dest="S").encode("latin-1")


# ------------------ SESSION ------------------
if "page" not in st.session_state:
    st.session_state.page = "login"
if "user" not in st.session_state:
    st.session_state.user = None


def go_to(page):
    st.session_state.page = page


# ------------------ PAGES ------------------
def login_page():
    st.title("🔐 Connexion")
    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        if authenticate(username, password):
            st.session_state.user = username
            go_to("form")
        else:
            st.error("Identifiants incorrects")

    st.markdown("---")
    st.subheader("📝 Inscription")
    new_user = st.text_input("Nouvel utilisateur")
    new_pass = st.text_input("Mot de passe", type="password", key="new_pass")
    if st.button("Créer un compte"):
        if register_user(new_user, new_pass):
            st.success("Compte créé. Vous pouvez vous connecter.")
        else:
            st.error("Ce nom d'utilisateur existe déjà.")


def form_page():
    st.title("🧑‍⚕️ Formulaire de collecte")
    name = st.text_input("Nom de la patiente")
    age = st.number_input("Âge", min_value=0, max_value=120)
    service = st.selectbox(
        "Type de service", ["Consultation", "Accouchement", "Suivi postnatal"]
    )
    pole = st.selectbox("Pôle", ["Pôle 1", "Pôle 2"])
    date_entry = st.date_input("Date", value=datetime.today())

    if st.button("Enregistrer"):
        cursor.execute(
            "INSERT INTO patients (name, age, service, pole, date) VALUES (?, ?, ?, ?, ?)",
            (name, age, service, pole, date_entry.strftime("%Y-%m-%d")),
        )
        conn.commit()
        st.success("Données enregistrées.")

    st.markdown("---")
    st.subheader("📄 Export PDF")
    if st.button("Télécharger le rapport PDF"):
        data = {
            "Nom": name,
            "Âge": age,
            "Service": service,
            "Pôle": pole,
            "Date": date_entry,
        }
        pdf_bytes = generate_pdf(data)
        st.download_button("Télécharger", data=pdf_bytes, file_name="rapport.pdf")

    st.markdown("---")
    st.subheader("📊 Statistiques avancées")


df = pd.read_sql_query("SELECT * FROM patients", conn)

if not df.empty:
    st.markdown("### 📌 Statistiques descriptives")
    stats = df.describe().T
    stats["median"] = df.median()
    stats["missing_values"] = df.isnull().sum()
    st.dataframe(stats)

    st.markdown("### 📌 Corrélations")
    corr_matrix = df.corr(numeric_only=True)
    fig_corr, ax = plt.subplots()
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", ax=ax)
    st.pyplot(fig_corr)

    st.markdown("### 📌 Répartition par service et pôle")
    fig1 = px.histogram(df, x="service", color="pole", barmode="group")
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("### 📌 Distribution des âges")
    fig2, ax2 = plt.subplots()
    sns.histplot(df["age"], kde=True, bins=10, ax=ax2)
    st.pyplot(fig2)

    st.markdown("### 📌 Boxplot des âges par service")
    fig3, ax3 = plt.subplots()
    sns.boxplot(x="service", y="age", data=df, ax=ax3)
    st.pyplot(fig3)

    st.markdown("### 📌 Nuage de points âge vs pôle")
    fig4 = px.scatter(df, x="age", y="pole", color="service", title="Âge vs Pôle")
    st.plotly_chart(fig4, use_container_width=True)
else:
    st.info("Aucune donnée disponible pour les statistiques.")

st.markdown("### 📤 Export des données")

csv = df.to_csv(index=False).encode("utf-8")
excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
    df.to_excel(writer, index=False, sheet_name="Données")
    writer.save()

st.download_button(
    "📄 Télécharger CSV", data=csv, file_name="donnees.csv", mime="text/csv"
)
st.download_button(
    "📊 Télécharger Excel",
    data=excel_buffer.getvalue(),
    file_name="donnees.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

st.markdown("### 📊 Tableau de bord interactif")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Nombre total de patientes", len(df))
with col2:
    st.metric("Âge moyen", round(df["age"].mean(), 1))
with col3:
    st.metric("Services uniques", df["service"].nunique())

st.markdown("### 📅 Évolution temporelle")
df["date"] = pd.to_datetime(df["date"])
df_time = df.groupby(df["date"].dt.to_period("M")).size().reset_index(name="Nombre")
df_time["date"] = df_time["date"].astype(str)
fig_time = px.line(df_time, x="date", y="Nombre", markers=True)
st.plotly_chart(fig_time, use_container_width=True)
# ------------------ ROUTER ------------------
if st.session_state.page == "login":
    login_page()
elif st.session_state.page == "form":
    if st.session_state.user:
        form_page()
    else:
        go_to("login")
