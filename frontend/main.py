import streamlit as st

# 1. Definisikan semua halaman
login_page = st.Page("views/login.py", title="Login", icon="🔑")
siswa_page = st.Page("views/dashboard_siswa.py", title="Dashboard Siswa", icon="🎓")
guru_page  = st.Page("views/dashboard_guru.py", title="Dashboard Guru", icon="👨‍🏫")
admin_page = st.Page("views/dashboard_admin.py", title="Dashboard Admin", icon="⚙️")

# 2. Logika Routing Berdasarkan Session State
if "access_token" not in st.session_state:
    # Jika belum login, HANYA muat halaman login.
    # position="hidden" akan menghilangkan menu default bawaan Streamlit.
    pg = st.navigation([login_page], position="hidden")
else:
    # Jika sudah login, ambil role dari user_data (Amankan dengan .upper() agar tidak case-sensitive)
    role = st.session_state.get("user_data", {}).get("role", "SISWA").upper()
    
    if role == "ADMIN":
        pg = st.navigation([admin_page], position="hidden")
    elif role == "GURU":
        pg = st.navigation([guru_page], position="hidden")
    else:
        pg = st.navigation([siswa_page], position="hidden")

# 3. Eksekusi Halaman
pg.run()