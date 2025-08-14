import streamlit as st

# 🎚️ Sélection du rôle (si applicable à l'inscription)
role = st.selectbox(
    "Sélectionner un rôle", ["Midwife", "Doctor", "Nurse", "Admin", "Other"]
)

# 🧠 Vérification de session_state
if "username" in st.session_state and "role" in st.session_state:
    st.sidebar.markdown(
        f"👤 Connecté en tant que : **{st.session_state['username']}** ({st.session_state['role']})"
    )

    # 🔐 Contrôle d'accès
    if st.session_state["role"] not in ["Admin", "Doctor", "Midwife", "Nurse"]:
        st.warning("⛔ Accès restreint aux professionnels autorisés.")
        st.stop()
else:
    st.sidebar.warning("⚠️ Session utilisateur incomplète.")
    st.stop()
