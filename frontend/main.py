import streamlit as st

st.set_page_config(page_title="FastPresensi", layout="wide")

login_page = st.Page("views/login.py", title="Login", icon="🔑")
settings_page = st.Page("views/settings.py", title="Settings", icon="⚙️")

admin_pages = [
    st.Page("views/admin/classes.py", title="Classes", icon="📚"),
    st.Page("views/admin/users.py", title="Users", icon="👥"),
    settings_page,
]

guru_pages = [
    st.Page("views/guru/attendance.py", title="Attendance", icon="📋"),
    settings_page,
]

siswa_pages = [
    st.Page("views/siswa/attendance.py", title="Attendance", icon="📋"),
    settings_page,
]

if "access_token" not in st.session_state:
    pg = st.navigation([login_page], position="hidden")
else:
    role = st.session_state.get("user_data", {}).get("role", "").upper()
    if role == "ADMIN":
        pg = st.navigation(admin_pages)
    elif role == "GURU":
        pg = st.navigation(guru_pages)
    else:
        pg = st.navigation(siswa_pages)

pg.run()
