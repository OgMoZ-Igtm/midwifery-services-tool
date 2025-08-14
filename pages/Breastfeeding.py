import streamlit as st


# 🔁 Navigation helpers
def prev_page():
    st.session_state.page = max(st.session_state.page - 1, 1)


def next_page():
    st.session_state.page = min(st.session_state.page + 1, total_pages)


# 🧠 Initialisation
if "form_data" not in st.session_state:
    st.session_state.form_data = {}

if "page" not in st.session_state:
    st.session_state.page = 1

total_pages = 7

# 📄 Step 1: Patient Info
if st.session_state.page == 1:
    st.header("1️⃣ Patient Information (Step 1/7)")

    st.session_state.form_data["Name"] = st.text_input(
        "Patient's full name", value=st.session_state.form_data.get("Name", "")
    )

    st.session_state.form_data["Age"] = st.number_input(
        "Age",
        min_value=0,
        max_value=120,
        value=st.session_state.form_data.get("Age", 30),
    )

    st.session_state.form_data["Contact"] = st.text_input(
        "Contact number or email", value=st.session_state.form_data.get("Contact", "")
    )

    col1, col2 = st.columns([1, 1])
    col1.button("⬅ Back", on_click=prev_page, disabled=True)
    col2.button("➡ Next", on_click=next_page)

# 📄 Step 2: Medical History
elif st.session_state.page == 2:
    st.header("2️⃣ Medical History (Step 2/7)")

    st.session_state.form_data["Known Conditions"] = st.text_area(
        "Known medical conditions",
        value=st.session_state.form_data.get("Known Conditions", ""),
    )

    st.session_state.form_data["Medications"] = st.text_area(
        "Current medications", value=st.session_state.form_data.get("Medications", "")
    )

    col1, col2 = st.columns([1, 1])
    col1.button("⬅ Back", on_click=prev_page)
    col2.button("➡ Next", on_click=next_page)

# 📄 Step 3: Pregnancy Details
elif st.session_state.page == 3:
    st.header("3️⃣ Pregnancy Details (Step 3/7)")

    st.session_state.form_data["Weeks Pregnant"] = st.number_input(
        "Weeks of pregnancy",
        min_value=0,
        max_value=42,
        value=st.session_state.form_data.get("Weeks Pregnant", 20),
    )

    st.session_state.form_data["Pregnancy Type"] = st.selectbox(
        "Type of pregnancy",
        ["Single", "Twins", "Triplets", "Other"],
        index=["Single", "Twins", "Triplets", "Other"].index(
            st.session_state.form_data.get("Pregnancy Type", "Single")
        ),
    )

    col1, col2 = st.columns([1, 1])
    col1.button("⬅ Back", on_click=prev_page)
    col2.button("➡ Next", on_click=next_page)

# 📄 Step 4: Lifestyle
elif st.session_state.page == 4:
    st.header("4️⃣ Lifestyle (Step 4/7)")

    st.session_state.form_data["Smoking"] = st.selectbox(
        "Does the patient smoke?",
        ["No", "Occasionally", "Regularly"],
        index=["No", "Occasionally", "Regularly"].index(
            st.session_state.form_data.get("Smoking", "No")
        ),
    )

    st.session_state.form_data["Alcohol"] = st.selectbox(
        "Alcohol consumption?",
        ["None", "Occasional", "Frequent"],
        index=["None", "Occasional", "Frequent"].index(
            st.session_state.form_data.get("Alcohol", "None")
        ),
    )

    st.session_state.form_data["Physical Activity"] = st.text_area(
        "Describe physical activity level",
        value=st.session_state.form_data.get("Physical Activity", ""),
    )

    col1, col2 = st.columns([1, 1])
    col1.button("⬅ Back", on_click=prev_page)
    col2.button("➡ Next", on_click=next_page)

# 📄 Step 5: Psychological State
elif st.session_state.page == 5:
    st.header("5️⃣ Psychological State (Step 5/7)")

    st.session_state.form_data["Mood"] = st.selectbox(
        "Current mood",
        ["Stable", "Anxious", "Depressed", "Irritable", "Other"],
        index=["Stable", "Anxious", "Depressed", "Irritable", "Other"].index(
            st.session_state.form_data.get("Mood", "Stable")
        ),
    )

    st.session_state.form_data["Mental Health Notes"] = st.text_area(
        "Additional mental health observations",
        value=st.session_state.form_data.get("Mental Health Notes", ""),
    )

    col1, col2 = st.columns([1, 1])
    col1.button("⬅ Back", on_click=prev_page)
    col2.button("➡ Next", on_click=next_page)

# 📄 Step 6: Breastfeeding & Nutrition
elif st.session_state.page == 6:
    st.header("6️⃣ Breastfeeding & Nutrition (Step 6/7)")

    st.subheader("Breastfeeding")

    st.session_state.form_data["Planned Breastfeeding"] = st.selectbox(
        "Is the patient planning to breastfeed?",
        ["Yes", "No", "Unsure"],
        index=["Yes", "No", "Unsure"].index(
            st.session_state.form_data.get("Planned Breastfeeding", "Yes")
        ),
    )

    st.session_state.form_data["Breastfeeding Notes"] = st.text_area(
        "Additional notes (optional)",
        value=st.session_state.form_data.get("Breastfeeding Notes", ""),
    )

    st.markdown("---")
    st.subheader("Nutrition")

    st.session_state.form_data["Suspected Deficiencies"] = st.multiselect(
        "Suspected deficiencies (select all that apply)",
        ["Iron", "Calcium", "Vitamin D", "Iodine", "Vitamin B12"],
        default=st.session_state.form_data.get("Suspected Deficiencies", []),
    )

    st.session_state.form_data["Supplementation Received"] = st.selectbox(
        "Has the patient received supplementation?",
        ["Yes", "No", "Pending"],
        index=["Yes", "No", "Pending"].index(
            st.session_state.form_data.get("Supplementation Received", "No")
        ),
    )

    col1, col2 = st.columns([1, 1])
    col1.button("⬅ Back", on_click=prev_page)
    col2.button("➡ Next", on_click=next_page)

# 📄 Step 7: Summary
elif st.session_state.page == 7:
    st.header("📋 Summary (Step 7/7)")
    st.write("Here is a summary of the information collected:")

    for key, value in st.session_state.form_data.items():
        st.markdown(f"**{key}**: {value if value else '—'}")

    st.markdown("---")
    st.success("✅ Form completed!")

    col1, col2 = st.columns([1, 1])
    col1.button("⬅ Back", on_click=prev_page)
    col2.button("📤 Submit", on_click=lambda: st.info("Data submitted! (placeholder)"))
