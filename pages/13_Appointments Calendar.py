import streamlit as st
import pandas as pd
import plotly.express as px
from utils.database import get_all_rendez_vous
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from ics import Calendar, Event
import tempfile
from datetime import datetime, timedelta
import os

# 🔐 Contrôle d'accès
if st.session_state.get("role") not in ["admin", "doctor", "nurse", "sage-femme"]:
    st.warning("⛔ Accès restreint aux professionnels autorisés.")
    st.stop()

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]


def get_google_calendar_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("client_id.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("calendar", "v3", credentials=creds)


def event_exists(service, rdv):
    query = rdv["Motif"]
    date = rdv["Datetime"].isoformat()
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=date,
            timeMax=(rdv["Datetime"] + timedelta(minutes=30)).isoformat(),
            q=query,
            singleEvents=True,
        )
        .execute()
    )
    return len(events_result.get("items", [])) > 0


def auto_sync_rdv(df):
    service = get_google_calendar_service()
    synced = 0
    for _, rdv in df.iterrows():
        if not event_exists(service, rdv):
            event = {
                "summary": rdv["Motif"],
                "description": f"Patient: {rdv['Nom']}",
                "start": {
                    "dateTime": rdv["Datetime"].isoformat(),
                    "timeZone": "America/Toronto",
                },
                "end": {
                    "dateTime": (rdv["Datetime"] + timedelta(minutes=30)).isoformat(),
                    "timeZone": "America/Toronto",
                },
            }
            service.events().insert(calendarId="primary", body=event).execute()
            synced += 1
    return synced


def generate_ics(df):
    calendar = Calendar()
    for _, rdv in df.iterrows():
        event = Event()
        event.name = rdv["Motif"]
        event.begin = rdv["Datetime"]
        event.duration = timedelta(minutes=30)
        event.description = f"Patient: {rdv['Nom']}"
        calendar.events.add(event)

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".ics")
    with open(temp_file.name, "w") as f:
        f.writelines(calendar)
    return temp_file.name


def page_calendrier_rendez_vous():
    st.set_page_config(page_title="Calendrier des rendez-vous", page_icon="📅")
    st.title("📅 Calendrier des rendez-vous")

    rdv_list = get_all_rendez_vous()
    if not rdv_list:
        st.info("📭 Aucun rendez-vous enregistré.")
        return

    df = pd.DataFrame(rdv_list, columns=["Nom", "Date", "Heure", "Motif"])
    df["Datetime"] = pd.to_datetime(
        df["Date"].astype(str) + " " + df["Heure"].astype(str), errors="coerce"
    )
    df = df.dropna(subset=["Datetime"])

    # 🔍 Filtres
    st.subheader("🔍 Filtrer les rendez-vous")
    noms = sorted(df["Nom"].unique())
    selected_nom = st.selectbox("Filtrer par nom", ["Tous"] + noms)
    selected_date = st.date_input("Filtrer par date", value=None)

    df_filtered = df.copy()
    if selected_nom != "Tous":
        df_filtered = df_filtered[df_filtered["Nom"] == selected_nom]
    if selected_date:
        df_filtered = df_filtered[df_filtered["Datetime"].dt.date == selected_date]

    if df_filtered.empty:
        st.info("Aucun rendez-vous correspondant aux filtres.")
        return

    # 📊 Vue calendrier
    fig = px.timeline(
        df_filtered,
        x_start="Datetime",
        x_end="Datetime",
        y="Nom",
        color="Nom",
        hover_data=["Motif"],
        title="Vue calendrier des rendez-vous",
    )
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)

    # 🔄 Synchronisation automatique
    synced_count = auto_sync_rdv(df_filtered)
    st.success(
        f"✅ {synced_count} rendez-vous synchronisés automatiquement avec Google Calendar."
    )

    # 📥 Export ICS
    if st.button("📅 Exporter les rendez-vous en ICS"):
        ics_path = generate_ics(df_filtered)
        with open(ics_path, "rb") as f:
            st.download_button(
                label="📥 Télécharger le fichier ICS",
                data=f,
                file_name="rendezvous.ics",
                mime="text/calendar",
            )
