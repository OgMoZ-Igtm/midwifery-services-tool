import sqlite3
import bcrypt

DB_PATH = "data.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Supprimer les anciennes tables
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("DROP TABLE IF EXISTS patients")
    cursor.execute("DROP TABLE IF EXISTS rendez_vous")
    cursor.execute("DROP TABLE IF EXISTS demographics")
    cursor.execute("DROP TABLE IF EXISTS prenatal_care")

    # Recréer les tables
    cursor.execute(
        """CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        mot_de_passe TEXT NOT NULL,
        photo TEXT,
        role TEXT DEFAULT 'utilisateur'
    )"""
    )

    # Table: demographics
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS demographics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chart_number TEXT,
            dob TEXT,
            date_of_referral TEXT,
            age TEXT,
            community_of_residence TEXT,
            status TEXT,
            referred_by TEXT,
            reason_for_referral TEXT,
            successful_first_contact TEXT,
            eligible_to_midwifery_care TEXT,
            reason_for_non_eligibility TEXT,
            weeks_at_first_appointment TEXT,
            reason_if_never_seen TEXT
        )
    """
    )

    # Table: prenatal_care
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS prenatal_care (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chart_number TEXT,
            date_collection TEXT,
            gpa TEXT,
            edd_date TEXT,
            tobacco_use TEXT,
            substance_use TEXT,
            bmi REAL,
            ce_cle_status TEXT,
            racism TEXT,
            domestic_violence TEXT,
            housing TEXT,
            pregnancy_loss TEXT,
            previous_c_section TEXT,
            previous_vbac TEXT,
            high_risk_pe TEXT,
            gdm TEXT,
            anemia TEXT,
            stbbis TEXT,
            trainee_involved TEXT,
            referral_worker TEXT,
            prenatal_consultation TEXT,
            reason1 TEXT,
            made_with1 TEXT,
            reason2 TEXT,
            made_with2 TEXT,
            reason3 TEXT,
            made_with3 TEXT,
            notes TEXT,
            telehealth TEXT,
            shared_care TEXT,
            transfer_care TEXT,
            other_transfer_reason TEXT,
            transfer_to TEXT,
            care_ended TEXT
        )
    """
    )

    # Table: patients
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            date_naissance TEXT,
            dossier TEXT
        )
    """
    )

    # Table: rendez_vous
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS rendez_vous (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chart_number TEXT,
            appointment_date TEXT,
            appointment_type TEXT,
            appointment_detail TEXT,
            duration_minutes INTEGER,
            attended TEXT,
            notes TEXT,
            user_id INTEGER,
            created_at TEXT,
            modified_at TEXT,
            modified_by INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(modified_by) REFERENCES users(id)
        )
    """
    )


# Supprimer les anciennes tables
cursor.execute("DROP TABLE IF EXISTS users")
cursor.execute("DROP TABLE IF EXISTS patients")
cursor.execute("DROP TABLE IF EXISTS appointments")
cursor.execute("DROP TABLE IF EXISTS messages")
cursor.execute("DROP TABLE IF EXISTS reports")

# Recréer les tables
cursor.execute(
    """
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
)
"""
)

cursor.execute(
    """
CREATE TABLE patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    birth_date TEXT,
    contact TEXT
)
"""
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS bebe (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date_val TEXT,
        poids REAL,
        sommeil TEXT,
        humeur TEXT
    )
    """
)

cursor.execute(
    """
CREATE TABLE appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    date TEXT,
    reason TEXT,
    FOREIGN KEY(patient_id) REFERENCES patients(id)
)
"""
)

cursor.execute(
    """
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT,
    receiver TEXT,
    content TEXT,
    timestamp TEXT
)
"""
)

cursor.execute(
    """
CREATE TABLE reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    report_type TEXT,
    content TEXT,
    date TEXT,
    FOREIGN KEY(patient_id) REFERENCES patients(id)
)
"""
)

cursor.execute("""
CREATE TABLE IF NOT EXISTS vaccination (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_val TEXT,
    type_vaccin TEXT,
    rappel TEXT,
    observations TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS suivi_grossesse (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_val TEXT,
    semaine INTEGER,
    observations TEXT,
    recommandations TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS nutrition (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_val TEXT,
    repas TEXT,
    quantite REAL,
    commentaire TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS bebe (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_val TEXT,
    poids REAL,
    sommeil TEXT,
    humeur TEXT
)
""")


# ⚠️ Ajouter ici toutes tes autres tables
# Exemple :
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS nutrition (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     date_val TEXT,
#     repas TEXT,
#     quantite REAL,
#     observations TEXT
# )
# """)


conn.commit()
conn.close()
print("✅ Base de données initialisée.")


# 🔧 Fonctions utilitaires


def mettre_a_jour_photo(user_id, chemin_photo):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET photo = ? WHERE id = ?", (chemin_photo, user_id))
    conn.commit()
    conn.close()


def ajouter_utilisateur(nom, email, mot_de_passe, role="utilisateur"):
    mot_de_passe_hash = bcrypt.hashpw(mot_de_passe.encode(), bcrypt.gensalt())
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (nom, email, mot_de_passe, role) VALUES (?, ?, ?, ?)",
            (nom, email, mot_de_passe_hash, role),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def verifier_utilisateur(email, mot_de_passe):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    if user and bcrypt.checkpw(mot_de_passe.encode(), user[3]):
        return user
    return None


if __name__ == "__main__":
    init_db()
