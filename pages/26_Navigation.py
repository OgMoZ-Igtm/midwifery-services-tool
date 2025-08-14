import streamlit as st

st.set_page_config(page_title="🧭 Navigation", page_icon="🧭", layout="wide")
st.title("🧭 Tableau de bord de navigation")
st.markdown(
    "Bienvenue dans le système de suivi de soins de sage-femme. Sélectionnez une section ci-dessous."
)

# 📁 Organisation des pages par thème
sections = {
    "👤 Données de la patiente": {
        "Démographie": "Demographics.py",
        "Suivi de grossesse": "Pregnancy.py",
        "Nutrition": "Nutrition.py",
        "Vaccination": "Vaccination.py",
        "Complications": "Complication.py",
    },
    "🤰 Soins prénatals": {
        "Soins prénatals": "Prenatal_Care.py",
        "Éducation & Prévention": "Education_and_Prevention.py",
    },
    "🧬 Accouchement": {
        "Intrapartum": "Intrapartum_Care.py",
        "Accouchement": "Child_Birth.py",
    },
    "🩺 Postnatal & bébé": {
        "Soins postnatals": "Post_Natal_Care.py",
        "Postpartum": "Postpartum.py",
        "Allaitement": "Breastfeeding.py",
        "Données bébé": "Baby_Data.py",
    },
    "📈 Suivi global": {"Suivi global": "Throughout_Midwifery_Care.py"},
}

# 🎨 Affichage par section
for section_title, pages in sections.items():
    st.markdown(f"### {section_title}")
    cols = st.columns(3)
    for i, (label, filename) in enumerate(pages.items()):
        with cols[i % 3]:
            if st.button(label):
                st.switch_page(filename)
    st.markdown("---")
