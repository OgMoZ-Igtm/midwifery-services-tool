import streamlit as st
import os
import pandas as pd

st.set_page_config(page_title="📚 Pages par Thème", page_icon="📚")
st.title("📚 Navigation par Thème")

# 📁 Dossier contenant les pages
PAGES_DIR = "pages"


# 🔍 Fonction pour détecter le thème
def detect_theme(name):
    name_lower = name.lower()
    if "user" in name_lower:
        return "👤 Utilisateurs"
    elif "message" in name_lower or "chat" in name_lower:
        return "💬 Messagerie"
    elif "password" in name_lower or "reset" in name_lower:
        return "🔐 Sécurité"
    elif "report" in name_lower:
        return "📄 Rapports"
    elif "dashboard" in name_lower:
        return "📊 Tableau de bord"
    elif "midwifery" in name_lower:
        return "🧑‍⚕️ Santé"
    else:
        return "📁 Autres"


# 🎨 Fonction pour formater le titre
def format_title(filename):
    name = filename.replace(".py", "").replace("_", " ").replace("-", " ")
    return name.strip().title()


# 🔗 Créer le lien vers la page
def create_link(filename):
    page_name = filename.replace(".py", "")
    return f"[Ouvrir]({page_name})"


# 📦 Construire le tableau
try:
    files = [f for f in os.listdir(PAGES_DIR) if f.endswith(".py")]
    data = []
    for file in sorted(files):
        title = format_title(file)
        theme = detect_theme(file)
        link = create_link(file)
        data.append(
            {"📄 Titre": title, "🔗 Lien": link, "🗂️ Thème": theme, "📁 Fichier": file}
        )

    df = pd.DataFrame(data)
    df_sorted = df.sort_values(by="🗂️ Thème")

    st.data_editor(
        df_sorted,
        column_config={
            "🔗 Lien": st.column_config.LinkColumn("🔗 Lien"),
        },
        hide_index=True,
        use_container_width=True,
    )

except FileNotFoundError:
    st.error("Le dossier `pages/` n'existe pas. Vérifie la structure de ton projet.")

# 🧑‍⚕️ Pages liées à la santé maternelle
midwifery_pages = [
    "Demographics.py",
    "Prenatal Care.py",
    "Intrapartum Care.py",
    "Throughout_midwifery_care_conflict1.py",
]

midwifery_data = []
for file in midwifery_pages:
    if os.path.exists(os.path.join(PAGES_DIR, file)):
        title = format_title(file)
        link = create_link(file)
        if "Demographics" in file:
            care_type = "📊 Démographie"
        elif "Prenatal" in file:
            care_type = "🤰 Soins prénataux"
        elif "Intrapartum" in file:
            care_type = "🩺 Soins intrapartum"
        else:
            care_type = "🧑‍⚕️ Suivi global"

        midwifery_data.append(
            {
                "📄 Titre": title,
                "🔗 Lien": link,
                "🩺 Type de soin": care_type,
                "📁 Fichier": file,
            }
        )

if midwifery_data:
    st.subheader("🧑‍⚕️ Pages Santé Maternelle")
    df_midwifery = pd.DataFrame(midwifery_data)
    st.data_editor(
        df_midwifery,
        column_config={
            "🔗 Lien": st.column_config.LinkColumn("🔗 Lien"),
        },
        hide_index=True,
        use_container_width=True,
    )
else:
    st.info("Aucune page liée à la santé maternelle n’a été trouvée.")
