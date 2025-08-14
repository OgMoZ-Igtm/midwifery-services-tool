import streamlit as st
from utils.database import get_patient_dossier
from fpdf import FPDF
from ics import Calendar, Event
import tempfile
from datetime import datetime, timedelta
import pandas as pd
from utils.auth import require_login, show_auth_sidebar
from utils.database import get_all_patients, save_patients
import io


# 🔐 Contrôle d'accès
if st.session_state.get("role") not in ["admin", "doctor", "nurse", "sage-femme"]:
    st.warning("⛔ Accès restreint aux professionnels autorisés.")
    st.stop()


def generate_pdf(dossier, patient_id):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(
        200, 10, txt=f"Dossier médical du patient #{patient_id}", ln=True, align="C"
    )

    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="📋 Informations démographiques", ln=True)
    pdf.set_font("Arial", size=10)
    for key, value in dossier["demographics"].items():
        pdf.cell(200, 8, txt=f"{key}: {value}", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="🤰 Soins prénatals", ln=True)
    pdf.set_font("Arial", size=10)
    for item in dossier["prenatal"]:
        pdf.cell(200, 8, txt=str(item), ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="📅 Rendez-vous", ln=True)
    pdf.set_font("Arial", size=10)
    for rdv in dossier["rdv"]:
        pdf.cell(200, 8, txt=str(rdv), ln=True)

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_file.name)
    return temp_file.name


def generate_ics(rdv_list):
    calendar = Calendar()
    for rdv in rdv_list:
        event = Event()
        event.name = rdv.get("motif", "Consultation")
        date_str = rdv.get("date", "")
        time_str = rdv.get("heure", "00:00")
        try:
            dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            event.begin = dt
            event.duration = timedelta(minutes=30)
            event.description = f"Patient: {rdv.get('nom', 'Inconnu')}"
            calendar.events.add(event)
        except Exception:
            continue

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".ics")
    with open(temp_file.name, "w") as f:
        f.writelines(calendar)
    return temp_file.name


def render_printable_view(dossier):
    st.markdown("### 🖨️ Vue imprimable")
    html_content = f"""
    <div>
        <h3>Informations démographiques</h3>
        <pre>{dossier['demographics']}</pre>
        <h3>Soins prénatals</h3>
        <pre>{dossier['prenatal']}</pre>
        <h3>Rendez-vous</h3>
        <pre>{dossier['rdv']}</pre>
        <button onclick="window.print()">🖨️ Imprimer cette page</button>
    </div>
    """
    st.components.v1.html(html_content, height=600)


def page_dossier_patient():
    st.set_page_config(page_title="Dossier patient", page_icon="🧾")
    st.title("🧾 Dossier médical du patient")

    patient_id = st.text_input("🔍 Numéro de dossier du patient")

    if patient_id:
        dossier = get_patient_dossier(patient_id)
        if dossier:
            st.subheader("📋 Informations démographiques")
            if dossier["demographics"]:
                st.json(dossier["demographics"])
            else:
                st.info("Aucune donnée démographique disponible.")

            st.subheader("🤰 Soins prénatals")
            if dossier["prenatal"]:
                st.dataframe(dossier["prenatal"], use_container_width=True)
            else:
                st.info("Aucun soin prénatal enregistré.")

            st.subheader("📅 Rendez-vous")
            if dossier["rdv"]:
                st.dataframe(dossier["rdv"], use_container_width=True)
            else:
                st.info("Aucun rendez-vous enregistré.")

            # 📄 Export PDF
            if st.button("📄 Exporter en PDF"):
                pdf_path = generate_pdf(dossier, patient_id)
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="📥 Télécharger le PDF",
                        data=f,
                        file_name=f"dossier_patient_{patient_id}.pdf",
                        mime="application/pdf",
                    )

            # 📅 Export ICS
            if dossier["rdv"] and st.button("📅 Exporter les rendez-vous en ICS"):
                ics_path = generate_ics(dossier["rdv"])
                with open(ics_path, "rb") as f:
                    st.download_button(
                        label="📥 Télécharger le fichier ICS",
                        data=f,
                        file_name="rendezvous.ics",
                        mime="text/calendar",
                    )

            # 🖨️ Vue imprimable
            render_printable_view(dossier)
        else:
            st.warning("❌ Aucun dossier trouvé pour ce numéro.")
    else:
        st.info("Veuillez entrer un numéro de dossier pour consulter les données.")


