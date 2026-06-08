import streamlit as st
from utils.api_client import api_login

st.set_page_config(page_title="Login - FastPresensi", layout="centered")

with st.container(border=True):
    st.subheader("🔐 Login FastPresensi")
    
    with st.form("form_login", border=False):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_login = st.form_submit_button("Login", type="primary", use_container_width=True)
        
        if submit_login:
            if not username or not password:
                st.warning("⚠️ Silakan isi username dan password terlebih dahulu.")
            else:
                with st.spinner("Memeriksa kredensial..."):
                    # Panggil fungsi penembak API
                    is_success, result = api_login(username, password)
                    
                    if is_success:
                        if not isinstance(result, dict):
                            st.error("Format respons tidak valid")
                            st.stop()

                        st.session_state["access_token"] = result["access_token"]
                        st.session_state["user_data"] = result["user"]

                        st.success("✅ Login berhasil! Mengarahkan ke dashboard...")

                        role = result["user"].get("role", "siswa").lower()
                        
                        if role == "admin":
                            st.switch_page("views/dashboard_admin.py")
                        elif role == "guru":
                            st.switch_page("views/dashboard_guru.py")
                        else:
                            st.switch_page("views/dashboard_siswa.py")
                            
                    else:
                        # Tampilkan pesan error dari backend jika gagal
                        st.error(f"❌ {result}")