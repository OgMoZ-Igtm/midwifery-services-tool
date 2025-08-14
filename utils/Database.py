import sqlite3
from typing import List, Tuple, Any, Optional
import utils.database

DB_PATH = "data.db"

# 🔌 Connexion à la base
def get_db_connection() -> sqlite3.Connection:
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        print(f"Erreur de connexion à la base de données : {e}")
        raise


# 📋 Lecture générique
def fetch_all(query: str, params: Tuple = ()) -> List[Tuple[Any]]:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return results
    except sqlite3.Error as e:
        print(f"Erreur lors de la lecture : {e}")
        return []


# ➕ Insertion générique
def insert_data(query: str, params: Tuple) -> bool:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de l'insertion : {e}")
        return False


# ✏️ Mise à jour générique
def update_data(query: str, params: Tuple) -> bool:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de la mise à jour : {e}")
        return False


# ❌ Suppression générique
def delete_data(query: str, params: Tuple) -> bool:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de la suppression : {e}")
        return False


# 👥 Utilisateurs
def get_all_users() -> List[Tuple[Any]]:
    return fetch_all("SELECT * FROM users")


def add_user(name: str, email: str) -> bool:
    return insert_data("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))


def update_user_email(user_id: int, new_email: str) -> bool:
    return update_data("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))


def delete_user(user_id: int) -> bool:
    return delete_data("DELETE FROM users WHERE id = ?", (user_id,))


# 🧑‍⚕️ Patients
def get_all_patients() -> List[Tuple[Any]]:
    return fetch_all("SELECT * FROM patients")


def add_patient(name: str, birthdate: str) -> bool:
    return insert_data(
        "INSERT INTO patients (name, birthdate) VALUES (?, ?)", (name, birthdate)
    )


def update_patient_name(patient_id: int, new_name: str) -> bool:
    return update_data(
        "UPDATE patients SET name = ? WHERE id = ?", (new_name, patient_id)
    )


def delete_patient(patient_id: int) -> bool:
    return delete_data("DELETE FROM patients WHERE id = ?", (patient_id,))


# 📅 Rendez-vous
def get_all_rendez_vous() -> List[Tuple[Any]]:
    return fetch_all("SELECT * FROM rendez_vous")


def add_rendez_vous(patient_id: int, date: str, notes: Optional[str]) -> bool:
    return insert_data(
        "INSERT INTO rendez_vous (patient_id, date, notes) VALUES (?, ?, ?)",
        (patient_id, date, notes),
    )


def update_rendez_vous_notes(rdv_id: int, new_notes: str) -> bool:
    return update_data(
        "UPDATE rendez_vous SET notes = ? WHERE id = ?", (new_notes, rdv_id)
    )


def delete_rendez_vous(rdv_id: int) -> bool:
    return delete_data("DELETE FROM rendez_vous WHERE id = ?", (rdv_id,))
