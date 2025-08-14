import streamlit as st
import sqlite3
import bcrypt

DB_PATH = "data.db"  # adjust if your database is elsewhere

st.set_page_config(page_title="🔑 Forgot Password", page_icon="🔑")
st.title("🔑 Reset Your Password")

st.markdown(
    "If you're a midwife and you've forgotten your password, you can reset it here."
)

email = st.text_input("Enter your email address")
new_password = st.text_input("New password", type="password")
confirmation = st.text_input("Confirm new password", type="password")

if st.button("Reset Password"):
    if not email or not new_password or not confirmation:
        st.warning("Please fill in all fields.")
    elif new_password != confirmation:
        st.error("❌ Passwords do not match.")
    else:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        if user and user[5] == "midwife":  # role at index 5
            hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
            cursor.execute(
                "UPDATE users SET mot_de_passe = ? WHERE email = ?", (hashed, email)
            )
            conn.commit()
            conn.close()
            st.success("✅ Password successfully reset.")
        else:
            st.error("❌ No midwife account found with that email.")
