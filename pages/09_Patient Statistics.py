import streamlit as st
import pandas as pd
import plotly.express as px
from utils.database import get_all_patients, get_all_rendez_vous


def page_statistiques_patients():
    st.set_page_config(page_title="Statistiques patients", page_icon="📊")
    st.title("📊 Statistiques des patients")

    # 🔄 Chargement des données
    patients = get_all_patients()
    rdv = get_all_rendez_vous()

    if not patients:
        st.warning("⚠️ Aucun patient enregistré.")
        return

    df_patients = pd.DataFrame(patients, columns=["Nom", "Âge", "Sexe", "Chart Number"])
    df_rdv = pd.DataFrame(rdv, columns=["Nom", "Date", "Heure", "Motif"])

    # 📈 Répartition par âge
    st.subheader("📈 Répartition des âges")
    fig_age = px.histogram(
        df_patients, x="Âge", nbins=10, title="Distribution des âges"
    )
    st.plotly_chart(fig_age, use_container_width=True)

    # 🚻 Répartition par sexe
    st.subheader("🚻 Répartition par sexe")
    fig_sexe = px.pie(df_patients, names="Sexe", title="Sexe des patients")
    st.plotly_chart(fig_sexe, use_container_width=True)

    # 📅 Nombre de visites par patient
    st.subheader("📅 Nombre de visites par patient")
    if not df_rdv.empty:
        rdv_counts = df_rdv["Nom"].value_counts().reset_index()
        rdv_counts.columns = ["Nom", "Nombre de visites"]
        fig_visites = px.bar(
            rdv_counts, x="Nom", y="Nombre de visites", title="Fréquence des visites"
        )
        st.plotly_chart(fig_visites, use_container_width=True)
    else:
        st.info("Aucun rendez-vous enregistré.")

    # 📌 Statistiques générales
    st.subheader("📌 Statistiques générales")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Nombre total de patients", len(df_patients))
    with col2:
        st.metric("Nombre total de rendez-vous", len(df_rdv))

    # 🔍 Filtrage facultatif
    st.markdown("---")
    st.subheader("🔍 Filtrer les patients")

    age_min, age_max = int(df_patients["Âge"].min()), int(df_patients["Âge"].max())
    age_range = st.slider(
        "Filtrer par âge",
        min_value=age_min,
        max_value=age_max,
        value=(age_min, age_max),
    )
    sexe_filter = st.multiselect(
        "Filtrer par sexe", options=df_patients["Sexe"].unique()
    )

    df_filtered = df_patients[
        (df_patients["Âge"] >= age_range[0]) & (df_patients["Âge"] <= age_range[1])
    ]
    if sexe_filter:
        df_filtered = df_filtered[df_filtered["Sexe"].isin(sexe_filter)]

    st.dataframe(df_filtered, use_container_width=True)