# 🔐 Authentification
require_login()
show_auth_sidebar()

# 📋 Chargement des données
patients = get_all_patients()

st.title("👩‍⚕️ Gestion des patientes")

# 📥 Ajout d'une nouvelle patiente
with st.expander("➕ Ajouter une nouvelle patiente"):
    nom = st.text_input("Nom")
    prenom = st.text_input("Prénom")
    age = st.number_input("Âge", min_value=0, max_value=120)
    telephone = st.text_input("Téléphone")
    if st.button("Ajouter"):
        new_patient = {"nom": nom, "prenom": prenom, "age": age, "telephone": telephone}
        patients = pd.concat([patients, pd.DataFrame([new_patient])], ignore_index=True)
        save_patients(patients)
        st.success(f"✅ Patiente {prenom} {nom} ajoutée.")
        st.rerun()

# 🧾 Liste des patientes
st.subheader("📄 Liste des patientes")
selected_index = st.selectbox(
    "Sélectionnez une patiente à modifier ou supprimer",
    patients.index,
    format_func=lambda i: f"{patients.loc[i, 'prenom']} {patients.loc[i, 'nom']}",
)

selected_patient = patients.loc[selected_index]

with st.expander("✏️ Modifier la patiente sélectionnée"):
    nom_mod = st.text_input("Nom", value=selected_patient["nom"])
    prenom_mod = st.text_input("Prénom", value=selected_patient["prenom"])
    age_mod = st.number_input(
        "Âge", value=int(selected_patient["age"]), min_value=0, max_value=120
    )
    telephone_mod = st.text_input("Téléphone", value=selected_patient["telephone"])
    if st.button("Enregistrer les modifications"):
        patients.at[selected_index, "nom"] = nom_mod
        patients.at[selected_index, "prenom"] = prenom_mod
        patients.at[selected_index, "age"] = age_mod
        patients.at[selected_index, "telephone"] = telephone_mod
        save_patients(patients)
        st.success("✅ Modifications enregistrées.")
        st.rerun()

# 🗑️ Suppression
with st.expander("🗑️ Supprimer la patiente sélectionnée"):
    if st.button("Supprimer cette patiente"):
        patients = patients.drop(index=selected_index).reset_index(drop=True)
        save_patients(patients)
        st.warning("⚠️ Patiente supprimée.")
        st.rerun()

# 🔍 Recherche et filtre
st.subheader("🔎 Rechercher ou filtrer les patientes")

col1, col2 = st.columns(2)

with col1:
    search_query = st.text_input("Rechercher par nom ou prénom")

with col2:
    age_range = st.slider("Filtrer par âge", min_value=0, max_value=100, value=(0, 100))

# 📊 Filtrage
filtered_patients = patients[patients["age"].between(age_range[0], age_range[1])]

if search_query:
    search_query = search_query.lower()
    filtered_patients = filtered_patients[
        filtered_patients["nom"].str.lower().str.contains(search_query)
        | filtered_patients["prenom"].str.lower().str.contains(search_query)
    ]
# 📊 Affichage des résultats
st.markdown(f"**Résultats : {len(filtered_patients)} patiente(s)**")
st.dataframe(filtered_patients, use_container_width=True)

# 📤 Préparation des fichiers CSV
csv_buffer = io.StringIO()
filtered_patients.to_csv(csv_buffer, index=False)
csv_bytes = csv_buffer.getvalue().encode("utf-8")

csv_all_buffer = io.StringIO()
patients.to_csv(csv_all_buffer, index=False)
csv_all_bytes = csv_all_buffer.getvalue().encode("utf-8")

# 📤 Encadré d'export CSV
with st.expander("📤 Exporter les données en CSV"):
    st.markdown(f"- **Filtrées** : {len(filtered_patients)} patiente(s)")
    st.markdown(f"- **Toutes** : {len(patients)} patiente(s)")

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            label="📥 Télécharger les patientes filtrées",
            data=csv_bytes,
            file_name="patientes_filtrées.csv",
            mime="text/csv",
        )

    with col2:
        st.download_button(
            label="📥 Télécharger toutes les patientes",
            data=csv_all_bytes,
            file_name="toutes_les_patientes.csv",
            mime="text/csv",
        )
