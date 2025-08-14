elif page == 12:
    st.header("1️⃣2️⃣ Éducation & Prévention (Étape 12/12)")
    st.session_state.form_data["Informations données"] = st.multiselect(
        "Informations transmises à la patiente",
        ["Hygiène", "Allaitement", "Contraception", "Nutrition", "Préparation accouchement"],
        default=st.session_state.form_data.get("Informations données", [])
    )
    st.session_state.form_data["Participation séances"] = st.selectbox(
        "Participation aux séances collectives",
        ["Oui", "Non"],
        index=["Oui", "Non"].index(
            st.session_state.form_data.get("Participation séances", "Oui")
        )
    )
    col1, col2 = st.columns([1, 1])
    col1.button("⬅ Retour", on_click=prev_page)
    col2.button("➡ Terminer", on_click=next_page)
