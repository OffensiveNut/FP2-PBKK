import streamlit as st

from utils.api_client import api_request
from utils.state import logout

st.subheader("⚙️ Settings", divider=True)

col1, col2 = st.columns([5, 1])
with col2:
    if st.button("🚪 Logout", type="secondary", use_container_width=True):
        logout()

user = st.session_state.get("user_data")
if not isinstance(user, dict):
    st.error("Data user tidak ditemukan")
    st.stop()

with st.container(border=True):
    st.write(f"**Nama:** {user.get('nama_lengkap', '-')}")
    st.write(f"**Username:** {user.get('username', '-')}")
    st.write(f"**Email:** {user.get('email', '-')}")
    st.write(f"**Role:** {user.get('role', '-')}")

st.write("")
with st.container(border=True):
    st.markdown("**Ganti Password**")
    with st.form("form_change_password", border=False):
        current = st.text_input("Password Saat Ini", type="password")
        new = st.text_input("Password Baru", type="password")
        confirm = st.text_input("Konfirmasi Password Baru", type="password")
        if st.form_submit_button("💾 Update Password", type="primary", use_container_width=True):
            if not current or not new or not confirm:
                st.error("Semua field harus diisi")
            elif new != confirm:
                st.error("Password baru tidak cocok")
            elif len(new) < 8:
                st.error("Password minimal 8 karakter")
            else:
                ok, msg = api_request("PUT", f"/users/{user['id']}", json={
                    "password": new,
                })
                if ok:
                    st.success("Password berhasil diubah")
                else:
                    st.error(msg)
