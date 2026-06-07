import streamlit as st





login_page = st.Page("views/login.py", title="Login", icon="🔑")
siswa_page = st.Page("views/dashboard_siswa.py", title="Dashboard Siswa", icon="🎓")
guru_page  = st.Page("views/dashboard_guru.py", title="Dashboard Guru", icon="👨‍🏫")
admin_page = st.Page("views/dashboard_admin.py", title="Dashboard Admin", icon="⚙️")


pg = st.navigation([login_page, siswa_page, guru_page, admin_page])


pg.run()