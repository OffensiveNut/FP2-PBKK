import streamlit as st

st.set_page_config(page_title="Dashboard Admin - FastPresensi", layout="wide")

users = [
    {"nama": "Jovan Oberto", "email": "jovan@fastpresensi.edu", "role": "ADMIN", "join": "Oct 12, 2023"},
    {"nama": "Budi Santoso", "email": "budis@fastpresensi.edu", "role": "GURU", "join": "Jan 15, 2024"},
    {"nama": "Siti Aminah", "email": "sitia@student.edu", "role": "SISWA", "join": "Feb 01, 2024"},
]

# --- HEADER SECTION ---
col_head, col_btns = st.columns([8, 2])
with col_head:
    st.subheader("User Management")
    st.caption("Manage students, teachers, and administrative staff.")

with col_btns:
    c1, c2 = st.columns(2)
    with c1: st.button("📤 Bulk")
    with c2: st.button("➕ Add", type="primary")

st.divider()

# --- MAIN CONTENT ---
col_left, col_right = st.columns([2.5, 1])

with col_left:
    # Filter Tabs
    tabs = st.tabs(["All Roles", "Admin", "Guru", "Siswa"])
    
    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    c1.write("**User Details**")
    c2.write("**Role**")
    c3.write("**Joined**")
    c4.write("**Actions**")
    
    # List Data
    for user in users:
        u1, u2, u3, u4 = st.columns([2, 1, 1, 1])
        u1.markdown(f"**{user['nama']}**\n\n{user['email']}")
        u2.write(user['role'])
        u3.write(user['join'])
        with u4:
            if st.button("⋮", key=f"edit_{user['nama']}"):
                pass

with col_right:
    # --- QUICK ADD FORM ---
    with st.container(border=True):
        st.subheader("Quick Add User")
        with st.form("add_user_form", border=False):
            st.text_input("Full Name", placeholder="e.g. John Doe")
            st.text_input("Email Address", placeholder="john@example.com")
            
            c_user, c_pass = st.columns(2)
            c_user.text_input("Username")
            c_pass.text_input("Password", type="password")
            
            st.selectbox("Role", ["Admin", "Guru", "Siswa"])
            st.selectbox("Assign Class (Optional)", ["Math", "Informatics", "Physics"])
            
            # Action Buttons
            c_cancel, c_create = st.columns(2)
            if c_create.form_submit_button("Create User", type="primary", use_container_width=True):
                st.toast("User created!")
    
    # --- BULK GENERATE SECTION ---
    with st.container(border=True):
        st.subheader("Bulk Generate")
        st.caption("Upload CSV to create multiple accounts.")
        st.file_uploader("Drop CSV here", type=["csv"], label_visibility="collapsed")
        st.button("⬇️ Download Template", use_container_width=True)