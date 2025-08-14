import streamlit as st
import plotly.express as px
from utils.notifications import get_message_stats

# 🔐 Contrôle d'accès
if st.session_state.get("role") not in ["admin", "doctor", "nurse", "sage-femme"]:
    st.warning("⛔ Accès restreint aux professionnels autorisés.")
    st.stop()


def page_tableau_de_bord():
    st.set_page_config(page_title="Tableau de bord", page_icon="📊")
    st.title("📊 Tableau de bord des échanges")

    stats = get_message_stats()

    if not stats:
        st.info("Aucune donnée disponible pour les échanges.")
        return

    # 📌 Statistiques principales
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📨 Messages envoyés", stats["total"])
    with col2:
        st.metric("👥 Conversations uniques", stats["threads"])
    with col3:
        st.metric("📎 Pièces jointes", stats["attachments"])

    # 📈 Répartition par rôle
    st.subheader("📈 Répartition des messages par rôle")

    if stats["by_role"]:
        df_roles = pd.DataFrame(
            list(stats["by_role"].items()), columns=["Rôle", "Messages"]
        ).sort_values(by="Messages", ascending=False)
        fig_roles = px.bar(
            df_roles, x="Rôle", y="Messages", color="Rôle", title="Messages par rôle"
        )
        st.plotly_chart(fig_roles, use_container_width=True)
    else:
        st.info("Aucun rôle n'a encore envoyé de message.")
