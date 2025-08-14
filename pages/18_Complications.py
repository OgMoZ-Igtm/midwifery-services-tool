elif page == 8:
    st.header("8️⃣ Complications médicales (Étape 8/12)")
    st.session_state.form_data["Diabète gestationnel"] = st.selectbox(
        "Diabète gestationnel diagnostiqué ?",
        ["Oui", "Non"],
        index=["Oui", "Non"].index(
            st.session_state.form_data.get("Diabète gestationnel", "Non")
        )
    )
    st.session_state.form_data["Hypertension"] = st.selectbox(
        "Hypertension artérielle ?",
        ["Oui", "Non"],
        index=["Oui", "Non"].index(
            st.session_state.form_data.get("Hypertension", "Non")
        )
    )
    st.session_state.form_data["Autres complications"] = st.text_area(
        "Autres complications",
        value=st.session_state.form_data.get("Autres complications", "")
    )
    col1, col2 = st.columns([1, 1])
    col1.button("⬅ Retour", on_click=prev_page)
    col2.button("➡ Suivant", on_click=next_page)
