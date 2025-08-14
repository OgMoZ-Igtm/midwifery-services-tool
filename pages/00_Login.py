import streamlit as st
import sqlite3
import bcrypt
from db import verifier_utilisateur

st.set_page_config(page_title="🔐 Connexion & Profil", page_icon="🔐")

# ------------------ Connexion ------------------
st.title("🔐 Connexion")

username = st.text_input("Nom d'utilisateur")
password = st.text_input("Mot de passe", type="password")
role = st.selectbox("Rôle", ["patient", "doctor", "nurse", "admin"])

if st.button("Se connecter"):
    utilisateur = verifier_utilisateur(username, role)
    if utilisateur and bcrypt.checkpw(password.encode(), utilisateur[3]):
        st.session_state.authenticated = True
        st.session_state.username = username
        st.session_state.role = role
        st.session_state.utilisateur = utilisateur
        st.success("✅ Connexion réussie.")
        st.rerun()
    else:
        st.error("❌ Identifiants incorrects ou rôle non autorisé.")

# 🔐 Contrôle d'accès
if st.session_state.get("authenticated") and st.session_state.get("role") not in [
    "admin",
    "doctor",
    "nurse",
]:
    st.warning("⛔ Accès restreint aux professionnels autorisés.")
    st.stop()

# ------------------ Réinitialisation du mot de passe ------------------
st.markdown("---")
st.subheader("🔁 Réinitialiser le mot de passe")

email = st.text_input("📧 Entrez votre adresse email")

if st.button("📩 Envoyer le lien de réinitialisation"):
    if email:
        # À intégrer avec un service d'envoi réel
        st.success(f"📬 Un lien de réinitialisation a été envoyé à {email}.")
    else:
        st.warning("⚠️ Veuillez entrer une adresse email valide.")

# ------------------ Modification du profil ------------------
st.markdown("---")
st.title("✏️ Modifier mes informations")

if "utilisateur" in st.session_state and st.session_state.utilisateur:
    user = st.session_state.utilisateur
    st.subheader(f"Modifier le profil de {user[1]}")

    with st.form("form_modif"):
        nouveau_nom = st.text_input("Nouveau nom", value=user[1])
        nouvel_email = st.text_input("Nouvel email", value=user[2])
        ancien_mdp = st.text_input("Mot de passe actuel", type="password")
        nouveau_mdp = st.text_input("Nouveau mot de passe", type="password")
        confirmer_mdp = st.text_input(
            "Confirmer le nouveau mot de passe", type="password"
        )

        submit = st.form_submit_button("Mettre à jour")

        if submit:
            if not bcrypt.checkpw(ancien_mdp.encode(), user[3]):
                st.error("❌ Mot de passe actuel incorrect.")
            elif nouveau_mdp and nouveau_mdp != confirmer_mdp:
                st.error("⚠️ Les nouveaux mots de passe ne correspondent pas.")
            else:
                conn = sqlite3.connect("users.db")
                cursor = conn.cursor()

                # Mise à jour du mot de passe si fourni
                hash_mdp = (
                    bcrypt.hashpw(nouveau_mdp.encode(), bcrypt.gensalt())
                    if nouveau_mdp
                    else user[3]
                )

                try:
                    cursor.execute(
                        """
                        UPDATE users SET nom = ?, email = ?, mot_de_passe = ?
                        WHERE id = ?
                        """,
                        (nouveau_nom, nouvel_email, hash_mdp, user[0]),
                    )
                    conn.commit()
                    st.success("✅ Profil mis à jour avec succès.")
                    st.session_state.utilisateur = (
                        user[0],
                        nouveau_nom,
                        nouvel_email,
                        hash_mdp,
                        user[4],
                    )
                except sqlite3.IntegrityError:
                    st.error("⚠️ Cet email est déjà utilisé.")
                finally:
                    conn.close()
else:
    st.warning("🔒 Vous devez être connecté pour modifier votre profil.")
