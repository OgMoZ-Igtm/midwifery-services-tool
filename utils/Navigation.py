import streamlit as st

def go_to_page(page_name: str):
    st.session_state["page"] = page_name
    st.rerun()


PAGES = {
    "Accueil": "page_accueil",
    "Données Démographiques": "page_demographics",
    "Soins Prénatals": "page_prenatal_care",
    "Rendez-vous": "page_rendez_vous",
    "Rapports": "page_rapports",
}


def navigation_buttons():
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

import os

def get_pages_from_directory(directory="pages"):
    page_files = [f for f in os.listdir(directory) if f.startswith("page_") and f.endswith(".py")]
    pages = {}
    for file in sorted(page_files):  # tri pour ordre stable
        # Nom lisible : "page_prenatal_care.py" → "Soins Prenatals"
        name = file.replace("page_", "").replace(".py", "")
        display_name = name.replace("_", " ").title()
        pages[display_name] = file.replace(".py", "")
    return pages

# 📦 Génération dynamique des pages
PAGES = get_pages_from_directory()


def reset_all_forms():
    for key in list(st.session_state.keys()):
        if key not in PAGES and not key.startswith("FormSubmitter:"):
            del st.session_state[key]
