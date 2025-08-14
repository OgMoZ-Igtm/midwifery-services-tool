import sqlite3

DB_PATH = "data.db"


def get_db_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table: users
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            hashed_password TEXT,
            professional_title TEXT,
            email TEXT,
            role TEXT DEFAULT 'patient'
        )
    """
    )

    # Table: rendez_vous
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS rendez_vous (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT,
            date TEXT,
            heure TEXT,
            motif TEXT
        )
    """
    )

    # Table: demographics
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS demographics (
            chart_number TEXT PRIMARY KEY,
            nom TEXT,
            prenom TEXT,
            date_naissance TEXT,
            sexe TEXT,
            adresse TEXT,
            telephone TEXT
        )
    """
    )

    # Table: prenatal_care
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS prenatal_care (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chart_number TEXT,
            nom TEXT,
            date_visite TEXT,
            semaines_gestation INTEGER,
            tension_arterielle TEXT,
            remarques TEXT
        )
    """
    )

    # Table: intrapartum_care
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS intrapartum_care (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT,
            date_accouchement TEXT,
            type_accouchement TEXT,
            observations TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Table: post_natal_care
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS post_natal_care (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT,
            date_suivi TEXT,
            etat_bebe TEXT,
            commentaires TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Table: throughout_midwifery_care
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS throughout_midwifery_care (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT,
            date_debut TEXT,
            date_fin TEXT,
            types_soins TEXT,
            resume TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # ✅ Correction ici
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS vaccination_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chart_number TEXT,
            nom TEXT,
            vaccin TEXT,
            date_admin TEXT,
            administrateur TEXT,
            remarques TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS nutrition_followup (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chart_number TEXT,
            nom TEXT,
            date_suivi TEXT,
            poids REAL,
            recommandations TEXT,
            nutritionniste TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS mental_health_visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chart_number TEXT,
            nom TEXT,
            date_visite TEXT,
            professionnel TEXT,
            diagnostic TEXT,
            plan_suivi TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    conn.commit()
    conn.close()


# 👇 Exécution directe
if __name__ == "__main__":
    init_db()
    print("✅ Base de données initialisée avec succès.")
