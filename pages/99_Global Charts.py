import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Tables globales", layout="wide")
st.title("🗂️ Vue globale des tables")


# Connexion à la base
def get_table(table_name):
    try:
        conn = sqlite3.connect("data.db")
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        conn.close()
        return df
    except Exception as e:
        return None, str(e)


# Liste des tables à afficher
tables = {
    "Utilisateurs": "users",
    "Patients": "demographics",
    "Soins prénatals": "prenatal_care",
    "Rendez-vous": "rendez_vous",
    "Vaccinations": "vaccinations",
    "Allergies": "allergies",
    "Antécédents médicaux": "antecedents",
    "Examens physiques": "examens_physiques",
    "Laboratoire": "laboratoire",
    "Échographies": "echographies",
    "Accouchements": "accouchements",
    "Suivi postnatal": "postnatal_followup",
    "Statistiques": "statistiques",
    "Notes cliniques": "notes_cliniques",
}

# Onglets dynamiques
tabs = st.tabs(list(tables.keys()))

for i, (label, table_name) in enumerate(tables.items()):
    with tabs[i]:
        df = get_table(table_name)
        if isinstance(df, tuple):  # Erreur
            st.error(
                f"❌ Erreur lors du chargement de la table '{table_name}': {df[1]}"
            )
            continue

        st.subheader(f"📋 Table : {table_name}")
        st.caption(f"Nombre d'enregistrements : {len(df)}")

        # 🔍 Filtres dynamiques
        with st.expander("🔍 Filtrer les colonnes"):
            selected_columns = st.multiselect(
                "Colonnes à afficher", df.columns.tolist(), default=df.columns.tolist()
            )
            df_filtered = df[selected_columns]

        st.dataframe(df_filtered, use_container_width=True)

        # 📥 Export CSV
        csv = df_filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Exporter en CSV",
            data=csv,
            file_name=f"{table_name}.csv",
            mime="text/csv",
        )
