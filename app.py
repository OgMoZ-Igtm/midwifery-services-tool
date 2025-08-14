# 📦 Core
import streamlit as st

# 🔐 Auth
from utils.auth import require_login, show_auth_sidebar
from utils.auth_secure import hash_password

# 🗄️ Database
from utils.database import get_all_users, get_all_patients, get_all_rendez_vous

# 🧩 UI Components
from components import show_user_info

# ⚙️ Page Configuration
st.set_page_config(page_title="Midwives Platform", page_icon="👩‍⚕️", layout="wide")

# 🔐 Authentication Flow
require_login()
show_auth_sidebar()
show_user_info()

# 🧪 Debug (remove in production)
print(hash_password("test123"))

# 🏠 Home
st.title("👩‍⚕️ Welcome to the Midwives Platform")
role = st.session_state.get("role")

# 📊 Quick Overview
users = get_all_users()
patients = get_all_patients()
rendez_vous = get_all_rendez_vous()

st.subheader("📊 Quick Overview")
col1, col2, col3 = st.columns(3)

if role == "admin":
    with col1:
        st.metric("Users", str(len(users)))
    with col2:
        st.metric("Patients", str(len(patients)))
    with col3:
        st.metric("Upcoming Appointments", str(len(rendez_vous)))
    st.success("🛠️ You are an administrator. You can manage all users.")
    st.markdown("👉 Use the menu to access account and data management.")
elif role == "midwife":
    with col1:
        st.metric("Your Patients", str(len(patients)))
    with col2:
        st.metric("Upcoming Appointments", str(len(rendez_vous)))
    with col3:
        st.empty()
    st.info(
        "👩‍⚕️ You are a midwife. Access your patients and appointments via the menu."
    )
else:
    st.warning("⚠️ Unknown role. Please contact the administrator.")

# 📂 Navigation Sidebar
st.sidebar.header("📂 Navigation")
st.sidebar.page_link("pages/1_📊_Statistics.py", label="📊 Statistics")
st.sidebar.page_link("pages/2_🛠️_Administration.py", label="🛠️ Administration")
st.sidebar.page_link("pages/3_📝_Data_Entry.py", label="📝 Data Entry")
st.sidebar.page_link("pages/4_💬_Messages.py", label="💬 Messages")
st.sidebar.page_link("pages/5_📅_Appointments.py", label="📅 Appointments")
st.sidebar.page_link("pages/6_📄_Reports.py", label="📄 Reports")
