import streamlit as st
from datetime import date as today_date
import pandas as pd
import plotly.express as px

from utils.navigation import go_to_page
from utils.database import (
    save_rendez_vous,
    delete_rendez_vous,
    get_all_rendez_vous,
    export_rendez_vous_to_excel,
)
from utils.pdf_generator import generate_rdv_pdf

st.set_page_config(page_title="Rendez-vous", layout="wide")

# 🔐 Contrôle d'accès
if st.session_state.get("role") not in ["admin", "doctor", "sage-femme"]:
    st.warning("⛔ Accès restreint aux professionnels autorisés.")
    st.stop()

# 📅 Titre
st.title("📅 Gestion des rendez-vous")

# 🔄 Réinitialisation
if st.button("🔄 Réinitialiser la page"):
    st.rerun()

# 📝 Formulaire de prise de rendez-vous
st.subheader("📌 Nouveau rendez-vous")
with st.form("form_rdv", clear_on_submit=True):
    nom = st.text_input("Nom du patient")
    date = st.date_input("Date du rendez-vous")
    heure = st.time_input("Heure du rendez-vous")
    motif = st.text_area("Motif du rendez-vous")

    submitted = st.form_submit_button("📌 Enregistrer")

    if submitted:
        save_rendez_vous(nom, date, heure, motif)
        pdf_file = generate_rdv_pdf(nom, date, heure, motif)
        st.success(f"✅ Rendez-vous enregistré pour {nom} le {date} à {heure}.")
        with open(pdf_file, "rb") as f:
            st.download_button(
                "📄 Télécharger la confirmation PDF", f, file_name=pdf_file
            )
        st.rerun()

# 🔍 Recherche et filtre
st.markdown("---")
st.subheader("🔎 Rechercher et filtrer les rendez-vous")

search_nom = st.text_input("Nom du patient à rechercher").strip().lower()
selected_date = st.date_input("Filtrer par date")

# 📋 Liste des rendez-vous
rendez_vous_list = get_all_rendez_vous()

filtered_list = [
    rdv
    for rdv in rendez_vous_list
    if search_nom in rdv[0].lower() and str(rdv[1]) == str(selected_date)
]

st.subheader("📋 Rendez-vous filtrés")
if filtered_list:
    for rdv in filtered_list:
        nom, date, heure, motif = rdv
        with st.expander(f"{date} à {heure} — {nom}"):
            st.write(f"**Motif :** {motif}")
            if st.button(
                f"🗑 Supprimer ce rendez-vous", key=f"delete_{nom}_{date}_{heure}"
            ):
                delete_rendez_vous(nom, date, heure)
                st.success("Rendez-vous supprimé.")
                st.rerun()
else:
    st.info("Aucun rendez-vous pour cette date ou ce nom.")

# 🔔 Rappels du jour
st.markdown("---")
st.subheader("🔔 Rappels pour aujourd’hui")

today_rdv = [rdv for rdv in rendez_vous_list if str(rdv[1]) == str(today_date.today())]
if today_rdv:
    for rdv in today_rdv:
        nom, date, heure, motif = rdv
        st.info(f"🕒 {heure} — {nom} : {motif}")
else:
    st.write("Aucun rendez-vous prévu aujourd’hui.")

# 📤 Export Excel
st.markdown("---")
st.subheader("📁 Exporter les rendez-vous")

if st.button("📤 Générer le fichier Excel"):
    excel_path = export_rendez_vous_to_excel()
    with open(excel_path, "rb") as f:
        st.download_button("⬇ Télécharger le fichier Excel", f, file_name=excel_path)

# 📆 Vue calendrier
st.markdown("---")
st.subheader("📆 Vue calendrier des rendez-vous")

if rendez_vous_list:
    df_rdv = pd.DataFrame(rendez_vous_list, columns=["Nom", "Date", "Heure", "Motif"])
    df_rdv["Datetime"] = pd.to_datetime(
        df_rdv["Date"].astype(str) + " " + df_rdv["Heure"].astype(str)
    )

    fig = px.timeline(
        df_rdv,
        x_start="Datetime",
        x_end="Datetime",
        y="Nom",
        color="Nom",
        hover_data=["Motif"],
    )
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Aucun rendez-vous à afficher dans le calendrier.")

# 🧭 Navigation
st.markdown("---")
if st.button("⬅ Retour à l'accueil"):
    go_to_page("01_accueil")
