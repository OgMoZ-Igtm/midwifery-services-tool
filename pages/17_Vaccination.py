elif page == 6:
    st.header("6️⃣ Allaitement (Étape 6/12)")
    st.session_state.form_data["Allaitement prévu"] = st.selectbox(
        "La patiente prévoit-elle d’allaiter ?",
        ["Oui", "Non", "Incertain"],
        index=["Oui", "Non", "Incertain"].index(
            st.session_state.form_data.get("Allaitement prévu", "Oui")
        )
    )
    st.session_state.form_data["Observations allaitement"] = st.text_area(
        "Observations (facultatif)",
        value=st.session_state.form_data.get("Observations allaitement", "")
    )
    col1, col2 = st.columns([1, 1])
    col1.button("⬅ Retour", on_click=prev_page)
    col2.button("➡ Suivant", on_click=next_page)
