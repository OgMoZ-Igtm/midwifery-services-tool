import streamlit as st
from datetime import date
import sqlite3
import pandas as pd

st.set_page_config(page_title="👶 Accouchement", page_icon="👶", layout="wide")
st.title("👶 Données d'accouchement")
st.write("Veuillez saisir les informations liées à l'accouchement de la patiente.")


# 📁 Connexion à la base
def get_db_connection():
    return sqlite3.connect("midwifery_data.db")


def create_childbirth_table():
    conn = get_db_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS childbirth (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chart_number TEXT,
            birth_date TEXT,
            gestational_age INTEGER,
            birth_type TEXT,
            complications TEXT,
            newborn_weight REAL,
            newborn_apgar TEXT,
            notes TEXT
        )
    """
    )
    conn.commit()
    conn.close()


def insert_childbirth_data(*args):
    conn = get_db_connection()
    conn.execute(
        """
        INSERT INTO childbirth (
            chart_number, birth_date, gestational_age, birth_type,
            complications, newborn_weight, newborn_apgar, notes
        ) VALUES (?,?,?,?,?,?,?,?)
    """,
        args,
    )
    conn.commit()
    conn.close()


def get_childbirth_data():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM childbirth ORDER BY birth_date DESC", conn)
    conn.close()
    return df


# 📝 Formulaire
create_childbirth_table()

with st.form("childbirth_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    chart_number = col1.text_input("Numéro de dossier")
    birth_date = col2.date_input("Date d'accouchement", value=date.today())
    gestational_age = col3.number_input(
        "Âge gestationnel (semaines)", min_value=20, max_value=45
    )

    birth_type = st.selectbox(
        "Type d'accouchement", ["", "Vaginal", "Césarienne", "Instrumental", "Autre"]
    )
    complications = st.text_area("Complications pendant l'accouchement")
    col4, col5 = st.columns(2)
    newborn_weight = col4.number_input(
        "Poids du nouveau-né (kg)", min_value=0.0, step=0.01
    )
    newborn_apgar = col5.text_input("Score APGAR")

    notes = st.text_area("Notes supplémentaires")

    submitted = st.form_submit_button("✅ Soumettre")
    if submitted:
        insert_childbirth_data(
            chart_number,
            str(birth_date),
            gestational_age,
            birth_type,
            complications,
            newborn_weight,
            newborn_apgar,
            notes,
        )
        st.success("✅ Données d'accouchement enregistrées avec succès !")
        st.rerun()

# 📋 Historique
st.markdown("---")
st.subheader("Historique des accouchements")
df = get_childbirth_data()
if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.info("Aucune donnée d'accouchement enregistrée.")
