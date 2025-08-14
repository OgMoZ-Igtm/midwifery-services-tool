def page_baby()):
    st.header("🍼 Suivi du bébé")
    date_val = st.date_input("Date")
    poids = st.number_input("Poids (kg)", min_value=0.0, step=0.1)
    sommeil = st.text_input("Sommeil")
    humeur = st.text_input("Humeur")

    if st.button("💾 Enregistrer"):
        save_bebe(date_val, poids, sommeil, humeur)
        st.success("✅ Données bébé enregistrées avec succès !")