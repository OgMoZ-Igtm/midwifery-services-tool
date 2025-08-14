elif page == 11:
    st.header("1️⃣1️⃣ Post-partum (Étape 11/12)")
    st.session_state.form_data["Allaitement en cours"] = st.selectbox(
        "Allaitement en cours ?",
        ["Oui", "Non"],
        index=["Oui", "Non"].index(
            st.session_state.form_data.get("Allaitement en cours", "Oui")
        )
    )
    st.session_state.form_data["État psychologique"] = st.selectbox(
        "État psychologique",
        ["Bon", "Moyen", "À surveiller"],
        index=["Bon", "Moyen", "À surveiller"].index(
            st.session_state.form_data.get("État psychologique", "Bon")
        )
    )
    col1, col2 = st.columns([1, 1])
    col1.button("⬅ Retour", on_click=prev_page)
    col2.button("➡ Suivant", on_click=next_page)
