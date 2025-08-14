# Étape 3 : Suivi de grossesse
elif page == 3:
    st.header("3️⃣ Suivi de grossesse")
    st.session_state.form_data["Nombre de grossesses"] = st.number_input(
        "Nombre de grossesses", min_value=0, step=1,
        value=st.session_state.form_data.get("Nombre de grossesses", 0)
    )
    st.session_state.form_data["Risque estimé"] = st.selectbox(
        "Risque estimé", ["Faible", "Modéré", "Élevé"],
        index=["Faible", "Modéré", "Élevé"].index(st.session_state.form_data.get("Risque estimé", "Faible"))
    )
    col1, col2 = st.columns([1, 1])
    col1.button("⬅ Retour", on_click=prev_page)
    col2.button("➡ Suivant", on_click=next_page)

# Étape 4 : Symptômes et commentaires
elif page == 4:
    st.header("4️⃣ Symptômes et commentaires")
    st.session_state.form_data["Symptômes"] = st.text_area("Symptômes", value=st.session_state.form_data.get("Symptômes", ""))
    st.session_state.form_data["Commentaires"] = st.text_area("Commentaires", value=st.session_state.form_data.get("Commentaires", ""))
    st.session_state.form_data["Date de consultation"] = st.date_input(
        "Date de consultation", value=st.session_state.form_data.get("Date de consultation", date.today())
    )
    col1, col2 = st.columns([1, 1])
    col1.button("⬅ Retour", on_click=prev_page)
    col2.button("➡ Suivant", on_click=next_page)
