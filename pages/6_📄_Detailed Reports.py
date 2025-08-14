import streamlit as st
from components import show_user_info
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import io
from fpdf import FPDF
import sqlite3

# 🔐 Contrôle d'accès
if st.session_state.get("role") not in ["admin", "doctor", "sage-femme"]:
    st.set_page_config(page_title="📄 Reports", page_icon="📄")
    st.warning("⛔ Accès restreint aux professionnels autorisés.")
    st.stop()

# ✅ Configuration de la page (placée en haut)
st.set_page_config(page_title="Rapports & Statistiques", layout="wide")

# 🔎 Infos utilisateur
show_user_info()

# 📄 Titre principal
st.title("📄 Reports")
st.write(
    "Welcome to the **Reports Page**. This section allows you to generate and view reports."
)

# 🗂️ Onglets
tab1, tab2 = st.tabs(["📊 Generate Report", "📁 View Archive"])

with tab1:
    st.subheader("📊 Generate New Report")
    st.selectbox("Report Type", ["Monthly Summary", "Patient Overview", "Appointments"])
    st.button("Generate")

with tab2:
    st.subheader("📁 Archived Reports")
    st.info("No archived reports yet.")

# 📊 Titre secondaire
st.title("📊 Rapports & Statistiques")

# ------------------ Connexion à la base ------------------
conn = sqlite3.connect("midwifery.db", check_same_thread=False)


# ------------------ PDF EXPORT ------------------
def generate_pdf(data_dict):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Rapport Sage-Femme", ln=True, align="C")
    pdf.ln(10)
    for key, value in data_dict.items():
        pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)
    return pdf.output(dest="S").encode("latin-1")


# 📄 Export PDF
st.subheader("📄 Export PDF")
data = {
    "Nom": "Marie",
    "Âge": 32,
    "Service": "Accouchement",
    "Pôle": "Pôle 1",
    "Date": "2025-08-12",
}
if st.button("📥 Télécharger le rapport PDF"):
    pdf_bytes = generate_pdf(data)
    st.download_button("📄 Télécharger", data=pdf_bytes, file_name="rapport.pdf")

# ------------------ Chargement des données ------------------
df = pd.read_sql_query("SELECT * FROM patients", conn)

if df.empty:
    st.info("Aucune donnée disponible pour les statistiques.")
else:
    # 📌 Statistiques descriptives
    st.markdown("---")
    st.subheader("📌 Statistiques descriptives")
    stats = df.describe().T
    stats["Médiane"] = df.median(numeric_only=True)
    stats["Valeurs manquantes"] = df.isnull().sum()
    st.dataframe(stats)

    # 📌 Corrélations
    st.markdown("### 🔗 Corrélations")
    corr_matrix = df.corr(numeric_only=True)
    fig_corr, ax = plt.subplots()
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", ax=ax)
    st.pyplot(fig_corr)

    # 📊 Répartition par service et pôle
    st.markdown("### 🏥 Répartition par service et pôle")
    fig1 = px.histogram(df, x="service", color="pole", barmode="group")
    st.plotly_chart(fig1, use_container_width=True)

    # 📊 Distribution des âges
    st.markdown("### 🎂 Distribution des âges")
    fig2, ax2 = plt.subplots()
    sns.histplot(df["age"], kde=True, bins=10, ax=ax2)
    st.pyplot(fig2)

    # 📊 Boxplot des âges par service
    st.markdown("### 📦 Boxplot des âges par service")
    fig3, ax3 = plt.subplots()
    sns.boxplot(x="service", y="age", data=df, ax=ax3)
    st.pyplot(fig3)

    # 📊 Nuage de points âge vs pôle
    st.markdown("### ☁️ Nuage de points âge vs pôle")
    fig4 = px.scatter(df, x="age", y="pole", color="service", title="Âge vs Pôle")
    st.plotly_chart(fig4, use_container_width=True)

    # 📤 Export des données
    st.markdown("---")
    st.subheader("📤 Export des données")
    csv = df.to_csv(index=False).encode("utf-8")
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Données")

    st.download_button(
        "📄 Télécharger CSV", data=csv, file_name="donnees.csv", mime="text/csv"
    )
    st.download_button(
        "📊 Télécharger Excel",
        data=excel_buffer.getvalue(),
        file_name="donnees.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    # 📊 Tableau de bord interactif
    st.markdown("---")
    st.subheader("📊 Tableau de bord interactif")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Nombre total de patientes", len(df))
    with col2:
        st.metric("Âge moyen", round(df["age"].mean(), 1))
    with col3:
        st.metric("Services uniques", df["service"].nunique())

    # 📅 Évolution temporelle
    st.markdown("### 📅 Évolution temporelle des consultations")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df_time = (
        df.dropna(subset=["date"])
        .groupby(df["date"].dt.to_period("M"))
        .size()
        .reset_index(name="Nombre")
    )
    df_time["date"] = df_time["date"].astype(str)
    fig_time = px.line(df_time, x="date", y="Nombre", markers=True)
    st.plotly_chart(fig_time, use_container_width=True)

# 🔔 Rappel de rôle
if st.session_state.get("role") == "sage-femme":
    st.info("ℹ️ Vous pouvez consulter les rapports, mais pas les modifier.")
