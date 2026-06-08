import streamlit as st
import pandas as pd
import numpy as np

# Catatan: Jika st.set_page_config sudah ada di main.py, baris ini bisa dihapus/dikomen
# agar tidak terjadi bentrok konfigurasi halaman.
st.set_page_config(page_title="Dashboard Admin - FastPresensi", layout="wide")

# ==========================================
# 1. DUMMY DATA
# ==========================================
users = [
    {"nama": "Jovan Oberto", "email": "jovan@fastpresensi.edu", "role": "ADMIN", "join": "Oct 12, 2023"},
    {"nama": "Budi Santoso", "email": "budis@fastpresensi.edu", "role": "GURU", "join": "Jan 15, 2024"},
    {"nama": "Siti Aminah", "email": "sitia@student.edu", "role": "SISWA", "join": "Feb 01, 2024"},
]

classes = [
    {"name": "Mathematics 101", "schedule": "Mon, Wed • 08:00 - 10:00", "teacher": "Ahmad Santoso"},
    {"name": "Physics Advanced", "schedule": "Tue, Thu • 10:30 - 12:30", "teacher": "Budi Darmawan"},
    {"name": "English Literature", "schedule": "Friday • 09:00 - 12:00", "teacher": "Citra Wijaya"},
    {"name": "National History", "schedule": "Mon, Wed • 13:00 - 15:00", "teacher": "Ahmad Santoso"}
]

# ==========================================
# 2. SIDEBAR NAVIGATION (Internal Router)
# ==========================================
with st.sidebar:
    st.title("🎓 FastPresensi")
    st.caption("ADMIN CONSOLE")
    st.divider()
    
    # Menu Navigasi Internal
    menu_selection = st.radio(
        "Admin Menu",
        ["Overview", "Classes", "Users", "Settings"],
        label_visibility="collapsed"
    )
    
    st.write("")
    st.write("")
    st.button("➕ New Session", type="primary", use_container_width=True)


# ==========================================
# 3. KONTEN HALAMAN BERDASARKAN PILIHAN
# ==========================================

if menu_selection == "Overview":
    # --- HALAMAN OVERVIEW ---
    st.subheader("Dashboard Overview")
    st.caption("Welcome back. Here's what's happening today.")
    
    # Metrics
    m1, m2, m3 = st.columns(3)
    with m1:
        with st.container(border=True):
            st.metric(label="👥 TOTAL STUDENTS", value="2,405", delta="-2%")
    with m2:
        with st.container(border=True):
            st.metric(label="🎓 ACTIVE CLASSES", value="142", delta="12%")
    with m3:
        with st.container(border=True):
            st.metric(label="✅ TODAY'S ATTENDANCE", value="94.2%", delta="0%")
            
    st.write("")
    
    # Main Content Area
    col_chart, col_activity = st.columns([2.5, 1])
    
    with col_chart:
        st.write("**Attendance Trends**")
        # Dummy Chart Data
        chart_data = pd.DataFrame(
            np.random.randint(60, 100, size=(7, 1)), 
            columns=["Attendance (%)"]
        )
        st.bar_chart(chart_data)
        
    with col_activity:
        st.write("**Recent Activity**")
        with st.container(border=True):
            st.markdown("👤 **New student enrolled**\n\nAdvanced Physics 101\n\n`2m ago`")
            st.divider()
            st.markdown("📝 **Class created: Intro to...**\n\nProf. Martinez\n\n`1h ago`")
            st.divider()
            st.markdown("⚠️ **Low attendance alert**\n\nCreative Writing (65%)\n\n`3h ago`")
            st.write("")
            st.button("VIEW ALL ACTIVITY", use_container_width=True)

elif menu_selection == "Classes":
    # --- HALAMAN CLASSES ---
    col_head, col_btns = st.columns([6, 4])
    with col_head:
        st.subheader("Class Management")
        st.caption("Manage class schedules and assigned teachers.")
    with col_btns:
        c1, c2 = st.columns(2)
        with c1: st.button("📅 Generate Semester Schedule")
        with c2: st.button("➕ Create New Class", type="primary")

    st.divider()

    with st.container(border=True):
        st.write("**Active Classes**")
        st.write("")
        
        # Table Header
        c1, c2, c3, c4 = st.columns([2.5, 2.5, 2.5, 1])
        c1.caption("**CLASS NAME**")
        c2.caption("**SCHEDULE**")
        c3.caption("**TEACHER**")
        c4.caption("**ACTIONS**")
        st.divider()
        
        # List Data Classes
        for cls in classes:
            u1, u2, u3, u4 = st.columns([2.5, 2.5, 2.5, 1])
            u1.markdown(f"🎒 **{cls['name']}**")
            u2.write(cls['schedule'])
            u3.write(f"🧑‍🏫 {cls['teacher']}")
            with u4:
                if st.button("⋮", key=f"edit_cls_{cls['name']}"):
                    pass
            st.divider()

elif menu_selection == "Users":
    # --- HALAMAN USERS -----
    col_head, col_btns = st.columns([8, 2])
    with col_head:
        st.subheader("User Management")
        st.caption("Manage students, teachers, and administrative staff.")

    with col_btns:
        c1, c2 = st.columns(2)
        with c1: st.button("📤 Bulk")
        with c2: st.button("➕ Add", type="primary")

    st.divider()

    col_left, col_right = st.columns([2.5, 1])

    with col_left:
        tabs = st.tabs(["All Roles", "Admin", "Guru", "Siswa"])
        
        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
        c1.caption("**USER DETAILS**")
        c2.caption("**ROLE**")
        c3.caption("**JOINED**")
        c4.caption("**ACTIONS**")
        st.divider()
        
        for user in users:
            u1, u2, u3, u4 = st.columns([2, 1, 1, 1])
            u1.markdown(f"**{user['nama']}**\n\n{user['email']}")
            u2.write(user['role'])
            u3.write(user['join'])
            with u4:
                if st.button("⋮", key=f"edit_user_{user['nama']}"):
                    pass
            st.divider()

    with col_right:
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
                
                c_cancel, c_create = st.columns(2)
                if c_create.form_submit_button("Create User", type="primary", use_container_width=True):
                    st.toast("User created!")
        
        with st.container(border=True):
            st.subheader("Bulk Generate")
            st.caption("Upload CSV to create multiple accounts.")
            st.file_uploader("Drop CSV here", type=["csv"], label_visibility="collapsed")
            st.button("⬇️ Download Template", use_container_width=True)

else:
    # --- UNTUK HALAMAN  SETTINGS ---
    st.info(f"Halaman **{menu_selection}** sedang dalam tahap pengembangan.")