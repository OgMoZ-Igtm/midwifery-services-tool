import os

# Nom du fichier à conserver
safe_file = "data.db"

# Lister tous les fichiers .db dans le dossier courant
db_files = [f for f in os.listdir() if f.endswith(".db") and f != safe_file]

if not db_files:
    print("✅ Aucun fichier .db à supprimer. Tout est propre.")
else:
    print("🧹 Suppression des fichiers suivants :")
    for file in db_files:
        print(f"  - {file}")
        os.remove(file)
    print("✅ Nettoyage terminé. Seul data.db est conservé.")
